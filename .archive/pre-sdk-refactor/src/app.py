"""
BusinessInfinity Application

This is the main BusinessInfinity application module that provides:
- Core business orchestration
- Agent coordination
- Workflow management
- Analytics and monitoring

Communicates with AgentOperatingSystem over Azure Service Bus.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from runtime import IMessagingProvider, IStorageProvider

from .config import BusinessInfinityConfig

# Import AOS Service Bus client (preferred for distributed deployment)
try:
    from .aos_client import (
        AOSServiceBusClient,
        get_aos_client,
        initialize_aos_client,
    )
    AOS_CLIENT_AVAILABLE = True
except ImportError:
    AOS_CLIENT_AVAILABLE = False
    AOSServiceBusClient = None

# Try importing AOS components (fallback for local development)
try:
    from AgentOperatingSystem import AgentOperatingSystem
    from AgentOperatingSystem.environment import UnifiedEnvManager
    from AgentOperatingSystem.storage.manager import UnifiedStorageManager

    AOS_DIRECT_AVAILABLE = True
except ImportError:
    AOS_DIRECT_AVAILABLE = False
    AgentOperatingSystem = None
    UnifiedStorageManager = None
    UnifiedEnvManager = None

# Try importing external agent packages
try:
    from BusinessAgent import BusinessAgent

    BUSINESS_AGENT_AVAILABLE = True
except ImportError:
    BUSINESS_AGENT_AVAILABLE = False
    BusinessAgent = None


@dataclass
class AgentInfo:
    """Information about a business agent."""

    id: str
    name: str
    role: str
    status: str = "available"
    capabilities: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None


@dataclass
class WorkflowInfo:
    """Information about a business workflow."""

    id: str
    name: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    progress: float = 0.0


class BusinessInfinity:
    """
    BusinessInfinity - Enterprise Business Application

    Orchestrates C-Suite agents, strategic decision-making, business
    operations, and compliance. Uses runtime abstractions with fallback to AOS.
    """

    def __init__(
        self,
        config: Optional[BusinessInfinityConfig] = None,
        storage: Optional[IStorageProvider] = None,
        messaging: Optional[IMessagingProvider] = None,
    ):
        """
        Initialize BusinessInfinity.

        Args:
            config: Application configuration
            storage: Optional storage provider (uses AOS if not provided)
            messaging: Optional messaging provider (uses AOS if not provided)
        """
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)

        # Runtime providers
        self._storage = storage
        self._messaging = messaging

        # AOS integration - prefer Service Bus client for distributed deployment
        self.aos: Optional[Any] = None
        self.aos_client: Optional[AOSServiceBusClient] = None
        self.storage_manager: Optional[Any] = None
        self.env_manager: Optional[Any] = None
        
        # Deployment mode
        self._use_servicebus = os.getenv("AOS_USE_SERVICEBUS", "true").lower() == "true"

        # Initialize based on deployment mode
        if self._use_servicebus and AOS_CLIENT_AVAILABLE:
            # Use Service Bus client for distributed deployment
            self.aos_client = get_aos_client()
            self.logger.info("Using AOS Service Bus client for distributed deployment")
        elif AOS_DIRECT_AVAILABLE:
            # Fallback to direct AOS for local development
            try:
                self.aos = AgentOperatingSystem()
                self.storage_manager = UnifiedStorageManager()
                self.env_manager = UnifiedEnvManager()
                self.logger.info("Using direct AOS integration for local development")
            except Exception as e:
                self.logger.warning(f"Could not initialize AOS: {e}")

        # MCP Servers registry
        self.mcp_servers = self._load_mcp_servers()

        # Business state
        self._agents: Dict[str, AgentInfo] = {}
        self._workflows: Dict[str, WorkflowInfo] = {}
        self._initialized = False

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []

        self.logger.info("BusinessInfinity created")

    def _load_mcp_servers(self) -> Dict[str, Any]:
        """Load MCP server configurations."""
        mcp_servers_path = os.path.join(os.path.dirname(__file__), "mcp_servers.json")
        try:
            with open(mcp_servers_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def initialize(self) -> None:
        """Initialize the BusinessInfinity application."""
        if self._initialized:
            return

        self.logger.info("Initializing BusinessInfinity...")

        try:
            # Initialize AOS Service Bus client if using distributed mode
            if self.aos_client:
                await self.aos_client.initialize()
                self.logger.info("AOS Service Bus client initialized")

            # Initialize default agents
            await self._initialize_agents()

            # Start background processes if enabled
            if self.config.workflows_enabled:
                await self._start_background_processes()

            self._initialized = True
            self.logger.info("BusinessInfinity initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize BusinessInfinity: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the BusinessInfinity application."""
        self.logger.info("Shutting down BusinessInfinity...")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._background_tasks.clear()
        
        # Shutdown AOS client
        if self.aos_client:
            await self.aos_client.shutdown()

        self._initialized = False
        self.logger.info("BusinessInfinity shutdown complete")

    async def _initialize_agents(self) -> None:
        """Initialize the configured business agents."""
        agent_configs = [
            AgentInfo(
                id="founder",
                name="Founder Agent",
                role="founder",
                capabilities=[
                    "strategic_planning",
                    "vision_setting",
                    "leadership",
                    "fundraising",
                ],
            ),
            AgentInfo(
                id="ceo",
                name="CEO Agent",
                role="ceo",
                capabilities=[
                    "executive_decisions",
                    "team_management",
                    "operations",
                    "stakeholder_relations",
                ],
            ),
            AgentInfo(
                id="cto",
                name="CTO Agent",
                role="cto",
                capabilities=[
                    "technical_architecture",
                    "technology_strategy",
                    "engineering",
                    "product_development",
                ],
            ),
            AgentInfo(
                id="cfo",
                name="CFO Agent",
                role="cfo",
                capabilities=[
                    "financial_planning",
                    "budget_management",
                    "financial_analysis",
                    "investment_decisions",
                ],
            ),
            AgentInfo(
                id="coo",
                name="COO Agent",
                role="coo",
                capabilities=[
                    "operations_management",
                    "process_optimization",
                    "supply_chain",
                    "quality_assurance",
                ],
            ),
            AgentInfo(
                id="cmo",
                name="CMO Agent",
                role="cmo",
                capabilities=[
                    "marketing_strategy",
                    "brand_management",
                    "customer_engagement",
                    "market_research",
                ],
            ),
            AgentInfo(
                id="chro",
                name="CHRO Agent",
                role="chro",
                capabilities=[
                    "talent_management",
                    "organizational_development",
                    "culture",
                    "hr_strategy",
                ],
            ),
            AgentInfo(
                id="cso",
                name="CSO Agent",
                role="cso",
                capabilities=[
                    "corporate_strategy",
                    "market_analysis",
                    "competitive_intelligence",
                    "strategic_planning",
                ],
            ),
        ]

        for agent_config in agent_configs:
            if agent_config.role in self.config.enabled_agents:
                self._agents[agent_config.id] = agent_config

        self.logger.info(f"Initialized {len(self._agents)} agents")

    async def _start_background_processes(self) -> None:
        """Start background monitoring and workflow processes."""
        if self.config.strategic_planning_interval > 0:
            task = asyncio.create_task(self._strategic_planning_loop())
            self._background_tasks.append(task)

        if self.config.performance_monitoring_interval > 0:
            task = asyncio.create_task(self._performance_monitoring_loop())
            self._background_tasks.append(task)

    async def _strategic_planning_loop(self) -> None:
        """Background loop for strategic planning updates."""
        while True:
            try:
                await asyncio.sleep(self.config.strategic_planning_interval)
                # Placeholder for strategic planning logic
                self.logger.debug("Strategic planning cycle completed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in strategic planning loop: {e}")

    async def _performance_monitoring_loop(self) -> None:
        """Background loop for performance monitoring."""
        while True:
            try:
                await asyncio.sleep(self.config.performance_monitoring_interval)
                # Placeholder for performance monitoring logic
                self.logger.debug("Performance monitoring cycle completed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")

    # Public API

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available business agents."""
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "status": agent.status,
                "capabilities": agent.capabilities,
            }
            for agent in self._agents.values()
        ]

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get a specific agent by ID."""
        return self._agents.get(agent_id)

    async def ask_agent(
        self, agent_role: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask a specific agent a question.

        Args:
            agent_role: The role of the agent to ask (e.g., "ceo", "cto")
            message: The message/question to ask
            context: Optional context for the query

        Returns:
            Agent response
        """
        agent = next(
            (a for a in self._agents.values() if a.role == agent_role), None
        )

        if not agent:
            return {
                "error": f"Agent with role '{agent_role}' not found",
                "available_roles": [a.role for a in self._agents.values()],
            }

        # Update last activity
        agent.last_activity = datetime.utcnow()

        # Use AOS Service Bus client if available (distributed mode)
        if self.aos_client and self.aos_client.is_available:
            try:
                response = await self.aos_client.ask_agent(
                    agent_id=agent_role,
                    query=message,
                    context=context
                )
                return {
                    "agent": agent_role,
                    "response": response.get("response", ""),
                    "confidence": response.get("confidence", 0.0),
                    "sources": response.get("sources", []),
                    "timestamp": datetime.utcnow().isoformat(),
                    "via": "servicebus",
                }
            except Exception as e:
                self.logger.error(f"Error calling AOS agent via Service Bus: {e}")
                # Fall through to local response

        # Local fallback response
        return {
            "agent": agent_role,
            "response": f"Response from {agent.name}: I received your message about '{message[:50]}...'",
            "timestamp": datetime.utcnow().isoformat(),
            "context_received": bool(context),
            "via": "local",
        }

    async def execute_workflow(
        self, workflow_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a business workflow.

        Args:
            workflow_name: Name of the workflow to execute
            params: Workflow parameters

        Returns:
            Workflow execution result
        """
        workflow_id = f"{workflow_name}_{datetime.utcnow().timestamp()}"

        workflow = WorkflowInfo(
            id=workflow_id,
            name=workflow_name,
            status="running",
        )
        self._workflows[workflow_id] = workflow

        # Use AOS Service Bus client if available (distributed mode)
        if self.aos_client and self.aos_client.is_available:
            try:
                result = await self.aos_client.execute_workflow(
                    workflow_name=workflow_name,
                    inputs=params,
                    workflow_id=workflow_id
                )
                workflow.status = result.get("status", "completed")
                workflow.progress = 100.0 if workflow.status == "completed" else 0.0
                return {
                    "workflow_id": workflow_id,
                    "name": workflow_name,
                    "status": workflow.status,
                    "progress": workflow.progress,
                    "outputs": result.get("outputs", {}),
                    "via": "servicebus",
                }
            except Exception as e:
                self.logger.error(f"Error executing workflow via Service Bus: {e}")
                workflow.status = "failed"
                return {
                    "workflow_id": workflow_id,
                    "name": workflow_name,
                    "status": "failed",
                    "error": str(e),
                }

        # Local fallback
        workflow.status = "completed"
        workflow.progress = 100.0

        return {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "status": workflow.status,
            "progress": workflow.progress,
            "via": "local",
        }

    async def get_business_status(self) -> Dict[str, Any]:
        """Get the current business status."""
        aos_status = "unavailable"
        
        # Check AOS availability
        if self.aos_client and self.aos_client.is_available:
            try:
                health = await self.aos_client.health_check()
                aos_status = health.get("status", "unknown")
            except Exception:
                aos_status = "unreachable"
        elif self.aos is not None:
            aos_status = "direct"
        
        return {
            "initialized": self._initialized,
            "agents_count": len(self._agents),
            "active_workflows": len(
                [w for w in self._workflows.values() if w.status == "running"]
            ),
            "completed_workflows": len(
                [w for w in self._workflows.values() if w.status == "completed"]
            ),
            "aos_status": aos_status,
            "deployment_mode": "servicebus" if self._use_servicebus else "direct",
            "config": {
                "company_name": self.config.company_name,
                "enabled_agents": self.config.enabled_agents,
                "workflows_enabled": self.config.workflows_enabled,
                "analytics_enabled": self.config.analytics_enabled,
            },
        }

    def list_mcp_servers(self) -> Dict[str, Any]:
        """Return metadata and endpoints for all registered MCP servers."""
        return self.mcp_servers

    @property
    def business_context(self) -> Dict[str, Any]:
        """Get the current business context."""
        return {
            "company_name": self.config.company_name,
            "company_domain": self.config.company_domain,
            "business_model": self.config.business_model,
            "industry": self.config.industry,
            "agents": list(self._agents.keys()),
        }


# Factory functions


async def create_business_infinity(
    config: Optional[BusinessInfinityConfig] = None,
) -> BusinessInfinity:
    """
    Create and initialize a BusinessInfinity instance.

    Args:
        config: Optional configuration

    Returns:
        Initialized BusinessInfinity instance
    """
    app = BusinessInfinity(config)
    await app.initialize()
    return app


# Global instance management
_instance: Optional[BusinessInfinity] = None


def get_business_infinity() -> Optional[BusinessInfinity]:
    """Get the global BusinessInfinity instance."""
    return _instance


def set_business_infinity(instance: BusinessInfinity) -> None:
    """Set the global BusinessInfinity instance."""
    global _instance
    _instance = instance
