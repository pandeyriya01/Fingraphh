# FinGraph – Real-Time Fraud Syndicate Analytics

> **Official Project Implementation | FinTech & Anti-Money Laundering (AML) Domain**  
> *A real-time fraud & money-laundering analytics system powered by Apache Kafka, Apache Flink, Neo4j Graph Database, Neo4j Graph Data Science (GDS), Explainable Risk Scoring, and an Interactive Dashboard.*

---

## 📌 Problem Statement & Business Context

Standard fraud analytics rely on relational tables (SQL) and isolated threshold rules (e.g., *"flag transactions over $10,000"*). Money laundering syndicates easily evade detection through **structuring / smurfing** (e.g. 50 seemingly unrelated accounts sending $9,900 each), **starburst funnels**, **multi-hop layering**, and **circular money flows ($A \to B \to C \to A$)**.

### Why Relational Databases Fail for AML
- Relational databases require expensive `JOIN` operations across deep multi-hop paths ($N$-hop joins scale exponentially $O(k^N)$).
- Relational models treat accounts as isolated rows rather than interconnected entities.
- Circular pattern detection requires expensive recursive table expressions.

### Why Graph Databases Excel for AML
- Graph databases treat relationships as first-class citizens ($O(1)$ index-free adjacency traversal).
- Topological algorithms (PageRank, Weakly Connected Components, Louvain Community Detection) algorithmically score centrality and discover hidden financial rings.

---

## 🏗️ Architecture

```
Python Transaction Simulator
           ↓
     Apache Kafka (transactions.raw)
           ↓
    Apache Flink (Stream Processing & Stateful Aggregations)
           ↓
   Neo4j Graph Database (Person, Account, Bank, IPAddress)
      /         \
     v           v
Cypher Queries  Neo4j Graph Data Science (PageRank, WCC, Louvain)
      \         /
       v       v
Explainable Risk Score Engine (0 - 100 Score + Reason Codes)
      /         \
     v           v
Alert System   Interactive Streamlit Dashboard
(Slack/Email)  (Node-Link Network Graph & Account Freeze)
```

---

## 📁 Directory Structure

```
Fingraph/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── src/
│   ├── simulator/
│   │   ├── generator.py             # Generates normal & fraud syndicate transaction patterns
│   │   └── producer.py              # Streams transactions to Kafka
│   ├── kafka/
│   │   ├── config.py                # Kafka topic & admin manager
│   │   ├── producer.py              # Producer wrapper with fallback
│   │   └── consumer.py              # Consumer client
│   ├── flink/
│   │   ├── streaming_job.py         # PyFlink streaming pipeline
│   │   └── processing_utils.py      # Stateful windowed aggregations
│   ├── neo4j/
│   │   ├── connection.py            # Neo4j driver connection manager
│   │   ├── schema.py                # Schema constraints & indexes
│   │   └── loader.py                # Ingestion loader & local graph model
│   ├── fraud_detection/
│   │   ├── cypher_detector.py       # Executes Cypher & graph pattern matching
│   │   └── pattern_rules.py         # Heuristic rule evaluator
│   ├── graph_algorithms/
│   │   ├── gds_runner.py            # Neo4j GDS wrapper (PageRank, WCC, Louvain)
│   │   └── fallback_analytics.py    # NetworkX fallback GDS analytics
│   ├── risk_scoring/
│   │   ├── engine.py                # Explainable Risk Scoring Engine
│   │   └── classifier.py            # LOW, MEDIUM, HIGH risk tier classifier
│   ├── alerts/
│   │   ├── alert_manager.py         # Risk score monitor & alert dispatcher
│   │   └── channels.py              # Slack & Email notification handlers
│   └── utils/
│       ├── config.py                # Configuration loader
│       └── logger.py                # Windows UTF-8 compatible logging
├── dashboard/
│   ├── app.py                       # Interactive Streamlit Web Application
│   └── components/                  # Graph, Table, Metrics, and Alert components
├── tests/                           # 100% Passing Pytest Test Suite
├── config/                          # Cypher schema, fraud queries, GDS projections
├── docs/                            # Deep architecture, GDS setup, & user guide
├── scripts/                         # Execution & E2E verification scripts
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## ⚡ Quick Start & Execution Commands

### 1. Installation & Environment Setup

```bash
# Clone or navigate to the project directory
cd Fingraph

