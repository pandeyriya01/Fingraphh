"""
Unit Tests for Graph Data Science Algorithms
"""

import pytest
import networkx as nx
from src.neo4j.connection import Neo4jConnection
from src.graph_algorithms.fallback_analytics import FallbackGraphAnalytics
from src.graph_algorithms.gds_runner import GDSRunner

def test_pagerank_and_components():
    g = nx.DiGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "A")
    g.add_edge("X", "Y")

    fa = FallbackGraphAnalytics(g)
    res = fa.run_all_algorithms()
    assert len(res) == 5
    assert "pagerank" in res["A"]
    assert "wcc_component_id" in res["A"]
    assert "louvain_community_id" in res["A"]
    assert res["A"]["wcc_component_id"] != res["X"]["wcc_component_id"]

def test_gds_runner_pipeline():
    g = nx.DiGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    
    conn = Neo4jConnection()
    runner = GDSRunner(conn, local_graph=g)
    results = runner.run_gds_pipeline()
    assert len(results) >= 2
    conn.close()
