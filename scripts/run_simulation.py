"""
Transaction Simulation Launcher Script
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.simulator.producer import FinGraphProducer
from src.utils.logger import get_logger

logger = get_logger("SimulationLauncher")

def main():
    logger.info("Launching FinGraph Transaction Simulator...")
    producer = FinGraphProducer()
    producer.stream_continuous(interval_sec=0.3, batch_size=5, duration_sec=10.0)

if __name__ == "__main__":
    main()
