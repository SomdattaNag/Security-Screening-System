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

# 🤝 Contribution Guidelines

We welcome contributions from everyone! If you’re participating in **GirlScript Summer of Code 2025 (GSSoC'25)** or just exploring open source — you're welcome here!

## 📌 How to Contribute

1. **Check Open Issues**  
   Browse the [Issues section](https://github.com/SomdattaNag/Security-Screening-System/issues) and look for ones labeled `gssoc25`, `level1`,`level2` or `level3`.

2. **Get Assigned**  
   Before working on an issue, comment on it and wait to be officially assigned by a maintainer. We follow a FCFS policy, contributors who are waiting in line for an issue, will only get assigned if the first assignee doesn't complete their task.


3. **Fork the Repository**  
   Click the `Fork` button at the top-right corner and clone your forked repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Security-Screening-System.git

4. **Create a New Branch**
    Use a meaningful branch name like:
    git checkout -b fix/readme-formatting

5. **Make Your Changes**
    Implement your fix or feature. Follow the coding style and comment where necessary.

6. **Commit Changes**
    Write clear, descriptive commit messages like:
    git commit -m "Improved README formatting"

7. **Push and Create Pull Request (PR)**
    git push origin your-branch-name
    Then go to your fork on GitHub and click "Compare & Pull Request".
    

## 🧩 Problem Statement
Traditional security checkpoints (e.g., airports, hotels, event venues) rely heavily on manual ID verification and human surveillance, which are time-consuming and prone to human error, vulnerable to identity fraud, forged documents, and look-alikes, inefficient in detecting wanted, banned, or high-risk individuals in real-time. Given the increasing need for automated, intelligent surveillance systems, there is a strong demand for a non-intrusive, reliable, and scalable solution to screen individuals based on biometric identity especially facial recognition without interrupting regular flow.

## 💡 Proposed Solution
A real-time security screening system, using face recognition with OpenCV. The system aims to scan individuals via a webcam at checkpoints (e.g., hotels, airports). If a person’s face matches an entry in the system’s dataset of known threats, runaway criminals or wanted individuals, the system triggers a threat alarm and sends messages and phone alerts to authorities based on the level of threat. Otherwise, a safe alarm is triggered, allowing them to proceed.

## 👥 Contributors and Learning Resources
As of July 2025, this project is a part of GirlScript Summer of Code 2025. Please read the README file carefully to understand the project workflow. For contribution tips and extended documentation, see the [Learn Guide](./learn.md).
Only the issue with the label __gssoc25__ are open for GSSoC contributors right now.

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

