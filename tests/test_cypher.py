"""
Unit Tests for Cypher Fraud Detector
"""

import pytest
import networkx as nx
from src.neo4j.connection import Neo4jConnection
from src.fraud_detection.cypher_detector import CypherFraudDetector

def test_detect_circular_flows():
    g = nx.DiGraph()
    g.add_edge("A", "B", amount=10000.0)
    g.add_edge("B", "C", amount=10000.0)
    g.add_edge("C", "A", amount=10000.0)

    conn = Neo4jConnection()
    detector = CypherFraudDetector(conn, local_graph=g)
    cycles = detector.detect_circular_flows()
    assert len(cycles) >= 1
    assert "A" in cycles[0]["cycle_nodes"]
    conn.close()

def test_detect_starburst_hubs():
    g = nx.DiGraph()
    for i in range(7):
        g.add_edge(f"SPOKE_{i}", "HUB_ACC", amount=2000.0)

    conn = Neo4jConnection()
    detector = CypherFraudDetector(conn, local_graph=g)
    hubs = detector.detect_starburst_hubs(min_in_degree=5)
    assert len(hubs) == 1
    assert hubs[0]["hub_account"] == "HUB_ACC"
    assert hubs[0]["in_degree"] == 7
    conn.close()

def test_detect_multihop_layering():
    g = nx.DiGraph()
    chain = ["A", "B", "C", "D", "E"]
    for i in range(len(chain) - 1):
        g.add_edge(chain[i], chain[i + 1], amount=5000.0)

    conn = Neo4jConnection()
    detector = CypherFraudDetector(conn, local_graph=g)
    layering = detector.detect_multihop_layering(min_hops=3)
    assert len(layering) >= 1
    conn.close()
