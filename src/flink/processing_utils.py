"""
Flink Stream Processing Utilities & Stateful Aggregations
Performs real-time transaction cleaning, normalization, velocity checks, and graph enrichment.
"""

from typing import Dict, Any, List

class TransactionStreamProcessor:
    def __init__(self, high_value_threshold: float = 10000.0):
        self.high_value_threshold = high_value_threshold
        # In-memory sliding window state for local streaming
        self.account_window_history: Dict[str, List[Dict[str, Any]]] = {}

    def clean_transaction(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Cleans and standardizes raw transaction fields."""
        cleaned = dict(record)
        cleaned["amount"] = float(cleaned.get("amount", 0.0))
        cleaned["sender_account"] = str(cleaned.get("sender_account", "")).strip().upper()
        cleaned["receiver_account"] = str(cleaned.get("receiver_account", "")).strip().upper()
        cleaned["sender_person"] = str(cleaned.get("sender_person", "")).strip().upper()
        cleaned["receiver_person"] = str(cleaned.get("receiver_person", "")).strip().upper()
        cleaned["sender_bank"] = str(cleaned.get("sender_bank", "")).strip().upper()
        cleaned["receiver_bank"] = str(cleaned.get("receiver_bank", "")).strip().upper()
        cleaned["is_high_value"] = cleaned["amount"] >= self.high_value_threshold
        return cleaned

    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Stateful processing: tracks velocity & window metrics."""
        cleaned = self.clean_transaction(record)
        sender = cleaned["sender_account"]
        
        if sender not in self.account_window_history:
            self.account_window_history[sender] = []
            
        self.account_window_history[sender].append(cleaned)
        
        # Retain last 20 transactions for velocity metric
        if len(self.account_window_history[sender]) > 20:
            self.account_window_history[sender].pop(0)

        sender_history = self.account_window_history[sender]
        total_recent_vol = sum(t["amount"] for t in sender_history)
        rapid_count = len(sender_history)

        cleaned["velocity_count_20"] = rapid_count
        cleaned["velocity_total_vol_20"] = round(total_recent_vol, 2)
        cleaned["is_velocity_suspicious"] = rapid_count >= 5 and total_recent_vol > 20000.0

        return cleaned
