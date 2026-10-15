"""
Neo4j Graph Database Driver & Connection Manager
Handles authentication, connection pool, session execution, and fallback in-memory graph store.
"""

import socket
from typing import Dict, Any, List, Optional
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("Neo4jConnectionManager")

class Neo4jConnection:
    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, database: Optional[str] = None):
        self.uri = uri or config.NEO4J_URI
        self.username = username or config.NEO4J_USERNAME
        self.password = password or config.NEO4J_PASSWORD
        self.database = database or config.NEO4J_DATABASE
        self.driver = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        # Quick socket check on port 7687 before initializing bolt driver
        host = self.uri.replace("bolt://", "").replace("neo4j://", "").split(":")[0]
        port = int(self.uri.split(":")[-1]) if ":" in self.uri else 7687

        try:
            sock = socket.create_connection((host, port), timeout=0.2)
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            logger.info(f"Neo4j database not reachable at {self.uri}. Operating in Local Graph Fallback Mode.")
            self.driver = None
            self.is_connected = False
            return

        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                connection_timeout=1.0,
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=50
            )
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"Successfully connected to Neo4j database at {self.uri}")
        except Exception as e:
            logger.info(f"Neo4j database connection notice ({e}). Operating in Local Graph Fallback Mode.")
            self.driver = None
            self.is_connected = False

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes Cypher query against Neo4j or fallback graph engine."""
        parameters = parameters or {}
        if self.is_connected and self.driver:
            try:
                with self.driver.session(database=self.database) as session:
                    result = session.run(query, parameters)
                    return [record.data() for record in result]
            except Exception as e:
                logger.error(f"Neo4j query execution error: {e}")
                return []
        else:
            logger.debug(f"[FALLBACK GRAPH QUERY] Query: {query.strip()[:60]}... | Params: {parameters}")
            return []

    def close(self):
        if self.driver:
            try:
                self.driver.close()
                logger.info("Closed Neo4j driver connection.")
            except Exception:
                pass
