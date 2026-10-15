"""
Neo4j Graph Data Science (GDS) Runner
Runs PageRank, Weakly Connected Components (WCC), and Louvain Community Detection procedures on Neo4j GDS.
Falls back seamlessly to local NetworkX graph analytics when GDS plugin is absent or offline.
"""

from typing import Dict, Any, Optional
import networkx as nx
from src.neo4j.connection import Neo4jConnection
from src.graph_algorithms.fallback_analytics import FallbackGraphAnalytics
from src.utils.logger import get_logger

logger = get_logger("GDSRunner")

class GDSRunner:
    def __init__(self, conn: Neo4jConnection, local_graph: Optional[nx.DiGraph] = None):
        self.conn = conn
        self.local_graph = local_graph or nx.DiGraph()

    def run_gds_pipeline(self) -> Dict[str, Dict[str, Any]]:
        """Executes PageRank, WCC, and Louvain algorithms."""
        if self.conn.is_connected:
            try:
                logger.info("Executing Neo4j GDS algorithms via Cypher...")
                # Project graph
                self.conn.execute_query("CALL gds.graph.drop('fingraph-projection', false)")
                self.conn.execute_query("""
                CALL gds.graph.project(
                  'fingraph-projection',
                  'Account',
                  { TRANSFERRED_TO: { type: 'TRANSFERRED_TO', orientation: 'NATURAL' } }
                )
                """)

                # PageRank
                self.conn.execute_query("""
                CALL gds.pageRank.write('fingraph-projection', { writeProperty: 'pagerank' })
                """)

                # WCC
                self.conn.execute_query("""
                CALL gds.wcc.write('fingraph-projection', { writeProperty: 'componentId' })
                """)

                # Louvain
                self.conn.execute_query("""
                CALL gds.louvain.write('fingraph-projection', { writeProperty: 'communityId' })
                """)

                # Retrieve results
                results_cypher = """
                MATCH (a:Account)
                RETURN a.account_id AS account_id,
                       coalesce(a.pagerank, 0.0) AS pagerank,
                       coalesce(a.componentId, 0) AS wcc_component_id,
                       coalesce(a.communityId, 0) AS louvain_community_id
                """
                records = self.conn.execute_query(results_cypher)
                return {r["account_id"]: r for r in records}
            except Exception as e:
                logger.warning(f"Neo4j GDS procedure execution notice ({e}). Running local graph analytics fallback.")
        
        # Fallback local networkx analytics
        fallback = FallbackGraphAnalytics(self.local_graph)
        return fallback.run_all_algorithms()
