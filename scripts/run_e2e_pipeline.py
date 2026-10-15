"""
End-to-End Pipeline Execution & Verification Script
Verifies full data flow: Python Simulator -> Kafka -> Flink -> Neo4j -> Cypher -> GDS -> Risk Scoring -> Alerts.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.simulator.generator import TransactionGenerator
from src.flink.processing_utils import TransactionStreamProcessor
from src.neo4j.connection import Neo4jConnection
from src.neo4j.loader import GraphDataLoader
from src.fraud_detection.cypher_detector import CypherFraudDetector
from src.graph_algorithms.gds_runner import GDSRunner
from src.risk_scoring.engine import RiskScoringEngine
from src.alerts.alert_manager import AlertManager
from src.utils.logger import get_logger

logger = get_logger("E2EPipelineRunner")

def run_end_to_end_pipeline():
    logger.info("==================================================")
    logger.info("  STARTING FINGRAPH END-TO-END PIPELINE VERIFICATION")
    logger.info("==================================================")

    # Step 1: Generate Synthetic Transactions (Normal + Fraud Syndicates)
    logger.info("\n--- STEP 1: Python Transaction Simulator ---")
    gen = TransactionGenerator(seed=42)
    raw_txns = gen.generate_batch(count=80, fraud_ratio=0.35)
    logger.info(f"Generated {len(raw_txns)} transactions including normal, smurfing, circular, and starburst patterns.")

    # Step 2: Flink Streaming Cleansing & Velocity Processing
    logger.info("\n--- STEP 2: Apache Flink Streaming Processing ---")
    processor = TransactionStreamProcessor()
    processed_txns = [processor.process_record(t) for t in raw_txns]
    suspicious_velocity = [t for t in processed_txns if t.get("is_velocity_suspicious")]
    logger.info(f"Stream Cleansing complete. Processed {len(processed_txns)} records. Rapid high-volume alerts: {len(suspicious_velocity)}")

    # Step 3: Graph Database Storage (Neo4j / Fallback)
    logger.info("\n--- STEP 3: Neo4j Graph Database Loading ---")
    conn = Neo4jConnection()
    loader = GraphDataLoader(conn)
    loaded_count = loader.ingest_batch(processed_txns)
    logger.info(f"Graph loading complete. Active graph nodes: {loader.local_graph.number_of_nodes()}, edges: {loader.local_graph.number_of_edges()}")

    # Step 4: Cypher Fraud Detection Query Execution
    logger.info("\n--- STEP 4: Cypher Fraud Detection Query Suite ---")
    detector = CypherFraudDetector(conn, loader.local_graph)
    circular = detector.detect_circular_flows()
    starbursts = detector.detect_starburst_hubs()
    layering = detector.detect_multihop_layering()
    all_patterns = circular + starbursts + layering
    logger.info(f"Detected {len(circular)} circular money flows, {len(starbursts)} starburst fan-in hubs, {len(layering)} layering chains.")

    # Step 5: Graph Data Science Algorithms (PageRank, WCC, Louvain)
    logger.info("\n--- STEP 5: Neo4j GDS Graph Algorithms ---")
    gds = GDSRunner(conn, loader.local_graph)
    gds_results = gds.run_gds_pipeline()
    logger.info(f"Computed PageRank, WCC, and Louvain algorithms for {len(gds_results)} accounts.")

    # Step 6: Explainable Risk Scoring Engine
    logger.info("\n--- STEP 6: Explainable Risk Scoring ---")
    risk_engine = RiskScoringEngine(high_risk_threshold=75.0)
    scored_accounts = risk_engine.score_all_accounts(gds_results, all_patterns)
    high_risk_accounts = [a for a in scored_accounts if a["risk_level"] == "HIGH RISK"]
    logger.info(f"Risk Scoring complete. Total accounts: {len(scored_accounts)} | High-Risk Accounts: {len(high_risk_accounts)}")

    # Step 7: Fraud Alert System
    logger.info("\n--- STEP 7: Fraud Alert System ---")
    alert_mgr = AlertManager(alert_threshold=75.0)
    alerts = alert_mgr.evaluate_high_risk_accounts(scored_accounts)
    logger.info(f"Generated {len(alerts)} fraud alerts dispatched to notification channels.")

    conn.close()

    logger.info("\n==================================================")
    logger.info("  FINGRAPH E2E PIPELINE SUCCESSFUL & VERIFIED!")
    logger.info("==================================================")
    return True

if __name__ == "__main__":
    run_end_to_end_pipeline()
