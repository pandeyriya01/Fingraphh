"""
Kafka Configuration & Topic Setup Utility
Manages Kafka topic creation and settings.
"""

import socket
from typing import List
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("KafkaConfig")

class KafkaManager:
    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS

    def ensure_topics_exist(self, topics: List[str] = None):
        if topics is None:
            topics = [
                config.KAFKA_TOPIC_RAW_TRANSACTIONS,
                config.KAFKA_TOPIC_PROCESSED_TRANSACTIONS,
                config.KAFKA_TOPIC_FRAUD_ALERTS
            ]

        host = self.bootstrap_servers.split(":")[0]
        port = int(self.bootstrap_servers.split(":")[1]) if ":" in self.bootstrap_servers else 9092
        
        try:
            sock = socket.create_connection((host, port), timeout=0.2)
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            logger.info(f"Kafka broker not reachable at {self.bootstrap_servers}. Skipping AdminClient topic creation.")
            return False

        try:
            from kafka.admin import KafkaAdminClient, NewTopic
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='fingraph-admin',
                request_timeout_ms=1000
            )

            existing_topics = admin_client.list_topics()
            new_topics = [
                NewTopic(name=t, num_partitions=3, replication_factor=1)
                for t in topics if t not in existing_topics
            ]

            if new_topics:
                admin_client.create_topics(new_topics=new_topics, validate_only=False)
                logger.info(f"Created Kafka topics: {[t.name for t in new_topics]}")
            else:
                logger.info("All Kafka topics already exist.")

            admin_client.close()
            return True
        except Exception as e:
            logger.warning(f"Could not initialize Kafka topics via AdminClient ({e}). Using automatic topic creation if enabled.")
            return False
