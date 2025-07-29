#!/usr/bin/env python3
"""
Security Screening System - Basic/Compatibility Mode
This version uses OpenCV for basic face detection when face_recognition library is not available.
For full functionality with identity matching, use main.py with face_recognition library installed.
"""
import cv2
import numpy as np
import os
import time
import sys
from gui.gui import guiwindow
import datetime
import threading  # Added for non-blocking operations

# Simple version without face_recognition library - uses OpenCV for basic face detection

prev_time = 0
LOG_DIR = "logs"

#create log if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Load OpenCV's built-in face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

try:
    face_cap = cv2.VideoCapture(0)
    if not face_cap.isOpened():
        raise RuntimeError("❌ Error: Could not access the webcam. Please check if it's connected, or if it's being used by another application.")
except Exception as e:
    print(str(e))
    sys.exit()

detection_time = {}
last_alarmed = {}
current_status = "System ready - Please position yourself in front of the camera"
status_color = '#00ff00'  # Green for ready state

def get_frame():
    global prev_time, current_status, status_color

    ret, frame = face_cap.read()
    if not ret:
        current_status = "❌ Camera error - Please check camera connection"
        status_color = '#ff0000'  # Red for error
        return None

    frame = cv2.flip(frame, 1)
    curr_time = time.time()

    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (520,250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using OpenCV
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Update status based on face detection
    if len(faces) == 0:
        current_status = "👁️ Scanning for faces... Please position yourself in front of the camera"
        status_color = '#ffff00'  # Yellow for scanning
    elif len(faces) > 1:
        current_status = "⚠️ Multiple faces detected - Please ensure only one person is in frame"
        status_color = '#ff8800'  # Orange for warning
    else:
        current_status = "🔍 Face detected - Basic detection mode (install face-recognition for full features)"
        status_color = '#00aaff'  # Blue for basic mode

    curr_names = []

    for (x, y, w, h) in faces:
        # For demo purposes, we'll just call it "Unknown Person"
        name = "Unknown Person"
        curr_names.append(name)

        # Draw rectangle around face
        color = (255, 165, 0)  # Orange color for unknown faces
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, "Basic Detection", (x+w-100, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Countdown timer for detected face
        if name in detection_time:
            scan_time = curr_time - detection_time[name]
            remaining_time = max(0, 10 - int(scan_time))
            cv2.putText(frame, f"{remaining_time:.1f}s", (x, y+h+20), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

            # Update status during countdown
            if remaining_time > 0:
                current_status = f"⏱️ Please stand still for {remaining_time:.0f} seconds - Processing..."
                status_color = '#ffaa00'  # Orange for processing

    # Timer logic
    detected_now = set(curr_names)
    for name in detected_now:
        if name not in detection_time:
            detection_time[name] = curr_time
            last_alarmed[name] = 0

    for name in detected_now:
        scan_time = curr_time - detection_time[name]
        if scan_time >= 10 and (curr_time - last_alarmed.get(name, 0)) >= 30:
            current_status = "✅ SCAN COMPLETE: Basic face detection completed - Install face-recognition for full security features"
            status_color = '#00ff00'  # Green for completion

            # Save image log
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.jpg"
            filepath = os.path.join(LOG_DIR, filename)
            cv2.imwrite(filepath, frame)
            print(f"Detection saved: {filepath}")

            last_alarmed[name] = curr_time

    # Clean up old detections
    for name in list(detection_time.keys()):
        if name not in detected_now:
            del detection_time[name]

    return frame

def get_status():
    """Return current status message and color for GUI"""
    return current_status, status_color

# Start GUI
print("🚀 Starting Security Screening System (Basic Mode)")
print("📋 Status Messages Feature: ✅ Active")
print("🔍 Face Recognition: ❌ Requires face-recognition library")
print("📷 Basic Face Detection: ✅ Using OpenCV")
print("")
print("⚠️  WARNING: This is basic mode with limited functionality")
print("For full identity matching and threat detection, install:")
print("1. CMake from cmake.org")
print("2. python -m pip install face-recognition")
print("3. Then use main.py")
print("")

video_app = guiwindow(get_frame_callback=get_frame, status_callback=get_status)
video_app.run()
