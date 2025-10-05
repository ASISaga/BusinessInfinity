# DecisionIntegrator.py
import time
import yaml
from agent_framework import Executor, WorkflowContext, handler
from DecisionLedger import DecisionLedger


class DecisionIntegrator(Executor):
    """
    Collects assessments and evidence from boardroom agents and tools,
    then produces a structured DecisionArtifact using configurable decision modes.
    Persists each decision into a ledger.
    """

    def __init__(self, config_path="boardroom.governance.yaml", name="DecisionIntegrator"):
        super().__init__(name)
        self.buffer = []
        self.ledger = None

        # Load governance config
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        self.mode = cfg.get("decision_mode", "consensus")
        self.weights = cfg.get("weights", {})
        self.veto_roles = set(cfg.get("veto_roles", []))
        self.quorum = cfg.get("quorum", {})
        self.escalation = cfg.get("escalation", {})
        self.assignments_cfg = cfg.get("assignments", {})
        self.logging_cfg = cfg.get("logging", {})

        # Initialize ledger if logging enabled
        if self.logging_cfg.get("format", "jsonl") == "jsonl":
            self.ledger = DecisionLedger(self.logging_cfg.get("ledger_path", "decisions.ledger.jsonl"))

    @handler
    async def collect(self, message: dict, ctx: WorkflowContext[dict]):
        self.buffer.append(message)

        if self.ready_to_decide():
            decision = self.make_decision(self.buffer)

            # Persist to ledger
            if self.ledger:
                self.ledger.log(decision)

            # Emit decision into the workflow
            await ctx.send_message({"type": "decision", "value": decision})
            await ctx.yield_output(decision)

            # Clear buffer for next topic
            self.buffer.clear()

    def ready_to_decide(self) -> bool:
        roles = {m.get("role") for m in self.buffer if "role" in m}

        # Quorum check
        if self.mode == "quorum":
            required_roles = set(self.quorum.get("required_roles", []))
            min_votes = self.quorum.get("minimum_votes", 0)
            return required_roles <= roles and len(roles) >= min_votes

        # Default: require CFO, CTO, COO, Investor
        return {"CFO", "CTO", "COO", "Investor"} <= roles

    def make_decision(self, items: list) -> dict:
        topic = next((i.get("topic") for i in items if i.get("topic")), "Unknown")
        votes = {i.get("role"): i.get("vote", "APPROVE") for i in items if "role" in i}

        # --- Veto check ---
        for role in self.veto_roles:
            if votes.get(role) == "REJECT":
                return self._artifact(topic, "REJECT", f"Veto by {role}", items)

        # --- Mode logic ---
        if self.mode == "consensus":
            outcome = "APPROVE" if all(v == "APPROVE" for v in votes.values()) else "REJECT"
            rationale = "Consensus required: all must agree."
        elif self.mode == "weighted":
            score = sum(self.weights.get(r, 1) for r, v in votes.items() if v == "APPROVE")
            total = sum(self.weights.get(r, 1) for r in votes)
            outcome = "APPROVE" if score > total / 2 else "REJECT"
            rationale = f"Weighted voting: {score}/{total} in favor."
        elif self.mode == "quorum":
            required_roles = set(self.quorum.get("required_roles", []))
            min_votes = self.quorum.get("minimum_votes", 0)
            if required_roles <= set(votes.keys()) and len(votes) >= min_votes:
                outcome = "APPROVE"
                rationale = f"Quorum met: {len(votes)}/{min_votes} votes."
            else:
                return self._escalate(topic, items)
        else:
            outcome = "APPROVE"
            rationale = "Default approve."

        return self._artifact(topic, outcome, rationale, items)

    def _artifact(self, topic, outcome, rationale, evidence_items):
        evidence = [i for i in evidence_items if i.get("source") or i.get("role")]

        # Build assignments from config
        default_owner = self.assignments_cfg.get("default_owner", "COO")
        due_days = self.assignments_cfg.get("default_due_days", 30)
        deps = []
        for dep_list in self.assignments_cfg.get("dependency_map", {}).values():
            deps.extend(dep_list)

        return {
            "id": f"DEC-{int(time.time())}",
            "topic": topic,
            "outcome": outcome,
            "rationale": rationale,
            "assignments": [
                {"owner": default_owner, "due_in_days": due_days, "dependencies": deps}
            ],
            "evidence": evidence if self.logging_cfg.get("include_evidence", True) else [],
        }

    def _escalate(self, topic, evidence_items):
        """Handle escalation if quorum or consensus fails."""
        fallback = self.escalation.get("fallback_role", "CEO")
        notify = self.escalation.get("notify_roles", [])
        action = self.escalation.get("action", "Reopen discussion")

        return {
            "id": f"DEC-{int(time.time())}",
            "topic": topic,
            "outcome": "ESCALATE",
            "rationale": f"Escalated to {fallback}. Action: {action}",
            "notify": notify,
            "evidence": evidence_items,
        }
