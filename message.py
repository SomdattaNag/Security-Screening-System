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
from twilio.rest import Client


load_dotenv()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if not password:
        return False
    clean = password.replace(" ", "")
    return len(clean) == 16


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

twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
alert_phones = os.getenv("ALERT_PHONE_NUMBERS", "").split(",")
client = Client(twilio_sid, twilio_token)

if not all(is_valid_email(email) for email in receiver_emails + [sender_email]):
    raise ValueError("One or more email addresses are invalid.")

if not is_valid_password(sender_password):
    raise ValueError("Invalid Gmail app password format. It should be 16 alphabetic characters (with or without spaces).")

def send_sms(name, confidence): 
     #city, region, googlemaps_link
    locate, coordinates = location()
    latitude, longitude = map(float, coordinates.split(','))
    googlemaps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    city=locate[0]
    region=locate[1]

    
    try:

        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_body = (
            f"🚨 Security Alert!\n"
            f"Name: {name}\n"
            f"Confidence: {int(confidence)}%\n"
            f"Time: {time_now}\n"
            f"Location: {city}, {region}\n"
            f"Map: {googlemaps_link}"
        )
        for number in alert_phones:
            client.messages.create(
                body=message_body,
                from_=twilio_phone,
                to=number.strip()
            )
        print("SMS alert sent successfully.")
    except Exception as e:
        print(f"SMS sending failed: {e}")


def send_email(name,frame,confidence):

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
    <head>
        <style>
            .container {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 10px;
                width: 90%;
                max-width: 600px;
                margin: auto;
            }}
            .header {{
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 10px 10px 0 0;
                font-size: 20px;
                text-align: center;
            }}
            .content {{
                background-color: white;
                padding: 20px;
                border-radius: 0 0 10px 10px;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                margin-top: 15px;
                font-style: italic;
            }}
            a {{
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">🚨 Security Alert: {name} Detected</div>
            <div class="content">
                <p><strong>Emergency!</strong> A face match has been detected.</p>
                <ul>
                    <li><strong>Name:</strong> {name}</li>
                    <li><strong>Confidence:</strong> {int(confidence)}%</li>
                    <li><strong>Time:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
                    <li><strong>City:</strong> {locate[0]}</li>
                    <li><strong>Region:</strong> {locate[1]}</li>
                    <li><strong>Location:</strong> <a href="{googlemaps_link}" target="_blank">View on Map</a></li>
                </ul>
                <p>Attached is the detected face image.</p>
                <div class="footer">
                    Disclaimer: This alert is based on facial similarity. Always verify identity before action.
                </div>
            </div>
        </div>
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



