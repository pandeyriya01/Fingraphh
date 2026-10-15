"""
Unit Tests for Transaction Simulator
"""

import pytest
from src.simulator.generator import TransactionGenerator

def test_generate_normal_transaction():
    gen = TransactionGenerator(seed=42)
    txn = gen.generate_normal_transaction()
    assert txn["transaction_id"].startswith("TXN_")
    assert txn["amount"] > 0
    assert txn["pattern_type"] == "NORMAL"
    assert txn["is_suspicious"] is False

def test_generate_smurfing_pattern():
    gen = TransactionGenerator(seed=42)
    txns = gen.generate_smurfing_pattern("ACC_SHELL_9999", num_mules=5)
    assert len(txns) == 5
    for t in txns:
        assert t["receiver_account"] == "ACC_SHELL_9999"
        assert 9000.0 <= t["amount"] <= 10000.0
        assert t["pattern_type"] == "SMURFING"
        assert t["is_suspicious"] is True

def test_generate_circular_flow():
    gen = TransactionGenerator(seed=42)
    txns = gen.generate_circular_flow(["A", "B", "C", "A"], amount=25000.0)
    assert len(txns) == 3
    assert txns[0]["sender_account"] == "A"
    assert txns[0]["receiver_account"] == "B"
    assert txns[2]["receiver_account"] == "A"

def test_generate_batch():
    gen = TransactionGenerator(seed=42)
    batch = gen.generate_batch(count=30, fraud_ratio=0.3)
    assert len(batch) >= 30
    fraud_txns = [t for t in batch if t["is_suspicious"]]
    assert len(fraud_txns) > 0
