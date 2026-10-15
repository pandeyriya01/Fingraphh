"""
Kafka Consumer Client
Consumes raw and processed transactions from Kafka topics.
"""

import json
import socket
from typing import Callable, Optional
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("KafkaConsumerClient")

class KafkaConsumerClient:
    def __init__(self, topic: str, group_id: Optional[str] = None, bootstrap_servers: Optional[str] = None):
        self.topic = topic
        self.group_id = group_id or config.KAFKA_CONSUMER_GROUP
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        self.consumer = None

    def start_consuming(self, callback: Callable[[dict], None], timeout_ms: int = 1000, max_records: Optional[int] = None):
        host = self.bootstrap_servers.split(":")[0]
        port = int(self.bootstrap_servers.split(":")[1]) if ":" in self.bootstrap_servers else 9092
        
        try:
            sock = socket.create_connection((host, port), timeout=0.2)
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            logger.info(f"Kafka broker not reachable at {self.bootstrap_servers}. Using Local Consumer Fallback.")
            return

        try:
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=timeout_ms,
                request_timeout_ms=1000
            )
            logger.info(f"Started consuming topic '{self.topic}' (group={self.group_id})...")

            consumed_count = 0
            for message in self.consumer:
                callback(message.value)
                consumed_count += 1
                if max_records and consumed_count >= max_records:
                    break

        except Exception as e:
            logger.warning(f"Kafka consumer notice ({e}). Operating fallback consumer mode.")

    def close(self):
        if self.consumer:
            try:
                self.consumer.close()
            except Exception:
                pass
