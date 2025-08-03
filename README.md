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


## 🧩 Problem Statement

In places like airports, hotels, and event venues, security checks are usually done by humans. They check ID cards and watch people manually. But this process takes a lot of time and can have many mistakes. For example, someone might use a fake ID, or look very similar to another person, and the security team might not notice. It’s also hard for them to quickly find people who are dangerous or not allowed to enter.
Because of this, there is a growing need for a better system. We need a smart, automatic solution that can check people’s identities using their face (facial recognition). This system should work smoothly without stopping the normal flow of people. It should also be safe, accurate, and easy to use in many places.


## 💡 Proposed Solution

We are creating a smart security system that uses facial recognition with the help of OpenCV. This system will work in real-time using a webcam at places like airports or hotels.
When a person walks in front of the camera, the system will scan their face and compare it with a database of known criminals, wanted people, or other threats.
If it finds a match, it will quickly raise a threat alert and send warning messages or phone alerts to the authorities, depending on how serious the threat is.
If there’s no match and the person is safe, a safe signal will be shown, and they can move ahead without any issues.This makes security faster, smarter, and more reliable.


## 👥 Contributors and Learning Resources

As of July 2025, this project is a part of GirlScript Summer of Code 2025. Please read the README file carefully to understand the project workflow. For contribution tips and extended documentation, see the [Learn Guide](./learn.md).
Only the issue with the label __gssoc25__ are open for GSSoC contributors right now.


## ✨ Features

1. The system uses a webcam to scan each person and detect their face.
2. Once a face is detected, it checks the system’s database to see if the person is on a list of wanted, banned, or runaway individuals.
3. The system takes around 10 seconds to carefully analyze the face and decide if it matches someone in the database.
4. If the person is not in the database, a safe signal is shown, and they can continue without any problem.
5. If the system does find a match:
   A threat alert is activated.
   An email or SMS is sent to the authorities based on how serious the threat is (low, medium, or high).
   If the match is very strong (over 90% confidence), a call alert is also triggered for urgent action.
6. The system automatically saves the image and details of the matched person for legal and verification records.
7. To improve accuracy, the system supports data augmentation. You can run a file called `data_augmentation.py` after adding new images to make the face recognition work better.


## 🔁 Workflow

The system starts by organizing images into folders—one for each wanted person. More images improve accuracy. These images are then encoded using the face_recognition library, converting facial features into numerical values and labeling them based on folder names.

During real-time scanning with OpenCV, the webcam detects and extracts faces, which are then compared with stored encodings. If the similarity is below 0.4, the person is considered a match. The system waits 10 seconds to confirm identity and avoids duplicate alerts within 30 seconds.

If no match is found, a safe_alarm is triggered. If a match is found, a threat_alarm is activated, followed by email and SMS alerts containing the individual’s name, photo, time, and IP location. If the threat is major (confidence > 90%), a call alert is also triggered.

Matched faces and related data (name, time, confidence) are saved to a .csv file for tracking and verification. To improve recognition accuracy, users can run data_augmentation.py after adding new images.

<h2>Technology Used🚀</h2>

Python, OpenCV,  Face Recognition, SMTPLib, playsound, Pytorch, Tkinter, Twilio, Pillow.


<h2>Getting Started</h2>
**1.** Start by forking the [**Security-Screening-System**](https://github.com/SomdattaNag/Security-Screening-System) repository. 
**2.** Clone your forked repository:

```bash
git clone https://github.com/<your-github-username>/Security-Screening-System
```
**3.** Navigate to the new project directory:

```bash
cd Security-Screening-System
```
**4.** Set upstream command:

```bash
git remote add upstream https://github.com/SomdattaNag/Security-Screening-System
```
**5.** Create a new branch:

```bash
git checkout -b YourBranchName
```

<i>or</i>

```bash
git branch YourBranchName
git switch YourBranchName
```
**6.** Sync your fork or local repository with the origin repository:

In your forked repository, click on the `Fetch upstream` button.
Then select `Fetch and merge` to sync changes from the original repo.

###  Alternatively, use Git CLI to sync with the original repository:

```bash
git fetch upstream
```

```bash
git merge upstream/main
```
**7.** After syncing, go ahead and make your changes in the codebase.

**8.** Stage your changes and commit them:

⚠️ **Make sure** not to commit sensitive files like .env or any files listed in .gitignore.

⚠️ **Make sure** not to run the commands `git add .` or `git add *`. Instead, stage your changes for each file/folder

```bash
git add file/folder
```

```bash
git commit -m "<your_commit_message>"
```

**9.** Push your changes to GitHub:
Use the command below to push your branch to your GitHub repository:

```bash
git push origin YourBranchName
```
**10.** Create a Pull Request!

 **🎉 Congratulations! You've successfully made your first contribution!**


## 📝 Note

1. This project is a working prototype built for security checkpoint scenarios. It showcases the core logic of real-time facial recognition and threat detection. The system is modular and can be expanded with IoT devices or a GUI if needed.

2. The matching threshold is set lower to avoid false positives. As a result, a few false negatives may occur.

3. For better accuracy, it's advised to include a large and diverse set of images for each individual in the dataset.

4. The system only stores data of individuals flagged as threats or confirmed matches for legal verification. No data is stored for safe or non-matching individuals, ensuring user privacy. All stored data is handled with strict confidentiality.

## 📄 License
This project is licensed under the [MIT License](LICENSE).

