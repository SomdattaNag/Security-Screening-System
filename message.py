import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime
import cv2
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if not password:
        return False
    clean = password.replace(" ", "")
    return len(clean) == 16 and clean.isalpha()





def location():
        response = requests.get('https://ipinfo.io/json').json()
        city = response.get('city', 'Unknown City')
        region = response.get('region', 'Unknown Region')
        coords = response.get('loc', '0,0') 
        locate=[city,region]
        return locate, coords

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
receiver_emails = os.getenv('RECEIVER_EMAIL', '').split(',')

if not all(is_valid_email(email) for email in receiver_emails + [sender_email]):
    raise ValueError("One or more email addresses are invalid.")

if not is_valid_password(sender_password):
    raise ValueError("Invalid Gmail app password format. It should be 16 alphabetic characters (with or without spaces).")



def send_email(name,frame):

    locate, coordinates = location()
    latitude, longitude = map(float, coordinates.split(','))
    googlemaps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_data = img_encoded.tobytes()
    msg = MIMEMultipart()
    msg['Subject'] = f"Security Alert: {name} Detected!"
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    
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
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print('Email sent successfully.')
