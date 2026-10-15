"""
Neo4j Schema Setup & Index Initialization
"""

from pathlib import Path
from src.neo4j.connection import Neo4jConnection
from src.utils.logger import get_logger

logger = get_logger("Neo4jSchemaSetup")

def setup_schema(conn: Neo4jConnection):
    """Reads cypher constraints file and creates indexes & constraints."""
    constraints_path = Path(__file__).resolve().parent.parent.parent / 'config' / 'neo4j_constraints.cypher'
    if not constraints_path.exists():
        logger.error(f"Constraints file not found at {constraints_path}")
        return False

    with open(constraints_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into individual cypher statements
    statements = [s.strip() for s in content.split(';') if s.strip() and not s.strip().startswith('//')]

    logger.info(f"Applying {len(statements)} schema statements to Neo4j...")
    for stmt in statements:
        if stmt:
            conn.execute_query(stmt)
    
    logger.info("Neo4j Schema and constraints initialization completed.")
    return True

if __name__ == "__main__":
    conn = Neo4jConnection()
    setup_schema(conn)
    conn.close()
