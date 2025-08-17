import os
import cv2
import numpy as np
import face_recognition
import pickle
import time
from datetime import datetime
import pandas as pd
from mtcnn import MTCNN
import pygame
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import threading

class EnhancedSecuritySystem:
    def __init__(self):
        # Initialize system
        load_dotenv()
        self.setup_directories()
        self.setup_audio()
        self.load_known_faces()
        self.detector = MTCNN()
        self.cap = cv2.VideoCapture(0)
        self.log_file = 'logs/security_log.csv'
        self.initialize_logs()
        
        # Configuration
        self.alert_threshold = 0.6
        self.known_faces = {}
        self.known_encodings = []
        self.known_names = []
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes cooldown

    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs('image_logs', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('known_faces', exist_ok=True)

    def setup_audio(self):
        """Initialize audio system"""
        pygame.mixer.init()
        self.alert_sound = pygame.mixer.Sound('alerts/alert.wav')

    def load_known_faces(self):
        """Load known faces from the known_faces directory"""
        known_faces_dir = 'known_faces'
        for filename in os.listdir(known_faces_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(os.path.join(known_faces_dir, filename))
                encoding = face_recognition.face_encodings(image)[0]
                self.known_encodings.append(encoding)
                self.known_names.append(name)

    def initialize_logs(self):
        """Initialize log file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write('timestamp,event_type,confidence,location,image_path\n')

    def log_event(self, event_type, confidence=0.0, location='', image=None):
        """Log security events to CSV"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_path = ''
        
        if image is not None:
            image_path = f"image_logs/event_{int(time.time())}.jpg"
            cv2.imwrite(image_path, image)
        
        log_entry = f"{timestamp},{event_type},{confidence:.2f},{location},{image_path}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(f"[{timestamp}] {event_type} - Confidence: {confidence:.2f}")

    def send_alert(self, event_type, confidence, image=None):
        """Send alert via email and play sound"""
        current_time = time.time()
        
        # Check cooldown
        if event_type in self.last_alert_time:
            if current_time - self.last_alert_time[event_type] < self.alert_cooldown:
                return
        
        self.last_alert_time[event_type] = current_time
        
        # Play alert sound
        try:
            self.alert_sound.play()
        except:
            print("Could not play alert sound")
        
        # Send email alert
        self.send_email_alert(event_type, confidence, image)

    def send_email_alert(self, event_type, confidence, image=None):
        """Send email alert with image attachment"""
        try:
            # Email configuration
            sender = os.getenv('EMAIL_USER')
            password = os.getenv('EMAIL_PASSWORD')
            recipient = os.getenv('ALERT_EMAIL')
            
            if not all([sender, password, recipient]):
                print("Email configuration missing. Please set up .env file.")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = f"Security Alert: {event_type}"
            
            # Add message body
            body = f"""
            Security Alert
            =============
            
            Event Type: {event_type}
            Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            Confidence: {confidence:.2f}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add image if available
            if image is not None:
                _, img_encoded = cv2.imencode('.jpg', image)
                img_data = img_encoded.tobytes()
                image = MIMEImage(img_data, name='alert.jpg')
                msg.attach(image)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
                
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")

    def detect_faces(self, frame):
        """Detect faces using MTCNN"""
        # Convert BGR to RGB (MTCNN uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.detector.detect_faces(rgb_frame)
        
        face_locations = []
        face_encodings = []
        
        for result in results:
            if result['confidence'] > self.alert_threshold:
                x, y, w, h = result['box']
                face_locations.append((y, x + w, y + h, x))
                
                # Get face encodings
                face_encoding = face_recognition.face_encodings(rgb_frame, [(y, x + w, y + h, x)])
                if face_encoding:
                    face_encodings.append(face_encoding[0])
        
        return face_locations, face_encodings

    def recognize_faces(self, face_encodings):
        """Recognize faces by comparing with known faces"""
        names = []
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_names[first_match_index]
            
            names.append(name)
        
        return names

    def run(self):
        """Main loop for the security system"""
        self.log_event("System", "Security system started")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    self.log_event("Error", "Failed to grab frame")
                    break
                
                # Detect faces
                face_locations, face_encodings = self.detect_faces(frame)
                
                # Recognize faces
                names = self.recognize_faces(face_encodings) if face_encodings else []
                
                # Process each detected face
                for (top, right, bottom, left), name in zip(face_locations, names):
                    # Draw rectangle around face
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    
                    # Draw label
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
                    
                    # Log and alert for unknown faces
                    if name == "Unknown":
                        confidence = max([result['confidence'] for result in self.detector.detect_faces(
                            cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2RGB)
                        )], default=0.0)
                        
                        self.log_event("UnknownPerson", confidence, f"({left},{top})-({right},{bottom})", frame)
                        self.send_alert("Unknown Person Detected", confidence, frame)
                
                # Display the resulting frame
                cv2.imshow('Security Feed', frame)
                
                # Break the loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            self.log_event("Error", 0, f"An error occurred: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release resources and clean up"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.log_event("System", "Security system stopped")

if __name__ == "__main__":
    security_system = EnhancedSecuritySystem()
    security_system.run()
