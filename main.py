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

# --- Pause/Resume global state ---
is_paused = False
pause_start_time = None
paused_names_time = {}
last_frame = None  # To freeze video while paused

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

print("🔧 Security Screening System - Full Face Recognition Mode")
print("📋 Status Messages Feature: ✅ Active")
print("🔍 Face Recognition: ✅ Using face_recognition library")
print("🎯 Identity Matching: ✅ Real confidence scores from face encodings")


try:
    face_cap = cv2.VideoCapture(0)
    if not face_cap.isOpened():
        raise RuntimeError(" Error: Could not access the webcam. Please check if it's connected, or if it's being used by another application.")
except Exception as e:
    print(f"Webcam access error: {e}")
    sys.exit()

detection_time = {}
last_alarmed = {}
current_status = "System ready - Please position yourself in front of the camera"
status_color = '#00ff00'  # Green for ready state

def get_frame():
    global prev_time, current_status, status_color, is_paused, pause_start_time, paused_names_time, last_frame
    # Read frame from camera
    ret, frame = face_cap.read()
    if not ret:
        current_status = " Camera error - Please check camera connection"
        status_color = '#ff0000'  # Red for error
        print("❌ Camera read failed.")
        return None

    frame = cv2.flip(frame, 1)
    curr_time = time.time()

    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0

    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (520,250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    # ------------- Pause Handling -----------------
    if is_paused:
        current_status = "⏸️ Detection Paused. Click Resume to continue."
        status_color = '#888888'
        # Return last frame to freeze the GUI
        if last_frame is not None:
            return last_frame
        else:
            last_frame = frame.copy()
            return last_frame
    else:
        last_frame = frame.copy()

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    curr_names = []

    # Update status based on face detection
    if len(face_locations) == 0:
        current_status = "👁️ Scanning for faces... Please position yourself in front of the camera"
        status_color = '#ffff00'  # Yellow for scanning
    elif len(face_locations) > 1:
        current_status = "⚠️ Multiple faces detected - Please ensure only one person is in frame"
        status_color = '#ff8800'  # Orange for warning

    for face_encoding, face_location in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(face_encode, face_encoding)
        best_match_index = np.argmin(face_distances)
        name = "No match"

        if face_distances[best_match_index] < 0.4:
            name = face_name[best_match_index]
            confidence = (1 - face_distances[best_match_index]) * 100
            confidence_text = f"{confidence:.2f}%"
            # Update status for recognized face
            current_status = f"✅ Match found: {name} (Confidence: {confidence:.1f}%)"
            status_color = '#00ff00'  # Green for match
        else:
            confidence_text = f"{(1 - face_distances[best_match_index]) * 100:.2f}%"
            # Update status for unrecognized face
            current_status = "❌ No match detected. You are safe to go."
            status_color = '#ff0000'  # Red for no match

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

            # Update status during countdown
            if remaining_time > 0:
                current_status = f"⏱️ Please stand still for {remaining_time:.0f} seconds - Processing..."
                status_color = '#ffaa00'  # Orange for processing

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
                current_status = f"🚨 THREAT DETECTED: {name} - Security alert triggered!"
                status_color = '#ff0000'  # Red for threat
                threat_alarm()
                send_email(name, frame, confidence)
                send_sms(name, confidence)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(LOG_DIR, filename)
                cv2.imwrite(filepath, frame)
            else:
                current_status = "✅ SCAN COMPLETE: No match detected - You are safe to proceed"
                status_color = '#00ff00'  # Green for safe
                safe_alarm()
                
            last_alarmed[name] = curr_time

    for name in list(detection_time.keys()):
        if name not in detected_now:
            del detection_time[name]

    return frame

def get_status():
    """Return current status message and color for GUI"""
    return current_status, status_color

# ------------- Add Pause/Resume Attribute Interface for GUI -----------
def set_pause_vars(
    get_is_paused, set_is_paused,
    get_pause_start_time, set_pause_start_time,
    get_paused_names_time, set_paused_names_time,
):
    global is_paused, pause_start_time, paused_names_time
    # Not strictly needed with globals (optional if handling state in one file), but included for clarity & future-proofing

# Start GUI

video_app = guiwindow(get_frame_callback=get_frame, status_callback=get_status)

# Set pause state references for bidirectional access
video_app.set_pause_vars(
    lambda: is_paused,
    lambda v: globals().__setitem__('is_paused', v),
    lambda: pause_start_time,
    lambda v: globals().__setitem__('pause_start_time', v),
    lambda: paused_names_time,
    lambda v: globals().__setitem__('paused_names_time', v),
    lambda: detection_time 
)


video_app.run()
