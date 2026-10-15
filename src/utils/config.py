"""
FinGraph Centralized Configuration Loader
Loads settings from environment variables or default fallbacks.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from root if present
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    env_example = Path(__file__).resolve().parent.parent.parent / '.env.example'
    if env_example.exists():
        load_dotenv(dotenv_path=env_example)

class Config:
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "fingraph_secret_password")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_RAW_TRANSACTIONS: str = os.getenv("KAFKA_TOPIC_RAW_TRANSACTIONS", "transactions.raw")
    KAFKA_TOPIC_PROCESSED_TRANSACTIONS: str = os.getenv("KAFKA_TOPIC_PROCESSED_TRANSACTIONS", "transactions.processed")
    KAFKA_TOPIC_FRAUD_ALERTS: str = os.getenv("KAFKA_TOPIC_FRAUD_ALERTS", "alerts.fraud")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "fingraph-analytics-group")

    # Flink
    FLINK_JOBMANAGER_HOST: str = os.getenv("FLINK_JOBMANAGER_HOST", "localhost")
    FLINK_JOBMANAGER_PORT: int = int(os.getenv("FLINK_JOBMANAGER_PORT", "8081"))

    # Alerts
    RISK_SCORE_ALERT_THRESHOLD: float = float(os.getenv("RISK_SCORE_ALERT_THRESHOLD", "75.0"))
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    EMAIL_ALERT_RECIPIENT: str = os.getenv("EMAIL_ALERT_RECIPIENT", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))

    # Dashboard
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_HOST: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")

config = Config()
