"""
Business Agent Manager

Manages the lifecycle and coordination of business agents
using the AOS infrastructure.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import Agent

from ChiefExecutiveOfficer import ChiefExecutiveOfficer
from ChiefTechnologyOfficer import ChiefTechnologyOfficer
from FounderAgent import FounderAgent
from ..core.config import BusinessInfinityConfig


class BusinessAgentManager:
    """
    Manages business agents and their coordination using AOS.
    
    Provides:
    - Agent lifecycle management
    - Business context coordination
    - Performance monitoring
    - Decision orchestration
    """
    
    def __init__(self, aos: AgentOperatingSystem, config: BusinessInfinityConfig, logger: logging.Logger):
        """Initialize Business Agent Manager."""
        self.aos = aos
        self.config = config
        self.logger = logger
        
        # Agent registry
        self.agents: Dict[str, Agent] = {}
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        
        # Business context
        self.business_context = {
            "company_name": config.company_name,
            "company_domain": config.company_domain,
            "business_model": config.business_model,
            "industry": config.industry,
            "status": "initializing"
        }
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        self.collaboration_network: Dict[str, List[str]] = {}
        
        # Background tasks
        self._monitoring_task = None
        self._coordination_task = None

    async def initialize(self):
        """Initialize business agents."""
        try:
            self.logger.info("Initializing Business Agent Manager...")
            
            # Ensure AOS has required attributes
            if not hasattr(self.aos, 'register_agent'):
                self.aos.register_agent = self._mock_register_agent
            if not hasattr(self.aos, 'unregister_agent'):
                self.aos.unregister_agent = self._mock_unregister_agent
            if not hasattr(self.aos, 'storage_manager'):
                self.aos.storage_manager = self._create_mock_storage_manager()
            
            # Create and register agents based on configuration
            await self._create_business_agents()
            
            # Start agent coordination and monitoring
            await self._start_agent_coordination()
            
            # Start background tasks
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._coordination_task = asyncio.create_task(self._coordination_loop())
            
            self.business_context["status"] = "operational"
            self.business_context["agents_count"] = len(self.agents)
            self.business_context["initialized_at"] = datetime.utcnow()
            
            self.logger.info(f"Business Agent Manager initialized with {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Agent Manager: {e}")
            self.business_context["status"] = "error"
            self.business_context["error"] = str(e)
            raise

    async def _create_business_agents(self):
        """Create business agents based on configuration."""
        agent_config = {
            "company_context": self.business_context,
            "analytics_engine": None,  # Will be set later
            "workflow_engine": None    # Will be set later
        }
        
        # Create CEO if enabled
        if self.config.ceo_enabled:
            ceo = ChiefExecutiveOfficer(config=agent_config)
            await self.aos.register_agent(ceo)
            self.agents["ceo"] = ceo
            self.agent_configs["ceo"] = agent_config
            self.logger.info("CEO agent created and registered")
        
        # Create CTO if enabled
        if self.config.cto_enabled:
            cto = ChiefTechnologyOfficer(config=agent_config)
            await self.aos.register_agent(cto)
            self.agents["cto"] = cto
            self.agent_configs["cto"] = agent_config
            self.logger.info("CTO agent created and registered")
        
        # Create Founder if enabled
        if self.config.founder_enabled:
            founder = FounderAgent(config=agent_config)
            await self.aos.register_agent(founder)
            self.agents["founder"] = founder
            self.agent_configs["founder"] = agent_config
            self.logger.info("Founder agent created and registered")
        
        # TODO: Add other C-Suite agents (CFO, CMO, COO, CHRO)
        # For now, focusing on the core three

    async def _mock_register_agent(self, agent):
        """Mock agent registration for compatibility."""
        self.logger.info(f"Mock registering agent: {agent.agent_id}")
        return True

    async def _mock_unregister_agent(self, agent_id):
        """Mock agent unregistration for compatibility."""
        self.logger.info(f"Mock unregistering agent: {agent_id}")
        return True

    def _create_mock_storage_manager(self):
        """Create mock storage manager."""
        class MockStorageManager:
            async def store_data(self, path, data):
                pass
            async def load_data(self, path):
                return None
        return MockStorageManager()

    async def _start_agent_coordination(self):
        """Start coordination between agents."""
        # Set up collaboration networks
        for agent_id in self.agents.keys():
            self.collaboration_network[agent_id] = [
                other_id for other_id in self.agents.keys() 
                if other_id != agent_id
            ]
        
        # Initialize performance tracking
        for agent_id in self.agents.keys():
            self.agent_performance[agent_id] = {
                "decisions_made": 0,
                "analyses_completed": 0,
                "collaboration_score": 0.0,
                "performance_score": 0.0,
                "last_activity": datetime.utcnow()
            }

    async def _monitoring_loop(self):
        """Background monitoring of agent performance."""
        while True:
            try:
                await self._collect_agent_metrics()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Agent monitoring error: {e}")
                await asyncio.sleep(60)

    async def _coordination_loop(self):
        """Background coordination of agent activities."""
        while True:
            try:
                await self._coordinate_agent_activities()
                await asyncio.sleep(600)  # Every 10 minutes
            except Exception as e:
                self.logger.error(f"Agent coordination error: {e}")
                await asyncio.sleep(120)

    async def _collect_agent_metrics(self):
        """Collect performance metrics from agents."""
        for agent_id, agent in self.agents.items():
            try:
                if hasattr(agent, 'get_performance_summary'):
                    performance = await agent.get_performance_summary()
                    self.agent_performance[agent_id].update({
                        "performance_summary": performance,
                        "last_metrics_update": datetime.utcnow()
                    })
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for {agent_id}: {e}")

    async def _coordinate_agent_activities(self):
        """Coordinate activities between agents."""
        # This is a placeholder for more sophisticated coordination logic
        # In a full implementation, this would handle:
        # - Cross-agent decision coordination
        # - Resource allocation
        # - Priority management
        # - Conflict resolution
        pass

    async def get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": getattr(agent, 'role', 'unknown'),
                "status": agent.status,
                "performance": self.agent_performance.get(agent_id, {}),
                "collaboration_network": self.collaboration_network.get(agent_id, [])
            }
        return status

    async def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self.agents.keys())

    def determine_relevant_agents(self, decision_context: Dict[str, Any]) -> List[str]:
        """Determine which agents are relevant for a decision context."""
        relevant_agents = []
        
        # Get decision type and domain
        decision_type = decision_context.get("type", "general")
        domain = decision_context.get("domain", "general")
        impact_level = decision_context.get("impact_level", "medium")
        
        # CEO is always relevant for high-impact decisions
        if impact_level == "high" and "ceo" in self.agents:
            relevant_agents.append("ceo")
        
        # Technology-related decisions
        if domain in ["technology", "technical", "engineering", "security"] and "cto" in self.agents:
            relevant_agents.append("cto")
        
        # Innovation and vision-related decisions
        if domain in ["innovation", "vision", "culture", "strategy"] and "founder" in self.agents:
            relevant_agents.append("founder")
        
        # Strategic decisions involve multiple agents
        if decision_type == "strategic":
            for agent_id in ["ceo", "founder", "cto"]:
                if agent_id in self.agents and agent_id not in relevant_agents:
                    relevant_agents.append(agent_id)
        
        # Ensure at least one agent is relevant
        if not relevant_agents and self.agents:
            relevant_agents.append(list(self.agents.keys())[0])
        
        return relevant_agents

    async def run_autonomous_boardroom(self):
        """Run autonomous boardroom session."""
        if not self.config.enable_autonomous_boardroom:
            return
        
        try:
            self.logger.info("Running autonomous boardroom session...")
            
            # Gather insights from all agents
            boardroom_context = {
                "session_type": "autonomous_boardroom",
                "timestamp": datetime.utcnow().isoformat(),
                "participants": list(self.agents.keys())
            }
            
            agent_insights = {}
            for agent_id, agent in self.agents.items():
                if hasattr(agent, 'analyze_business_context'):
                    insights = await agent.analyze_business_context(boardroom_context)
                    agent_insights[agent_id] = insights
            
            # Coordinate cross-agent discussion
            boardroom_summary = {
                "session_id": f"boardroom_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "participants": list(self.agents.keys()),
                "insights": agent_insights,
                "key_decisions": [],
                "action_items": [],
                "next_session": "scheduled"
            }
            
            # Store boardroom session results
            await self._store_boardroom_session(boardroom_summary)
            
            self.logger.info("Autonomous boardroom session completed")
            
        except Exception as e:
            self.logger.error(f"Autonomous boardroom session failed: {e}")

    async def _store_boardroom_session(self, session_data: Dict[str, Any]):
        """Store boardroom session data."""
        # Use AOS storage manager to persist session
        try:
            await self.aos.storage_manager.store_data(
                f"boardroom_sessions/{session_data['session_id']}.json",
                session_data
            )
        except Exception as e:
            self.logger.error(f"Failed to store boardroom session: {e}")

    def get_business_context(self) -> Dict[str, Any]:
        """Get current business context."""
        return {
            **self.business_context,
            "agents": list(self.agents.keys()),
            "collaboration_network": self.collaboration_network,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown agent manager."""
        try:
            self.logger.info("Shutting down Business Agent Manager...")
            
            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
            if self._coordination_task:
                self._coordination_task.cancel()
            
            # Unregister agents from AOS
            for agent_id, agent in self.agents.items():
                try:
                    await self.aos.unregister_agent(agent.agent_id)
                except Exception as e:
                    self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            
            self.business_context["status"] = "shutdown"
            self.logger.info("Business Agent Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during agent manager shutdown: {e}")
            raise