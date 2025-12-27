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

# Try to import from runtime first
try:
    from runtime import RuntimeConfig, IStorageProvider, IMessagingProvider
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False
    RuntimeConfig = None

# Import AOS from existing structure (will be updated when AOS is fully refactored)
try:
    from AgentOperatingSystem import AgentOperatingSystem
    from AgentOperatingSystem.config import AOSConfig
    from AgentOperatingSystem.storage.manager import StorageManager
    from AgentOperatingSystem.environment.manager import EnvironmentManager
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    AgentOperatingSystem = None
    AOSConfig = None
    StorageManager = None
    EnvironmentManager = None

from .config import BusinessInfinityConfig
from .covenant_manager import BusinessCovenantManager
from .conversation_manager import BusinessConversationManager
from agents.manager import BusinessAgentManager
from workflows.manager import BusinessWorkflowManager
from analytics.manager import BusinessAnalyticsManager

# Import new AOS utilization improvements (Priority 1)
from .service_interfaces import (
    IStorageService, IMessagingService, IWorkflowService,
)
try:
    from .service_interfaces import AOSStorageService, AOSMessagingService, AOSWorkflowService
except ImportError:
    AOSStorageService = None
    AOSMessagingService = None
    AOSWorkflowService = None

from .observability import (
    create_structured_logger, correlation_scope,
    get_metrics_collector, get_health_check
)
from .reliability import CircuitBreaker, RetryPolicy


