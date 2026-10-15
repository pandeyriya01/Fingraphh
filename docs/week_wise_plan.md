# FinGraph Week-Wise Implementation Alignment

Aligned with the official Infotact Solutions Project Document (Vol. II):

| Week | Data Engineering (Kafka, Flink, Neo4j) | Analytics & UI (Cypher, GDS, Dashboard) | FinGraph Module Implementation |
| :--- | :--- | :--- | :--- |
| **Week 1** | Ingestion Setup: Python simulator generating realistic syndicate transactions. Stream to Kafka. | Graph Schema: Design Neo4j schema (Person, Account, Bank, TRANSFERRED_TO). | `src/simulator/`, `src/kafka/`, `config/neo4j_constraints.cypher` |
| **Week 2** | Stream Processing: Apache Flink jobs consuming Kafka stream, cleaning data, upserting to Neo4j. | Cypher Queries: Detect circular money flows ($A \to B \to C \to A$) & node risk scores. | `src/flink/`, `src/neo4j/`, `config/fraud_queries.cypher`, `src/fraud_detection/` |
| **Mid-Review Audit** | Pipeline Audit: Prove transactions appear in graph. | Query Optimization: Ensure multi-hop Cypher queries execute fast. | `scripts/run_e2e_pipeline.py`, `tests/` |
| **Week 3** | Graph Data Science: Implement Neo4j GDS algorithms (PageRank, WCC, Louvain). | Dashboard UI: Interactive network visualization connected to graph endpoint. | `src/graph_algorithms/`, `dashboard/` |
| **Week 4** | Automation: Rules engine triggering automated alerts when Graph Risk Score exceeds threshold. | Refine & Polish: Finalize visual layout, allow analyst to freeze accounts and trace money trail. | `src/risk_scoring/`, `src/alerts/`, `dashboard/components/alerts_view.py` |
