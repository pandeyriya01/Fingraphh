"""
Risk Classifier & Risk Level Enum
Classifies calculated risk scores into LOW, MEDIUM, and HIGH risk categories.
"""

from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW RISK"
    MEDIUM = "MEDIUM RISK"
    HIGH = "HIGH RISK"

def classify_risk_score(score: float) -> RiskLevel:
    """Classifies risk score (0-100) into risk tier."""
    if score >= 71.0:
        return RiskLevel.HIGH
    elif score >= 31.0:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
