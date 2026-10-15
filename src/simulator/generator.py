"""
FinGraph Synthetic Transaction & Fraud Syndicate Generator
Generates realistic normal financial transactions and explicit fraud patterns:
1. Normal legimate transfers
2. Smurfing (multiple micro transfers to 1 target)
3. Starburst / Fan-in (50 accounts funneling to 1 shell account)
4. Circular money flows (A -> B -> C -> A)
5. Multi-hop layering (A -> B -> C -> D -> E)
6. Connected suspicious IP networks
"""

import time
import random
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

class TransactionGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.banks = ["BANK_US_01", "BANK_US_02", "BANK_UK_01", "BANK_CH_01", "BANK_OFFSHORE_99"]
        self.ip_pool = [f"192.168.1.{i}" for i in range(1, 50)] + [f"10.0.0.{i}" for i in range(1, 50)]
        self.suspicious_ips = ["185.220.101.45", "185.220.101.46", "194.26.29.100", "45.154.255.88"]
        
        # Pre-generated legimate entities
        self.persons = [f"PERS_{i:04d}" for i in range(1, 200)]
        self.accounts = [f"ACC_{i:04d}" for i in range(1, 300)]
        
        # Map persons to primary accounts
        self.person_account_map = {
            self.persons[i]: [self.accounts[i], self.accounts[i + 100]]
            for i in range(len(self.persons))
        }

    def generate_transaction_id(self) -> str:
        return f"TXN_{uuid.uuid4().hex[:12].upper()}"

    def generate_normal_transaction(self) -> Dict[str, Any]:
        sender = random.choice(self.accounts)
        receiver = random.choice([acc for acc in self.accounts if acc != sender])
        sender_person = f"PERS_{sender.split('_')[1]}"
        receiver_person = f"PERS_{receiver.split('_')[1]}"
        
        return {
            "transaction_id": self.generate_transaction_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender_account": sender,
            "receiver_account": receiver,
            "sender_person": sender_person,
            "receiver_person": receiver_person,
            "sender_bank": random.choice(self.banks[:4]),
            "receiver_bank": random.choice(self.banks[:4]),
            "amount": round(random.uniform(10.0, 4500.0), 2),
            "currency": "USD",
            "sender_ip": random.choice(self.ip_pool),
            "receiver_ip": random.choice(self.ip_pool),
            "transaction_type": "WIRE",
            "pattern_type": "NORMAL",
            "is_suspicious": False
        }

    def generate_smurfing_pattern(self, target_account: str = "ACC_SHELL_9999", num_mules: int = 10) -> List[Dict[str, Any]]:
        """Smurfing: Multiple distinct accounts sending micro-amounts under reporting thresholds."""
        transactions = []
        base_time = time.time()
        suspicious_ip = random.choice(self.suspicious_ips)
        
        for i in range(num_mules):
            mule_acc = f"ACC_MULE_{i:04d}"
            mule_pers = f"PERS_MULE_{i:04d}"
            txn = {
                "transaction_id": self.generate_transaction_id(),
                "timestamp": datetime.fromtimestamp(base_time + i * 2, tz=timezone.utc).isoformat(),
                "sender_account": mule_acc,
                "receiver_account": target_account,
                "sender_person": mule_pers,
                "receiver_person": "PERS_SHELL_9999",
                "sender_bank": random.choice(self.banks[:4]),
                "receiver_bank": "BANK_OFFSHORE_99",
                "amount": round(random.uniform(9500.0, 9950.0), 2), # Just under $10,000 threshold
                "currency": "USD",
                "sender_ip": suspicious_ip, # Shared suspicious IP
                "receiver_ip": "194.26.29.100",
                "transaction_type": "STRUCTURING_TRANSFER",
                "pattern_type": "SMURFING",
                "is_suspicious": True
            }
            transactions.append(txn)
        return transactions

    def generate_starburst_pattern(self, hub_account: str = "ACC_STARBURST_HUB", num_spokes: int = 50) -> List[Dict[str, Any]]:
        """Starburst pattern: 50 distinct accounts funneling funds to 1 single hub account."""
        transactions = []
        base_time = time.time()
        
        for i in range(num_spokes):
            spoke_acc = f"ACC_SPOKE_{i:04d}"
            spoke_pers = f"PERS_SPOKE_{i:04d}"
            txn = {
                "transaction_id": self.generate_transaction_id(),
                "timestamp": datetime.fromtimestamp(base_time + (i * 0.5), tz=timezone.utc).isoformat(),
                "sender_account": spoke_acc,
                "receiver_account": hub_account,
                "sender_person": spoke_pers,
                "receiver_person": "PERS_STARBURST_HUB",
                "sender_bank": random.choice(self.banks),
                "receiver_bank": "BANK_OFFSHORE_99",
                "amount": round(random.uniform(500.0, 2500.0), 2),
                "currency": "USD",
                "sender_ip": random.choice(self.ip_pool),
                "receiver_ip": "45.154.255.88",
                "transaction_type": "STARBURST_FUNNEL",
                "pattern_type": "STARBURST",
                "is_suspicious": True
            }
            transactions.append(txn)
        return transactions

    def generate_circular_flow(self, chain: List[str] = None, amount: float = 50000.0) -> List[Dict[str, Any]]:
        """Circular money flow: A -> B -> C -> A (money returns to origin)."""
        if not chain:
            chain = ["ACC_CIRC_A", "ACC_CIRC_B", "ACC_CIRC_C", "ACC_CIRC_A"]
        
        transactions = []
        base_time = time.time()
        shared_ip = random.choice(self.suspicious_ips)
        
        for i in range(len(chain) - 1):
            sender = chain[i]
            receiver = chain[i + 1]
            txn = {
                "transaction_id": self.generate_transaction_id(),
                "timestamp": datetime.fromtimestamp(base_time + i * 5, tz=timezone.utc).isoformat(),
                "sender_account": sender,
                "receiver_account": receiver,
                "sender_person": f"PERS_{sender}",
                "receiver_person": f"PERS_{receiver}",
                "sender_bank": "BANK_US_01",
                "receiver_bank": "BANK_US_02",
                "amount": amount,
                "currency": "USD",
                "sender_ip": shared_ip,
                "receiver_ip": shared_ip,
                "transaction_type": "CIRCULAR_TRANSFER",
                "pattern_type": "CIRCULAR_FLOW",
                "is_suspicious": True
            }
            transactions.append(txn)
        return transactions

    def generate_multihop_layering(self, hop_count: int = 5, amount: float = 100000.0) -> List[Dict[str, Any]]:
        """Multi-hop layering flow: A -> B -> C -> D -> E."""
        chain = [f"ACC_HOP_{i:02d}" for i in range(hop_count + 1)]
        transactions = []
        base_time = time.time()
        
        for i in range(len(chain) - 1):
            sender = chain[i]
            receiver = chain[i + 1]
            txn = {
                "transaction_id": self.generate_transaction_id(),
                "timestamp": datetime.fromtimestamp(base_time + i * 3, tz=timezone.utc).isoformat(),
                "sender_account": sender,
                "receiver_account": receiver,
                "sender_person": f"PERS_{sender}",
                "receiver_person": f"PERS_{receiver}",
                "sender_bank": random.choice(self.banks),
                "receiver_bank": random.choice(self.banks),
                "amount": amount * (0.98 ** i), # Slightly reduced by fees
                "currency": "USD",
                "sender_ip": random.choice(self.ip_pool),
                "receiver_ip": random.choice(self.ip_pool),
                "transaction_type": "LAYERING_TRANSFER",
                "pattern_type": "MULTIHOP_LAYERING",
                "is_suspicious": True
            }
            transactions.append(txn)
        return transactions

    def generate_batch(self, count: int = 100, fraud_ratio: float = 0.2) -> List[Dict[str, Any]]:
        """Generate a mixed batch of normal and fraud syndicate transactions."""
        batch = []
        fraud_count = int(count * fraud_ratio)
        normal_count = count - fraud_count

        for _ in range(normal_count):
            batch.append(self.generate_normal_transaction())

        # Distribute fraud count across fraud patterns
        if fraud_count > 0:
            batch.extend(self.generate_smurfing_pattern(num_mules=max(3, fraud_count // 4)))
            batch.extend(self.generate_starburst_pattern(num_spokes=max(5, fraud_count // 4)))
            batch.extend(self.generate_circular_flow(amount=45000.0))
            batch.extend(self.generate_multihop_layering(hop_count=4, amount=80000.0))

        random.shuffle(batch)
        return batch
