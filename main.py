import cv2
import numpy as np
import os
import face_recognition
from playsound import playsound
from message import send_call, send_email, send_sms
import time
import sys
from gui.gui import guiwindow
import datetime
import pickle
import threading
import torch
import pathlib
from voice import speak_event
# --- Pause/Resume global state ---
is_paused = False
pause_start_time = None
paused_names_time = {}
last_frame = None  # To freeze video while paused

# for night mode
night_mode_active = False  # Tracks if night mode is currently active

# for start camera
face_cap = None
camera_started = False
camera_error = None

# for tamper detection
tamper_detected = False
tamper_last_check = 0
tamper_alert_sent = False

# Voice/state management for start conditions
start_alert_playing = False
scroll_x = 640

prev_time = 0
IMAGE_LOG_DIR = "image_logs"
CSV_LOG_DIR = "csv_logs"

#create log if it doesn't exist
for directory in [IMAGE_LOG_DIR, CSV_LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)


# Alarms
def threat_alarm():
    threading.Thread(target=playsound, args=("alarms/threat.wav",), daemon=True).start()

def safe_alarm():
    threading.Thread(target=playsound, args=("alarms/safe.wav",), daemon=True).start()

def run_in_background(func, *args, **kwargs):
    threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()


encodings_path = "encodings/face_encodings.pkl"

if os.path.exists(encodings_path):
    with open(encodings_path, "rb") as f:
        face_encode, face_name = pickle.load(f)
else:
    raise FileNotFoundError("❌ Face encodings not found. Please run `save_encodings.py` first.")

print("🔧 Security Screening System - Full Face Recognition Mode")
print("📋 Status Messages Feature: ✅ Active")
print("🔍 Face Recognition: ✅ Using face_recognition library")
print("🎯 Identity Matching: ✅ Real confidence scores from face encodings")


detection_time = {}
last_alarmed = {}
current_status = "System ready - Please position yourself in front of the camera"
status_color = '#00ff00'  # Green for ready state

def log_event(event,name, confidence,image_filename=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}, {event}, {name}, {confidence}"
    if image_filename:
        log_entry += f", {image_filename}"
    log_entry += "\n"
    log_file = os.path.join(CSV_LOG_DIR, "security_log.csv")
    with open(log_file, "a") as f:
        f.write(log_entry)

def is_low_light(frame, brightness_threshold=60):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < brightness_threshold

