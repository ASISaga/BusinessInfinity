"""
Business Infinity - Enterprise Business Application

REFACTORED: Now uses runtime abstractions with fallback to AOS

This module provides the main Business Infinity application built on top of the
Agent Operating System (AOS). It focuses purely on business logic, workflows,
and business-specific agent orchestration while leveraging runtime and AOS for all
infrastructure needs.

Enhanced with Covenant-Based Compliance for the Global Boardroom Network.

Architecture:
- BusinessInfinity: Main business application orchestrator
- BusinessAgents: Business-specific agents extending AOS LeadershipAgent
- Business Workflows: Strategic decision-making and operational processes
- Business Analytics: KPIs, metrics, and performance tracking
- Business Integration: External system connections via MCP
- Covenant Management: Compliance and governance for global network participation
- LinkedIn Verification: Enterprise identity verification and trust
- Peer Recognition: Network validation and compliance badges
"""

# Business-Specific Agent Implementations (merged from BusinessAgents.py)
"""
Business-Specific Agent Implementations

This module provides business-specific agent implementations that extend
AOS LeadershipAgent with business intelligence and domain expertise.
These agents integrate with Business Infinity workflows and provide
specialized business capabilities built on AOS foundation.
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from BusinessAgent import BusinessAgent
from .agents.chief_technology_officer import ChiefTechnologyOfficer
from .founder_agent import FounderAgent
from .investor_agent import InvestorAgent

# Try to import from runtime first
try:
    from runtime import RuntimeConfig, IStorageProvider, IMessagingProvider
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False

# Import AOS and UnifiedStorageManager
try:
    from AgentOperatingSystem import AgentOperatingSystem
    from AgentOperatingSystem.storage.manager import UnifiedStorageManager
    from AgentOperatingSystem.environment import UnifiedEnvManager
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    AgentOperatingSystem = None
    UnifiedStorageManager = None
    UnifiedEnvManager = None

# Modular managers
from config.business_infinity_config import BusinessInfinityConfig
from agents.business_agent_manager import BusinessAgentManager
from workflows.business_workflow_manager import BusinessWorkflowManager
from workflows.business_workflows import BusinessWorkflowEngine, WorkflowStatus
from network.business_covenant_manager import BusinessCovenantManager
from conversations.business_conversation_manager import BusinessConversationManager
from analytics.business_analytics_manager import BusinessAnalyticsManager
from analytics.business_analytics import BusinessAnalyticsEngine, BusinessMetric, MetricType


"""
Business Infinity - Enterprise Business Application

This module provides the main Business Infinity application built on top of the
Agent Operating System (AOS). It focuses purely on business logic, workflows,
and business-specific agent orchestration while leveraging AOS for all
infrastructure needs.

Enhanced with Covenant-Based Compliance for the Global Boardroom Network.

