from dotenv import load_dotenv
import os

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime
import cv2
import requests
import tkinter as tk
from tkinter import messagebox

# GUI popup 
def show_error(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide main window
    messagebox.showerror(title, message)
    root.destroy()

# Get location details
def location():
    try:
        response = requests.get('https://ipinfo.io/json').json()
        city = response.get('city', 'Unknown City')
        region = response.get('region', 'Unknown Region')
        coords = response.get('loc', '0,0') 
        locate = [city, region]
        return locate, coords
    except requests.RequestException as e:
        show_error("Location Error", f"Failed to get location: {e}")
        return ["Unknown City", "Unknown Region"], "0,0"

# Main function to send alert email
def send_email(name, frame):
    try:
        locate, coordinates = location()
        latitude, longitude = map(float, coordinates.split(','))
        googlemaps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        # Encode frame to image
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_data = img_encoded.tobytes()

        # Compose email
        msg = MIMEMultipart()
        msg['Subject'] = f"Security Alert: {name} Detected!"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        body = f"""
        <html>
          <body>
            <p>Emergency! A match was detected:</p>
            <p style="color: #666; font-size: 0.8em;">
                <i>Disclaimer: This alert indicates facial similarity to a registered individual.
                Verify identity through official channels before taking action.</i>
            </p>
            <ul>
              <li>Name: {name}</li>
              <li>Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
              <li>City: {locate[0]}</li>
              <li>Region: {locate[1]}</li>
              <li>Location: <a href="{googlemaps_link}">IP Location</a></li>
            </ul>
            <p>See attached image.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach face image
        image = MIMEImage(img_data, name="detected_face.jpg")
        msg.attach(image)

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print('✅ Email sent successfully.')

    except smtplib.SMTPException as e:
        show_error("Email Sending Failed", f"[SMTP Error] {e}")
    except Exception as e:
        show_error("Unexpected Error", f"[Error] {e}")
