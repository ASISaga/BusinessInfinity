from typing import Dict, List
from .service_bus import Bus

class Governance:
    def __init__(self):
        self.bus = Bus()

    def blend_scores(self, scores: List[Dict[str, float]], method: str, weights: Dict[str, float] | None = None) -> Dict[str, float]:
        labels = {label for s in scores for label in s.keys()}
        blended = {}
        for label in labels:
            vals = []
            if method == "weighted" and weights:
                # weights aligned with scores order; in practice map by legend
                total, wsum = 0.0, 0.0
                for i, s in enumerate(scores):
                    w = list(weights.values())[i]
                    total += w * s.get(label, 0.0)
                    wsum += w
                blended[label] = total / max(wsum, 1e-9)
            elif method == "mean":
                vals = [s.get(label, 0.0) for s in scores]
                blended[label] = sum(vals) / max(len(vals), 1)
            elif method == "median":
                vals = sorted([s.get(label, 0.0) for s in scores])
                n = len(vals)
                blended[label] = (vals[n//2] if n % 2 else 0.5*(vals[n//2-1]+vals[n//2])) if n else 0.0
            else:
                blended[label] = 0.0
        return blended

    def audit_log(self, event_type: str, payload: dict):
        self.bus.publish(subject=event_type, payload=payload)