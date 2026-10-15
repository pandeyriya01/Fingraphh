"""
Standalone Fallback Graph Data Science Analytics Engine
Provides PageRank, Weakly Connected Components (WCC), and Louvain / Community Detection on NetworkX graphs.
"""

from typing import Dict, Any, List
import networkx as nx
from src.utils.logger import get_logger

logger = get_logger("FallbackGraphAnalytics")

class FallbackGraphAnalytics:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def run_pagerank(self, alpha: float = 0.85, max_iter: int = 100) -> Dict[str, float]:
        """Calculates PageRank centrality scores using NetworkX or pure power iteration."""
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {}
        try:
            scores = nx.pagerank(self.graph, alpha=alpha, max_iter=max_iter)
            return {node: round(score, 6) for node, score in scores.items()}
        except Exception:
            # Custom power iteration fallback if scipy/numpy solver is unavailable
            nodes = list(self.graph.nodes())
            N = len(nodes)
            if N == 0:
                return {}
            ranks = {node: 1.0 / N for node in nodes}
            for _ in range(max_iter):
                new_ranks = {}
                for node in nodes:
                    rank_sum = 0.0
                    for predecessor in self.graph.predecessors(node):
                        out_degree = self.graph.out_degree(predecessor)
                        if out_degree > 0:
                            rank_sum += ranks[predecessor] / out_degree
                    new_ranks[node] = (1.0 - alpha) / N + alpha * rank_sum
                ranks = new_ranks
            return {node: round(score, 6) for node, score in ranks.items()}

    def run_wcc(self) -> Dict[str, int]:
        """Calculates Weakly Connected Component IDs."""
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {}
        try:
            undirected_graph = self.graph.to_undirected()
            components = list(nx.connected_components(undirected_graph))
            wcc_map = {}
            for comp_id, comp_nodes in enumerate(components):
                for node in comp_nodes:
                    wcc_map[node] = comp_id
            return wcc_map
        except Exception as e:
            logger.error(f"Error computing WCC: {e}")
            return {node: 0 for node in self.graph.nodes()}

    def run_louvain(self) -> Dict[str, int]:
        """Calculates Louvain / Community Detection IDs."""
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {}
        try:
            undirected = self.graph.to_undirected()
            communities = list(nx.community.greedy_modularity_communities(undirected))
            community_map = {}
            for comm_id, comm_nodes in enumerate(communities):
                for node in comm_nodes:
                    community_map[node] = comm_id
            return community_map
        except Exception:
            return self.run_wcc()

    def run_all_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """Runs PageRank, WCC, and Louvain community detection on graph."""
        pr = self.run_pagerank()
        wcc = self.run_wcc()
        louvain = self.run_louvain()

        results = {}
        for node in self.graph.nodes():
            results[node] = {
                "account_id": node,
                "pagerank": pr.get(node, 0.0),
                "wcc_component_id": wcc.get(node, 0),
                "louvain_community_id": louvain.get(node, 0)
            }
        return results
