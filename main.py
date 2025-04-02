import cv2
import numpy as np
import os
import face_recognition
import winsound
from message import send_email
import time

#initialising threatalarm
def threat_alarm():
    duration = 5000  
    frequency = 1000  
    winsound.Beep(frequency, duration)  

#initialising safealarm
def safe_alarm():
    duration=500
    frequency=1000
    winsound.Beep(frequency,duration)

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

face_cap = cv2.VideoCapture(0)
detection_time = {}  
last_alarmed = {}    

#setting opencv
try:
    while True:
        ret, frame = face_cap.read()
        if not ret:
            break
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # Resize
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # rgb-format
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        curr_names = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            face_distances = face_recognition.face_distance(face_encode, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            name = "No match"
            if face_distances[best_match_index] < 0.4:
                name = face_name[best_match_index]
            curr_names.append(name)

            top, right, bottom, left = [coord * 4 for coord in face_location]
            color = (0, 255, 0) if name != "No match" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        #starting timer
        curr_time = time.time()
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