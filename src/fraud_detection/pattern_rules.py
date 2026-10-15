"""
Fraud Pattern Rules & Heuristics Evaluator
Evaluates specific transaction structural features against predefined AML compliance rules.
"""

from typing import Dict, Any, List

class FraudPatternRules:
    @staticmethod
    def evaluate_smurfing(in_degree: int, avg_amount: float, total_amount: float) -> float:
        """Scores smurfing / structuring indicator (0.0 to 1.0)."""
        if in_degree >= 5 and 500.0 <= avg_amount <= 9999.0:
            return min(1.0, 0.4 + (in_degree * 0.05))
        return 0.0

    @staticmethod
    def evaluate_circular_flow(has_cycle: bool, cycle_length: int) -> float:
        """Scores circular money flow indicator."""
        if has_cycle:
            return 0.95 if cycle_length == 3 else 0.85
        return 0.0

    @staticmethod
    def evaluate_starburst(fan_in_count: int, fan_out_count: int) -> float:
        """Scores starburst fan-in hub indicator."""
        if fan_in_count >= 10 and fan_out_count <= 2:
            return min(1.0, 0.5 + (fan_in_count * 0.01))
        return 0.0

    @staticmethod
    def evaluate_shared_ip(shared_ip_account_count: int) -> float:
        """Scores shared IP network cluster indicator."""
        if shared_ip_account_count >= 3:
            return min(0.9, 0.3 + (shared_ip_account_count * 0.1))
        return 0.0
