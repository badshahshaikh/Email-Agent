import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = "bigmicky100@gmail.com"
PASS = os.getenv("emailPassword") # or hardcode your app password here

def test_imap():
    try:
        print("Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASS)
        mail.select("inbox")
        
        status, messages = mail.search(None, 'UNSEEN')
        ids = messages[0].split()
        
        print(f"✅ Success! Connected to {EMAIL}")
        print(f"Total emails in Inbox: {len(ids)}")
        
        mail.logout()
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_imap()