import imaplib
import email
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = "emails.db"
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("❌ Missing email credentials. Set EMAIL_USER and EMAIL_PASS in .env")

def store_email(email_id, sender, recipient, subject, body, timestamp, label="INBOX"):
    """Stores an email in the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR IGNORE INTO emails (email_id, sender, recipient, subject, body, timestamp, label)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email_id, sender, recipient, subject, body, timestamp, label))
    
    conn.commit()
    conn.close()

def fetch_emails():
    """Fetches emails using IMAP and stores them in the database."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        for email_id in email_ids[-10:]:  # Fetch last 10 emails
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            sender = msg["From"]
            recipient = msg["To"]
            subject = msg["Subject"]
            timestamp = msg["Date"]

            # Extract email body
            body = "No Body"
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            store_email(email_id.decode(), sender, recipient, subject, body, timestamp)  # ✅ FIXED

        print("✅ Emails fetched and stored successfully!")

    except Exception as error:
        print(f"❌ Error fetching emails: {error}")

if __name__ == "__main__":
    fetch_emails()
