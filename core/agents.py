"""
Unified Agent Management System for Business Infinity

This module provides the core agent management system that integrates with
the new C-Suite agents architecture. It provides a unified interface for
managing and orchestrating all business-specific agents.

The actual agent implementations are in the /agents/ module and inherit
from LeadershipAgent in AOS (Agent Operating System).
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union


# Import the new C-Suite agents directly from RealmOfAgents
try:
    from RealmOfAgents.CEO.ChiefExecutiveOfficer import ChiefExecutiveOfficer
    from RealmOfAgents.CFO.ChiefFinancialOfficer import ChiefFinancialOfficer
    from RealmOfAgents.CMO.ChiefMarketingOfficer import ChiefMarketingOfficer
    from RealmOfAgents.COO.ChiefOperatingOfficer import ChiefOperatingOfficer
    from RealmOfAgents.CTO.ChiefTechnologyOfficer import ChiefTechnologyOfficer
    from RealmOfAgents.CHRO.ChiefHumanResourcesOfficer import ChiefHumanResourcesOfficer
    from RealmOfAgents.Founder.FounderAgent import FounderAgent
    from RealmOfAgents.Investor.InvestorAgent import InvestorAgent
    AGENT_REGISTRY = {
        "CEO": ChiefExecutiveOfficer,
        "CFO": ChiefFinancialOfficer,
        "CMO": ChiefMarketingOfficer,
        "COO": ChiefOperatingOfficer,
        "CTO": ChiefTechnologyOfficer,
        "CHRO": ChiefHumanResourcesOfficer,
        "Founder": FounderAgent,
        "Investor": InvestorAgent
    }
    AGENTS_AVAILABLE = True
except ImportError:
    AGENT_REGISTRY = {}
    AGENTS_AVAILABLE = False

# Optional imports with fallbacks
try:
    from semantic_kernel import Kernel
    from semantic_kernel.contents import ChatHistory
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False

try:
    from chromadb import Client as ChromaClient
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


# Import environment manager from AOS
try:
    from RealmOfAgents.AgentOperatingSystem.environment import UnifiedEnvManager as env_manager
except ImportError:
    env_manager = None


logger = logging.getLogger(__name__)


class UnifiedAgentManager:
    """
    Unified agent management system that provides:
    - C-Suite agent instantiation and management
    - Agent orchestration and coordination
    - Backward compatibility with legacy systems
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the unified agent manager.
        
        Args:
            config: Configuration dictionary for agents
        """
        self.config = config or {}
        self.agents: Dict[str, Any] = {}
        self.initialized = False
        
        if AGENTS_AVAILABLE:
            self._initialize_agents()
        else:
            logger.warning("Agent modules not available - running in compatibility mode")
    
    def _initialize_agents(self):
        """Initialize all available C-Suite agents."""
        try:
            for agent_name, agent_class in AGENT_REGISTRY.items():
                agent_config = self.config.get(agent_name.lower(), {})
                self.agents[agent_name] = agent_class(config=agent_config)
                logger.info(f"Initialized {agent_name} agent")
            
            self.initialized = True
            logger.info(f"Successfully initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            self.initialized = False
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get a specific agent by name.
        
        Args:
            agent_name: Name of the agent (CEO, CFO, etc.)
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name.upper())
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all initialized agents."""
        return self.agents.copy()
    
    def get_agent_profiles(self) -> str:
        """
        Get JSON string of all agent profiles for backward compatibility.
        
        Returns:
            JSON string of agent profiles
        """
        if not self.initialized:
            return "[]"
        
        profiles = []
        for agent_name, agent in self.agents.items():
            try:
                # Try to get profile from agent if it has the method
                if hasattr(agent, 'get_profile'):
                    profile = agent.get_profile()
                else:
                    # Create basic profile
                    profile = {
                        "agentId": agent_name.lower(),
                        "name": agent_name,
                        "role": getattr(agent, 'role', agent_name),
                        "leadership_style": getattr(agent, 'leadership_style', 'strategic'),
                        "active": True
                    }
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Failed to get profile for {agent_name}: {e}")
                
        return json.dumps(profiles, indent=2)
    
    async def execute_agent_task(self, agent_name: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task with a specific agent.
        
        Args:
            agent_name: Name of the agent
            task: Task to execute
            context: Additional context for the task
            
        Returns:
            Result of the task execution
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        try:
            # Map task to appropriate agent method
            task_method = self._map_task_to_method(task)
            
            if hasattr(agent, task_method):
                method = getattr(agent, task_method)
                if asyncio.iscoroutinefunction(method):
                    result = await method(context or {})
                else:
                    result = method(context or {})
                return {"success": True, "result": result}
            else:
                # Try generic decision making if available
                if hasattr(agent, 'make_decision'):
                    if asyncio.iscoroutinefunction(agent.make_decision):
                        result = await agent.make_decision(task, context or {})
                    else:
                        result = agent.make_decision(task, context or {})
                    return {"success": True, "result": result}
                else:
                    return {"error": f"Agent {agent_name} does not support task: {task}"}
                    
        except Exception as e:
            logger.error(f"Failed to execute task {task} with agent {agent_name}: {e}")
            return {"error": str(e)}
    
    def _map_task_to_method(self, task: str) -> str:
        """
        Map a task description to an agent method name.
        
        Args:
            task: Task description
            
        Returns:
            Method name to call
        """
        # Simple mapping - can be enhanced with more sophisticated logic
        task_lower = task.lower()
        
        if "strategy" in task_lower:
            return "develop_strategy"
        elif "analysis" in task_lower or "analyze" in task_lower:
            return "conduct_analysis"
        elif "plan" in task_lower:
            return "create_plan"
        elif "budget" in task_lower:
            return "manage_budget"
        elif "performance" in task_lower:
            return "evaluate_performance"
        elif "decision" in task_lower:
            return "make_decision"
        else:
            return "execute_task"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "initialized": self.initialized,
            "agent_count": len(self.agents),
            "agents": list(self.agents.keys()) if self.initialized else [],
            "capabilities": {
                "semantic_kernel": SEMANTIC_KERNEL_AVAILABLE,
                "chromadb": CHROMADB_AVAILABLE,
                "c_suite_agents": AGENTS_AVAILABLE
            }
        }