class BusinessInfinity:
    """
    Business Infinity - Enterprise Business Application
    
    Orchestrates C-Suite agents, strategic decision-making, business operations, 
    and compliance using the new AOS infrastructure and modular managers.
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        """Initialize Business Infinity with configuration."""
        self.config = config or BusinessInfinityConfig()
        
        # Use structured logger with correlation IDs (Priority 1: Enhanced Observability)
        self.logger = create_structured_logger(__name__)
        
        # Get metrics collector and health check (Priority 1: Enhanced Observability)
        self.metrics = get_metrics_collector()
        self.health_check = get_health_check()
        
        # Initialize AOS as the foundation
        if AOS_AVAILABLE:
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
                self.storage_manager = StorageManager() if StorageManager else None
                self.env_manager = EnvironmentManager() if EnvironmentManager else None
        else:
            self.aos = None
            self.storage_manager = None
            self.env_manager = None
        
        # Wrap AOS services with clean interfaces (Priority 1: Adopt Service Interfaces)
        self.storage_service: IStorageService = AOSStorageService(self.storage_manager)
        
        # Initialize messaging and workflow services if available
        # These will be properly initialized when AOS components are available
        if hasattr(self.aos, 'messaging_manager'):
            self.messaging_service: IMessagingService = AOSMessagingService(self.aos.messaging_manager)
        else:
            self.messaging_service: Optional[IMessagingService] = None
        
        if hasattr(self.aos, 'orchestration_engine'):
            self.workflow_service: IWorkflowService = AOSWorkflowService(self.aos.orchestration_engine)
        else:
            self.workflow_service: Optional[IWorkflowService] = None
        
        # Initialize reliability patterns (Priority 1: Implement Reliability Patterns)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0
        )
        
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
        # Use correlation scope for tracing (Priority 1: Enhanced Observability)
        with correlation_scope(operation_name="business_infinity_initialization"):
            try:
                self.logger.info("Initializing Business Infinity application",
                                application="BusinessInfinity",
                                version=self.business_context["version"])
                
                # Track initialization metric
                self.metrics.increment_counter("bi.initialization.started")
                
                # Start AOS infrastructure with retry (Priority 1: Reliability Patterns)
                await self.retry_policy.execute(self.aos.start)
                
                # Delegate initialization to managers
                await self.agent_manager.initialize()
                await self.workflow_manager.initialize()
                await self.analytics_manager.initialize()
                await self.covenant_manager.initialize()
                await self.conversation_manager.initialize()
                
                # Register health checks (Priority 1: Enhanced Observability)
                self.health_check.register_check("aos", self._check_aos_health)
                self.health_check.register_check("agents", self._check_agents_health)
                self.health_check.register_check("workflows", self._check_workflows_health)
                
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
                
                # Track successful initialization
                self.metrics.increment_counter("bi.initialization.success")
                self.logger.info("Business Infinity application initialized successfully",
                                agents_count=self.business_context["agents_count"],
                                workflows_active=self.business_context["workflows_active"])
                
            except Exception as e:
                # Track failed initialization
                self.metrics.increment_counter("bi.initialization.failed")
                self.logger.error("Failed to initialize Business Infinity",
                                 error=str(e),
                                 error_type=type(e).__name__)
                self.business_context.update({
                    "status": "error",
                    "error": str(e),
                    "error_at": datetime.utcnow()
                })
                raise
    
    async def _check_aos_health(self) -> Dict[str, Any]:
        """Health check for AOS infrastructure."""
        try:
            # Check if AOS is responsive
            if hasattr(self.aos, 'health_check'):
                return await self.aos.health_check()
            return {"healthy": True, "status": "running"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_agents_health(self) -> Dict[str, Any]:
        """Health check for agents."""
        try:
            agents = await self.agent_manager.list_agents()
            return {
                "healthy": len(agents) > 0,
                "agent_count": len(agents)
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_workflows_health(self) -> Dict[str, Any]:
        """Health check for workflows."""
        try:
            count = await self.workflow_manager.get_active_workflows_count()
            return {
                "healthy": True,
                "active_workflows": count
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _strategic_planning_loop(self):
        """Background loop for strategic planning."""
        while True:
            try:
                with correlation_scope(operation_name="strategic_planning_loop"):
                    await self.workflow_manager.run_strategic_planning()
                    self.metrics.increment_counter("bi.strategic_planning.completed")
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.metrics.increment_counter("bi.strategic_planning.failed")
                self.logger.error("Strategic planning loop error",
                                 error=str(e),
                                 error_type=type(e).__name__)
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def _performance_monitoring_loop(self):
        """Background loop for performance monitoring."""
        while True:
            try:
                with correlation_scope(operation_name="performance_monitoring_loop"):
                    await self.analytics_manager.collect_performance_metrics()
                    self.metrics.increment_counter("bi.performance_monitoring.completed")
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                self.metrics.increment_counter("bi.performance_monitoring.failed")
                self.logger.error("Performance monitoring loop error",
                                 error=str(e),
                                 error_type=type(e).__name__)
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _autonomous_boardroom_loop(self):
        """Background loop for autonomous boardroom operations."""
        while True:
            try:
                with correlation_scope(operation_name="autonomous_boardroom_loop"):
                    await self.agent_manager.run_autonomous_boardroom()
                    self.metrics.increment_counter("bi.autonomous_boardroom.completed")
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                self.metrics.increment_counter("bi.autonomous_boardroom.failed")
                self.logger.error("Autonomous boardroom loop error",
                                 error=str(e),
                                 error_type=type(e).__name__)
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    # Business Operations API
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a strategic business decision using workflow engine."""
        # Use correlation scope and reliability patterns (Priority 1)
        with correlation_scope(operation_name="make_strategic_decision"):
            self.logger.info("Making strategic decision",
                           decision_type=decision_context.get("type"))
            self.metrics.increment_counter("bi.decisions.requested")
            
            try:
                # Execute with retry policy for resilience
                result = await self.retry_policy.execute(
                    self.workflow_manager.make_strategic_decision,
                    decision_context
                )
                self.metrics.increment_counter("bi.decisions.success")
                return result
            except Exception as e:
                self.metrics.increment_counter("bi.decisions.failed")
                self.logger.error("Strategic decision failed",
                                 error=str(e),
                                 decision_type=decision_context.get("type"))
                raise

    async def execute_business_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a business workflow."""
        # Use correlation scope and metrics (Priority 1)
        with correlation_scope(operation_name="execute_business_workflow"):
            self.logger.info("Executing business workflow",
                           workflow_name=workflow_name)
            self.metrics.increment_counter("bi.workflows.executed",
                                          tags={"workflow": workflow_name})
            
            try:
                # Use circuit breaker for workflow execution
                result = await self.circuit_breaker.call(
                    self.workflow_manager.execute_business_workflow,
                    workflow_name,
                    parameters
                )
                self.metrics.increment_counter("bi.workflows.success",
                                              tags={"workflow": workflow_name})
                return result
            except Exception as e:
                self.metrics.increment_counter("bi.workflows.failed",
                                              tags={"workflow": workflow_name})
                self.logger.error("Workflow execution failed",
                                 workflow_name=workflow_name,
                                 error=str(e))
                raise

    async def get_business_analytics(self) -> Dict[str, Any]:
        """Get comprehensive business analytics."""
        with correlation_scope(operation_name="get_business_analytics"):
            return await self.analytics_manager.get_business_analytics()

    async def get_business_context(self) -> Dict[str, Any]:
        """Get current business context and status."""
        with correlation_scope(operation_name="get_business_context"):
            # Update with real-time data
            self.business_context.update({
                "last_updated": datetime.utcnow(),
                "agents_status": await self.agent_manager.get_agents_status(),
                "workflows_status": await self.workflow_manager.get_workflows_status(),
                "analytics_summary": await self.analytics_manager.get_summary(),
                "aos_metrics": await self.aos.get_system_metrics() if hasattr(self.aos, 'get_system_metrics') else {},
                "health": await self.health_check.check_health()
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
        with correlation_scope(operation_name="business_infinity_shutdown"):
            try:
                self.logger.info("Shutting down Business Infinity",
                                status=self.business_context.get("status"))
                self.metrics.increment_counter("bi.shutdown.initiated")
                
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
                
                self.metrics.increment_counter("bi.shutdown.completed")
                self.logger.info("Business Infinity shutdown completed",
                                shutdown_duration=str(datetime.utcnow() - self.business_context.get("created_at", datetime.utcnow())))
                
            except Exception as e:
                self.metrics.increment_counter("bi.shutdown.failed")
                self.logger.error("Error during shutdown",
                                 error=str(e),
                                 error_type=type(e).__name__)
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