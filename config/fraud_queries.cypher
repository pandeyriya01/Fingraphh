// Dedicated Cypher Fraud Detection Query Suite

// Query 1: Detect Circular Money Flows (A -> B -> C -> A)
MATCH path = (a:Account)-[r1:TRANSFERRED_TO]->(b:Account)-[r2:TRANSFERRED_TO]->(c:Account)-[r3:TRANSFERRED_TO]->(a)
WHERE a <> b AND b <> c AND a <> c
RETURN a.account_id AS origin_account,
       b.account_id AS node_b,
       c.account_id AS node_c,
       r1.amount + r2.amount + r3.amount AS total_cycle_volume,
       [r1.transaction_id, r2.transaction_id, r3.transaction_id] AS txn_ids,
       "CIRCULAR_FLOW" AS pattern_detected;

// Query 2: Detect Starburst / Fan-in Funneling (N distinct senders -> 1 target shell account)
MATCH (sender:Account)-[r:TRANSFERRED_TO]->(hub:Account)
WITH hub, count(DISTINCT sender) AS fan_in_count, sum(r.amount) AS total_funneled_amount, collect(r.transaction_id) AS txns
WHERE fan_in_count >= 5
RETURN hub.account_id AS hub_account,
       fan_in_count,
       total_funneled_amount,
       "STARBURST_FANIN" AS pattern_detected;

// Query 3: Multi-hop Layering Chains (3 to 6 hops)
MATCH path = (startAcc:Account)-[:TRANSFERRED_TO*3..6]->(endAcc:Account)
WHERE startAcc <> endAcc
WITH path, length(path) AS hop_length, nodes(path) AS chain_nodes
RETURN [n in chain_nodes | n.account_id] AS layering_path,
       hop_length,
       "MULTIHOP_LAYERING" AS pattern_detected;

// Query 4: Shared IP Fraud Cluster Detection
MATCH (a1:Account)-[:CONNECTED_FROM_IP]->(ip:IPAddress)<-[:CONNECTED_FROM_IP]-(a2:Account)
WHERE a1 <> a2
WITH ip, count(DISTINCT a1) AS connected_accounts, collect(DISTINCT a1.account_id) AS account_list
WHERE connected_accounts >= 3
RETURN ip.ip_address AS shared_ip,
       connected_accounts,
       account_list,
       "SHARED_IP_CLUSTER" AS pattern_detected;
