from .business_agent import BusinessAgent
from typing import Dict, Any, List

class InvestorAgent(BusinessAgent):
    """
    Investor - Investment analysis and funding strategy
    Responsibilities:
    - Investment opportunity analysis
    - Funding strategy and capital raising
    - Financial performance evaluation
    - Growth strategy assessment
    - Exit strategy planning
    """
    def __init__(self, domain: str = "investment_strategy", config: Dict[str, Any] = None):
        super().__init__("Investor", domain, config)

    def _define_domain_expertise(self) -> List[str]:
        return [
            "investment_analysis",
            "valuation_methods",
            "market_assessment",
            "growth_strategy",
            "financial_modeling",
            "risk_evaluation",
            "exit_planning"
        ]
