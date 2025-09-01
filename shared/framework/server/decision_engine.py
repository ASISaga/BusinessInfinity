from typing import Any, Dict, List, Tuple
from .adapters import LegendAdapterRouter
from .governance import Governance

class DecisionEngine:
    def __init__(self, tree: Dict[str, Any], adapters: Dict[str, Any], principles: Dict[str, Any]):
        self.tree = tree
        self.router = LegendAdapterRouter(adapters)
        self.gov = Governance()
        self.principles_map = {p["principle_id"]: p for p in principles["principles"]}

    def run_node(self, node: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
        legends = node.get("legend_modes", [])
        applied = []
        per_legend_scores = []
        for legend in legends:
            pr_ids = [pid for pid in node.get("principles", self.principles_map.keys())]
            resp = self.router.score(legend=legend, role=node["role"], evidence=evidence, principles=pr_ids)
            per_legend_scores.append(resp["decision_scores"])
            applied.append({"legend": legend, "applied_principles": resp.get("applied_principles", [])})
        gov = node.get("governance", {"blend": "mean"})
        blended = self.gov.blend_scores(per_legend_scores, method=gov.get("blend", "mean"), weights=gov.get("weights"))
        choice = max(blended.items(), key=lambda kv: kv[1])[0]
        self.gov.audit_log("decision.node.completed", {
            "node_id": node["node_id"], "role": node["role"], "legends": legends,
            "per_legend_scores": per_legend_scores, "blended": blended, "choice": choice
        })
        return {"choice": choice, "blended": blended, "legend_heatmap": per_legend_scores, "applied": applied}

    def next_node(self, current: Dict[str, Any], choice: str) -> Dict[str, Any] | None:
        for o in current["outputs"]:
            if o["label"] == choice:
                nxt = o.get("next_node")
                if not nxt or nxt == "END":
                    return None
                for n in self.tree["nodes"]:
                    if n["node_id"] == nxt:
                        return n
        return None

    def run(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        node = self.tree["nodes"][0]
        path = []
        while node:
            result = self.run_node(node, evidence)
            path.append({"node_id": node["node_id"], "result": result})
            node = self.next_node(node, result["choice"])
        self.gov.audit_log("decision.tree.completed", {"tree_id": self.tree["tree_id"], "path": path})
        return {"tree_id": self.tree["tree_id"], "path": path}