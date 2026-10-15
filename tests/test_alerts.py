"""
Unit Tests for Fraud Alert System
"""

import pytest
from src.alerts.alert_manager import AlertManager
from src.alerts.channels import NotificationChannels

def test_notification_channels():
    channels = NotificationChannels()
    payload = {"account_id": "ACC_TEST", "risk_score": 90.0, "risk_level": "HIGH RISK", "reasons": ["CIRCULAR_FLOW"]}
    assert channels.send_slack_alert(payload) is True
    assert channels.send_email_alert(payload) is True

def test_alert_manager_threshold():
    mgr = AlertManager(alert_threshold=70.0)
    scored = [
        {"account_id": "ACC_HIGH", "risk_score": 85.0, "risk_level": "HIGH RISK", "reasons": ["STARBURST"]},
        {"account_id": "ACC_LOW", "risk_score": 20.0, "risk_level": "LOW RISK", "reasons": []}
    ]
    alerts = mgr.evaluate_high_risk_accounts(scored)
    assert len(alerts) == 1
    assert alerts[0]["account_id"] == "ACC_HIGH"
