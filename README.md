# Security Screening System
Built a real-time security screening system, using face recognition with OpenCV. The system scans individuals via a webcam at check- points (e.g., hotels, airports). If a person’s face matches an
entry in the system’s dataset of known threats, runaway criminals or wanted individuals, the system triggers a threat alarm and sends
an email alert to authorities. Otherwise, a safe alarm is triggered, allowing them to proceed.

# Tech Stack: OpenCV, Face Recognition, SMTPLib, Winsound

# Features:
1. The system scans individuals and detects faces.

2. Compares detected faces against a dataset, consisting of wanted/banned/runaway individuals.

3. The system takes 10 seconds to analyze and confirm the match before coming to a conclusion.

4. if no match is found a safe_alarm is triggered indicating the person is harmless and safe to go.

5. if a match is found a threat_alarm is triggered and an email is sent directly to the authorities notifying them of the potential threat.

# Workflow:
1. Dataset: The dataset consists of folders, each representing an individual who is a known threat or wanted. Each folder contains images of that individual for identification.

2. Face Encoding & Labeling: The system loads all images, extracts facial features using the face_recognition model , and encodes them into numerical vectors.It then assigns each encoding to the person’s name based on the folder structure.

3. Real time face recognition: Scans the individuals' face using OpenCV. Detects and extracts faces in real time. Compares detected faces against stored encodings using distance metrics. If similarity is above a certain threshold (< 0.4), the person is identified.

4. Identity Confirmation:  The system takes 10 seconds to analyze and confirm the match. If the match remains consistent for 10 seconds and the alarm has not been trigerred for last 30 seconds, it triggers the alarm based on the match type: safe_alarm for "No match" and threat_alarm for "match".

5. Email Notification: If a threat is identified and threat_alarm is trigerred an email is sent to authorities including the name, photo, time and Ip location of the individual. The authorities can be the organisation security, admin, police authorities, local authorities, public safety etc.

