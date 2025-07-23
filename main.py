import cv2
import sys
import numpy as np
import os
import face_recognition
from playsound import playsound
from message import send_email
import time

prev_time = 0


#alarm if a match is found
def threat_alarm():
    playsound("alarms/threat.wav")

#alarm if no match found
def safe_alarm():
    playsound("alarms/safe.wav")

data_path = "data/"
face_encode = []
face_name = []

#labelling image data
for person_name in os.listdir(data_path):  
    person_folder = os.path.join(data_path, person_name)

    if os.path.isdir(person_folder):  
        for file in os.listdir(person_folder):  
            if file.lower().endswith(("jpg", "jpeg", "png")):  
                img_path = os.path.join(person_folder, file)
                
                img = face_recognition.load_image_file(img_path)
                face_encodings = face_recognition.face_encodings(img)

                if face_encodings:  
                    face_encode.append(face_encodings[0])  
                    face_name.append(person_name)  

try:
    face_cap = cv2.VideoCapture(0)
    if not face_cap.isOpened():
        raise RuntimeError("❌ Error: Could not access the webcam. Please check if it's connected, or if it's being used by another application.")
except Exception as e:
    print(str(e))
    sys.exit()
detection_time = {}  
last_alarmed = {}    

#setting opencv
try:
    while True:
        ret, frame = face_cap.read()
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        fps_text = f"FPS: {int(fps)}"
        
        if not ret:
            break

        frame = cv2.flip(frame,1)
        cv2.putText(frame, fps_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)
        
        small_frame =cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # Resize
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # rgb-format
        
        face_locations =face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        curr_names = []
        curr_time = time.time() 
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            face_distances =face_recognition.face_distance(face_encode, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            name = "No match"
            if face_distances[best_match_index] < 0.4:
                name = face_name[best_match_index]
                confidence = (1 - face_distances[best_match_index]) * 100
                confidence = max(0, min(confidence, 100))
                confidence_text = f"{confidence:.2f}%"
            else:
                confidence_text = f"{(1 - face_distances[best_match_index]) * 100:.2f}%"

            curr_names.append(name)

            top, right, bottom, left =[coord * 4 for coord in face_location]
            color = (0, 255, 0) if name!= "No match" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, confidence_text, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            #added: a countdown timer for each detected face
            if name in detection_time:
                scan_time = curr_time - detection_time[name]
                remaining_time = max(0, 10 - int(scan_time))
                timer_text = f"{remaining_time:.1f}s"
                cv2.putText(frame, timer_text, (left, top + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)
                
        #starting timer
        
        detected_now = set(curr_names)
        
        for name in detected_now:
            if name not in detection_time:
                
                #first detection
                detection_time[name] = curr_time
                last_alarmed[name] = 0  

                

        for name in detected_now:
            scan_time= curr_time - detection_time[name]
            if scan_time>= 10 and (curr_time - last_alarmed.get(name, 0)) >= 30:
                if name!="No match":
                    threat_alarm()
                    send_email(name,frame)
                else:
                    safe_alarm()
                last_alarmed[name] = curr_time

        for name in list(detection_time.keys()):
            if name not in detected_now:
                del detection_time[name]
        
        cv2.imshow("Face Recognition", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty("Face Recognition", cv2.WND_PROP_VISIBLE) < 1:
            break

finally:
    face_cap.release()
    cv2.destroyAllWindows()
