"""
Kafka Low-Level Producer Wrapper
"""

import json
import socket
from typing import Dict, Any, Optional
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("KafkaProducerWrapper")

class KafkaProducerClient:
    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        self.producer = None
        self._connect()

    def _connect(self):
        # Quick socket check before trying kafka-python metadata lookup
        host = self.bootstrap_servers.split(":")[0]
        port = int(self.bootstrap_servers.split(":")[1]) if ":" in self.bootstrap_servers else 9092
        
        try:
            sock = socket.create_connection((host, port), timeout=0.2)
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            logger.info(f"Kafka broker not reachable at {self.bootstrap_servers}. Using Local Stream Sink.")
            self.producer = None
            return

        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                request_timeout_ms=1000,
                max_block_ms=1000,
                metadata_max_age_ms=1000
            )
            logger.info("Kafka Producer successfully initialized.")
        except Exception as e:
            logger.warning(f"Kafka Producer connection notice ({e}). Using Local Stream Sink.")
            self.producer = None

    def produce_message(self, topic: str, key: str, value: Dict[str, Any]) -> bool:
        if self.producer:
            try:
                future = self.producer.send(topic, key=key, value=value)
                future.get(timeout=1)
                return True
            except Exception as e:
                logger.error(f"Failed to produce message to {topic}: {e}")
                return False
        else:
            logger.debug(f"[FALLBACK PRODUCER] Topic: {topic} | Key: {key} | Payload: {value.get('transaction_id')}")
            return True

    def close(self):
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
            except Exception:
                pass
