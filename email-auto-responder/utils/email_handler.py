# import imaplib
# import smtplib
# import email
# import logging
# from email.message import EmailMessage

# class EmailService:
#     def __init__(self, user, password):
#         self.user = user
#         self.password = password

#     def fetch_unread_emails(self):
#         """Connects to IMAP and gets unread messages"""
#         try:
#             mail = imaplib.IMAP4_SSL("imap.gmail.com")
#             mail.login(self.user, self.password)
#             mail.select("inbox")
            
#             # 1. Audit Log: Check Attempt
#             logging.info("IMAP: Checking for new UNSEEN emails...")

#             _, messages = mail.search(None, 'UNSEEN')
#             email_ids = messages[0].split()
            
#             # 2. Audit Log: Results found
#             logging.info(f"IMAP: Found {len(email_ids)} unread emails.")

#             email_list = []

#             for num in email_ids:
#                 _, data = mail.fetch(num, '(RFC822)')
#                 msg = email.message_from_bytes(data[0][1])

#                 body = ""
#                 if msg.is_multipart():
#                     for part in msg.walk():
#                         if part.get_content_type() == "text/plain":
#                             payload = part.get_payload(decode=True)
#                             if payload:
#                                 body = payload.decode(errors='ignore')
#                                 break
#                 else:
#                     payload = msg.get_payload(decode=True)
#                     if payload:
#                         body = payload.decode(errors='ignore')
                
#                 email_data = {
#                     "from": msg['from'],
#                     "subject": msg['subject'] or "No Subject",
#                     "body": body or ""
#                 }
                
#                 # 3. Audit Log: Individual Email Detail
#                 logging.info(f"IMAP: Successfully read email from {email_data['from']}")
#                 email_list.append(email_data)

#             mail.logout()
#             return email_list

#         except Exception as e:
#             logging.error(f"IMAP Error: {str(e)}")
#             return []

import smtplib
import imaplib
import logging
import email
import logging
from email.message import EmailMessage


class EmailService:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        # This will store the ID of the last email seen when the script started
        self.last_seen_id = 0

    def initialize_checkpoint(self):
        """Finds the ID of the latest email currently in the inbox"""
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.user, self.password)
            mail.select("inbox")
            
            # Search for ALL emails to find the absolute latest one
            _, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            if email_ids:
                # Store the highest ID number
                self.last_seen_id = int(email_ids[-1])
                logging.info(f"CHECKPOINT: Bot starting. Ignoring all emails with ID <= {self.last_seen_id}")
            else:
                self.last_seen_id = 0
                logging.info("CHECKPOINT: Inbox is empty. Bot will process all incoming mail.")
                
            mail.logout()
        except Exception as e:
            logging.error(f"Checkpoint Error: {e}")

    def fetch_unread_emails(self):
        """Fetches only UNSEEN emails that arrived AFTER the checkpoint"""
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.user, self.password)
            mail.select("inbox")
            
            # Search for unread emails
            _, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            email_list = []
            new_max_id = self.last_seen_id

            for num_bytes in email_ids:
                current_id = int(num_bytes)
                
                # --- THE MAGIC FILTER ---
                # Only process if this ID is higher than our last checkpoint
                if current_id > self.last_seen_id:
                    _, data = mail.fetch(num_bytes, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(errors='ignore')
                                    break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors='ignore')
                    
                    email_data = {
                        "from": msg['from'],
                        "subject": msg['subject'] or "No Subject",
                        "body": body or ""
                    }
                    
                    email_list.append({
                        "from": msg['from'],
                        "subject": msg['subject'],
                        "body": body
                    })
                    
                    # Track the highest ID we've seen in this loop
                    if current_id > new_max_id:
                        new_max_id = current_id
            
            # Update the checkpoint so we don't process these again
            self.last_seen_id = new_max_id
            
            mail.logout()
            return email_list

        except Exception as e:
            logging.error(f"IMAP Error: {e}")
            return []

    def _extract_body(self, msg):
        """Helper to extract body text safely"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors='ignore')
        else:
            return msg.get_payload(decode=True).decode(errors='ignore')
        return ""

    def send_reply(self, to_email, subject, body):
        """Sends a response via SMTP"""
        try:
            logging.info(f"SMTP: Attempting to send reply to {to_email}...")
            
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = f"Re: {subject}"
            msg['From'] = self.user
            msg['To'] = to_email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.user, self.password)
                server.send_message(msg)
            
            logging.info(f"SMTP: Reply sent successfully to {to_email}")
            
        except Exception as e:
            logging.error(f"SMTP Error: Failed to send to {to_email}. Error: {str(e)}")