Architecture:
- BusinessInfinity: Main business application orchestrator
- BusinessAgents: Business-specific agents extending AOS LeadershipAgent
- Business Workflows: Strategic decision-making and operational processes
- Business Analytics: KPIs, metrics, and performance tracking
- Business Integration: External system connections via MCP
- Covenant Management: Compliance and governance for global network participation
- LinkedIn Verification: Enterprise identity verification and trust
- Peer Recognition: Network validation and compliance badges
"""





# BusinessInfinityConfig is now responsible for all configuration logic. See business_infinity_config.py.


class BusinessInfinity:
    """
    Business Infinity - Enterprise Business Application
    
    Orchestrates C-Suite agents, strategic decision-making, business operations, and compliance using modular managers.
    Uses runtime abstractions with fallback to AOS.
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        # Background process tasks
        self._strategic_planning_task = None
        self._performance_monitoring_task = None
        self._autonomous_boardroom_task = None
        
        # MCP Servers registry (metadata and endpoints) loaded from JSON file
        mcp_servers_path = os.path.join(os.path.dirname(__file__), "mcp_servers.json")
        try:
            with open(mcp_servers_path, "r", encoding="utf-8") as f:
                self.mcp_servers = json.load(f)
        except FileNotFoundError:
            self.mcp_servers = {}
            
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AOS as the foundation if available
        if AOS_AVAILABLE:
            self.aos = AgentOperatingSystem(getattr(self.config, 'aos_config', None))
            # Initialize unified storage manager
            self.storage_manager = UnifiedStorageManager() if UnifiedStorageManager else None
            # Initialize unified environment manager
            self.env_manager = UnifiedEnvManager() if UnifiedEnvManager else None
        else:
            self.aos = None
            self.storage_manager = None
            self.env_manager = None
            
        # Initialize MCP Service Bus Client
        if self.env_manager:
            servicebus_conn_str = self.env_manager.get_azure_connection_string("servicebus")
            servicebus_topic = self.env_manager.get("SERVICEBUS_TOPIC", "mcp-topic")
            servicebus_subscription = self.env_manager.get("SERVICEBUS_SUBSCRIPTION", None)
            try:
                from RealmOfAgents.AgentOperatingSystem.mcp_servicebus_client import MCPServiceBusClient
                self.mcp_servicebus_client = MCPServiceBusClient(
                    servicebus_conn_str,
                    servicebus_topic,
                    servicebus_subscription
                )
            except ImportError:
                self.mcp_servicebus_client = None
                self.logger.warning("MCPServiceBusClient could not be imported. Service Bus integration is disabled.")
        else:
            self.mcp_servicebus_client = None
            
        # Initialize managers (delegating logic to them, pass aos if needed)
        self.agent_manager = BusinessAgentManager(self.config, self.logger)
        self.workflow_manager = BusinessWorkflowManager(self.config, self.logger)
        self.analytics_manager = BusinessAnalyticsManager(self.config, self.logger)
        self.covenant_manager = BusinessCovenantManager(self.config, self.logger)
        self.conversation_manager = BusinessConversationManager(self.config, self.logger)
        
        # Business state
        self.business_context = self.agent_manager.get_business_context()
        
        # Async initialization
        self._initialize_task = asyncio.create_task(self._initialize())

    def list_mcp_servers(self) -> dict:
        """Return metadata and endpoints for all registered MCP servers."""
        return self.mcp_servers
    
    async def _initialize(self):
        try:
            self.logger.info("Initializing Business Infinity application...")
            # Start AOS infrastructure if available
            if self.aos:
                await self.aos.start()
            # Delegate initialization to managers
            await self.agent_manager.initialize()
            await self.workflow_manager.initialize()
            await self.analytics_manager.initialize()
            await self.covenant_manager.initialize()
            # Start background loops
            self._strategic_planning_task = asyncio.create_task(self._strategic_planning_loop())
            self._performance_monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
            self._autonomous_boardroom_task = asyncio.create_task(self._autonomous_boardroom_loop())
            self.business_context["status"] = "operational"
            self.business_context["initialized_at"] = datetime.utcnow()
            self.logger.info("Business Infinity application initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Infinity: {e}")
            self.business_context["status"] = "error"
            self.business_context["error"] = str(e)
            raise

    async def _strategic_planning_loop(self):
        """Background loop for strategic planning."""
        while True:
            try:
                # TODO: Implement strategic planning logic
                await asyncio.sleep(60)  # Run every 60 seconds
            except Exception as e:
                self.logger.error(f"Strategic planning loop error: {e}")
                await asyncio.sleep(10)

    async def _performance_monitoring_loop(self):
        """Background loop for performance monitoring."""
        while True:
            try:
                # TODO: Implement performance monitoring logic
                await asyncio.sleep(60)  # Run every 60 seconds
            except Exception as e:
                self.logger.error(f"Performance monitoring loop error: {e}")
                await asyncio.sleep(10)

    async def _autonomous_boardroom_loop(self):
        """Background loop for autonomous boardroom operations."""
        while True:
            try:
                # TODO: Implement autonomous boardroom logic
                await asyncio.sleep(60)  # Run every 60 seconds
            except Exception as e:
                self.logger.error(f"Autonomous boardroom loop error: {e}")
                await asyncio.sleep(10)
    
    # Infrastructure initialization is now handled by the relevant manager(s).
    
    # Covenant/network management initialization is now handled by BusinessCovenantManager.
    
    # Business engine initialization is now handled by the respective manager classes.
    
    # Business agent initialization is now handled by BusinessAgentManager.
    
    # Enterprise covenant initialization is now handled by BusinessCovenantManager.
    
    # Covenant creation/loading is now handled by BusinessCovenantManager.
    
    # Ongoing business processes are now managed by the relevant manager classes.
    
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.workflow_manager.make_strategic_decision(decision_context)

    async def execute_business_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return await self.workflow_manager.execute_business_workflow(workflow_name, parameters)

    async def get_business_analytics(self) -> Dict[str, Any]:
        return await self.analytics_manager.get_business_analytics()

    def _determine_relevant_agents(self, decision_context: Dict[str, Any]) -> List[str]:
        return self.agent_manager.determine_relevant_agents(decision_context)
    
    # Strategic planning, performance monitoring, and boardroom loops are now handled by the relevant manager classes.
    
    # Covenant Management API Methods
    async def publish_covenant(self) -> bool:
        return await self.covenant_manager.publish_covenant()

    async def get_covenant_status(self) -> Dict[str, Any]:
        return await self.covenant_manager.get_covenant_status()

    async def propose_covenant_amendment(self, changes: Dict[str, Any], rationale: str, proposer_agent: str = "ceo") -> Optional[str]:
        return await self.covenant_manager.propose_covenant_amendment(changes, rationale, proposer_agent)

    async def vote_on_amendment(self, amendment_id: str, agent_id: str, vote: str, rationale: str = None) -> bool:
        return await self.covenant_manager.vote_on_amendment(amendment_id, agent_id, vote, rationale)

    async def discover_peer_boardrooms(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await self.covenant_manager.discover_peer_boardrooms(criteria)

    async def get_compliance_statistics(self) -> Dict[str, Any]:
        return await self.covenant_manager.get_compliance_statistics()
    
    async def shutdown(self):
        """Gracefully shutdown Business Infinity"""
        try:
            self.logger.info("Shutting down Business Infinity...")
            await self.agent_manager.shutdown()
            await self.workflow_manager.shutdown()
            await self.analytics_manager.shutdown()
            await self.covenant_manager.shutdown()
            # Shutdown AOS infrastructure
            await self.aos.stop()
            self.business_context["status"] = "shutdown"
            self.logger.info("Business Infinity shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Factory functions for easy instantiation
def create_business_infinity(config: BusinessInfinityConfig = None) -> BusinessInfinity:
    """Create and initialize Business Infinity application"""
    return BusinessInfinity(config)

business_infinity = None

def get_business_infinity() -> BusinessInfinity:
    global business_infinity
    if business_infinity is None:
        business_infinity = create_business_infinity()
    return business_infinity

def create_default_business_infinity() -> BusinessInfinity:
    """Create Business Infinity with default configuration"""
    return BusinessInfinity(BusinessInfinityConfig())

# Export main classes and functions for external use
__all__ = [
    # Core Business Application
    "BusinessInfinity",
    "BusinessInfinityConfig", 
    "create_business_infinity",
    "create_default_business_infinity",
    # Business Agents
    "BusinessAgent",
    "ChiefExecutiveOfficer",
    "ChiefFinancialOfficer",
    "ChiefTechnologyOfficer",
    "FounderAgent",
    "InvestorAgent",
    # Business Engines
    "BusinessWorkflowEngine",
    "BusinessAnalyticsEngine",
    # Supporting Classes
    "WorkflowStatus",
    "BusinessMetric", 
    "MetricType"
]
