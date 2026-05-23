

import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
# Configuration
EMAIL_ADDRESS = "bigmicky100@gmail.com"
EMAIL_PASSWORD = os.getenv("emailPassword") # Use the App Password here

def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


send_email("Python Test", "Hello! This is a test from Python.", "badshahshaikh147@gmail.com")

