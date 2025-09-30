"""
BusinessAgentManager - Handles agent management for Business Infinity
"""
from typing import Dict, Any, List, Optional
import logging

class BusinessAgentManager:
    def __init__(self, c_suite, founder, investor, mvp_manager=None):
        self.c_suite = c_suite
        self.founder = founder
        self.investor = investor
        self.mvp_manager = mvp_manager
        self.logger = logging.getLogger(__name__)

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
