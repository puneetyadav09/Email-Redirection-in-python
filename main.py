import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "YOUR_EMAIL_ID"
SENDER_PASSWORD = "YOUR_EMAIL_PASSWORD"
FORWARD_TO_EMAIL = "DEFAULT_EMAIL_ID_TO_FORWARD"

# Email id list on which we forward
EMAILS = ["ABC@gmail.com", "DEF@gmail.com", "GHI@gmail.com", "JKL@gmail.com"]

academic_keywords = ["fees", "paid", "payment", "invoice", "bill", "billing", "finance", "late fees", "pending", "dues", "scholarship", "receipt", "transaction"]
hostel_keywords = ["hostel", "accommodation", "dormitory", "residence", "room", "allocate", "allocation", "allote", "warden", "mess", "hostel fees", "lodging", "boarding", "room request", "room change", "hostel admission", "accomodation allotment"]
examination_keywords = ["exam", "examination", "assessment", "test", "results", "grades", "marksheet", "hall ticket", "admit card", "re-evaluation", "evaluation", "answer sheet", "exam schedule", "grade sheet", "re-exam", "supplementary exam"]
dsw_keywords = ["welfare", "student welfare", "counseling", "scholarship", "financial aid", "extracurricular", "student support", "mentorship", "student activity", "clubs", "societies", "co-curricular activities", "student grievance"]


def fetch_latest_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(SENDER_EMAIL, SENDER_PASSWORD)
    mail.select("inbox")


    status, messages = mail.search(None, "UNSEEN")

    if status != "OK":
        print("Failed to retrieve emails.")
        return None

    email_id = messages[0].split()

    if len(email_id) == 0:
        return None

    email_bodies = []
    email_ids = []
    email_ids.append(email_id[0])
    for num in email_ids:
        status, msg_data = mail.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject, encoding = decode_header(msg["Subject"])[0]

                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if "attachment" not in content_disposition and content_type == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8")
                            email_bodies.append(body)
                else:
                    body = msg.get_payload(decode=True).decode("utf-8")
                    email_bodies.append(body)

    email_category = get_category(email_bodies)



    global FORWARD_TO_EMAIL
    FORWARD_TO_EMAIL = email_category



    print(email_category)
    print(FORWARD_TO_EMAIL)


    latest_email_id = email_ids[-1]
    status, data = mail.fetch(latest_email_id, "(RFC822)")

    if status != "OK":
        print("Failed to fetch the email.")
        return None

    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)

    mail.logout()
    return msg

def forward_email(msg):
    forward_msg = MIMEMultipart()
    forward_msg["From"] = SENDER_EMAIL
    forward_msg["To"] = FORWARD_TO_EMAIL
    forward_msg["Subject"] = "Fwd: " + msg["Subject"]

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain":
                part_payload = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                forward_msg.attach(MIMEText(part_payload, "plain"))
            elif content_type == "text/html":
                part_payload = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                forward_msg.attach(MIMEText(part_payload, "html"))
    else:
        part_payload = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')
        forward_msg.attach(MIMEText(part_payload, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, FORWARD_TO_EMAIL, forward_msg.as_string())


def get_category(email_bodies):
    hostel = 0
    academic = 0
    exam = 0
    dsw = 0

    for i, email_body in enumerate(email_bodies, 1):
        for j in hostel_keywords:
            hostel = hostel + (email_body.count(j))
        for j in academic_keywords:
            academic = academic + (email_body.count(j))
        for j in examination_keywords:
            exam = exam + (email_body.count(j))
        for j in dsw_keywords:
            dsw = dsw + (email_body.count(j))

    if academic >= hostel and academic >= exam and academic >= dsw and academic!=0:
        type_email = EMAILS[0]
    elif hostel >= academic and hostel >= exam and hostel >= dsw and hostel!=0:
        type_email = EMAILS[1]
    elif exam >= hostel and exam >= academic and exam >= dsw and exam!=0:
        type_email = EMAILS[2]
    elif dsw >= hostel and dsw >= academic and dsw >= exam and dsw!=0:
        type_email = EMAILS[3]
    else:
        type_email = "DEFAULT_EMAIL_ID_TO_FORWARD"

    print(hostel, academic, exam, dsw)

    return type_email



if __name__ == "__main__":
    latest_email = fetch_latest_email()
    while latest_email is not None:
        if latest_email:
            forward_email(latest_email)
            print(f"Email forwarded to {FORWARD_TO_EMAIL}")
        else:
            print("No email to forward.")
            break
        latest_email = fetch_latest_email()
