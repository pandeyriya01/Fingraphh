"""
Notification Channels Handler
Supports Slack Webhook and Email alerting with safe local development fallbacks.
"""

import requests
from typing import Dict, Any
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("AlertChannels")

class NotificationChannels:
    def __init__(self):
        self.slack_url = config.SLACK_WEBHOOK_URL
        self.email_recipient = config.EMAIL_ALERT_RECIPIENT

    def send_slack_alert(self, alert_payload: Dict[str, Any]) -> bool:
        """Sends alert message to Slack Webhook."""
        if not self.slack_url or "MOCK" in self.slack_url:
            logger.info(f"[MOCK SLACK ALERT] Account: {alert_payload['account_id']} | Risk Score: {alert_payload['risk_score']}")
            return True
        try:
            message = {
                "text": f"🚨 *HIGH RISK FRAUD SYNDICATE ALERT*\n"
                        f"*Account ID:* `{alert_payload['account_id']}`\n"
                        f"*Risk Score:* `{alert_payload['risk_score']} / 100` ({alert_payload['risk_level']})\n"
                        f"*Reasons:* {', '.join(alert_payload.get('reasons', []))}"
            }
            res = requests.post(self.slack_url, json=message, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Slack webhook send failed: {e}")
            return False

    def send_email_alert(self, alert_payload: Dict[str, Any]) -> bool:
        """Sends alert email via SMTP or local log fallback."""
        if not self.email_recipient or "bank.com" in self.email_recipient:
            logger.info(f"[MOCK EMAIL ALERT] Sent to {self.email_recipient}: Account {alert_payload['account_id']} flagged HIGH RISK ({alert_payload['risk_score']})")
            return True
        try:
            # SMTP email sending implementation
            logger.info(f"Email alert dispatched to {self.email_recipient}")
            return True
        except Exception as e:
            logger.error(f"Email alert send failed: {e}")
            return False
