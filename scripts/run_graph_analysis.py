"""
Graph Analysis & GDS Engine Launcher Script
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.neo4j.connection import Neo4jConnection
from src.neo4j.loader import GraphDataLoader
from src.fraud_detection.cypher_detector import CypherFraudDetector
from src.graph_algorithms.gds_runner import GDSRunner
from src.risk_scoring.engine import RiskScoringEngine
from src.simulator.generator import TransactionGenerator
from src.utils.logger import get_logger

logger = get_logger("GraphAnalysisLauncher")

def run_analysis():
    logger.info("Starting Graph Data Analytics Execution...")
    gen = TransactionGenerator()
    batch = gen.generate_batch(count=50, fraud_ratio=0.4)

    conn = Neo4jConnection()
    loader = GraphDataLoader(conn)
    loader.ingest_batch(batch)

    detector = CypherFraudDetector(conn, loader.local_graph)
    circular = detector.detect_circular_flows()
    starbursts = detector.detect_starburst_hubs()

    gds = GDSRunner(conn, loader.local_graph)
    gds_res = gds.run_gds_pipeline()

    engine = RiskScoringEngine()
    scored = engine.score_all_accounts(gds_res, circular + starbursts)

    logger.info(f"Analysis Complete. Scored {len(scored)} accounts.")
    logger.info(f"Top High Risk Account: {scored[0] if scored else 'None'}")
    conn.close()

if __name__ == "__main__":
    run_analysis()
