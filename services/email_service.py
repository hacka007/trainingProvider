import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from utils.config import settings

logger = logging.getLogger(__name__)


async def send_email_async(email: str, subject: str, message: str):
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, send_email_sync, email, subject, message)
    except Exception as e:
        logger.error(f"[Email] Failed to send email to {email}: {e}")


def send_email_sync(email: str, subject: str, message: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_USERNAME
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"[Email] Email sent to {email}")
    except Exception as e:
        logger.exception(f"[Email] Exception while sending email to {email}: {e}")
