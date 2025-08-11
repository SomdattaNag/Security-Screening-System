# Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Usage Instructions](#usage-instructions)
- [Folder Structure](#folder-structure)
- [Project Setup](#project-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Rules for Contributors](#rules-for-contributors)
- [For Testing and Development](#for-testing-and-development)
- [Notes on object detection- Yolov5](#notes-on-yolov5-custom-model--object-detection-inference-in-our-system)
- [Additional Tip](#additional-tip)

# Project Overview

This project is a Real-Time Security Screening System utilizing face recognition technology to identify potential threats at security checkpoints such as airports, hotels, or event venues. The system scans individuals via webcam, compares faces against a dataset of known individuals, and triggers alarms with notifications when a threat is detected.

# Features

1. Real-time face detection using OpenCV.
2. Facial encoding and matching using the face_recognition library.
3. Advanced data augmentation for more diverse images.
4. 10-second continuous match confirmation to avoid false triggers.
5. Threat & Safe Alarms:
    1. Threat Alarm: When a known individual is detected
    2. Safe Alarm: When no match is found
6. Email and SMS notifications are automatically sent to authorities when a potential threat is detected, containing the suspect's details and threat level. If the threat is classified as major — with a confidence level exceeding 90% — a call alert is also triggered, ensuring immediate action in cases where the individual is almost certainly a known or wanted person.
7. If a match is found, the individual's image is automatically logged in the system for future verification and other legal procedures. Their data is also logged in a csv file for further legal verification process.
8. Clean and interactive GUI for user interaction.
9. Real time object detection to warn users to remove any face accessory like cap, scarf, masks etc. that can hamper the face recognition scanning.
10. Modular and extendable prototype suitable for further integrations (IoT hardware etc.).

# Usage Instructions

1. Webcam is activated to scan faces.
2. Matches are checked in real-time against known dataset.
3. System triggers one of the following:
    Threat Detected → Threat Alarm + Email/SMS + Logs created
    No Match Found → Safe Alarm
4. Exit the program by pressing 'q' or closing the webcam window

**Note**: The system optionally checks for face accessories that stop screening to ensure users cooperate with scanning without any obstruction. 

# Folder Structure

```
project/
│
├── alarms/
│   └── threat.wav
│   └── safe.wav
│
├── data/
│   └── [Person Name]/
│        └── image1.jpg
│        └── image2.png
├── Readme_images/
│   └── banner.jpg
│
├── gui/
│   └── gui.py
│
├── image_logs/
│   └── matched_individual_image.jpg
│
├── csv_logs/
│   └──security_log.csv
│
├── encoding/
│   └── face_encodings.pkl
│
├── models/
│   └── data.yaml
│   └── yolov5n_best.pt
│
├── yolov5/
│   
│
├── saveencodings
├── Data_Augmentation.py
│   
├── main.py                
├── message.py             
├── requirements.txt       
├── .gitignore             
├── .env.example           
├── README.md              
├── learn.md 
├── LICENCE
└── codeofConduct.md
```

__alarms/__: Contains audio files used for alerts (threat_alarm and safe_alarm), triggered from main.py.

__data/__: Each subfolder represents an individual, containing multiple images to improve recognition accuracy.

__gui/__: Logic for the graphical User Inerface of the System.

__image_log/__: If a match is found, the individual's image is automatically logged here.If it doesn't exist, created automatically.

__csv_log/__: If a match is found, the individual's data is automatically logged here in a csv file.If it doesn't exist, created automatically. The gui has a 'export logs' button to export and download this file when needed.

__Readme_images__/: Stores images used in documentation.

__models/__: Contains the trained model weights (yolov5n_best.pt) and related configuration files (data.yaml) used for accessory detection.

__yolov5/__: Includes a minimal set of files from the official Ultralytics YOLOv5 repository required to run inference with the custom-trained model.

__encodings.pkl__: A binary file storing the precomputed face encodings and names, used to speed up face recognition in the main application.

__saveencodings__: A script that scans the dataset, extracts facial encodings for each image, and saves them with corresponding names.

__Data_Augmentation__:A script that applies random transformations (e.g., rotation, occlusion, blur) to images to generate additional training data and improve model robustness.

__.env.example__: Template for required environment variables. Actual sensitive .env file is ignored via .gitignore.

__.gitignore__: Ensures sensitive and unnecessary files like .env, venv/ __pycache__/, are never committed to the repository.

__requirements.txt__: Defines the Python dependencies needed to run the project.

__main.py__: Central application logic (face detection, alarm triggers, notification handling).

__message.py__: Handles email notifications using credentials from the .env file.

__README.md__: Original project description.

__learn.md__: This learning and documentation guide.

__LICENSE__: This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html).

__codeofConduct.md__: Ethical and moral guidelines to be followed while working on the project by all the respective members.

# Project Setup

1. Clone the Repository as mentioned in the contribution guidelines.
2. Open the folder and install Dependencies as mentioned in the guidelines.
3. Prepare the Dataset
    1. Inside the data/ folder, create subfolders for each individual (named after the person). The subfolder with contain the individual's images.
    2. Add multiple images of each person in their respective subfolder to improve recognition accuracy.
4. Data Augmentation: Run the Data_Augmentation.py script to add more diverse images for each individual in the dataset.
5. Environment Configuration:
    1. Copy .env.example to a .env file.
    2. Replace placeholder values with your actual credentials.
6. Configure Email Settings
    1. Ensure message.py loads email settings from the .env file.
    2. Ensure the send_email() function can send emails from your desired account.
    3. Verify SMTP server details are correctly handled (smtp.gmail.com and port 587 for Gmail).
7. Configure SMS Settings
    1. Ensure message.py loads SMS settings (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, ALERT_PHONE_NUMBERS) from the .env file.
    2. Set up a free Twilio account, obtain your credentials from the dashboard, and verify your test phone numbers.
8. Run the Project
    1. run the saveencodings file to save face encoding for the individual once before starting the project.
        ```python saveencodings.py```
    2. run the main file 
        ```python main.py```
9. Stop the System
    Press 'q' in the webcam window or close the window to stop.

# Contribution Guidelines:

1. Check Open Issues or Open a new issue: Browse the [Issues section](https://github.com/SomdattaNag/Security-Screening-System/issues) and look for ones labeled `gssoc25`, `level1`,`level2` or `level3`. If you want to implement a new feature or enhance an existing feature, first open a new issue and wait for it to get labeled. Only the labeled issues will be considered to be availaible for contribution.

2. Get Assigned: Before working on an issue, comment on it and wait to be officially assigned by a maintainer. We follow a FCFS policy, contributors who are waiting in line for an issue, will only get assigned if the first assignee doesn't complete their task.

3. Fork the Repository: Click the Fork button on GitHub to create your own copy of the repository.
    Clone Your Fork Locally
    ```
    git clone <your-fork-url>
    cd <cloned-project-folder-name>
    ```


4. Set Up a Virtual Environment (Optional):
    
    ```
    python -m venv venv
    source venv/bin/activate #for linux
    venv\Scripts\activate #for windows
    ```


5. Install Dependencies
    Dependencies are listed in requirements.txt. Install them with:
    ```
    pip install -r requirements.txt
    ```

6. Work on a Feature or Fix

7. Create a new branch:
    
    ```
    git checkout -b feature/your-feature-name
    ```

8. Follow Best Practices:
    1. Keep code modular and readable.
    2. Add comments where needed.
    3. Test your changes before committing.

9. Commit Changes and Push
    
    ```
    git add .
    git commit -m "Add: short description of feature"
    git push origin feature/your-feature-name
    ```
    

10. Submit a PR (pull request)
    1. Go to your fork on GitHub and click Compare & pull request.
    2. Provide a clear explanation of your changes.

# Rules for Contributors

**1.** Assignement to contributors is on a FCFS ( First Come First Serve basis), whoever comments first gets assigned first.
**2.** The contributors who comes next, gets assigned if the previous assignee doesn't complete their task.
**3.** General deadline for each level of assignment:
       1. level 1: maximum 2-3 days
       2. level 2: maximum 5-6 days
       3. level 3: maximum 7-8 days
**4.** If contributors want more days to work, deadline can be extended.

# For testing and development

1. __Preparing dataset__:
    1. The data folder will contain subfolders for each individual, named after them. The subfolders will contain their images.
    2. For now sample stock images are used. Use your own personal images for testing.
    3. Use clear, bright, reliable images. The threshold is intentionally set lower (0.4 from 0.6) to reduce false positives since it can lead to harassment. Use multiple reliable images for each folder to improve precision if any problem persists.

2. __Data Augmentation__: Advanced data augmentation: Everytime an image is added, run the data augmentation.py script to add more diverse set images for each person.

3. __Face encoding__: Run the saveencodings file to save face encoding for the individual once before starting the project.

4. __Email Setup and testing__:
    1. Normal testing: (Production-based: sends real emails)
        1.  Configure Emails in message.py:
            Instead of hardcoding credentials, store them in a .env file:
            Example .env:
            
            ```
                SENDER_EMAIL=your_email@gmail.com
                SENDER_PASSWORD=your_email_password
                RECEIVER_EMAIL=admin1@example.com,admin2@example.com,admin3@example.com,admin4@example.com
            ```

        3. Secure Authentication Setup:
        4. Google may block apps using your main password. To avoid this:
        5. Enable Two-Factor Authentication (2FA) on your Google account.
        6. Go to:
            Google Account → Security → App Passwords
        7. Generate a new App Password (choose "Mail" as the app).
        8. Use this App Password in:
            ```
            SENDER_PASSWORD=your_app_password
            ```


        9. Test the System:
        10. Run the project.
        11. On threat detection, you should receive an email with the required details.

    2. Alternative testing (If you are unable to use app password):
        
        For safer local testing without sending real emails, use Python’s built-in SMTP Debugging Server.
        Why Use This?
            No real emails are sent.
            You can visually inspect email formatting, message content, and attachments.
            Email contents can be saved locally for detailed review.
        
        1. Edit message.py:
            Replace email server configuration:
            
                ```
                smtp_server = 'localhost'
                smtp_port = 1025
                sender_email = 'test@example.com'
                receiver_email = 'debug@example.com'
                ```


        2. Start a Local Debug SMTP Server:
            In a separate terminal window, run:
            ```
                python -m smtpd -c DebuggingServer -n localhost:1025
            ```


            This will simulate an SMTP server and print email details directly to the terminal.
        3. Optional: Save Emails as Files
            In the send_email() function, email messages are saved locally:
            ```
            with open("debug_email.eml", "wb") as f:
                f.write(msg.as_bytes())
            ```
        5. Open this .eml file using Outlook, Thunderbird, or any email client to view the message exactly as a recipient would.
        6. Console Output Includes:
            1. Subject line,
            2. Body content,
            3. Image attachment,
            4. Any SMTP errors, if applicable.
        7. Troubleshooting Local Server:
            If you see a connection error like Connection refused, ensure your SMTP Debug Server is running.
5. __Twilio SMS and Call alert Setup and Testing__:
    Send real-time SMS alerts when a threat is detected (match found). Useful when email monitoring is delayed.
    1. Requirements:
        1. Free Twilio account
        2. Verified sender and receiver phone numbers (trial accounts)
        3. Internet access during runtime
    2. Twilio Account Setup:
        1. Create a Free Twilio Account: Go to https://www.twilio.com/try-twilio and sign up.
        2. Verify Your Phone Number.
        3. During signup, Twilio will ask you to verify a phone number. This will be used as the receiver during testing.
        4. Access Console Dashboard: After login, go to your Twilio Console. There, you will find:
            1. Account SID (e.g., ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX)
            2. Auth Token (click "View" to reveal it)
            3. Trial Phone Number (usually starts with +1)
    3. Set up credentials in Code:
        1. Copy the Credentials to Your .env File:
        ```
            TWILIO_ACCOUNT_SID=your_twilio_sid
            TWILIO_AUTH_TOKEN=your_twilio_auth_token
            TWILIO_PHONE_NUMBER=your_twilio_trial_number
            ALERT_PHONE_NUMBERS=+91XXXXXXXXXX,+91YYYYYYYYYY
        ```

        ⚠️ Note: In a Twilio trial account, the alert phone numbers must be verified in the console.

# Notes on Yolov5 custom model & object detection inference in our system:

This project incorporates a custom-trained YOLOv5 model for accessory detection (cap, mask, scarf-kerchief, sunglasses) as a key component of the security screening system.

The model was developed by a contributor who:

1. Extended the dataset to 1005 images (852 training, 153 validation) using images collected from Google/Bing and manual downloads.

2. Annotated the dataset via Roboflow in YOLOv5 PyTorch format, labeling normal glasses as part of the person class.

3. Trained the model on the YOLOv5 pretrained weights (yolov5n.pt) for 100 epochs, achieving approximately 85–90% accuracy.

4. Saved the best weights as yolov5n_best.pt, which is used in this system for real-time accessory detection.

5. The minimal subset of the official Ultralytics YOLOv5 repository is included locally to support inference with this custom model, ensuring compliance with the AGPL-3.0 license.

6. By integrating YOLOv5 under AGPL-3.0, this project honors all requirements including providing source code for any modifications and distributing the custom trained weights under the same license.

Model loading in the code uses the local files only:

```
import torch
yolo_model = torch.hub.load('yolov5', 'custom', path='models/yolov5n_best.pt', source='local')
```
This setup enables fast, on-device accessory detection while complying with the original YOLOv5 licensing terms.



# Additional tip

    1. Keep your .env and private data uncommitted.
    2. Only use sample data/images in public repositories.
    3. Always test locally before pushing.

# Troubleshooting tip

If you're facing issues with installing face-recognition:
```
pip install cmake
pip install dlib
pip install face-recognition
```
# GSSoC Notes and Contributors

This project is actively maintained under GSSoC 2025. Contributions are welcome via issues and PRs.

Ethical Reminder: This system is designed for responsible use. Do not deploy in real-world environments without proper legal permissions and privacy compliance.

🚫 Never store or share real user images or credentials publicly.

