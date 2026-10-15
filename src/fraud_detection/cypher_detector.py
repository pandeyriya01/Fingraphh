"""
Cypher Fraud Detector Module
Runs Cypher queries against Neo4j or executes equivalent graph pattern matching algorithms on NetworkX graph.
"""

from typing import List, Dict, Any, Optional
import networkx as nx
from src.neo4j.connection import Neo4jConnection
from src.utils.logger import get_logger

logger = get_logger("CypherFraudDetector")

class CypherFraudDetector:
    def __init__(self, conn: Neo4jConnection, local_graph: Optional[nx.DiGraph] = None):
        self.conn = conn
        self.local_graph = local_graph or nx.DiGraph()

    def set_local_graph(self, graph: nx.DiGraph):
        self.local_graph = graph

    def detect_circular_flows(self) -> List[Dict[str, Any]]:
        """Detects circular money flows (A -> B -> C -> A)."""
        cypher = """
        MATCH (a:Account)-[r1:TRANSFERRED_TO]->(b:Account)-[r2:TRANSFERRED_TO]->(c:Account)-[r3:TRANSFERRED_TO]->(a)
        WHERE a <> b AND b <> c AND a <> c
        RETURN DISTINCT a.account_id AS origin_account,
               b.account_id AS node_b,
               c.account_id AS node_c,
               (r1.amount + r2.amount + r3.amount) AS cycle_volume,
               "CIRCULAR_FLOW" AS pattern
        """
        if self.conn.is_connected:
            return self.conn.execute_query(cypher)
        else:
            # Fallback NetworkX cycle detection
            results = []
            try:
                cycles = list(nx.simple_cycles(self.local_graph))
                for cycle in cycles:
                    if 3 <= len(cycle) <= 5:
                        total_vol = 0.0
                        for i in range(len(cycle)):
                            u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                            edge_data = self.local_graph.get_edge_data(u, v, default={})
                            total_vol += edge_data.get("amount", 0.0)
                        
                        results.append({
                            "origin_account": cycle[0],
                            "cycle_nodes": cycle,
                            "cycle_volume": round(total_vol, 2),
                            "pattern": "CIRCULAR_FLOW"
                        })
            except Exception as e:
                logger.error(f"Error in local cycle detection: {e}")
            return results

    def detect_starburst_hubs(self, min_in_degree: int = 5) -> List[Dict[str, Any]]:
        """Detects starburst fan-in hubs where many distinct accounts transfer funds to one target."""
        cypher = f"""
        MATCH (sender:Account)-[r:TRANSFERRED_TO]->(hub:Account)
        WITH hub, count(DISTINCT sender) AS in_degree, sum(r.amount) AS total_amount
        WHERE in_degree >= {min_in_degree}
        RETURN hub.account_id AS hub_account,
               in_degree,
               total_amount,
               "STARBURST_HUB" AS pattern
        """
        if self.conn.is_connected:
            return self.conn.execute_query(cypher)
        else:
            # Fallback NetworkX in-degree scan
            results = []
            for node in self.local_graph.nodes():
                in_edges = self.local_graph.in_edges(node, data=True)
                senders = set(u for u, v, _ in in_edges)
                if len(senders) >= min_in_degree:
                    total_vol = sum(d.get("amount", 0.0) for _, _, d in in_edges)
                    results.append({
                        "hub_account": node,
                        "in_degree": len(senders),
                        "total_amount": round(total_vol, 2),
                        "pattern": "STARBURST_HUB"
                    })
            return results

    def detect_multihop_layering(self, min_hops: int = 3) -> List[Dict[str, Any]]:
        """Detects multi-hop layering paths."""
        if self.conn.is_connected:
            cypher = f"""
            MATCH path = (startAcc:Account)-[:TRANSFERRED_TO*{min_hops}..6]->(endAcc:Account)
            WHERE startAcc <> endAcc
            RETURN [n in nodes(path) | n.account_id] AS layering_path,
                   length(path) AS hop_length,
                   "MULTIHOP_LAYERING" AS pattern
            LIMIT 50
            """
            return self.conn.execute_query(cypher)
        else:
            results = []
            try:
                for source in self.local_graph.nodes():
                    for target in self.local_graph.nodes():
                        if source != target and nx.has_path(self.local_graph, source, target):
                            paths = list(nx.all_simple_paths(self.local_graph, source, target, cutoff=5))
                            for p in paths:
                                if len(p) - 1 >= min_hops:
                                    results.append({
                                        "layering_path": p,
                                        "hop_length": len(p) - 1,
                                        "pattern": "MULTIHOP_LAYERING"
                                    })
                                    if len(results) >= 50:
                                        return results
            except Exception as e:
                logger.error(f"Error in local layering detection: {e}")
            return results
