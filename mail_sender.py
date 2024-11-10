import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()


def send_email(sender_email, sender_password, recipient_email, subject, body, file_path=None):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach the JSON file if a path is provided
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            json_attachment = MIMEApplication(file.read(), _subtype="json")
            json_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(json_attachment)

    try:
        # Connect to the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())

        # Disconnect from the server
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Example usage
if __name__ == "__main__":
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    recipient_email = "barara98@gmail.com"
    subject = "Test Email with JSON Attachment"
    body = "This is a test email sent from Python with a JSON file attachment."
    file_path = "celebrity_db.json"

    send_email(sender_email, sender_password, recipient_email, subject, body, file_path)
