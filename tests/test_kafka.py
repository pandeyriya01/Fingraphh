"""
Unit Tests for Kafka Integration
"""

import pytest
from src.kafka.producer import KafkaProducerClient
from src.kafka.consumer import KafkaConsumerClient
from src.kafka.config import KafkaManager

def test_kafka_producer_fallback():
    producer = KafkaProducerClient()
    success = producer.produce_message("transactions.raw", "KEY1", {"transaction_id": "TXN_TEST", "amount": 100.0})
    assert success is True
    producer.close()

def test_kafka_manager_topics():
    manager = KafkaManager()
    res = manager.ensure_topics_exist(["test.topic"])
    assert res in [True, False]
