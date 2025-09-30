

# Import LeadershipAgent from RealmOfAgents
from RealmOfAgents.LeadershipAgent.LeadershipAgent import LeadershipAgent

"""
Minimal Agent Base Classes for BusinessInfinity MVP
Replaces the missing RealmOfAgents dependency with simplified local implementations
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentManager:
    """Simple agent manager for MVP"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default C-Suite and Founder agents"""
        default_agents = [
            ("ceo", "Chief Executive Officer", "CEO", "Executive Leadership"),
            ("cfo", "Chief Financial Officer", "CFO", "Finance"),
            ("cto", "Chief Technology Officer", "CTO", "Technology"),
            ("cmo", "Chief Marketing Officer", "CMO", "Marketing"),
            ("coo", "Chief Operating Officer", "COO", "Operations"),
            ("chro", "Chief Human Resources Officer", "CHRO", "Human Resources"),
            ("founder", "Founder", "Founder", "Entrepreneurship"),
        ]
        
        for agent_id, name, role, domain in default_agents:
            agent = LeadershipAgent(agent_id, name, role, domain)
            self.agents[agent_id] = agent
            
    def get_agent(self, agent_id: str) -> Optional[LeadershipAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id.lower())
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        return [agent.get_profile() for agent in self.agents.values()]
    
    async def ask_agent(self, agent_id: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Ask an agent a question"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
            
        try:
            response = await agent.process_message(message, context)
            return response
        except Exception as e:
            logger.error(f"Error asking agent {agent_id}: {e}")
            return None
    
    def get_agent_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent profile"""
        agent = self.get_agent(agent_id)
        return agent.get_profile() if agent else None


# Global agent manager instance
agent_manager = AgentManager()