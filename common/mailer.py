"""Sends email to Mailpit, the local test mail catcher. Nothing leaves your computer."""
import smtplib
from email.message import EmailMessage

from common import config


class MailpitMailer:
    def send(self, to, subject, body):
        message = EmailMessage()
        message["From"] = config.SUPPORT_SENDER
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(config.MAILPIT_SMTP_HOST, config.MAILPIT_SMTP_PORT, timeout=10) as smtp:
            smtp.send_message(message)


class RecordingMailer:
    """Stand-in for tests: keeps sent mail in a list instead of sending it."""

    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append({"to": to, "subject": subject, "body": body})
