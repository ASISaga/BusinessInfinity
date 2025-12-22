"""
Business Infinity Main Application - Refactored for Clean AOS Separation

This module demonstrates the proper refactoring of BusinessInfinity to be
a pure business orchestration layer built on AOS infrastructure.

Key Principles:
1. No infrastructure code - use AOS services
2. Business logic and orchestration only
3. Clean dependency injection of AOS services
4. Business-focused configuration
5. Proper extension of AOS base classes
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import AOS infrastructure services
# These will work once AOS is refactored with clean interfaces
try:
    from AgentOperatingSystem import AgentOperatingSystem
    from AgentOperatingSystem.agents import UnifiedAgentManager
    from AgentOperatingSystem.storage.manager import UnifiedStorageManager
    from AgentOperatingSystem.environment import UnifiedEnvManager
    from AgentOperatingSystem.messaging import ServiceBusManager
    from AgentOperatingSystem.orchestration import OrchestrationEngine
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    logging.warning("AOS not available - running in fallback mode")

# Import business-specific components
from .agents.business_agent_refactored import BusinessAgent
from .agents.ceo_refactored import ChiefExecutiveOfficerRefactored, create_ceo


class BusinessInfinityConfig:
    """
    Business-specific configuration for BusinessInfinity.
    
    This config focuses on business parameters only.
    Infrastructure config is handled by AOS.
    """
    
    def __init__(self):
        # Business identity
        self.business_name = "Business Infinity"
        self.industry = "Technology"
        self.stage = "Growth"  # Startup, Growth, Mature
        self.market = "Global"
        
        # Agent configuration (business-specific)
        self.enable_c_suite = True
        self.enable_founder = True
        self.enable_investor = True
        
        # Business operational settings
        self.decision_threshold = 0.7
        self.collaboration_mode = "consensus"  # consensus, delegation, hierarchy
        self.reporting_enabled = True
        self.metrics_collection = True
        
        # Business workflow settings
        self.workflow_approval_required = True
        self.strategic_review_frequency = "quarterly"
        
        # Governance settings
        self.compliance_enabled = True
        self.audit_trail_enabled = True
        self.risk_management_enabled = True
        
        # Network settings (Global Boardroom Network)
        self.network_participation_enabled = True
        self.covenant_compliance_enabled = True
        self.linkedin_verification_enabled = True


class BusinessInfinityRefactored:
    """
    Business Infinity - Enterprise Business Application (Refactored)
    
    Pure business orchestration layer that:
    1. Uses AOS for all infrastructure needs
    2. Focuses on business logic and workflows
    3. Orchestrates business-specific agents
    4. Provides business analytics and KPIs
    5. Manages business workflows and decisions
    
    AOS Provides (Infrastructure):
    - Agent lifecycle management
    - Message bus and communication
    - Storage and persistence
    - Environment and configuration
    - Authentication and security
    - ML pipeline and model management
    - Base agent classes
    - System monitoring
    
    BusinessInfinity Provides (Business Logic):
    - Business agent implementations (CEO, CFO, etc.)
    - Strategic decision-making processes
    - Business workflow definitions
    - Business analytics and KPIs
    - External business integrations
    - Business governance and compliance
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        """
        Initialize Business Infinity.
        
        Args:
            config: Business-specific configuration
        """
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger("business_infinity")
        
        # AOS infrastructure services (injected)
        self.aos: Optional['AgentOperatingSystem'] = None
        self.agent_manager: Optional['UnifiedAgentManager'] = None
        self.storage: Optional['UnifiedStorageManager'] = None
        self.messaging: Optional['ServiceBusManager'] = None
        self.orchestration: Optional['OrchestrationEngine'] = None
        
        # Business agents
        self.agents: Dict[str, BusinessAgent] = {}
        
        # Business workflow engine
        self.workflows = {}
        
        # Business analytics
        self.analytics = {}
        
        # Initialization state
        self.initialized = False
    
    async def initialize(self):
        """
        Initialize Business Infinity with AOS services.
        
        This method shows proper dependency injection of AOS services.
        """
        try:
            self.logger.info("Initializing Business Infinity...")
            
            # Initialize AOS infrastructure
            if AOS_AVAILABLE:
                await self._initialize_aos()
            else:
                self.logger.warning("AOS not available - limited functionality")
            
            # Initialize business agents
            await self._initialize_business_agents()
            
            # Initialize business workflows
            await self._initialize_business_workflows()
            
            # Initialize business analytics
            await self._initialize_business_analytics()
            
            # Initialize business governance
            if self.config.compliance_enabled:
                await self._initialize_governance()
            
            self.initialized = True
            self.logger.info("Business Infinity initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Infinity: {e}")
            raise
    
    async def _initialize_aos(self):
        """Initialize AOS infrastructure services."""
        if not AOS_AVAILABLE:
            return
        
        # Create AOS instance (infrastructure layer)
        self.aos = AgentOperatingSystem()
        await self.aos.initialize()
        
        # Get AOS service instances (dependency injection)
        self.agent_manager = self.aos.get_agent_manager()
        self.storage = self.aos.get_storage_manager()
        self.messaging = self.aos.get_messaging_service()
        self.orchestration = self.aos.get_orchestration_engine()
        
        self.logger.info("AOS infrastructure initialized")
    
    async def _initialize_business_agents(self):
        """
        Initialize business-specific agents.
        
        This shows how to create and register business agents
        that extend AOS base classes.
        """
        # Create CEO agent (business-specific)
        ceo = create_ceo(config={
            "business_name": self.config.business_name,
            "industry": self.config.industry
        })
        
        # Register with AOS agent manager (infrastructure)
        if self.agent_manager:
            await self.agent_manager.register_agent(ceo)
        
        # Store in business agents registry
        self.agents["CEO"] = ceo
        
        # TODO: Create and register other C-Suite agents
        # CFO, CTO, CMO, COO, CHRO, CSO
        
        # TODO: Create Founder and Investor agents if enabled
        if self.config.enable_founder:
            # founder = create_founder(...)
            pass
        
        if self.config.enable_investor:
            # investor = create_investor(...)
            pass
        
        self.logger.info(f"Initialized {len(self.agents)} business agents")
    
    async def _initialize_business_workflows(self):
        """
        Initialize business-specific workflows.
        
        Workflows use AOS orchestration engine but contain
        business-specific logic and steps.
        """
        # Define business workflows
        self.workflows = {
            "strategic_planning": self._create_strategic_planning_workflow(),
            "product_launch": self._create_product_launch_workflow(),
            "funding_round": self._create_funding_round_workflow(),
            "market_analysis": self._create_market_analysis_workflow()
        }
        
        self.logger.info(f"Initialized {len(self.workflows)} business workflows")
    
    async def _initialize_business_analytics(self):
        """
        Initialize business analytics and KPI tracking.
        
        Uses AOS storage for persistence but business logic
        for analytics calculations.
        """
        self.analytics = {
            "kpi_tracker": {},
            "performance_metrics": {},
            "strategic_dashboard": {}
        }
        
        self.logger.info("Business analytics initialized")
    
    async def _initialize_governance(self):
        """
        Initialize business governance and compliance.
        
        Business-specific governance rules using AOS
        audit trail and storage.
        """
        # Initialize covenant management for Global Boardroom Network
        if self.config.covenant_compliance_enabled:
            # Initialize covenant manager
            pass
        
        # Initialize LinkedIn verification
        if self.config.linkedin_verification_enabled:
            # Initialize verification service
            pass
        
        self.logger.info("Business governance initialized")
    
    # ===== Business Operations =====
    
    async def ask_agent(self, role: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ask a business agent a question.
        
        Args:
            role: Agent role (CEO, CFO, etc.)
            message: Question or request
            context: Optional context
            
        Returns:
            Agent response
        """
        agent = self.agents.get(role)
        if not agent:
            return {
                "error": f"Agent {role} not found",
                "available_agents": list(self.agents.keys())
            }
        
        # Use AOS message handling (if available)
        if hasattr(agent, 'handle_message'):
            response = await agent.handle_message({
                "type": "question",
                "message": message,
                "context": context or {}
            })
        else:
            response = {
                "answer": f"Agent {role} received: {message}",
                "confidence": 0.0
            }
        
        return response
    
    async def make_strategic_decision(
        self,
        decision_context: Dict[str, Any],
        stakeholders: List[str] = None
    ) -> Dict[str, Any]:
        """
        Make a strategic business decision.
        
        This is business logic that uses AOS decision patterns.
        
        Args:
            decision_context: Context for the decision
            stakeholders: Agent roles to involve
            
        Returns:
            Decision with rationale
        """
        # Default stakeholders for strategic decisions
        if not stakeholders:
            stakeholders = ["CEO", "CFO", "CTO"]
        
        # Get CEO to lead the decision
        ceo = self.agents.get("CEO")
        if not ceo:
            return {"error": "CEO agent not available"}
        
        # Make decision using business agent's decision framework
        decision = await ceo.make_business_decision(
            decision_context=decision_context,
            stakeholders=stakeholders
        )
        
        # Store decision (using AOS storage)
        if self.storage:
            await self.storage.save(
                collection="strategic_decisions",
                key=decision.get("id", "unknown"),
                data=decision
            )
        
        # Publish decision event (using AOS messaging)
        if self.messaging:
            await self.messaging.publish(
                topic="business_decisions",
                message={
                    "type": "strategic_decision_made",
                    "decision_id": decision.get("id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return decision
    
    async def execute_business_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a business workflow.
        
        Business workflows using AOS orchestration.
        
        Args:
            workflow_name: Name of the workflow
            params: Workflow parameters
            
        Returns:
            Workflow execution result
        """
        workflow_def = self.workflows.get(workflow_name)
        if not workflow_def:
            return {
                "error": f"Workflow {workflow_name} not found",
                "available_workflows": list(self.workflows.keys())
            }
        
        # Execute using AOS orchestration (if available)
        if self.orchestration:
            result = await self.orchestration.execute_workflow(
                workflow_name=workflow_name,
                params=params
            )
        else:
            result = {
                "status": "simulated",
                "workflow": workflow_name,
                "message": "AOS orchestration not available"
            }
        
        return result
    
    # ===== Business Workflow Definitions =====
    
    def _create_strategic_planning_workflow(self) -> Dict[str, Any]:
        """Define strategic planning workflow."""
        return {
            "name": "strategic_planning",
            "description": "Quarterly strategic planning process",
            "steps": [
                {"name": "market_analysis", "agent": "CEO"},
                {"name": "financial_review", "agent": "CFO"},
                {"name": "technology_assessment", "agent": "CTO"},
                {"name": "strategy_synthesis", "agent": "CEO"},
                {"name": "board_approval", "agent": "CEO"}
            ]
        }
    
    def _create_product_launch_workflow(self) -> Dict[str, Any]:
        """Define product launch workflow."""
        return {
            "name": "product_launch",
            "description": "New product launch process",
            "steps": [
                {"name": "market_validation", "agent": "CMO"},
                {"name": "technical_readiness", "agent": "CTO"},
                {"name": "financial_analysis", "agent": "CFO"},
                {"name": "launch_decision", "agent": "CEO"},
                {"name": "execution_plan", "agent": "COO"}
            ]
        }
    
    def _create_funding_round_workflow(self) -> Dict[str, Any]:
        """Define funding round workflow."""
        return {
            "name": "funding_round",
            "description": "Investment funding round process",
            "steps": [
                {"name": "financial_assessment", "agent": "CFO"},
                {"name": "investor_outreach", "agent": "Investor"},
                {"name": "pitch_preparation", "agent": "Founder"},
                {"name": "due_diligence", "agent": "CEO"},
                {"name": "negotiation", "agent": "Founder"},
                {"name": "closing", "agent": "CFO"}
            ]
        }
    
    def _create_market_analysis_workflow(self) -> Dict[str, Any]:
        """Define market analysis workflow."""
        return {
            "name": "market_analysis",
            "description": "Comprehensive market analysis",
            "steps": [
                {"name": "market_research", "agent": "CMO"},
                {"name": "competitive_analysis", "agent": "CSO"},
                {"name": "technology_trends", "agent": "CTO"},
                {"name": "strategic_implications", "agent": "CEO"}
            ]
        }
    
    # ===== Health and Status =====
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Business Infinity.
        
        Returns:
            Health status of all components
        """
        health = {
            "status": "healthy",
            "initialized": self.initialized,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check AOS infrastructure
        if self.aos:
            health["components"]["aos"] = await self.aos.health_check()
        
        # Check business agents
        if self.agent_manager:
            agent_health = await self.agent_manager.health_check_all()
            health["components"]["agents"] = {
                "total": len(self.agents),
                "healthy": sum(1 for h in agent_health.values() if h.get("healthy")),
                "details": agent_health
            }
        
        # Check workflows
        health["components"]["workflows"] = {
            "available": len(self.workflows),
            "names": list(self.workflows.keys())
        }
        
        return health


# Factory function for creating Business Infinity
async def create_business_infinity(config: BusinessInfinityConfig = None) -> BusinessInfinityRefactored:
    """
    Create and initialize Business Infinity.
    
    Args:
        config: Business configuration
        
    Returns:
        Initialized BusinessInfinity instance
    """
    bi = BusinessInfinityRefactored(config=config)
    await bi.initialize()
    return bi
