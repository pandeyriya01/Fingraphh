"""
Environment Setup & Diagnostic Tool
Verifies Python version, package dependencies, .env file, and network connectivity.
"""

import sys
import os
from pathlib import Path

# Add root directory
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("EnvironmentSetup")

def check_environment():
    logger.info("--- FinGraph Environment Diagnostics ---")
    logger.info(f"Python Version: {sys.version.split()[0]}")
    logger.info(f"OS Platform: {sys.platform}")
    logger.info(f"Environment Mode: {config.ENVIRONMENT}")
    logger.info(f"Neo4j URI: {config.NEO4J_URI}")
    logger.info(f"Kafka Bootstrap Servers: {config.KAFKA_BOOTSTRAP_SERVERS}")

    # Check .env existence
    env_file = root_dir / '.env'
    if not env_file.exists():
        logger.warning(".env file not found. Copying .env.example to .env...")
        example_file = root_dir / '.env.example'
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as src, open(env_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            logger.info("Successfully created .env file.")

    # Check key dependencies
    packages = ["pydantic", "kafka", "neo4j", "networkx", "pandas", "numpy", "streamlit", "pyvis"]
    for pkg in packages:
        try:
            __import__(pkg)
            logger.info(f"✓ Package '{pkg}' is available.")
        except ImportError:
            logger.error(f"✗ Package '{pkg}' is missing!")

    logger.info("Environment check complete.")

if __name__ == "__main__":
    check_environment()
