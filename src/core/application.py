"""
Business Infinity - Enterprise Business Application

This module provides the main Business Infinity application built on top of the
Agent Operating System (AOS). It focuses purely on business logic, workflows,
and business-specific agent orchestration while leveraging AOS for all
infrastructure needs.

Enhanced with Covenant-Based Compliance for the Global Boardroom Network.

Architecture:
- BusinessInfinity: Main business application orchestrator
- BusinessAgents: Business-specific agents extending AOS Agent
- Business Workflows: Strategic decision-making and operational processes
- Business Analytics: KPIs, metrics, and performance tracking
- Business Integration: External system connections via MCP
- Covenant Management: Compliance and governance for global network participation
- LinkedIn Verification: Enterprise identity verification and trust
- Peer Recognition: Network validation and compliance badges
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import AOS from existing structure (will be updated when AOS is fully refactored)

from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.core.config import AOSConfig
from AgentOperatingSystem.storage import StorageManager
from AgentOperatingSystem.environment import EnvironmentManager

from .config import BusinessInfinityConfig
from .covenant_manager import BusinessCovenantManager
from .conversation_manager import BusinessConversationManager
from ..agents.manager import BusinessAgentManager
from ..workflows.manager import BusinessWorkflowManager
from ..analytics.manager import BusinessAnalyticsManager


class BusinessInfinity:
    """
    Business Infinity - Enterprise Business Application
    
    Orchestrates C-Suite agents, strategic decision-making, business operations, 
    and compliance using the new AOS infrastructure and modular managers.
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        """Initialize Business Infinity with configuration."""
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AOS as the foundation
        try:
            # Try to use AOS with configuration if available
            aos_config = AOSConfig(
                agent_config=self.config.agent_config,
                messaging_config=self.config.messaging_config,
                storage_config=self.config.storage_config,
                monitoring_config=self.config.monitoring_config,
                ml_config=self.config.ml_config,
                auth_config=self.config.auth_config,
                environment_config=self.config.environment_config,
                mcp_config=self.config.mcp_config
            )
            self.aos = AgentOperatingSystem(aos_config)
        except:
            # Fall back to simple AOS initialization
            self.aos = AgentOperatingSystem()
        
        # Initialize storage and environment managers
        try:
            self.storage_manager = self.aos.storage_manager
            self.env_manager = self.aos.environment_manager
        except AttributeError:
            # Create placeholder managers if not available
            self.storage_manager = StorageManager()
            self.env_manager = EnvironmentManager()
        
        # Load MCP Servers registry (metadata and endpoints) from JSON file
        mcp_servers_path = os.path.join(os.path.dirname(__file__), "../../mcp_servers.json")
        try:
            with open(mcp_servers_path, "r", encoding="utf-8") as f:
                self.mcp_servers = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"MCP servers config not found at {mcp_servers_path}")
            self.mcp_servers = {}
        
        # Initialize business managers (delegating logic to them)
        self.agent_manager = BusinessAgentManager(self.aos, self.config, self.logger)
        self.workflow_manager = BusinessWorkflowManager(self.aos, self.config, self.logger)
        self.analytics_manager = BusinessAnalyticsManager(self.aos, self.config, self.logger)
        self.covenant_manager = BusinessCovenantManager(self.aos, self.config, self.logger)
        self.conversation_manager = BusinessConversationManager(self.aos, self.config, self.logger)
        
        # Business state
        self.business_context = {
            "status": "initializing",
            "created_at": datetime.utcnow(),
            "version": "2.0",  # New AOS-based version
            "aos_version": self.aos.version if hasattr(self.aos, 'version') else "1.0"
        }
        
        # Background process tasks
        self._strategic_planning_task = None
        self._performance_monitoring_task = None
        self._autonomous_boardroom_task = None
        
        # Async initialization
        self._initialize_task = asyncio.create_task(self._initialize())

    def list_mcp_servers(self) -> dict:
        """Return metadata and endpoints for all registered MCP servers."""
        return self.mcp_servers
    
    async def _initialize(self):
        """Initialize Business Infinity application with AOS."""
        try:
            self.logger.info("Initializing Business Infinity application...")
            
            # Start AOS infrastructure
            await self.aos.start()
            
            # Delegate initialization to managers
            await self.agent_manager.initialize()
            await self.workflow_manager.initialize()
            await self.analytics_manager.initialize()
            await self.covenant_manager.initialize()
            await self.conversation_manager.initialize()
            
            # Start background loops
            self._strategic_planning_task = asyncio.create_task(self._strategic_planning_loop())
            self._performance_monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
            self._autonomous_boardroom_task = asyncio.create_task(self._autonomous_boardroom_loop())
            
            # Update business context
            self.business_context.update({
                "status": "operational",
                "initialized_at": datetime.utcnow(),
                "agents_count": len(await self.agent_manager.list_agents()),
                "workflows_active": await self.workflow_manager.get_active_workflows_count(),
                "aos_status": "running"
            })
            
            self.logger.info("Business Infinity application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Infinity: {e}")
            self.business_context.update({
                "status": "error",
                "error": str(e),
                "error_at": datetime.utcnow()
            })
            raise

    async def _strategic_planning_loop(self):
        """Background loop for strategic planning."""
        while True:
            try:
                await self.workflow_manager.run_strategic_planning()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Strategic planning loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def _performance_monitoring_loop(self):
        """Background loop for performance monitoring."""
        while True:
            try:
                await self.analytics_manager.collect_performance_metrics()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                self.logger.error(f"Performance monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _autonomous_boardroom_loop(self):
        """Background loop for autonomous boardroom operations."""
        while True:
            try:
                await self.agent_manager.run_autonomous_boardroom()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                self.logger.error(f"Autonomous boardroom loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    # Business Operations API
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a strategic business decision using workflow engine."""
        return await self.workflow_manager.make_strategic_decision(decision_context)

    async def execute_business_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a business workflow."""
        return await self.workflow_manager.execute_business_workflow(workflow_name, parameters)

    async def get_business_analytics(self) -> Dict[str, Any]:
        """Get comprehensive business analytics."""
        return await self.analytics_manager.get_business_analytics()

    async def get_business_context(self) -> Dict[str, Any]:
        """Get current business context and status."""
        # Update with real-time data
        self.business_context.update({
            "last_updated": datetime.utcnow(),
            "agents_status": await self.agent_manager.get_agents_status(),
            "workflows_status": await self.workflow_manager.get_workflows_status(),
            "analytics_summary": await self.analytics_manager.get_summary(),
            "aos_metrics": await self.aos.get_system_metrics() if hasattr(self.aos, 'get_system_metrics') else {}
        })
        return self.business_context

    def determine_relevant_agents(self, decision_context: Dict[str, Any]) -> List[str]:
        """Determine which agents are relevant for a decision context."""
        return self.agent_manager.determine_relevant_agents(decision_context)
    
    # Covenant Management API Methods
    async def publish_covenant(self) -> bool:
        """Publish the business covenant."""
        return await self.covenant_manager.publish_covenant()

    async def get_covenant_status(self) -> Dict[str, Any]:
        """Get current covenant status."""
        return await self.covenant_manager.get_covenant_status()

    async def propose_covenant_amendment(self, changes: Dict[str, Any], rationale: str, 
                                       proposer_agent: str = "ceo") -> Optional[str]:
        """Propose an amendment to the covenant."""
        return await self.covenant_manager.propose_covenant_amendment(changes, rationale, proposer_agent)

    async def vote_on_amendment(self, amendment_id: str, agent_id: str, vote: str, 
                              rationale: str = None) -> bool:
        """Vote on a covenant amendment."""
        return await self.covenant_manager.vote_on_amendment(amendment_id, agent_id, vote, rationale)

    async def discover_peer_boardrooms(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Discover peer boardrooms."""
        return await self.covenant_manager.discover_peer_boardrooms(criteria)

    async def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get compliance statistics."""
        return await self.covenant_manager.get_compliance_statistics()
    
    async def shutdown(self):
        """Gracefully shutdown Business Infinity."""
        try:
            self.logger.info("Shutting down Business Infinity...")
            
            # Cancel background tasks
            if self._strategic_planning_task:
                self._strategic_planning_task.cancel()
            if self._performance_monitoring_task:
                self._performance_monitoring_task.cancel()
            if self._autonomous_boardroom_task:
                self._autonomous_boardroom_task.cancel()
            
            # Shutdown managers
            await self.agent_manager.shutdown()
            await self.workflow_manager.shutdown()
            await self.analytics_manager.shutdown()
            await self.covenant_manager.shutdown()
            await self.conversation_manager.shutdown()
            
            # Shutdown AOS infrastructure
            await self.aos.stop()
            
            self.business_context.update({
                "status": "shutdown",
                "shutdown_at": datetime.utcnow()
            })
            
            self.logger.info("Business Infinity shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise


# Factory functions for easy instantiation
def create_business_infinity(config: BusinessInfinityConfig = None) -> BusinessInfinity:
    """Create and initialize Business Infinity application."""
    return BusinessInfinity(config)


# Global instance management
_business_infinity_instance = None


def get_business_infinity() -> BusinessInfinity:
    """Get or create the global Business Infinity instance."""
    global _business_infinity_instance
    if _business_infinity_instance is None:
        _business_infinity_instance = create_business_infinity()
    return _business_infinity_instance


def create_default_business_infinity() -> BusinessInfinity:
    """Create Business Infinity with default configuration."""
    return BusinessInfinity(BusinessInfinityConfig())