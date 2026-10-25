"""SHA-256 Merkle Audit Tree Module for VeriLedger / Kizuna-Vault.

Anchors tamper-proof digital proof over ingested RBI Account Aggregator banking
ledgers, GSTN tax invoices, and MCA registry records. Guarantees non-repudiation
and immutability for institutional corporate venture diligence.
"""

from __future__ import annotations
import hashlib
from typing import List, Dict, Any, Tuple


class MerkleAuditTree:
    """Computes and validates a SHA-256 Merkle Audit Tree over financial transactions."""

    def __init__(self, data_items: List[Dict[str, Any]]):
        self.data_items = data_items
        self.leaves = [self._hash_item(item) for item in data_items]
        if not self.leaves:
            self.leaves = [hashlib.sha256(b"EMPTY_AUDIT_LEAF").hexdigest()]
        self.tree_levels = self._build_tree(self.leaves)
        self.root = self.tree_levels[-1][0] if self.tree_levels else ""

    @staticmethod
    def _hash_item(item: Dict[str, Any]) -> str:
        """Deterministically serialize and hash a financial record leaf."""
        # Sort keys to ensure deterministic serialization
        serialized = "|".join(f"{k}:{item[k]}" for k in sorted(item.keys()))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _combine_hashes(left: str, right: str) -> str:
        """Combine two child node hashes to form parent hash."""
        combined = f"{left}:{right}".encode("utf-8")
        return hashlib.sha256(combined).hexdigest()

    def _build_tree(self, leaves: List[str]) -> List[List[str]]:
        """Construct all levels of the Merkle Tree upwards to the single root."""
        levels = [leaves]
        current_level = leaves

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Duplicate odd leaf to balance tree
                    right = left
                parent = self._combine_hashes(left, right)
                next_level.append(parent)
            levels.append(next_level)
            current_level = next_level

        return levels

    def get_merkle_root(self) -> str:
        """Return the 64-character SHA-256 Merkle Root anchored with 0x prefix."""
        return f"0x{self.root}"

    def get_audit_proof(self, index: int) -> List[Tuple[str, str]]:
        """Generate audit trail proof path for a leaf index: List of (hash, 'left'|'right')."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds")

        proof = []
        current_idx = index

        for level in self.tree_levels[:-1]:
            is_odd = current_idx % 2 == 1
            sibling_idx = current_idx - 1 if is_odd else current_idx + 1

            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[current_idx]

            direction = "left" if is_odd else "right"
            proof.append((sibling_hash, direction))
            current_idx = current_idx // 2

        return proof

    @classmethod
    def verify_proof(cls, leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """Cryptographically verify that a leaf hash is part of the anchored root."""
        current = leaf_hash
        clean_root = root.replace("0x", "")

        for sibling_hash, direction in proof:
            if direction == "left":
                current = cls._combine_hashes(sibling_hash, current)
            else:
                current = cls._combine_hashes(current, sibling_hash)

        return current == clean_root
