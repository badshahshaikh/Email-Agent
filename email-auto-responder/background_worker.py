# background_worker.py
import os
import time
from orchestrator import EmailOrchestrator
from workflows.processor import RequestWorkflow
from utils.email_handler import EmailService
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
# Config (Use App Passwords!)
# EMAIL = "bigmicky100@gmail.com"
# PASS = "your_app_password"

EMAIL = "bigmicky100@gmail.com"
PASS = os.getenv("emailPassword") # Use the App Password here


bot = EmailOrchestrator()
email_service = EmailService(EMAIL, PASS)

def run_auto_responder():
    print("Bot is listening for emails...")
    while True:
        try:
            # 1. Fetch
            unread_emails = email_service.fetch_unread_emails()
            
            for mail in unread_emails:

                if not mail['body'] or len(mail['body'].strip()) < 5:
                    print(f"Skipping empty email from {mail['from']}")
                    continue

                print(f"Processing email from: {mail['from']}")
                
                # 2. Analyze (Your AI)
                analysis = bot.analyze(mail['body'])
                
                # 3. Bank API Logic (Your Workflow)
                processor = RequestWorkflow(analysis)
                api_results = processor.execute_actions()
                
                # 4. Construct Reply
                reply_body = f"Hello {analysis['entities']['customer_name'] or 'Customer'},\n\n"
                reply_body += f"Summary of your request: {analysis['summary']}\n\n"
                
                for res in api_results:
                    if 'data' in res:
                        reply_body += f"Result for {res['intent']}: {res['data']}\n"
                    else:
                        reply_body += f"Error: {res['error']}\n"
                
                reply_body += "\nThank you for banking with us!"

                # 5. Send
                email_service.send_reply(mail['from'], mail['subject'], reply_body)
                print(f"Reply sent to {mail['from']}")

        except Exception as e:
            print(f"Error in loop: {e}")
            
        time.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    run_auto_responder()