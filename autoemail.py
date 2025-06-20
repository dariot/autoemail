import csv
import os
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

email_user = config['EMAIL']['username']
email_password = config['EMAIL']['password']
from_address = config['EMAIL']['from_address']
smtp_server = config['SMTP']['server']
smtp_port = int(config['SMTP']['port'])

email_subject = config['EMAIL']['subject']
attachment_folder = config['EMAIL']['attachment_folder']

# ──────────────────────────────────────────────────────────────────────────────
# Open a log file for append. Every time we print to stdout, we also write it here.
# ──────────────────────────────────────────────────────────────────────────────
log_path = 'email_sender.log'
log_file = open(log_path, 'a', encoding='utf-8')  # keep open until the end

def log_print(message):
    """
    Print to stdout and also append the same message (with newline) to log_file.
    """
    print(message)
    log_file.write(message + "\n")
    log_file.flush()  # ensure it appears immediately

# Reading the preconfigured email content
with open('email_message.html', 'r') as file:
    email_body = file.read()

# Function to send email
def send_email(to_email, name, subject, body, cc=None, bcc=None):
    msg = MIMEMultipart('alternative')
    msg['From'] = from_address
    msg['To'] = to_email
    msg['Subject'] = subject
    if cc:
        msg['Cc'] = cc
    if bcc:
        msg['Bcc'] = bcc

    body = body.replace("{name}", name)  # Replace placeholder with actual name
    msg.attach(MIMEText(body, 'html'))

    # Attach files from the specified folder
    if os.path.exists(attachment_folder) and os.path.isdir(attachment_folder):
        for filename in os.listdir(attachment_folder):
            filepath = os.path.join(attachment_folder, filename)
            if os.path.isfile(filepath):
                part = MIMEBase('application', 'octet-stream')
                with open(filepath, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_user, email_password)
    text = msg.as_string()
    recipients = [to_email] + ([cc] if cc else []) + ([bcc] if bcc else [])
    server.sendmail(from_address, recipients, text)
    server.quit()

# Reading CSV and sending emails
log_print("Begin sending emails...")
with open('contacts.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # Skip header row
    line_count = sum(1 for row in reader)

    csvfile.seek(0)
    next(reader, None)  # Skip header row again
    current_row_index = 1
    for row in reader:
        name, email, cc, bcc = row[0], row[1], row[2], row[3]

        try:
            log_print(f"[{current_row_index}/{line_count}] Sending email to {email}...")
            send_email(email, name, email_subject, email_body, cc, bcc)
        except Exception as e:
            log_print(f"Failed to send email to {email}: {e}")

        current_row_index += 1

log_print("Finished sending emails")
