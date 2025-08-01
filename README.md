<p align="center">
  <img src="Readme_images/banner.png" alt="Real-Time Security Screening System" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/SomdattaNag/Security-Screening-System" alt="License">
  <img src="https://img.shields.io/badge/GSSoC-2025-orange" alt="GSSoC'25">
  <img src="https://img.shields.io/github/issues/SomdattaNag/Security-Screening-System" alt="Open Issues">
</p>

## 📑 Table of Contents

- [Problem Statement](#problem-statement)
- [Proposed Solution](#proposed-solution)
- [Features](#features)
- [Workflow](#workflow)
- [Note](#note)
- [License](#license)

Security-Screening-System/
│
├── alarms/                        # Alert sounds
│   ├── safe.wav                   # Safe event audio
│   └── threat.wav                 # Threat detection audio
│
├── csv_logs/                      # CSV logs of security events
│   └── security_log.csv
│
├── data/Sample_image/            # Sample images for testing
│   └── <uuid>.jpg                # Unique user image samples
│
├── encodings/                     # Saved face encodings
│   └── face_encodings.pkl
│
├── gui/                           # GUI module
│   └── gui.py
│
├── image_logs/                    # Captured images from detections
│   └── Sample_image_<timestamp>.jpg
│
├── Readme_images/                 # Images used in documentation
│   └── banner.png
│
├── .env.example                   # Sample environment config
├── .gitignore                     # Git ignored files
├── codeofConduct.md               # Community guidelines
├── Data_Augmentation.py           # Data augmentation script
├── learn.md                       # Training workflow details
├── LICENSE                        # MIT License
├── main.py                        # Main execution script
├── message.py                     # Alert messaging logic
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
└── save_encodings.py              # Generate and save face encodings

🛠️ Tech Stack
Python – Core programming language

OpenCV – For image processing and video stream handling

Face Recognition – For facial encoding and identification

SMTPLib – For sending email alerts on threats

Winsound – For playing alert sounds (Windows only)



## 🧩 Problem Statement
Traditional security checkpoints (e.g., airports, hotels, event venues) rely heavily on manual ID verification and human surveillance, which are time-consuming and prone to human error, vulnerable to identity fraud, forged documents, and look-alikes, inefficient in detecting wanted, banned, or high-risk individuals in real-time. Given the increasing need for automated, intelligent surveillance systems, there is a strong demand for a non-intrusive, reliable, and scalable solution to screen individuals based on biometric identity especially facial recognition without interrupting regular flow.

## 💡 Proposed Solution
A real-time security screening system, using face recognition with OpenCV. The system aims to scan individuals via a webcam at checkpoints (e.g., hotels, airports). If a person’s face matches an entry in the system’s dataset of known threats, runaway criminals or wanted individuals, the system triggers a threat alarm and sends messages and phone alerts to authorities based on the level of threat. Otherwise, a safe alarm is triggered, allowing them to proceed.

⚙️ Installation & Setup
To run the Security Screening System locally, follow these steps:

🚀 1. Fork the Repository (if contributing)
If you plan to collaborate or contribute:

Click on the Fork button at the top right of this repo

Clone your forked repo:

bash
Copy
Edit
git clone https://github.com/<your-username>/Security-Screening-System.git
cd Security-Screening-System
Otherwise, to only run the project locally:

bash
Copy
Edit
git clone https://github.com/SomdattaNag/Security-Screening-System.git
cd Security-Screening-System
📦 2. Set Up a Virtual Environment (Optional but Recommended)
bash
Copy
Edit
# Create virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
📚 3. Install Dependencies
Make sure you have Python 3.8+ installed. Then run:

bash
Copy
Edit
pip install -r requirements.txt
If face_recognition gives issues on Windows, try:

bash
Copy
Edit
pip install cmake
pip install dlib
pip install face_recognition
🔐 4. Configure Environment Variables
Duplicate the .env.example and rename it to .env. Fill in your email credentials (used to send alerts):

ini
Copy
Edit
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=yourpassword
EMAIL_RECEIVER=securityteam@example.com
⚠️ Important: For Gmail, you may need to allow "Less Secure Apps" or use an App Password.

🖥️ 5. Run the Application
bash
Copy
Edit
python main.py
Optional:

bash
Copy
Edit
python save_encodings.py        # Save encodings for new faces
python Data_Augmentation.py     # If you want to train with more data
🤝 Contribution Guidelines
We welcome contributions! To contribute:

Fork the repository

Create a new branch:

bash
Copy
Edit
git checkout -b feature/YourFeatureName
Commit your changes:

bash
Copy
Edit
git commit -m "Add: Your message"
Push to the branch:

bash
Copy
Edit
git push origin feature/YourFeatureName
Open a Pull Request 🛠️

Please follow our Code of Conduct and ensure your changes are well-documented.

## ✨ Features
1. The system scans individuals and detects faces.

2. Compares detected faces against a dataset of wanted/banned/runaway individuals.

3. The system takes 10 seconds to analyze and confirm the match before coming to a conclusion.

4. If no match is found a safe_alarm is triggered indicating the person is harmless and safe to go.

5. If a match is found a threat_alarm is triggered and email/SMS messages are sent directly to the authorities, based on the level of threat (low/medium/high) notifying them of the potential threat.If the threat is classified as major — with a confidence level exceeding 90% — a call alert is also triggered, ensuring immediate action in cases where the individual is almost certainly a known or wanted person.

6. Matched individuals' images and details are automatically logged into the system for verification and legal tracking purposes.

7. Includes data augmentation support — run `data_augmentation.py` after adding new images to improve face recognition accuracy.

## 🔁 Workflow
1. Dataset: The dataset contains folders for each wanted individual. The folder contains images of that individual. The larger the number of images, the better the precision of the system. The system has been tested with personal images. For now, sample images are used to fill the folder.

2. Face Encoding & Labeling: The system loads all images, extracts facial features using the face_recognition model, and encodes them into numerical vectors.It then assigns each encoding to the person’s name based on the folder structure.

3. Real time face recognition: Scans the individual's face using OpenCV. Detects and extracts faces in real time. Compares detected faces against stored encodings using distance metrics. If similarity is below a certain threshold (< 0.4), the person is identified. The threshold is intentionally set lower in order to avoid false positives. While false negatives can be handled with additional procedures, false positives can cause serious harassment and authority disturbances and are therefore minimized.

4. Identity Confirmation: The system takes 10 seconds to analyze and confirm the match. If the match remains consistent for 10 seconds and the alarm has not been triggered for the last 30 seconds, it triggers the alarm based on the match type: safe_alarm for "No match" and threat_alarm for "match".

5. Email Notification: If a threat is identified and threat_alarm is triggered an email is sent to authorities including the name, photo, time and IP location of the individual. The authorities can be the organisation's security, admin, police authorities, local authorities, public safety etc.

6. SMS Notification:
If a threat is identified and threat_alarm is triggered, an SMS alert is sent to the concerned authorities. The message includes key details such as the individual's name, time of detection and IP location of the individual.

7. Call alert: If the threat is classified as major — with a confidence level exceeding 90% — a call alert is also triggered, ensuring immediate action in cases where the individual is almost certainly a known or wanted suspect.

8. Logging Matched faces: When a match is detected, the system automatically saves the individual’s face image and logs associated data (like name, timestamp, confidence level) into a `.csv` file for legal and verification purposes.

9. Advanced data augmentation: Every time an image is added, run the `data_augmentation.py` script to add more diverse set images for each person.

## 📝 Note
1. This is a functional prototype designed for a security checkpoint use case. It demonstrates the core facial recognition and threat-detection logic of a real-time screening system. The project is modular and can be extended to integrate with IoT hardware or GUI modules as needed.
2. Due to a deliberately lower matching threshold to reduce false positives, the system might produce false negatives in a few cases.
3. To improve accuracy and reliability, it is recommended to use a larger number of diverse images of each individual in the dataset.
4. Only the data of individuals identified as potential threats or confirmed matches is temporarily stored in the system for legal verification purposes. We prioritize civilian privacy and, as such, the system does not store any data of non-matching or safe individuals. All data retention is limited to potential threats only handled with strict confidentiality.

## 📄 License
This project is licensed under the [MIT License](LICENSE).

