"""
Neo4j Graph Data Loader
Upserts transactions, nodes, and relationships into Neo4j graph database.
Also maintains an in-memory NetworkX graph representation for local graph operations.
"""

from typing import Dict, Any, List
import networkx as nx
from src.neo4j.connection import Neo4jConnection
from src.utils.logger import get_logger

logger = get_logger("Neo4jDataLoader")

class GraphDataLoader:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn
        # Local fallback in-memory graph
        self.local_graph = nx.DiGraph()

    def ingest_transaction(self, txn: Dict[str, Any]) -> bool:
        """Upserts a transaction event as Cypher nodes and relationships into Neo4j."""
        cypher = """
        MERGE (sp:Person {person_id: $sender_person})
        MERGE (rp:Person {person_id: $receiver_person})

        MERGE (sa:Account {account_id: $sender_account})
        MERGE (ra:Account {account_id: $receiver_account})

        MERGE (sb:Bank {bank_code: $sender_bank})
        MERGE (rb:Bank {bank_code: $receiver_bank})

        MERGE (sip:IPAddress {ip_address: $sender_ip})
        MERGE (rip:IPAddress {ip_address: $receiver_ip})

        MERGE (sp)-[:HAS_ACCOUNT]->(sa)
        MERGE (rp)-[:HAS_ACCOUNT]->(ra)

        MERGE (sa)-[:HELD_AT]->(sb)
        MERGE (ra)-[:HELD_AT]->(rb)

        MERGE (sa)-[:CONNECTED_FROM_IP]->(sip)
        MERGE (ra)-[:CONNECTED_FROM_IP]->(rip)

        CREATE (sa)-[r:TRANSFERRED_TO {
            transaction_id: $transaction_id,
            amount: $amount,
            timestamp: $timestamp,
            currency: $currency,
            transaction_type: $transaction_type,
            pattern_type: $pattern_type,
            is_suspicious: $is_suspicious
        }]->(ra)
        """

        # Populate local NetworkX fallback graph
        sa = txn["sender_account"]
        ra = txn["receiver_account"]
        sp = txn.get("sender_person", f"PERS_{sa}")
        rp = txn.get("receiver_person", f"PERS_{ra}")
        sip = txn.get("sender_ip", "127.0.0.1")
        rip = txn.get("receiver_ip", "127.0.0.1")

        self.local_graph.add_node(sa, type="Account", person=sp, ip=sip, risk_score=0.0)
        self.local_graph.add_node(ra, type="Account", person=rp, ip=rip, risk_score=0.0)
        self.local_graph.add_edge(
            sa, ra,
            transaction_id=txn["transaction_id"],
            amount=float(txn["amount"]),
            timestamp=txn["timestamp"],
            pattern_type=txn.get("pattern_type", "NORMAL"),
            is_suspicious=txn.get("is_suspicious", False)
        )

        if self.conn.is_connected:
            res = self.conn.execute_query(cypher, txn)
            return True
        else:
            logger.debug(f"[LOCAL GRAPH LOADED] {sa} -> {ra} (${txn['amount']}) | Nodes: {self.local_graph.number_of_nodes()}")
            return True

    def ingest_batch(self, transactions: List[Dict[str, Any]]) -> int:
        """Batch ingests list of transactions."""
        success_count = 0
        for txn in transactions:
            if self.ingest_transaction(txn):
                success_count += 1
        logger.info(f"Ingested batch of {success_count}/{len(transactions)} transactions into graph model.")
        return success_count
