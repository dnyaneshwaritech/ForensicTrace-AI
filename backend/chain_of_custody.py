import hashlib
import json
import time
import os

GENESIS_HASH = "0" * 64

class ChainOfCustodyLedger:
    """
    Cryptographic SHA-256 Tamper-Evident Ledger for Field Drug Evidence.
    """

    def __init__(self, ledger_file="backend/chain_ledger.json"):
        self.ledger_file = ledger_file
        self.blocks = []
        self._load_or_init_ledger()

    def _load_or_init_ledger(self):
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r', encoding='utf-8') as f:
                    self.blocks = json.load(f)
            except Exception:
                self.blocks = []

        if not self.blocks:
            # Create Genesis Block
            genesis_block = {
                "block_index": 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "case_id": "GENESIS-000",
                "officer_id": "SYSTEM",
                "sample_id": "N/A",
                "presumptive_result": "GENESIS BLOCK",
                "previous_hash": GENESIS_HASH,
                "current_hash": ""
            }
            genesis_block["current_hash"] = self._compute_hash(genesis_block)
            self.blocks.append(genesis_block)
            self._save_ledger()

    def _compute_hash(self, block):
        payload = f"{block['block_index']}|{block['timestamp']}|{block['case_id']}|{block['officer_id']}|{block['sample_id']}|{block['presumptive_result']}|{block['previous_hash']}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def add_case_record(self, case_id, officer_id, sample_id, location, reagent, presumptive_result, confidence, signature="DIGITALLY_SIGNED_OFFICER"):
        """
        Appends a cryptographically linked evidence record to the audit chain.
        """
        previous_block = self.blocks[-1]
        new_index = len(self.blocks)

        new_block = {
            "block_index": new_index,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "case_id": case_id,
            "officer_id": officer_id,
            "sample_id": sample_id,
            "location": location,
            "reagent_used": reagent,
            "presumptive_result": presumptive_result,
            "confidence_score": confidence,
            "signature": signature,
            "previous_hash": previous_block["current_hash"],
            "current_hash": ""
        }
        new_block["current_hash"] = self._compute_hash(new_block)
        self.blocks.append(new_block)
        self._save_ledger()
        return new_block

    def verify_integrity(self):
        """
        Validates cryptographic integrity of the entire chain.
        Returns (is_valid, list_of_violations).
        """
        violations = []
        for i in range(len(self.blocks)):
            current = self.blocks[i]

            # 1. Verify self-computed hash
            recomputed = self._compute_hash(current)
            if recomputed != current["current_hash"]:
                violations.append(f"Block #{i} ({current['case_id']}) content hash mismatch! (Tampered data)")

            # 2. Verify link to previous block
            if i > 0:
                previous = self.blocks[i - 1]
                if current["previous_hash"] != previous["current_hash"]:
                    violations.append(f"Block #{i} previous_hash mismatch with Block #{i-1}!")

        is_valid = len(violations) == 0
        return is_valid, violations

    def _save_ledger(self):
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            json.dump(self.blocks, f, indent=2)

    def get_all_blocks(self):
        return self.blocks
