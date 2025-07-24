import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ollama
import time
from dotenv import load_dotenv
import os

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = os.getenv("IMAP_PORT")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

SENDER_EMAIL = os.getenv("EMAIL_ACCOUNT")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
FORWARD_TO_EMAIL = os.getenv("DEFAULT_DEPARTMENT_EMAIL")

EMAILS = {
    "Academic": "academic@domain.com",
    "Hostel": "hostel@domain.com",
    "Examination": "exam@domain.com",
    "DSW": "dsw@domain.com",
    "Other": FORWARD_TO_EMAIL,
}

MODEL = os.getenv("OLLAMA_MODEL")


def fetch_latest_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(SENDER_EMAIL, SENDER_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        print("Failed to retrieve emails.")
        return None

    email_ids = messages[0].split()
    if not email_ids:
        return None

    email_id = email_ids[0]
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        print("Failed to fetch the email.")
        return None

    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    mail.logout()
    return msg


def forward_email(msg, to_email):
    forward_msg = MIMEMultipart()
    forward_msg["From"] = SENDER_EMAIL
    forward_msg["To"] = to_email
    forward_msg["Subject"] = "Fwd: " + msg["Subject"]

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    payload = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                    forward_msg.attach(MIMEText(payload, "plain" if content_type == "text/plain" else "html"))
                except Exception as e:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')
            forward_msg.attach(MIMEText(payload, "plain"))
        except Exception:
            pass

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, forward_msg.as_string())


def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return ""


def classify_email(body: str) -> str:
    prompt = f"""You are an email classifier for a university system.

        Classify the following email into one of the following departments:
        - Academic
        - Hostel
        - Examination
        - DSW
        - Other
        
        Email content:
        \"\"\"
        {body}
        \"\"\"
        
        Respond with ONLY the department name."""

    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    department = response['message']['content'].strip().capitalize()
    if department not in EMAILS:
        department = "Other"
    return department


if __name__ == "__main__":
    while True:
        latest_email = fetch_latest_email()
        if latest_email:
            body = extract_body(latest_email)
            department = classify_email(body)
            to_email = EMAILS[department]
            forward_email(latest_email, to_email)
            print(f"Email forwarded to {department} department at {to_email}")
        else:
            print("No new emails. Waiting 60 seconds...")
            time.sleep(60)
