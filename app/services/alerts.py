import os
import smtplib
import httpx
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        
        # Queue length threshold for alerts
        self.queue_threshold = int(os.getenv("QUEUE_THRESHOLD", "100"))
        
    async def send_email_alert(self, subject: str, message: str, to_email: Optional[str] = None) -> bool:
        """Send email alert via SMTP"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_pass]):
            logger.warning("SMTP configuration incomplete, skipping email alert")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email or self.admin_email
            msg['Subject'] = f"[Queue System] {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                
            logger.info(f"Email alert sent to {msg['To']}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    async def send_webhook_alert(self, title: str, message: str, level: str = "info") -> bool:
        """Send webhook alert to Slack/Teams"""
        if not self.webhook_url:
            logger.warning("Webhook URL not configured, skipping webhook alert")
            return False
            
        try:
            # Slack format
            payload = {
                "text": f"*{title}*\n{message}",
                "color": self._get_color_for_level(level)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
            logger.info(f"Webhook alert sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def _get_color_for_level(self, level: str) -> str:
        """Get color for alert level"""
        colors = {
            "info": "#2196F3",
            "warning": "#ff9800",
            "error": "#f44336",
            "success": "#4CAF50"
        }
        return colors.get(level, colors["info"])
    
    async def alert_queue_length(self, queue_id: str, queue_name: str, current_length: int) -> None:
        """Alert when queue length exceeds threshold"""
        if current_length >= self.queue_threshold:
            subject = f"Queue Length Alert: {queue_name}"
            message = f"""
Queue '{queue_name}' (ID: {queue_id}) has exceeded the threshold.
Current length: {current_length}
Threshold: {self.queue_threshold}

Please review the queue configuration and consider increasing the release rate.
            """.strip()
            
            await self.send_email_alert(subject, message)
            await self.send_webhook_alert(
                "Queue Length Alert",
                f"Queue '{queue_name}' has {current_length} users waiting (threshold: {self.queue_threshold})",
                "warning"
            )
    
    async def alert_callback_failure(self, app_id: str, queue_id: str, user_id: str, error_details: str) -> None:
        """Alert on callback failure after retries"""
        subject = "Callback Failure Alert"
        message = f"""
A callback has failed after multiple retry attempts.

Application ID: {app_id}
Queue ID: {queue_id}
User ID: {user_id}
Error Details: {error_details}

Please check the application's callback URL and ensure it's responding correctly.
            """.strip()
            
        await self.send_email_alert(subject, message)
        await self.send_webhook_alert(
            "Callback Failure Alert",
            f"Callback failed for app {app_id}, queue {queue_id}, user {user_id}",
            "error"
        )
    
    async def alert_system_health(self, status: str, details: str) -> None:
        """Alert on system health issues"""
        subject = f"System Health Alert: {status}"
        message = f"""
System health check failed.

Status: {status}
Details: {details}

Please investigate the system immediately.
            """.strip()
            
        await self.send_email_alert(subject, message)
        await self.send_webhook_alert(
            "System Health Alert",
            f"System health check failed: {status} - {details}",
            "error"
        )

# Global alert service instance
alert_service = AlertService() 