# Install Python dependencies
pip install -r requirements.txt

# Verify environment setup
python scripts/setup_env.py
```

### 2. Launch Services via Docker (Kafka, Flink, Neo4j)

```bash
# Start Kafka, Zookeeper, Flink, and Neo4j containers
docker-compose up -d
```

> **Note for Windows / Local Dev**: If Docker is not running, FinGraph seamlessly operates with native local drivers and in-memory graph fallbacks so all commands and dashboards execute smoothly.

### 3. Run End-to-End Pipeline Verification

```bash
python scripts/run_e2e_pipeline.py
```

### 4. Run the Full Test Suite

```bash
pytest tests/ -v
```

### 5. Launch the Interactive Analyst Dashboard

```bash
streamlit run dashboard/app.py
```

Open your web browser at **`http://localhost:8501`**.

---

## 💻 Module Execution Guide

### Transaction Generator & Simulator
```bash
python scripts/run_simulation.py
```

### Graph Analytics Execution
```bash
python scripts/run_graph_analysis.py
```

### Pre-populate Sample Dataset
```bash
python scripts/load_sample_data.py
```

---

## 🧠 Graph Data Science (GDS) Algorithms

1. **PageRank Centrality**:
   - Scores centrality of accounts. Accounts acting as central collection hubs for multiple money mules rank high.
2. **Weakly Connected Components (WCC)**:
   - Partitions the overall financial graph into isolated subgraphs to expose autonomous fraud rings.
3. **Louvain Community Detection**:
   - Identifies densely connected clusters of accounts sharing common transaction volume or IP infrastructure.

---

## 🛡️ Explainable Risk Scoring Matrix

| Component | Max Points | Trigger Condition |
| :--- | :--- | :--- |
| **PageRank Centrality** | 30 pts | High central node score |
| **Circular Flow** | 35 pts | $A \to B \to C \to A$ transfer loop |
| **Starburst Hub** | 35 pts | 5+ distinct senders funneling micro-amounts |
| **Multi-Hop Layering** | 20 pts | 3-6 hop intermediary chain |
| **Velocity Burst** | 15 pts | Rapid high-volume transaction stream |

### Risk Tiers
- **LOW RISK**: 0 – 30 points
- **MEDIUM RISK**: 31 – 69 points
- **HIGH RISK**: 70 – 100 points *(Triggers automated alerts & Freeze Action)*

---

## 🎤 Interview & Technical Q&A Guide

**Q: How does FinGraph handle real-time streaming to graph database updates?**  
*A: FinGraph uses Apache Kafka as the event bus to ingest high-throughput transaction streams. Apache Flink consumes raw transactions, performs windowed stateful aggregations (tracking velocity and structuring thresholds), and upserts nodes and edges into Neo4j in real time.*

**Q: What happens if Neo4j or Kafka services are temporarily unreachable?**  
*A: FinGraph is built with production resilience. Drivers feature instant socket connection checks (0.2s) and fallback to local NetworkX graph storage and streaming drivers, guaranteeing zero service interruption for analysts.*

**Q: How do you explain the Risk Score to auditors and compliance officers?**  
*A: Rather than using a black-box model, FinGraph computes an Explainable Risk Score (0-100) accompanied by exact reason codes (e.g. `['PARTICIPATED_IN_CIRCULAR_MONEY_FLOW', 'STARBURST_DESTINATION_SHELL_HUB']`), allowing AML investigators to audit every decision.*

---

## 📜 License & Accreditation

FinGraph - Real-Time Fraud Syndicate Analytics  
Advanced Data Analytics Portfolio Project (Vol. II) | Infotact Solutions
