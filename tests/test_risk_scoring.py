"""
Unit Tests for Explainable Risk Scoring Engine
"""

import pytest
from src.risk_scoring.classifier import classify_risk_score, RiskLevel
from src.risk_scoring.engine import RiskScoringEngine

def test_classify_risk_score():
    assert classify_risk_score(85.0) == RiskLevel.HIGH
    assert classify_risk_score(45.0) == RiskLevel.MEDIUM
    assert classify_risk_score(15.0) == RiskLevel.LOW

def test_calculate_account_risk_high():
    engine = RiskScoringEngine(high_risk_threshold=70.0)
    gds = {"pagerank": 0.15, "wcc_component_id": 1, "louvain_community_id": 1}
    patterns = [
        {"pattern": "CIRCULAR_FLOW", "cycle_nodes": ["ACC_HUB"]},
        {"pattern": "STARBURST_HUB", "hub_account": "ACC_HUB"}
    ]
    res = engine.calculate_account_risk("ACC_HUB", gds, patterns)
    assert res["risk_score"] >= 70.0
    assert res["risk_level"] == "HIGH RISK"
    assert res["is_alert_triggered"] is True
    assert len(res["reasons"]) >= 2
