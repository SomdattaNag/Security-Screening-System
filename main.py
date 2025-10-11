

# Only use _import_or_exit for simple imports
def _import_or_exit(module, pip_name=None):
    try:
        return __import__(module)
    except ImportError:
        pkg = pip_name if pip_name else module
        print(f"\n[ERROR] Required package '{pkg}' is not installed.\nPlease install it with: pip install {pkg}\n")
        exit(1)

# Simple imports
os = _import_or_exit('os')
sys = _import_or_exit('sys')
time = _import_or_exit('time')
pickle = _import_or_exit('pickle')
threading = _import_or_exit('threading')
datetime = _import_or_exit('datetime')
json = _import_or_exit('json')

# Imports that may fail and need user-friendly error
try:
    import cv2
except ImportError:
    print("\n[ERROR] Required package 'cv2' is not installed.\nPlease install it with: pip install opencv-python\n")
    exit(1)
try:
    import numpy as np
except ImportError:
    print("\n[ERROR] Required package 'numpy' is not installed.\nPlease install it with: pip install numpy\n")
    exit(1)
try:
    import face_recognition
except ImportError:
    print("\n[ERROR] Required package 'face_recognition' is not installed.\nPlease install it with: pip install face_recognition\n")
    exit(1)
try:
    from playsound import playsound
except ImportError:
    print("\n[ERROR] Required package 'playsound' is not installed.\nPlease install it with: pip install playsound\n")
    exit(1)
try:
    from message import send_call, send_email, send_sms
except ImportError:
    print("\n[ERROR] Required module 'message' is missing or has import errors.\n")
    exit(1)
try:
    from gui.gui import guiwindow
except ImportError:
    print("\n[ERROR] Required module 'gui.gui' is missing or has import errors.\n")
    exit(1)
try:
    import torch
except ImportError:
    print("\n[ERROR] Required package 'torch' is not installed.\nPlease install it with: pip install torch\n")
    exit(1)
try:
    import pathlib
except ImportError:
    print("\n[ERROR] Required package 'pathlib' is not installed.\nPlease install it with: pip install pathlib\n")
    exit(1)
try:
    from voice import speak_event
except ImportError:
    print("\n[ERROR] Required module 'voice' is missing or has import errors.\n")
    exit(1)

