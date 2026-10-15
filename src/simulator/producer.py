"""
FinGraph Transaction Producer
Streams generated financial transactions to Kafka topics or local file/stream sinks.
"""

import json
import time
from typing import Optional, List, Dict, Any
from src.utils.config import config
from src.utils.logger import get_logger
from src.simulator.generator import TransactionGenerator

logger = get_logger("TransactionProducer")

class FinGraphProducer:
    def __init__(self, bootstrap_servers: Optional[str] = None, topic: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        self.topic = topic or config.KAFKA_TOPIC_RAW_TRANSACTIONS
        self.kafka_producer = None
        self._init_kafka()

    def _init_kafka(self):
        try:
            from kafka import KafkaProducer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                request_timeout_ms=5000,
                max_block_ms=5000
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Could not connect to Kafka broker ({e}). Operating in Local Stream Mode.")
            self.kafka_producer = None

    def send_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Send single transaction event."""
        key = transaction.get("sender_account", "")
        if self.kafka_producer:
            try:
                future = self.kafka_producer.send(self.topic, key=key, value=transaction)
                future.get(timeout=5)
                logger.debug(f"Published to Kafka [{self.topic}]: {transaction['transaction_id']}")
                return True
            except Exception as e:
                logger.error(f"Kafka send failed: {e}")
                return False
        else:
            logger.info(f"[LOCAL STREAM SINK] Txn ID: {transaction['transaction_id']} | "
                        f"{transaction['sender_account']} -> {transaction['receiver_account']} | "
                        f"Amount: ${transaction['amount']} | Pattern: {transaction['pattern_type']}")
            return True

    def stream_continuous(self, interval_sec: float = 0.5, batch_size: int = 10, duration_sec: Optional[float] = None):
        """Continuously stream transactions."""
        generator = TransactionGenerator()
        logger.info(f"Starting continuous transaction streaming (interval={interval_sec}s)...")
        start_time = time.time()
        count = 0

        try:
            while True:
                batch = generator.generate_batch(count=batch_size, fraud_ratio=0.3)
                for txn in batch:
                    self.send_transaction(txn)
                    count += 1
                
                time.sleep(interval_sec)
                if duration_sec and (time.time() - start_time) >= duration_sec:
                    logger.info(f"Completed streaming test duration ({duration_sec}s). Total sent: {count}")
                    break
        except KeyboardInterrupt:
            logger.info("Streaming stopped by user.")
        finally:
            if self.kafka_producer:
                self.kafka_producer.flush()
                self.kafka_producer.close()

if __name__ == "__main__":
    producer = FinGraphProducer()
    producer.stream_continuous(interval_sec=0.2, batch_size=5, duration_sec=5.0)
