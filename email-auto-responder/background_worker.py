# background_worker.py
import os
import time
import logging

import requests
# from orchestrator import EmailOrchestrator
from workflows.processor import RequestWorkflow
from workflows.response_generator import ResponseGenerator
from utils.email_handler import EmailService
from utils.security import audit_log
# from apis.bank_services import BankAPI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

EMAIL = os.getenv("EMAIL")
PASS = os.getenv("emailPassword") # Use the App Password here
API_URL = os.getenv("API_URL")

# bank_api = BankAPI() 
# bot = EmailOrchestrator()
email_service = EmailService(EMAIL, PASS)

def run_auto_responder():
    print("Bot is listening for emails...")
    email_service.initialize_checkpoint() 
    while True:
        try:
            # 1. Fetch
            unread_emails = email_service.fetch_unread_emails()
            
            for mail in unread_emails:
                sender = mail['from_email']  # Extract just the email address
                payload = {
                    "subject": mail['subject'], 
                    "body": mail['body'], 
                    "sender": sender
                }

                # response = requests.post(API_URL, json=payload)

                print(f"Processing email from: {sender}")
                audit_log("WORKER", "API_START", f"Requesting analysis for {sender}")

                try:
                    response = requests.post(API_URL, json=payload, timeout=90)
                    response.raise_for_status()
                    result = response.json()
                except Exception as api_err:
                    audit_log("API_CALL", "FAILED", str(api_err))
                    print(f"API Error: {api_err}")
                    continue

                customer_name = result.get("customer_name", "Customer")
                api_results = result.get("api_results", [])


                reply_body = ResponseGenerator.generate(
                    customer_name=customer_name,
                    api_results=api_results
                )

                # 5. Send
                email_service.send_reply(sender, mail['subject'], reply_body)
                audit_log("OUTBOUND", "SENT", f"To: {sender}")
                print(f"Reply sent to {sender}")

        except Exception as e:
            print(f"Error in loop: {e}")
            audit_log("SYSTEM", "ERROR", str(e))

        time.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    run_auto_responder()