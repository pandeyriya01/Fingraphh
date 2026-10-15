"""
Explainable Risk Scoring Engine
Combines graph algorithms (PageRank, WCC, Louvain) and Cypher fraud patterns to calculate
a transparent, explainable 0-100 risk score with detailed reason codes.
"""

from typing import Dict, Any, List, Optional
from src.risk_scoring.classifier import classify_risk_score, RiskLevel
from src.utils.logger import get_logger

logger = get_logger("RiskScoringEngine")

class RiskScoringEngine:
    def __init__(self, high_risk_threshold: float = 70.0):
        self.high_risk_threshold = high_risk_threshold

    def calculate_account_risk(
        self,
        account_id: str,
        gds_metrics: Dict[str, Any],
        fraud_patterns: List[Dict[str, Any]],
        velocity_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculates transparent composite risk score with reason codes."""
        velocity_metrics = velocity_metrics or {}
        reasons: List[str] = []
        score = 0.0

        # 1. PageRank Centrality Weight (0 - 30 points)
        pagerank = float(gds_metrics.get("pagerank", 0.0))
        if pagerank > 0.02:
            pr_pts = min(30.0, pagerank * 300.0)
            score += pr_pts
            reasons.append(f"HIGH_PAGERANK_CENTRALITY (PageRank={pagerank:.4f})")

        # 2. Circular Money Flow Participation (35 points)
        in_cycle = any(
            p.get("pattern") == "CIRCULAR_FLOW" and account_id in p.get("cycle_nodes", [p.get("origin_account")])
            for p in fraud_patterns
        )
        if in_cycle:
            score += 35.0
            reasons.append("PARTICIPATED_IN_CIRCULAR_MONEY_FLOW")

        # 3. Starburst Fan-in Hub (35 points)
        is_starburst_hub = any(
            p.get("pattern") == "STARBURST_HUB" and p.get("hub_account") == account_id
            for p in fraud_patterns
        )
        if is_starburst_hub:
            score += 35.0
            reasons.append("STARBURST_DESTINATION_SHELL_HUB")

        # 4. Multi-hop Layering Involvement (20 points)
        in_layering = any(
            p.get("pattern") == "MULTIHOP_LAYERING" and account_id in p.get("layering_path", [])
            for p in fraud_patterns
        )
        if in_layering:
            score += 20.0
            reasons.append("MULTIHOP_LAYERING_PATH_MEMBER")

        # 5. Rapid Velocity / Structuring (15 points)
        if velocity_metrics.get("is_velocity_suspicious", False):
            score += 15.0
            reasons.append("RAPID_HIGH_VOLUME_TRANSACTION_BURST")

        # Bound score between 0.0 and 100.0
        final_score = round(min(100.0, score), 2)
        risk_level = classify_risk_score(final_score)

        return {
            "account_id": account_id,
            "risk_score": final_score,
            "risk_level": risk_level.value,
            "reasons": reasons if reasons else ["NORMAL_TRANSACTION_BEHAVIOR"],
            "wcc_component_id": gds_metrics.get("wcc_component_id", 0),
            "louvain_community_id": gds_metrics.get("louvain_community_id", 0),
            "pagerank": pagerank,
            "is_alert_triggered": final_score >= self.high_risk_threshold
        }

    def score_all_accounts(
        self,
        gds_results: Dict[str, Dict[str, Any]],
        fraud_patterns: List[Dict[str, Any]],
        velocity_map: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Scores all graph accounts."""
        velocity_map = velocity_map or {}
        scored_accounts = []

        all_accounts = set(gds_results.keys()).union(velocity_map.keys())
        for acc in all_accounts:
            gds = gds_results.get(acc, {})
            vel = velocity_map.get(acc, {})
            res = self.calculate_account_risk(acc, gds, fraud_patterns, vel)
            scored_accounts.append(res)

        # Sort by risk score descending
        scored_accounts.sort(key=lambda x: x["risk_score"], reverse=True)
        return scored_accounts
