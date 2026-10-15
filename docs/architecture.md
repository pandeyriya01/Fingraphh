# FinGraph Architecture & System Design Document

## System Overview

FinGraph is a real-time anti-money laundering (AML) and fraud syndicate analytics system built on a streaming graph database architecture. Standard relational databases evaluate isolated rows or static rules (e.g. `flag transactions over $10,000`), missing complex multi-hop layering, smurfing structures, starburst funnels, and circular money flows. FinGraph models transactions as a connected graph and evaluates structural topology in real time.

## Architecture Data Flow

```
+-----------------------------+
| Python Transaction Simulator| (Generates normal & syndicate patterns)
+-----------------------------+
               |
               v
+-----------------------------+
|    Apache Kafka Brokers     | (Topic: transactions.raw)
+-----------------------------+
               |
               v
+-----------------------------+
|  Apache Flink Streaming Engine| (Stateful windowing & cleansing)
+-----------------------------+
               |
               v
+-----------------------------+
|     Neo4j Graph Database    | (Person, Account, Bank, IPAddress)
+-----------------------------+
        /              \
       v                v
+---------------+  +--------------------------+
| Cypher Queries|  | Neo4j Graph Data Science | (PageRank, WCC, Louvain)
+---------------+  +--------------------------+
        \              /
         v            v
+--------------------------------+
|  Explainable Risk Score Engine | (0 - 100 Risk Score + Reason Codes)
+--------------------------------+
        /                \
       v                  v
+-------------------+  +-----------------------+
|  Alert Manager    |  | Streamlit Dashboard   |
| (Slack/Email/Logs)|  | (PyVis Network Graph) |
+-------------------+  +-----------------------+
```

## Graph Schema Model

### Nodes
- `:Person {person_id: String}`
- `:Account {account_id: String, risk_score: Float}`
- `:Bank {bank_code: String}`
- `:IPAddress {ip_address: String}`

### Relationships
- `(Account)-[:TRANSFERRED_TO {transaction_id, amount, timestamp, pattern_type, is_suspicious}]->(Account)`
- `(Person)-[:HAS_ACCOUNT]->(Account)`
- `(Account)-[:HELD_AT]->(Bank)`
- `(Account)-[:CONNECTED_FROM_IP]->(IPAddress)`

## Risk Engine Scoring Mechanics

The Explainable Risk Score engine calculates a transparent $0 - 100$ score:
1. **PageRank Centrality Weight**: Up to 30 pts for central transaction hubs.
2. **Circular Flow Participation**: 35 pts for $A \to B \to C \to A$ cycles.
3. **Starburst Hub**: 35 pts for 5+ distinct micro-senders funneling into 1 shell account.
4. **Multi-Hop Layering**: 20 pts for 3-6 hop layering chains.
5. **Rapid Velocity**: 15 pts for rapid high-volume transaction bursts.

Risk Tiers:
- **LOW RISK**: Score 0 – 30
- **MEDIUM RISK**: Score 31 – 69
- **HIGH RISK**: Score 70 – 100 (Triggers automated alerts & Freeze Action)
