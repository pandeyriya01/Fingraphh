# Neo4j Graph Data Science (GDS) Setup & Execution Guide

## Overview

FinGraph relies on native Graph Data Science (GDS) algorithms to uncover structural properties of the financial network:
- **PageRank**: Measures node importance/centrality. Accounts with high PageRank in financial networks often act as primary money laundering hubs.
- **Weakly Connected Components (WCC)**: Partition the graph into disconnected subgraphs to isolate fraud syndicates from legitimate banking traffic.
- **Louvain Community Detection**: Detects tightly knit financial communities to expose money laundering rings.

## Enabling GDS in Neo4j

In `docker-compose.yml`, GDS is automatically enabled via environment flags:

```yaml
environment:
  - NEO4J_PLUGINS=["graph-data-science", "apoc"]
  - NEO4J_dbms_security_procedures_unrestricted=gds.*,apoc.*
```

## Running GDS via Cypher

```cypher
// 1. Drop existing projection
CALL gds.graph.drop('fingraph-projection', false);

// 2. Create in-memory projection
CALL gds.graph.project(
  'fingraph-projection',
  'Account',
  { TRANSFERRED_TO: { type: 'TRANSFERRED_TO', orientation: 'NATURAL' } }
);

// 3. PageRank
CALL gds.pageRank.write('fingraph-projection', { writeProperty: 'pagerank' });

// 4. WCC
CALL gds.wcc.write('fingraph-projection', { writeProperty: 'componentId' });

// 5. Louvain
CALL gds.louvain.write('fingraph-projection', { writeProperty: 'communityId' });
```

## Standalone Fallback Analytics

If Neo4j GDS plugin is not installed on your Neo4j instance, FinGraph automatically falls back to NetworkX graph algorithms in Python (`FallbackGraphAnalytics`), executing PageRank, WCC, and Louvain community detection in memory without interrupting pipeline execution.
