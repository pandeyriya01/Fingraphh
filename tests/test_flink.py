"""
Unit Tests for Flink Stream Processor
"""

import pytest
from src.flink.processing_utils import TransactionStreamProcessor
from src.flink.streaming_job import FlinkJobRunner

def test_flink_clean_transaction():
    processor = TransactionStreamProcessor(high_value_threshold=10000.0)
    raw = {"sender_account": " acc_001 ", "receiver_account": "acc_002", "amount": 15000.0}
    cleaned = processor.clean_transaction(raw)
    assert cleaned["sender_account"] == "ACC_001"
    assert cleaned["is_high_value"] is True

def test_flink_velocity_tracking():
    processor = TransactionStreamProcessor()
    for _ in range(6):
        res = processor.process_record({"sender_account": "ACC_RAPID", "receiver_account": "ACC_TARGET", "amount": 5000.0})
    assert res["velocity_count_20"] == 6
    assert res["velocity_total_vol_20"] == 30000.0
    assert res["is_velocity_suspicious"] is True

def test_flink_job_runner():
    runner = FlinkJobRunner()
    batch = runner.process_stream_batch([{"sender_account": "A", "receiver_account": "B", "amount": 50.0}])
    assert len(batch) == 1
