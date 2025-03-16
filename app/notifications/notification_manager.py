import logging
from typing import Optional, Dict, List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.db.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._initialize_email_settings()

    def _initialize_email_settings(self):
        """Initialize email notification settings"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.example.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')

    def send_email(self, to_email: str, subject: str, body: str, html: Optional[str] = None):
        """Send an email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Attach both plain text and HTML versions
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)
            
            if html:
                part2 = MIMEText(html, 'html')
                msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def log_notification(self, user_id: int, message: str, channel: str = 'email'):
        """Log a notification in the database"""
        try:
            self.db_manager.pg_cursor.execute("""
                INSERT INTO notifications (user_id, message, created_at)
                VALUES (%s, %s, %s)
            """, (user_id, message, datetime.now(datetime.timezone.utc)))
            self.db_manager.pg_conn.commit()
            logger.debug(f"Notification logged for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
            raise
