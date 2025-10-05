# DecisionLedgerExplorer.py
import json
from typing import List, Dict, Optional
from datetime import datetime


class DecisionLedgerExplorer:
    """
    Server-side utility for exploring decision artifacts stored in a JSONL ledger.
    Can be called from HTTP route handlers to query past decisions.
    """

    def __init__(self, path: str = "decisions.ledger.jsonl"):
        self.path = path

    def _load_all(self) -> List[Dict]:
        """Load all decision artifacts from the ledger."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def get_all(self, limit: Optional[int] = None) -> List[Dict]:
        """Return all decisions, optionally limited to the most recent N."""
        records = self._load_all()
        if limit:
            return records[-limit:]
        return records

    def filter_by_topic(self, keyword: str) -> List[Dict]:
        """Return all decisions where the topic contains a keyword."""
        return [d for d in self._load_all() if keyword.lower() in d.get("topic", "").lower()]

    def filter_by_role(self, role: str) -> List[Dict]:
        """Return all decisions where a given role contributed evidence."""
        return [
            d for d in self._load_all()
            if any(ev.get("role") == role for ev in d.get("evidence", []))
        ]

    def filter_by_outcome(self, outcome: str) -> List[Dict]:
        """Return all decisions with a given outcome (APPROVE, REJECT, ESCALATE)."""
        return [d for d in self._load_all() if d.get("outcome") == outcome]

    def get_summary(self) -> Dict[str, int]:
        """Return a simple summary: counts of outcomes."""
        records = self._load_all()
        summary = {"APPROVE": 0, "REJECT": 0, "ESCALATE": 0}
        for d in records:
            outcome = d.get("outcome")
            if outcome in summary:
                summary[outcome] += 1
        return summary

    def get_recent(self, since: datetime) -> List[Dict]:
        """Return all decisions logged after a given datetime."""
        records = self._load_all()
        return [
            d for d in records
            if "logged_at" in d and datetime.fromisoformat(d["logged_at"]) > since
        ]

    def search(
        self,
        topic: Optional[str] = None,
        role: Optional[str] = None,
        outcome: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Flexible search across multiple filters.
        Example: search(topic="energy", role="CFO", outcome="APPROVE")
        """
        records = self._load_all()

        if topic:
            records = [d for d in records if topic.lower() in d.get("topic", "").lower()]

        if role:
            records = [
                d for d in records
                if any(ev.get("role") == role for ev in d.get("evidence", []))
            ]

        if outcome:
            records = [d for d in records if d.get("outcome") == outcome]

        if since:
            records = [
                d for d in records
                if "logged_at" in d and datetime.fromisoformat(d["logged_at"]) > since
            ]

        return records
