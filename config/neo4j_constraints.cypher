// FinGraph Schema Constraints and Indexes

// 1. Account Node Constraints & Indexes
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;

CREATE INDEX account_risk_score_idx IF NOT EXISTS
FOR (a:Account) ON (a.risk_score);

// 2. Person Node Constraints
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

// 3. Bank Node Constraints
CREATE CONSTRAINT bank_code_unique IF NOT EXISTS
FOR (b:Bank) REQUIRE b.bank_code IS UNIQUE;

// 4. IPAddress Node Constraints
CREATE CONSTRAINT ip_address_unique IF NOT EXISTS
FOR (i:IPAddress) REQUIRE i.ip_address IS UNIQUE;

// 5. Transaction Edge Index
CREATE INDEX transaction_id_idx IF NOT EXISTS
FOR ()-[r:TRANSFERRED_TO]-() ON (r.transaction_id);

CREATE INDEX transaction_pattern_idx IF NOT EXISTS
FOR ()-[r:TRANSFERRED_TO]-() ON (r.pattern_type);
