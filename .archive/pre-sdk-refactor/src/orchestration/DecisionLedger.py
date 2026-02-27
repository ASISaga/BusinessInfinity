# DecisionLedger.py
import json
import os
from datetime import datetime


class DecisionLedger:
    """
    Simple JSONL-based ledger for storing decision artifacts.
    Each decision is appended as a JSON object on its own line.
    """

    def __init__(self, path: str = "decisions.ledger.jsonl"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                f.write("")

    def log(self, artifact: dict):
        """Append a decision artifact to the ledger with timestamp."""
        artifact["logged_at"] = datetime.utcnow().isoformat()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(artifact, ensure_ascii=False) + "\n")

    def load_all(self):
        """Load all decision artifacts from the ledger."""
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
