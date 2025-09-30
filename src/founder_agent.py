from .business_agent import BusinessAgent
from typing import Dict, Any, List

class FounderAgent(BusinessAgent):
    """
    Founder - Vision, innovation, and entrepreneurial leadership
    Responsibilities:
    - Company vision and mission
    - Innovation and creative direction
    - Culture and values definition
    - Long-term strategic vision
    - Entrepreneurial opportunity identification
    """
    def __init__(self, domain: str = "vision_innovation", config: Dict[str, Any] = None):
        super().__init__("Founder", domain, config)

    def _define_domain_expertise(self) -> List[str]:
        return [
            "vision_setting",
            "innovation_strategy",
            "entrepreneurial_thinking",
            "culture_building",
            "opportunity_identification",
            "creative_problem_solving",
            "market_disruption"
        ]
