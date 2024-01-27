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
smtp_server = config['SMTP']['server']
smtp_port = int(config['SMTP']['port'])

email_subject = config['EMAIL']['subject']
attachment_folder = config['EMAIL']['attachment_folder']

# Reading the preconfigured email content
with open('email_message.txt', 'r') as file:
    email_body = file.read()

# Function to send email
def send_email(to_email, name, subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = subject

    body = body.replace("{name}", name)  # Replace placeholder with actual name
    msg.attach(MIMEText(body, 'plain'))

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
    server.sendmail(email_user, to_email, text)
    server.quit()

# Reading CSV and sending emails
with open('contacts.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # Skip header row
    for row in reader:
        name, email = row[0], row[1]
        send_email(email, name, email_subject, email_body)

print("Emails sent successfully.")