# Create global agent manager instance
agent_manager = UnifiedAgentManager()


# Legacy compatibility classes and functions
class BaseAgent:
    """Legacy base agent class for backward compatibility."""
    
    def __init__(self, agent_id: str, purpose: str, interval: int = 5):
        self.agent_id = agent_id
        self.purpose = purpose
        self.interval = interval
        self.active = False
        
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        """Legacy execute task method."""
        return f"Legacy agent {self.agent_id} processing: {input_data}"
    
    def get_profile(self) -> Dict[str, Any]:
        """Get agent profile information."""
        return {
            "agentId": self.agent_id,
            "name": self.agent_id.replace("_", " ").title(),
            "purpose": self.purpose,
            "interval": self.interval,
            "active": self.active
        }


# Legacy agent classes for backward compatibility
class OperationsAgent(BaseAgent):
    """Legacy Operations agent - replaced by ChiefOperatingOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Operations Agent - use ChiefOperatingOfficer instead"
        super().__init__("operations", purpose, interval)


class FinanceAgent(BaseAgent):
    """Legacy Finance agent - replaced by ChiefFinancialOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Finance Agent - use ChiefFinancialOfficer instead"
        super().__init__("finance", purpose, interval)


class MarketingAgent(BaseAgent):
    """Marketing and customer engagement agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Marketing Strategy: Develop and execute marketing campaigns.
        Customer Analytics: Analyze customer behavior and market trends.
        Brand Management: Maintain brand consistency and reputation.
        """
        super().__init__("marketing", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Marketing Agent processing: {input_data}"


class HRAgent(BaseAgent):
    """Human Resources agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Talent Management: Recruit, develop, and retain talent.
        Employee Relations: Handle employee concerns and engagement.
        Policy Management: Maintain HR policies and compliance.
        """
        super().__init__("hr", purpose, interval)


# Additional legacy agent classes for backward compatibility
class MarketingAgent(BaseAgent):
    """Legacy Marketing agent - replaced by ChiefMarketingOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Marketing Agent - use ChiefMarketingOfficer instead"
        super().__init__("marketing", purpose, interval)


class HRAgent(BaseAgent):
    """Legacy HR agent - replaced by ChiefHumanResourcesOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy HR Agent - use ChiefHumanResourcesOfficer instead"
        super().__init__("hr", purpose, interval)


class AccountsAgent(BaseAgent):
    """Legacy Accounts agent - replaced by ChiefFinancialOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Accounts Agent - use ChiefFinancialOfficer instead"
        super().__init__("accounts", purpose, interval)


class QualityAgent(BaseAgent):
    """Legacy Quality agent - replaced by ChiefOperatingOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Quality Agent - use ChiefOperatingOfficer instead"
        super().__init__("quality", purpose, interval)


class PurchaseAgent(BaseAgent):
    """Legacy Purchase agent - replaced by ChiefOperatingOfficer."""
    
    def __init__(self, interval: int = 5):
        purpose = "Legacy Purchase Agent - use ChiefOperatingOfficer instead"
        super().__init__("purchase", purpose, interval)


# Export for backward compatibility
def get_default_agent_cfg():
    """Return default agent configuration for backward compatibility."""
    return {
        "ceo": {"instructions": "Use ChiefExecutiveOfficer agent instead"},
        "cfo": {"instructions": "Use ChiefFinancialOfficer agent instead"},
        "cmo": {"instructions": "Use ChiefMarketingOfficer agent instead"},
        "coo": {"instructions": "Use ChiefOperatingOfficer agent instead"},
        "cto": {"instructions": "Use ChiefTechnologyOfficer agent instead"},
        "chro": {"instructions": "Use ChiefHumanResourcesOfficer agent instead"}
    }


__all__ = [
    'UnifiedAgentManager',
    'agent_manager',
    'BaseAgent',
    'OperationsAgent',
    'FinanceAgent',
    'MarketingAgent',
    'HRAgent',
    'AccountsAgent',
    'QualityAgent',
    'PurchaseAgent',
    'get_default_agent_cfg'
]