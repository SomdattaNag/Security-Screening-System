# Simple Security Screening System

This is a simplified version of the Security Screening System that works with minimal dependencies.

## Features
- Face detection using OpenCV's Haar Cascade classifier
- Real-time video feed from your webcam
- Logs all security events to `security_log.txt`
- Saves images when faces are detected in the `image_logs` directory

## Requirements
- Python 3.6+
- OpenCV (will be installed automatically)
- NumPy (will be installed automatically)
- Pillow (will be installed automatically)
- python-dotenv (will be installed automatically)

## Installation
1. Make sure you have Python 3.6 or higher installed
2. Install the required packages:
   ```
   pip install opencv-python numpy Pillow python-dotenv
   ```

## Usage
1. Run the security system:
   ```
   python simple_security_system.py
   ```
2. The system will start your webcam and begin monitoring
3. Press 'q' to quit the application

## How It Works
- The system uses OpenCV's Haar Cascade classifier to detect faces in the video feed
- When a face is detected, it will be highlighted with a green rectangle
- Each detection is logged with a timestamp in `security_log.txt`
- Images are automatically saved to the `image_logs` directory when faces are detected

## Logs
- All security events are logged to `security_log.txt`
- Detected face images are saved in the `image_logs` directory with timestamps

## Notes
- This is a simplified version with basic functionality
- For better accuracy, consider using more advanced face detection models
- Make sure you have proper lighting for better detection results
