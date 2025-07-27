import cv2
import numpy as np
import os
import face_recognition
from playsound import playsound
from message import send_email, send_sms
import time
import sys
from gui.gui import guiwindow
import datetime
import pickle



prev_time = 0
LOG_DIR = "logs"

#create log if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    

# Alarms
def threat_alarm():
    playsound("alarms/threat.wav")

def safe_alarm():
    playsound("alarms/safe.wav")




encodings_path = "encodings/face_encodings.pkl"

if os.path.exists(encodings_path):
    with open(encodings_path, "rb") as f:
        face_encode, face_name = pickle.load(f)
else:
    raise FileNotFoundError("❌ Face encodings not found. Please run `save_encodings.py` first.")




try:
    face_cap = cv2.VideoCapture(0)
    if not face_cap.isOpened():
        raise RuntimeError("❌ Error: Could not access the webcam. Please check if it's connected, or if it's being used by another application.")
except Exception as e:
    print(str(e))
    sys.exit()

detection_time = {}
last_alarmed = {}

def log_event(event_type,name, confidence):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp},{event_type} ,{name}, {confidence}\n"
    file_exist=os.path.isfile(os.path.join(LOG_DIR, "detection_alerts.csv"))
    with open(os.path.join(LOG_DIR, "detection_alerts.csv"), "a") as log_file:
        if not file_exist:
            log_file.write("Timestamp,Event Type ,Name, Confidence\n")
        log_file.write(log_entry)
def get_frame():
    global prev_time

    ret, frame = face_cap.read()
    if not ret:
        return None

    frame = cv2.flip(frame, 1)
    curr_time = time.time()

    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0

    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (520,250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    curr_names = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(face_encode, face_encoding)
        best_match_index = np.argmin(face_distances)
        name = "No match"

        if face_distances[best_match_index] < 0.4:
            name = face_name[best_match_index]
            confidence = (1 - face_distances[best_match_index]) * 100
            confidence_text = f"{confidence:.2f}%"
        else:
            confidence_text = f"{(1 - face_distances[best_match_index]) * 100:.2f}%"

        curr_names.append(name)

        top, right, bottom, left = [coord * 4 for coord in face_location]
        color = (0, 255, 0) if name != "No match" else (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, confidence_text, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        #added: a countdown timer for each detected face

        if name in detection_time:
            scan_time = curr_time - detection_time[name]
            remaining_time = max(0, 10 - int(scan_time))
            cv2.putText(frame, f"{remaining_time:.1f}s", (left, top + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

    #starting timer

    detected_now = set(curr_names)
    for name in detected_now:
        if name not in detection_time:

            #first detection
            detection_time[name] = curr_time
            last_alarmed[name] = 0

    for name in detected_now:
        scan_time = curr_time - detection_time[name]
        if scan_time >= 10 and (curr_time - last_alarmed.get(name, 0)) >= 30:
            if name != "No match":
                threat_alarm()
                send_email(name, frame, confidence)
                send_sms(name,confidence)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(LOG_DIR, filename)
                cv2.imwrite(filepath, frame)
                log_event("THREAT",name, confidence)
            else:
                safe_alarm()
            last_alarmed[name] = curr_time
            log_event("SAFE", name, confidence)
    for name in list(detection_time.keys()):
        if name not in detected_now:
            del detection_time[name]

    return frame

# Start GUI
video_app = guiwindow(get_frame_callback=get_frame)
video_app.run()