def enhance_for_low_light(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    enhanced = cv2.merge((l, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def is_frame_suspicious(frame, gray_thresh=15, color_var_thresh=30, edge_thresh=25):
    """
    Detects suspicious frames: black/white/gray, or low-texture plain color frames with slight gradient.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_mean = np.mean(gray)
    gray_var = np.var(gray)

    # Color channel variances
    b_var = np.var(frame[:, :, 0])
    g_var = np.var(frame[:, :, 1])
    r_var = np.var(frame[:, :, 2])
    color_var_avg = (b_var + g_var + r_var) / 3

    # Laplacian edge variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 1. Too dark/bright with low variance
    if (gray_mean < 10 or gray_mean > 245) and gray_var < gray_thresh:
        return True

    # 2. Very flat grayscale
    if gray_var < gray_thresh:
        return True

    # 3. Plain color frame (even with slight gradient)
    if color_var_avg < color_var_thresh and laplacian_var < edge_thresh:
        return True

    return False

# Load YOLOv5 model
temp = pathlib.PosixPath

if os.name == 'nt':
    pathlib.PosixPath = pathlib.WindowsPath
yolo_model = torch.hub.load('yolov5', 'custom', path='models/yolov5n_best.pt', source='local')
ACCESSORY_CLASSES = ["mask", "sunglasses", "cap", "scarf-kerchief"]
pathlib.PosixPath = temp

def detect_accessories(frame, conf_threshold=0.5):
    results = yolo_model(frame)
    detections = results.pandas().xyxy[0]
    accessories_found = []

    for _, row in detections.iterrows():
        label = str(row['name']).lower()
        conf = float(row['confidence'])
        if label in ACCESSORY_CLASSES :
            if label == "mask" and conf>=0.4:
                accessories_found.append(label)
            elif conf>= conf_threshold:
                accessories_found.append(label)

    return accessories_found

def get_frame():
    global prev_time, current_status, status_color, is_paused, pause_start_time, paused_names_time, last_frame,tamper_detected,tamper_last_check,tamper_alert_sent,start_alert_playing,scroll_x
    # Check if camera is started and opened
    if not camera_started or face_cap is None or not face_cap.isOpened():
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        msg = "Camera not started" if not camera_error else f"Camera error: {camera_error}"
        cv2.putText(blank, msg, (90, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (170, 100, 100), 2)
        current_status = msg
        status_color = "#888888" if not camera_error else "#ff0000"
        return blank

    
    # Read frame from camera
    ret, frame = face_cap.read()
    if not ret:
        current_status = " Camera error - Please check camera connection"
        status_color = '#ff0000'  # Red for error
        print("❌ Camera read failed.")
        return None
    
    # Detect tamper every 3 seconds
    global night_mode_active
    suspicious = is_frame_suspicious(frame)

    if not suspicious and is_low_light(frame):
        night_mode_active = True
        frame = enhance_for_low_light(frame)
    else:
        night_mode_active = False
    
    if time.time() - tamper_last_check > 3:
        if is_frame_suspicious(frame):
            if not tamper_detected:
                tamper_detected = True
                print("[Tamper] Suspicious frame started")
            
            if not tamper_alert_sent:
                current_status = "⚠️ Possible tampering detected - Low visual content. Please review the camera device"
                status_color = '#ff0000'
                print("[Tamper Alert] Visual anomaly Detected. Please review the camera device")
                tamper_alert_sent = True

                # Update status panel
                if 'video_app' in globals() and hasattr(video_app, 'update_status'):
                    video_app.update_status(current_status, status_color)

        else:
            if tamper_detected:
                print("[Tamper] Tampering ended")
                current_status = "✅ Camera recovered from tampering"
                status_color = "#00ff00"

                # Update GUI immediately
                if 'video_app' in globals() and hasattr(video_app, 'update_status'):
                    video_app.update_status(current_status, status_color)
            tamper_detected = False
            tamper_alert_sent = False

        tamper_last_check = time.time()

    if tamper_detected:
        cv2.putText(frame, "⚠️ CAMERA TAMPERING DETECTED", (40, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        return frame  # Just show the suspicious frame but skip detection


    frame = cv2.flip(frame, 1)
    curr_time = time.time()

    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0

    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (520,250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    # ------------- Pause Handling -----------------
    if is_paused:
        current_status = "⏸️ Detection Paused. Click Resume to continue."
        status_color = '#888888'
        # Return last frame to freeze the GUI
        if last_frame is not None:
            return last_frame
        else:
            last_frame = frame.copy()
            return last_frame
    else:
        last_frame = frame.copy()

    # --- START CAMERA START MESSAGE FEATURE ---
    if start_alert_playing:
        message = "Security Screening System starting. Peaople are waiting in the line. Please cooperate with the scanning procedure."
        scroll_x -= 8
        if scroll_x < -len(message) * 15:
            scroll_x = 640
        cv2.putText(frame, message, (scroll_x, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2 )
        return frame  # show live video but skip detection
    
    # -------------- Accessory Detection Before Face Recognition --------------
    accessories = detect_accessories(frame)
    if accessories:
        current_status = f"⚠️ Please remove: {', '.join(accessories).title()}"
        speak_event("remove_accessory",f"Please remove: {', '.join(accessories)}")
        status_color = '#ff0000'    
        return frame  # Skip face recognition while showing live frames
    
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    curr_names = []

    # Update status based on face detection
    if len(face_locations) == 0:
        current_status = "👁️ Scanning for faces... Please position yourself in front of the camera"
        status_color = '#ffff00'  # Yellow for scanning
    elif len(face_locations) > 1:
        current_status = "⚠️ Multiple faces detected - Please ensure only one person is in frame"
        status_color = '#ff8800'  # Orange for warning

    for face_encoding, face_location in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(face_encode, face_encoding)
        best_match_index = np.argmin(face_distances)
        name = "No match"

        if face_distances[best_match_index] < 0.4:
            name = face_name[best_match_index]
            confidence = (1 - face_distances[best_match_index]) * 100
            confidence_text = f"{confidence:.2f}%"
            # Update status for recognized face
            current_status = f"✅ Match found: {name} (Confidence: {confidence:.1f}%)"
            status_color = '#00ff00'  # Green for match
        else:
            confidence_text = f"{(1 - face_distances[best_match_index]) * 100:.2f}%"
            # Update status for unrecognized face
            current_status = "❌ No match detected. You are safe to go."
            status_color = '#ff0000'  # Red for no match

        curr_names.append(name)

        top, right, bottom, left = [coord * 4 for coord in face_location]
        color = (0, 255, 0) if name != "No match" else (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, confidence_text, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        #added: a countdown timer for each detected face

        if name in detection_time:
            scan_time = curr_time - detection_time[name]
            remaining_time = max(0, 10 - int(scan_time))
            cv2.putText(frame, f"{remaining_time:.1f}s", (left, top + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

            # Update status during countdown
            if remaining_time > 0:
                current_status = f"⏱️ Please stand still for {remaining_time:.0f} seconds - Processing..."
                status_color = '#ffaa00'  # Orange for processing
    
    #starting timer
    detected_now = set(curr_names)
    for name in detected_now:
        if name not in detection_time:
            #first detection
            detection_time[name] = curr_time
            last_alarmed[name] = 0
            speak_event("face_detected","Please stand still for 10 seconds.")

    for name in detected_now:
        scan_time = curr_time - detection_time[name]
        if scan_time >= 10 and (curr_time - last_alarmed.get(name, 0)) >= 30:
            if name != "No match":
                current_status = f"🚨 THREAT DETECTED: {name} - Security alert triggered!"
                status_color = '#ff0000'  # Red for threat
                speak_event("scan_complete_threat","scan complete",sync = True)
                threat_alarm()
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.jpg"
                filepath = os.path.join(IMAGE_LOG_DIR, filename)
                cv2.imwrite(filepath, frame)
                
                if confidence > 90:
                    send_call(name, confidence)
                    send_sms(name, confidence)
                    current_status = f"🚨 Very HIGH THREAT DETECTED: {name} - Security alert triggered! Call and SMS sent."
                    status_color = '#8B0000' #Crimson for very high alert
                    log_event("Very High Threat", name, confidence, filename)
                elif confidence >80:
                    send_email(name, frame, confidence)
                    send_sms(name, confidence)
                    current_status = f"🚨 HIGH THREAT DETECTED: {name} - Security alert triggered! Email and SMS sent."
                    status_color = '#ff0000'  # Red for high threat
                    log_event("High Threat", name, confidence, filename)
                elif confidence >70:
                    send_email(name, frame, confidence)
                    current_status = f"🚨 MEDIUM THREAT DETECTED: {name} - Security alert triggered! Email sent."
                    status_color = '#ff8800'  # Orange for medium threat
                    log_event("Medium Threat", name, confidence, filename)
                elif confidence > 60:
                    current_status = f"🚨 LOW THREAT DETECTED: {name} - Security alert triggered!"
                    status_color = '#ffaa00'
                    log_event("Low Threat", name, confidence, filename)

            else:
                current_status = "✅ SCAN COMPLETE: No match detected - You are safe to proceed"
                status_color = '#00ff00'  # Green for safe
                speak_event("scan_complete_safe","scan completed you are free to go.",sync = True)
                safe_alarm()

            last_alarmed[name] = curr_time

    for name in list(detection_time.keys()):
        if name not in detected_now:
            del detection_time[name]
            
    if night_mode_active:
        cv2.putText(frame, "🌙 Night Mode", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 255), 1)

    return frame

def start_camera():
    """
    Initializes the webcam only when called (e.g., from GUI's Start button).
    Prevents re-initialization and sets status messages.
    """
    global face_cap, current_status, status_color, camera_error, camera_started,start_alert_playing
    if camera_started:
        current_status = "Camera already started"
        status_color = "#28ce5a"
        return
    try:
        face_cap = cv2.VideoCapture(0)
        if not face_cap.isOpened():
            raise RuntimeError("Could not access the webcam.")
        
        current_status = "Camera started"
        camera_started = True
        start_alert_playing = True

        def resume_scanning():
            global start_alert_playing
            start_alert_playing = False

        # Play asynchronously but call resume_scanning after it finishes
        threading.Thread(
            target=lambda: (speak_event(
                "camera_start",
                "Security Screening System starting. People are waiting in the line, please cooperate with the scanning procedure.",
                sync=True  # force blocking in this thread so we know when it ends
            ), resume_scanning()),
            daemon=True
        ).start()

        status_color = "#00ff00"
        camera_error = None
    except Exception as e:
        current_status = f"Camera error: {e}"
        camera_error = str(e)
        status_color = "#ff0000"
        face_cap = None
        camera_started = False


def get_status():
    """Return current status message and color for GUI"""
    return current_status, status_color

# ------------- Add Pause/Resume Attribute Interface for GUI -----------
def set_pause_vars(
    get_is_paused, set_is_paused,
    get_pause_start_time, set_pause_start_time,
    get_paused_names_time, set_paused_names_time,
):
    global is_paused, pause_start_time, paused_names_time
    # Not strictly needed with globals (optional if handling state in one file), but included for clarity & future-proofing

# Start GUI

video_app = guiwindow(
    get_frame_callback=get_frame,
    status_callback=get_status,
    start_camera_callback=start_camera 
)

# Set pause state references for bidirectional access
video_app.set_pause_vars(
    lambda: is_paused,
    lambda v: globals().__setitem__('is_paused', v),
    lambda: pause_start_time,
    lambda v: globals().__setitem__('pause_start_time', v),
    lambda: paused_names_time,
    lambda v: globals().__setitem__('paused_names_time', v),
    lambda: detection_time 
)


video_app.run()
