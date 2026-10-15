"""
Unit Tests for Neo4j Database Connection & Loader
"""

import pytest
from src.neo4j.connection import Neo4jConnection
from src.neo4j.loader import GraphDataLoader

def test_neo4j_connection_fallback():
    conn = Neo4jConnection()
    # Should safely initialize without throwing exception regardless of Neo4j server status
    assert hasattr(conn, "is_connected")
    conn.close()

def test_graph_data_loader():
    conn = Neo4jConnection()
    loader = GraphDataLoader(conn)
    txn = {
        "transaction_id": "TXN_TEST_001",
        "sender_account": "ACC_SENDER",
        "receiver_account": "ACC_RECEIVER",
        "amount": 9900.0,
        "timestamp": "2026-08-20T00:00:00Z",
        "currency": "USD",
        "transaction_type": "WIRE",
        "pattern_type": "SMURFING",
        "is_suspicious": True
    }
    success = loader.ingest_transaction(txn)
    assert success is True
    assert loader.local_graph.number_of_nodes() == 2
    assert loader.local_graph.number_of_edges() == 1
    conn.close()
