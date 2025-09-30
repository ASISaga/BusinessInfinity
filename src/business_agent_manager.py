"""
BusinessAgentManager - Handles agent management for Business Infinity
"""
from typing import Dict, Any, List, Optional
import logging


class BusinessAgentManager:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.c_suite = {}
        self.founder = None
        self.investor = None
        self.mvp_manager = None
        self.business_context = {
            "company_name": getattr(config, "company_name", "Business Infinity Corp"),
            "industry": getattr(config, "industry", "Technology"),
            "stage": getattr(config, "business_stage", "growth"),
            "market_focus": getattr(config, "market_focus", "global"),
            "initialized_at": None,
            "status": "initializing"
        }

    async def initialize(self):
        # Initialize agents here (stub)
        self.logger.info("BusinessAgentManager initialized")
        self.business_context["status"] = "operational"

    async def shutdown(self):
        self.logger.info("BusinessAgentManager shutdown")

    def get_business_context(self):
        return self.business_context

    def determine_relevant_agents(self, decision_context):
        decision_type = decision_context.get("type", "general")
        if decision_type in ["funding", "investment", "valuation"]:
            return ["cfo", "founder", "investor"]
        elif decision_type in ["product", "technology", "innovation"]:
            return ["ceo", "cto", "founder"]
        elif decision_type in ["strategy", "vision", "market"]:
            return ["ceo", "founder", "investor"]
        elif decision_type in ["operations", "finance", "resources"]:
            return ["ceo", "cfo", "cto"]
        else:
            return ["ceo", "cfo", "cto"]

    def get_agent(self, role: str):
        if role in self.c_suite:
            return self.c_suite[role]
        if role == "Founder":
            return self.founder
        elif role == "Investor":
            return self.investor
        if self.mvp_manager:
            return self.mvp_manager.get_agent(role.lower())
        return None

    def list_agents(self) -> List[Dict[str, Any]]:
        agents = []
        for role, agent in self.c_suite.items():
            agents.append({"role": role, "type": "C-Suite", "status": "active" if agent else "inactive"})
        if self.founder:
            agents.append({"role": "Founder", "type": "Stakeholder", "status": "active"})
        if self.investor:
            agents.append({"role": "Investor", "type": "Stakeholder", "status": "active"})
        return agents

    async def ask_agent(self, role: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        agent = self.get_agent(role)
        if not agent:
            return f"Agent {role} not available"
        try:
            if hasattr(agent, 'process_message'):
                return await agent.process_message(message, context)
            else:
                return f"Agent {role} does not support message processing"
        except Exception as e:
            self.logger.error(f"Error asking agent {role}: {e}")
            return f"Error communicating with {role}: {e}"
