# Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Usage Instructions](#usage-instructions)
- [Folder Structure](#folder-structure)
- [Project Setup](#project-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [For Testing and Development](#for-testing-and-development)
- [Additional Tip](#additional-tip)

# Project Overview
This project is a Real-Time Security Screening System utilizing face recognition technology to identify potential threats at security checkpoints such as airports, hotels, or event venues. The system scans individuals via webcam, compares faces against a dataset of known individuals, and triggers alarms with notifications when a threat is detected.

# Features

1. Real-time face detection using OpenCV.
2. Facial encoding and matching using the face_recognition library.
3. 10-second continuous match confirmation to avoid false triggers.
4. Distinct alarms:
    1. Threat Alarm: If a known individual is detected.
    2. Safe Alarm: If no match is found.
5. Email notifications sent to authorities with suspect details when a threat is detected.
6. Modular and extendable prototype suitable for further integrations (IoT hardware, GUI, etc.).

# Usage Instructions

1. The system uses your webcam to detect and analyze faces.
2. It continuously compares detected faces to the dataset.
3. On identification:
4. Threat detected → Threat alarm triggers + Email sent.
5. No match found → Safe alarm triggers.
6. Press 'q' or close the webcam window to exit. 

# Folder Structure

```
project/
│
├── data/
│   └── [Person Name]/
│        └── image1.jpg
│        └── image2.png
│
├── main.py
├── message.py
├── README.md
└── learn.md
```

data/: Contains subfolders for each individual, filled with multiple images for accurate recognition.

main.py: Main execution file handling face detection, recognition, alarms, and notifications.

message.py: Handles email sending functionality (not provided here).

README.md: Original project description.

learn.md: This learning and documentation guide.

# Project Setup

1. Clone the Repository as mentioned in the contribution guidelines.
2. Open the folder and install Dependencies as mentioned in the guidelines.
3. Prepare the Dataset
    1. Inside the data/ folder, create subfolders for each individual (named after the person). The subfolder with contain the individual's images.
    2. Add multiple images of each person in their respective subfolder to improve recognition accuracy.

4. Configure Email Settings
    1. Edit message.py to set your SMTP server details and credentials.
    2. Ensure the send_email() function can send emails from your desired account.

5. Run the Project
    run the main file 
        python main.py
6. Stop the System
    Press 'q' in the webcam window or close the window to stop.

# Contribution Guidelines:

1. Fork the Repository: Click the Fork button on GitHub to create your own copy of the repository.
    Clone Your Fork Locally
    ```
    git clone <your-fork-url>
    cd <cloned-project-folder-name>
    
    ```

2. Set Up a Virtual Environment (Optional):
    
    ```
    python -m venv venv
    source venv/bin/activate (for linux) 
    venv\Scripts\activate (for windows)
    
    ```

3. Install Dependencies
    Dependencies are listed in requirements.txt. Install them with:
    ```
    pip install -r requirements.txt 

    ```
            or type manually
    ```
    pip install opencv-python face-recognition numpy
    ```

4. Work on a Feature or Fix

5. Create a new branch:
    
    ```
    git checkout -b feature/your-feature-name
    ```

6. Follow Best Practices
    Keep code modular and readable.
    Add comments where needed.
    Test your changes before committing.

7. Commit Changes and Push
    
    ```
    git add .
    git commit -m "Add: short description of feature"
    git push origin feature/your-feature-name
    ```
    

8. Submit a PR (pull request)
    1. Go to your fork on GitHub and click Compare & pull request
    2. Clearly explain what you’ve changed or added.

# For testing and development

1. Preparing dataset:
    1. The data folder will contain subfolders for each individual, named after them. The subfolders will contain their images.
    2. For now sample stock images are used. Use your own personal images for testing.
    3. Use clear, bright, reliable images. The threshold is intentionally set lower (0.4 from 0.6) to reduce false positives since it can lead to harassment. Use multiple reliable images for each folder to improve precision if any problem persists.

2. Email Setup and testing:
    1. Normal testing: (Production-based: sends real emails)
        1. Configure Emails in message.py:
            Replace placeholder values with your credentials:
            ```
            sender_email = 'your_email@gmail.com'
            sender_password = 'your_app_password'
            receiver_email = 'receiver_email@example.com'
            ```
        3. Secure Authentication Setup:
        4. Google may block apps using your main password. To avoid this:
        5. Enable Two-Factor Authentication (2FA) on your Google account.
        6. Go to:
            Google Account → Security → App Passwords
        7. Generate a new App Password (choose "Mail" as the app).
        8. Use this App Password in:
            ```
            sender_password = 'your_app_password'
            ```

        9. Test the System:
        10. Run the project.
        11. On threat detection, you should receive an email with the required details.

    2. Alternative testing: (If you are unable to use app password)
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
            Subject line.
            Body content.
            Image attachment
            Any SMTP errors, if applicable.
        7. Troubleshooting Local Server:
            If you see a connection error like Connection refused, ensure your SMTP Debug Server is running.

# Additional tip
Never commit personal data (like your images, email credentials, or passwords) in the project repository. Only use test data for development and local testing.