"""
Fraud Alert Manager
Monitors risk scores and dispatches alerts across registered channels.
"""

from typing import List, Dict, Any
from src.utils.config import config
from src.utils.logger import get_logger
from src.alerts.channels import NotificationChannels

logger = get_logger("AlertManager")

class AlertManager:
    def __init__(self, alert_threshold: float = None):
        self.alert_threshold = alert_threshold or config.RISK_SCORE_ALERT_THRESHOLD
        self.channels = NotificationChannels()
        self.alert_history: List[Dict[str, Any]] = []

    def evaluate_high_risk_accounts(self, scored_accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters high-risk accounts and dispatches alert notifications."""
        triggered_alerts = []
        for acc in scored_accounts:
            score = float(acc.get("risk_score", 0.0))
            if score >= self.alert_threshold:
                alert_item = dict(acc)
                alert_item["alert_id"] = f"ALT_{acc['account_id']}_{int(score)}"
                triggered_alerts.append(alert_item)

                # Dispatch notifications across channels
                self.channels.send_slack_alert(alert_item)
                self.channels.send_email_alert(alert_item)
                logger.warning(f"🚨 FRAUD ALERT TRIGGERED: Account {acc['account_id']} | Risk Score: {score} | Level: {acc['risk_level']}")

        self.alert_history.extend(triggered_alerts)
        return triggered_alerts