class SecuritySystem:
    def __init__(self):
        self.last_alerted = {} 
        self.alert_cooldown = 10  # Cooldown period in seconds  

        # --- Pause/Resume global state ---
        self.is_paused = False
        self.pause_start_time = None
        self.paused_names_time = {}
        self.last_frame = None  # To freeze video while paused

        # for night mode
        self.night_mode_active = False  # Tracks if night mode is currently active

        # for start camera
        self.face_cap = None
        self.camera_started = False
        self.camera_error = None

        # for tamper detection
        self.tamper_detected = False
        self.tamper_last_check = 0
        self.tamper_alert_sent = False

        # Voice/state management for start conditions
        self.start_alert_playing = False
        self.scroll_x = 640
        self.prev_time = 0
        self.IMAGE_LOG_DIR = "image_logs"
        self.CSV_LOG_DIR = "csv_logs"

        # Audio control - Track alarm state
        self.alarm_playing = False
        self.alarm_lock = threading.Lock()

        # Confidence threshold configuration
        self.face_conf_threshold = 0.4  # Default value
        self.user_conf_threshold = 0.4  # User configured value
        
        # Load saved threshold if exists
        self.load_threshold_settings()

        for directory in [self.IMAGE_LOG_DIR, self.CSV_LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        self.encodings_path = "encodings/face_encodings.pkl"
        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, "rb") as f:
                self.face_encode, self.face_name = pickle.load(f)
        else:
            raise FileNotFoundError("❌ Face encodings not found. Please run `save_encodings.py` first.")

        print("🔧 Security Screening System - Full Face Recognition Mode")
        print("📋 Status Messages Feature: ✅ Active")
        print("🔍 Face Recognition: ✅ Using face_recognition library")
        print("🎯 Identity Matching: ✅ Real confidence scores from face encodings")
        print(f"⚙️ Recognition Threshold: {self.user_conf_threshold:.2f}")
        
        self.detection_time = {}
        self.last_alarmed = {}
        self.current_status = "System ready - Please position yourself in front of the camera"
        self.status_color = '#00ff00'  # Green for ready state
        
        # Load YOLOv5 model
        temp = pathlib.PosixPath
        if os.name == 'nt':
            pathlib.PosixPath = pathlib.WindowsPath
        self.yolo_model = torch.hub.load('yolov5', 'custom', path='models/yolov5n_best.pt', source='local')
        self.ACCESSORY_CLASSES = ["mask", "sunglasses", "cap", "scarf-kerchief"]
        pathlib.PosixPath = temp
        
    def load_threshold_settings(self):
        """Load threshold setting from config file"""
        config_file = "config/system_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    saved_threshold = config.get('recognition_threshold', 0.4)
                    # Ensure the saved value is within allowed range
                    if 0.1 <= saved_threshold <= 0.39:
                        self.user_conf_threshold = saved_threshold
                        print(f"[Config] Loaded threshold: {saved_threshold:.2f}")
        except Exception as e:
            print(f"[Config] Error loading settings: {e}")

    def save_threshold_settings(self):
        """Save threshold setting to config file"""
        config_file = "config/system_config.json"
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            config = {
                'recognition_threshold': self.user_conf_threshold,
                'last_updated': time.time()
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")

    # Safe speak method that checks alarm state
    def safe_speak(self, event, text, sync=False):
        """Speak only if no alarm is currently playing"""
        with self.alarm_lock:
            if self.alarm_playing:
                print(f"[Audio] Suppressing voice message during alarm: {text}")
                return False
        
        speak_event(event, text, sync)
        return True

    # Alarms with alarm_playing flag management
    def threat_alarm(self):
        def play_threat_alarm():
            with self.alarm_lock:
                self.alarm_playing = True
            try:
                playsound("alarms/threat.wav")
            finally:
                with self.alarm_lock:
                    self.alarm_playing = False
                    
        threading.Thread(target=play_threat_alarm, daemon=True).start()

    def safe_alarm(self):
        def play_safe_alarm():
            with self.alarm_lock:
                self.alarm_playing = True
            try:
                playsound("alarms/safe.wav")
            finally:
                with self.alarm_lock:
                    self.alarm_playing = False
                    
        threading.Thread(target=play_safe_alarm, daemon=True).start()

    def run_in_background(self,func, *args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()


    def log_event(self,event,name, confidence,image_filename=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}, {event}, {name}, {confidence}"
        if image_filename:
            log_entry += f", {image_filename}"
        log_entry += "\n"
        log_file = os.path.join(self.CSV_LOG_DIR, "security_log.csv")
        with open(log_file, "a") as f:
            f.write(log_entry)

    def is_low_light(self,frame, brightness_threshold=60):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) < brightness_threshold

    def enhance_for_low_light(self,frame):
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.equalizeHist(l)
        enhanced = cv2.merge((l, a, b))
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


    def is_frame_suspicious(self,frame, gray_thresh=15, color_var_thresh=30, edge_thresh=25):
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

    #Accessory detection using object-detection model module
    def detect_accessories(self,frame, conf_threshold=0.5):
        results = self.yolo_model(frame)
        detections = results.pandas().xyxy[0]
        accessories_found = []

        for _, row in detections.iterrows():
            label = str(row['name']).lower()
            conf = float(row['confidence'])
            if label in self.ACCESSORY_CLASSES :
                if label == "mask" and conf>=0.4:
                    accessories_found.append(label)
                elif conf>= conf_threshold:
                    accessories_found.append(label)

        return accessories_found

    def get_frame(self):
        # Check if camera is started and opened
        if not self.camera_started or self.face_cap is None or not self.face_cap.isOpened():
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            msg = "Camera not started" if not self.camera_error else f"Camera error: {self.camera_error}"
            cv2.putText(blank, msg, (90, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (170, 100, 100), 2)
            self.current_status = msg
            self.status_color = "#888888" if not self.camera_error else "#ff0000"
            return blank

        # Read frame from camera
        ret, frame = self.face_cap.read()
        if not ret:
            self.current_status = " Camera error - Please check camera connection"
            self.status_color = '#ff0000'  # Red for error
            print("❌ Camera read failed.")
            return None

        # Detect tamper every 3 seconds
        suspicious = self.is_frame_suspicious(frame)

        if not suspicious and self.is_low_light(frame):
            self.night_mode_active = True
            frame = self.enhance_for_low_light(frame)
        else:
            self.night_mode_active = False

        if time.time() - self.tamper_last_check > 3:
            if self.is_frame_suspicious(frame):
                if not self.tamper_detected:
                    self.tamper_detected = True
                    print("[Tamper] Suspicious frame started")

                if not self.tamper_alert_sent:
                    self.current_status = "⚠️ Possible tampering detected - Low visual content. Please review the camera device"
                    self.status_color = '#ff0000'
                    print("[Tamper Alert] Visual anomaly Detected. Please review the camera device")
                    self.tamper_alert_sent = True

                    # Update status panel
                    if hasattr(self, 'video_app') and hasattr(self.video_app, 'update_status'):
                        self.video_app.update_status(self.current_status, self.status_color)

            else:
                if self.tamper_detected:
                    print("[Tamper] Tampering ended")
                    self.current_status = "✅ Camera recovered from tampering"
                    self.status_color = "#00ff00"

                    # Update GUI immediately
                    if hasattr(self, 'video_app') and hasattr(self.video_app, 'update_status'):
                        self.video_app.update_status(self.current_status, self.status_color)
                self.tamper_detected = False
                self.tamper_alert_sent = False

            self.tamper_last_check = time.time()

        if self.tamper_detected:
            cv2.putText(frame, "⚠️ CAMERA TAMPERING DETECTED", (40, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            return frame  # Just show the suspicious frame but skip detection

        frame = cv2.flip(frame, 1)
        curr_time = time.time()

        fps = 1 / (curr_time - self.prev_time) if (curr_time - self.prev_time) > 0 else 0

        self.prev_time = curr_time

        cv2.putText(frame, f"FPS: {int(fps)}", (520, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        # ------------- Pause Handling -----------------
        if self.is_paused:
            self.current_status = "⏸️ Detection Paused. Click Resume to continue."
            self.status_color = '#888888'
            # Return last frame to freeze the GUI
            if self.last_frame is not None:
                return self.last_frame
            else:
                self.last_frame = frame.copy()
                return self.last_frame
        else:
            self.last_frame = frame.copy()

        # --- START CAMERA START MESSAGE FEATURE ---
        if self.start_alert_playing:
            message = "Security Screening System starting. Peaople are waiting in the line. Please cooperate with the scanning procedure."
            self.scroll_x -= 8
            if self.scroll_x < -len(message) * 15:
                self.scroll_x = 640
            cv2.putText(frame, message, (self.scroll_x, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame  # show live video but skip detection

        # -------------- Accessory Detection Before Face Recognition --------------
        accessories = self.detect_accessories(frame)
        if accessories:
            # Reset the countdown timer when an accessory is detected
            self.detection_time.clear()
            
            self.current_status = f"⚠️ Please remove: {', '.join(accessories).title()}"
            self.safe_speak("remove_accessory", f"Please remove: {', '.join(accessories)}")
            self.status_color = '#ff0000'
            return frame  # Skip face recognition while showing live frames

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        curr_names = []

        # Update status based on face detection
        if len(face_locations) == 0:
            self.current_status = "👁️ Scanning for faces... Please position yourself in front of the camera"
            self.status_color = '#ffff00'  # Yellow for scanning
        elif len(face_locations) > 1:
            self.current_status = "⚠️ Multiple faces detected - Please ensure only one person is in frame"
            self.status_color = '#ff8800'  # Orange for warning

        for face_encoding, face_location in zip(face_encodings, face_locations):
            face_distances = face_recognition.face_distance(self.face_encode, face_encoding)
            best_match_index = np.argmin(face_distances)
            name = "No match"

            # Use user-configured threshold instead of hardcoded 0.4
            if face_distances[best_match_index] < self.user_conf_threshold:
                name = self.face_name[best_match_index]
                confidence = (1 - face_distances[best_match_index]) * 100
                confidence_text = f"{confidence:.2f}%"
                # Update status for recognized face
                self.current_status = f"✅ Match found: {name} (Confidence: {confidence:.1f}%)"
                self.status_color = '#00ff00'  # Green for match
            else:
                confidence_text = f"{(1 - face_distances[best_match_index]) * 100:.2f}%"
                # Update status for unrecognized face
                self.current_status = "❌ No match detected. You are safe to go."
                self.status_color = '#ff0000'  # Red for no match

            curr_names.append(name)

            top, right, bottom, left = [coord * 4 for coord in face_location]
            color = (0, 255, 0) if name != "No match" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, confidence_text, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # added: a countdown timer for each detected face
            if name in self.detection_time:
                scan_time = curr_time - self.detection_time[name]
                remaining_time = max(0, 10 - int(scan_time))
                cv2.putText(frame, f"{remaining_time:.1f}s", (left, top + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

                # Update status during countdown
                if remaining_time > 0:
                    self.current_status = f"⏱️ Please stand still for {remaining_time:.0f} seconds - Processing..."
                    self.status_color = '#ffaa00'  # Orange for processing

        # starting timer
        detected_now = set(curr_names)
        for name in detected_now:
            if name not in self.detection_time:
                self.detection_time[name] = curr_time
                self.last_alarmed[name] = 0
                    
                last_time = self.last_alerted.get(name, 0)
                if (curr_time - last_time) >= self.alert_cooldown:
                        self.safe_speak("face_detected", "Please stand still for 10 seconds.")
                        self.last_alerted[name] = curr_time


        for name in detected_now:
            scan_time = curr_time - self.detection_time[name]
            if scan_time >= 10 and (curr_time - self.last_alarmed.get(name, 0)) >= 30:
                if name != "No match":
                    self.current_status = f"🚨 THREAT DETECTED: {name} - Security alert triggered!"
                    self.status_color = '#ff0000'  # Red for threat
                    self.safe_speak("scan_complete_threat", "scan complete", sync=True)
                    self.threat_alarm()
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{name}_{timestamp}.jpg"
                    filepath = os.path.join(self.IMAGE_LOG_DIR, filename)
                    cv2.imwrite(filepath, frame)

                    if confidence > 90:
                        send_call(name, confidence)
                        send_sms(name, confidence)
                        self.current_status = f"🚨 Very HIGH THREAT DETECTED: {name} - Security alert triggered! Call and SMS sent."
                        self.status_color = '#8B0000'  # Crimson for very high alert
                        self.log_event("Very High Threat", name, confidence, filename)
                    elif confidence > 80:
                        send_email(name, frame, confidence)
                        send_sms(name, confidence)
                        self.current_status = f"🚨 HIGH THREAT DETECTED: {name} - Security alert triggered! Email and SMS sent."
                        self.status_color = '#ff0000'  # Red for high threat
                        self.log_event("High Threat", name, confidence, filename)
                    elif confidence > 70:
                        send_email(name, frame, confidence)
                        
                        self.current_status = f"🚨 MEDIUM THREAT DETECTED: {name} - Security alert triggered! Email sent."
                        self.status_color = '#ff8800'  # Orange for medium threat
                        self.log_event("Medium Threat", name, confidence, filename)
                    elif confidence > 60:
                        self.current_status = f"🚨 LOW THREAT DETECTED: {name} - Security alert triggered!"
                        self.status_color = '#ffaa00'
                        self.log_event("Low Threat", name, confidence, filename)

                else:
                    self.current_status = "✅ SCAN COMPLETE: No match detected - You are safe to proceed"
                    self.status_color = '#00ff00'  # Green for safe
                    self.safe_speak("scan_complete_safe", "scan completed you are free to go.", sync=True)
                    self.safe_alarm()

                self.last_alarmed[name] = curr_time

        for name in list(self.detection_time.keys()):
            if name not in detected_now:
                del self.detection_time[name]

        if self.night_mode_active:
            cv2.putText(frame, "🌙 Night Mode", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 255), 1)

        return frame


    def start_camera(self):
        """
        Initializes the webcam only when called (e.g., from GUI's Start button).
        Prevents re-initialization and sets status messages.
        """
        if self.camera_started:
            self.current_status = "Camera already started"
            self.status_color = "#28ce5a"
            return
        try:
            self.face_cap = cv2.VideoCapture(0)
            if not self.face_cap.isOpened():
                raise RuntimeError("Could not access the webcam.")

            self.current_status = "Camera started"
            self.camera_started = True
            self.start_alert_playing = True

            def resume_scanning():
                self.start_alert_playing = False

            # Play asynchronously but call resume_scanning after it finishes
            threading.Thread(
                target=lambda: (self.safe_speak(
                    "camera_start",
                    "Security Screening System starting. People are waiting in the line, please cooperate with the scanning procedure.",
                    sync=True  # force blocking in this thread so we know when it ends
                ), resume_scanning()),
                daemon=True
            ).start()

            self.status_color = "#00ff00"
            self.camera_error = None
        except Exception as e:
            self.current_status = f"Camera error: {e}"
            self.camera_error = str(e)
            self.status_color = "#ff0000"
            self.face_cap = None
            self.camera_started = False


    def get_status(self):
        """Return current status message and color for GUI"""
        return self.current_status, self.status_color


    # Start GUI
    def run(self):
        self.video_app = guiwindow(
            get_frame_callback=self.get_frame,
            status_callback=self.get_status,
            start_camera_callback=self.start_camera 
        )

    # Set pause state references for bidirectional access
        self.video_app.set_pause_vars(
            lambda: self.is_paused,
            lambda v: setattr(self, 'is_paused', v),
            lambda: self.pause_start_time,
            lambda v: setattr(self, 'pause_start_time', v),
            lambda: self.paused_names_time,
            lambda v: setattr(self, 'paused_names_time', v),
            lambda: self.detection_time
        )

        self.video_app.run()

if __name__== '__main__':
    Security_Screening_System=SecuritySystem()
    Security_Screening_System.run()
