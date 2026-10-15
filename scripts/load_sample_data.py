"""
Sample Data Generator & Storage Script
Generates a representative sample transaction dataset and saves it to data/sample/transactions_sample.json.
"""

import json
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.simulator.generator import TransactionGenerator
from src.utils.logger import get_logger

logger = get_logger("SampleDataLoader")

def generate_sample_file(count: int = 150, output_path: Path = None):
    output_path = output_path or (root_dir / "data" / "sample" / "transactions_sample.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    gen = TransactionGenerator(seed=123)
    batch = gen.generate_batch(count=count, fraud_ratio=0.35)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2)

    logger.info(f"Saved {len(batch)} sample transactions to {output_path}")

if __name__ == "__main__":
    generate_sample_file()
