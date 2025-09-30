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

from .business_agents_refactored import (
    BusinessAgent,
    ChiefExecutiveOfficer,
    BusinessCFO, 
    BusinessCTO,
    BusinessFounder,
    BusinessInvestor
)
from .business_workflows import BusinessWorkflowEngine, WorkflowStatus
from .business_analytics import BusinessAnalyticsEngine, BusinessMetric, MetricType

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
    "BusinessCFO",
    "BusinessCTO", 
    "BusinessFounder",
    "BusinessInvestor",
    # Business Engines
    "BusinessWorkflowEngine",
    "BusinessAnalyticsEngine",
    # Supporting Classes
    "WorkflowStatus",
    "BusinessMetric", 
    "MetricType"
]
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

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Core AOS Infrastructure Imports
from RealmOfAgents.AgentOperatingSystem import AgentOperatingSystem
from RealmOfAgents.AgentOperatingSystem.config import AOSConfig
from RealmOfAgents.AgentOperatingSystem.storage.manager import UnifiedStorageManager
from RealmOfAgents.AgentOperatingSystem.environment import UnifiedEnvManager
from RealmOfAgents.AgentOperatingSystem.mcp_servicebus_client import MCPServiceBusClient

# Business-specific imports
from .business_agents import (
    ChiefExecutiveOfficer, BusinessCFO, BusinessCTO, 
    BusinessFounder, BusinessInvestor
)
from .business_workflows import BusinessWorkflowEngine
from .business_analytics import BusinessAnalyticsEngine

# Network and Covenant imports
from .network.covenant_manager import CovenantManager, create_covenant_manager
from .network.verification import LinkedInVerificationService, create_linkedin_verification_service
from .network.discovery import NetworkDiscovery, create_network_discovery
from .network.covenant_ledger import CovenantLedger


class BusinessInfinityConfig:
    """Configuration for Business Infinity application"""
    
    def __init__(self):
        # Business Identity
        self.company_name = os.getenv("COMPANY_NAME", "Business Infinity Corp")
        self.industry = os.getenv("INDUSTRY", "Technology")
        self.business_stage = os.getenv("BUSINESS_STAGE", "growth")  # startup, growth, enterprise
        self.market_focus = os.getenv("MARKET_FOCUS", "global")
        
        # Business Features
        self.enable_autonomous_boardroom = True
        self.enable_strategic_planning = True
        self.enable_performance_analytics = True
        self.enable_external_integrations = True
        
        # Covenant and Network Features
        self.enable_covenant_compliance = True
        self.linkedin_verification_enabled = True
        self.peer_validation_enabled = True
        self.federation_participation = True
        
        # LinkedIn Verification Settings
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.linkedin_company_url = os.getenv("LINKEDIN_COMPANY_URL")
        
        # Business Decision Making
        self.decision_consensus_threshold = float(os.getenv("DECISION_THRESHOLD", "0.75"))
        self.strategic_planning_interval = int(os.getenv("STRATEGIC_PLANNING_INTERVAL", "86400"))  # daily
        self.performance_review_interval = int(os.getenv("PERFORMANCE_REVIEW_INTERVAL", "604800"))  # weekly
        
        # Covenant Governance Settings
        self.covenant_quorum_requirement = float(os.getenv("COVENANT_QUORUM_REQUIREMENT", "0.6"))
        self.covenant_consensus_threshold = float(os.getenv("COVENANT_CONSENSUS_THRESHOLD", "0.7"))
        self.amendment_cooling_period = int(os.getenv("AMENDMENT_COOLING_PERIOD", "7"))  # days
        
        # MCP Integration for External Systems
        self.mcp_servers = {
            "linkedin": os.getenv("LINKEDIN_MCP_QUEUE", "bi-linkedin-mcp"),
            "reddit": os.getenv("REDDIT_MCP_QUEUE", "bi-reddit-mcp"), 
            "erpnext": os.getenv("ERPNEXT_MCP_QUEUE", "bi-erpnext-mcp")
        }
        
        # AOS Configuration (Infrastructure layer)
        self.aos_config = AOSConfig()


class BusinessInfinity:
    """
    Business Infinity - Enterprise Business Application
    
    A comprehensive business application that orchestrates C-Suite agents,
    strategic decision-making, and business operations using the Agent
    Operating System (AOS) as its foundation.
    
    Enhanced with Covenant-Based Compliance for Global Boardroom Network participation.
    
    Responsibilities:
    - Business agent management and orchestration
    - Strategic planning and decision-making workflows
    - Business performance analytics and KPI tracking
    - Integration with external business systems via MCP
    - Business process automation and optimization
    - Covenant-based compliance management
    - LinkedIn verification and enterprise identity
    - Peer validation and network recognition
    - Federation membership and governance
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)
        
        # AOS Infrastructure (provided by Agent Operating System)
        self.aos = None
        self.storage_manager = None
        self.env_manager = None
        self.mcp_client = None
        
        # Business-specific engines
        self.workflow_engine = None
        self.analytics_engine = None
        
        # Network and Covenant Management
        self.covenant_manager = None
        self.verification_service = None
        self.network_discovery = None
        
        # Business agents registry
        self.business_agents = {}
        
        # Covenant and compliance state
        self.covenant_id = None
        self.covenant_status = "not_created"
        self.compliance_badge = None
        self.network_memberships = []
        
        # Business state
        self.business_context = {
            "company_name": self.config.company_name,
            "industry": self.config.industry,
            "stage": self.config.business_stage,
            "market_focus": self.config.market_focus,
            "initialized_at": datetime.utcnow(),
            "status": "initializing"
        }
        
        # Initialize asynchronously
        self._initialize_task = asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """Initialize Business Infinity application"""
        try:
            self.logger.info("Initializing Business Infinity application...")
            
            # Initialize AOS infrastructure
            await self._initialize_aos_infrastructure()
            
            # Initialize network and covenant management
            await self._initialize_covenant_management()
            
            # Initialize business engines
            await self._initialize_business_engines()
            
            # Initialize business agents
            await self._initialize_business_agents()
            
            # Initialize or load covenant
            await self._initialize_enterprise_covenant()
            
            # Start business processes
            await self._start_business_processes()
            
            self.business_context["status"] = "operational"
            self.business_context["initialized_at"] = datetime.utcnow()
            
            self.logger.info("Business Infinity application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Infinity: {e}")
            self.business_context["status"] = "error"
            self.business_context["error"] = str(e)
            raise
    
    async def _initialize_aos_infrastructure(self):
        """Initialize AOS infrastructure components"""
        try:
            # Initialize Agent Operating System
            self.aos = AgentOperatingSystem(self.config.aos_config)
            await self.aos.start()
            
            # Initialize AOS-managed services
            self.storage_manager = UnifiedStorageManager()
            self.env_manager = UnifiedEnvManager()
            
            # Initialize MCP client for external integrations
            service_bus_connection = self.env_manager.get("AZURE_SERVICEBUS_CONNECTION_STRING")
            if service_bus_connection:
                self.mcp_client = MCPServiceBusClient(
                    connection_string=service_bus_connection,
                    topic_name="business-infinity"
                )
            
            self.logger.info("AOS infrastructure initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AOS infrastructure: {e}")
            raise
    
    async def _initialize_covenant_management(self):
        """Initialize covenant and network management components"""
        try:
            if not self.config.enable_covenant_compliance:
                self.logger.info("Covenant compliance disabled, skipping network initialization")
                return
            
            # Initialize LinkedIn verification service
            if self.config.linkedin_verification_enabled:
                self.verification_service = create_linkedin_verification_service(
                    client_id=self.config.linkedin_client_id,
                    client_secret=self.config.linkedin_client_secret
                )
                self.logger.info("LinkedIn verification service initialized")
            
            # Initialize covenant manager
            self.covenant_manager = create_covenant_manager(
                verification_service=self.verification_service
            )
            
            # Initialize network discovery
            self.network_discovery = create_network_discovery()
            
            self.logger.info("Covenant management components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize covenant management: {e}")
            raise
    
    async def _initialize_business_engines(self):
        """Initialize business-specific engines"""
        try:
            # Business workflow engine for process automation
            self.workflow_engine = BusinessWorkflowEngine(
                aos=self.aos,
                storage_manager=self.storage_manager,
                config=self.config
            )
            
            # Business analytics engine for KPIs and metrics
            self.analytics_engine = BusinessAnalyticsEngine(
                storage_manager=self.storage_manager,
                config=self.config
            )
            
            self.logger.info("Business engines initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize business engines: {e}")
            raise
    
    async def _initialize_business_agents(self):
        """Initialize business-specific agents"""
        try:
            # Create business agents that extend AOS LeadershipAgent
            agents_config = {
                "company_context": self.business_context,
                "analytics_engine": self.analytics_engine,
                "workflow_engine": self.workflow_engine
            }
            
            # C-Suite agents
            self.business_agents["ceo"] = ChiefExecutiveOfficer(
                domain="strategic_leadership",
                config=agents_config
            )
            
            self.business_agents["cfo"] = BusinessCFO(
                domain="financial_management", 
                config=agents_config
            )
            
            self.business_agents["cto"] = BusinessCTO(
                domain="technology_leadership",
                config=agents_config
            )
            
            # Stakeholder agents
            self.business_agents["founder"] = BusinessFounder(
                domain="vision_innovation",
                config=agents_config
            )
            
            self.business_agents["investor"] = BusinessInvestor(
                domain="investment_strategy",
                config=agents_config
            )
            
            # Register all agents with AOS
            for agent_id, agent in self.business_agents.items():
                await self.aos.register_agent(agent)
            
            self.logger.info(f"Initialized {len(self.business_agents)} business agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize business agents: {e}")
            raise
    
    async def _initialize_enterprise_covenant(self):
        """Initialize or load the enterprise covenant"""
        try:
            if not self.config.enable_covenant_compliance or not self.covenant_manager:
                self.logger.info("Covenant compliance disabled, skipping covenant initialization")
                return
            
            # Check if covenant already exists
            covenant_id = await self._load_existing_covenant()
            
            if covenant_id:
                self.covenant_id = covenant_id
                self.covenant_status = await self.covenant_manager.get_covenant_status(covenant_id)
                self.logger.info(f"Loaded existing covenant: {covenant_id} (status: {self.covenant_status})")
            else:
                # Create new covenant if LinkedIn URL is provided
                if self.config.linkedin_company_url:
                    covenant_id = await self._create_enterprise_covenant()
                    if covenant_id:
                        self.covenant_id = covenant_id
                        self.covenant_status = "draft"
                        self.logger.info(f"Created new covenant: {covenant_id}")
                else:
                    self.logger.warning("No LinkedIn company URL provided, covenant creation skipped")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enterprise covenant: {e}")
            # Don't raise - covenant is optional for basic operation
    
    async def _load_existing_covenant(self) -> Optional[str]:
        """Load existing covenant from storage"""
        try:
            # Check if covenant ID is stored in business context
            # In a real implementation, this would load from persistent storage
            return None  # For now, always create new
        except Exception as e:
            self.logger.error(f"Failed to load existing covenant: {e}")
            return None
    
    async def _create_enterprise_covenant(self) -> Optional[str]:
        """Create a new enterprise covenant"""
        try:
            enterprise_data = {
                "company_name": self.config.company_name,
                "linkedin_url": self.config.linkedin_company_url,
                "industry": self.config.industry,
                "jurisdiction": "United States",  # Should be configurable
                "mission_statement": f"To operate {self.config.company_name} as an autonomous, transparent, and collaborative enterprise within the global network of verified businesses.",
                "core_values": [
                    "Innovation", "Transparency", "Collaboration", 
                    "Integrity", "Excellence", "Sustainability"
                ],
                "declaration_of_intent": (
                    f"We, {self.config.company_name}, hereby commit to operating as a verified member "
                    f"of the Global Boardroom Network, maintaining the highest standards of transparency, "
                    f"accountability, and collaboration in all our autonomous business operations."
                )
            }
            
            governance_preferences = {
                "quorum_requirement": self.config.covenant_quorum_requirement,
                "consensus_threshold": self.config.covenant_consensus_threshold,
                "amendment_cooling_period": self.config.amendment_cooling_period,
                "federation_participation": self.config.federation_participation,
                "public_reporting": False,  # Can be configured later
                "external_arbitration": False
            }
            
            covenant_id = await self.covenant_manager.create_covenant(
                enterprise_data, governance_preferences
            )
            
            return covenant_id
            
        except Exception as e:
            self.logger.error(f"Failed to create enterprise covenant: {e}")
            return None
    
    async def _start_business_processes(self):
        """Start ongoing business processes"""
        try:
            # Start strategic planning process
            if self.config.enable_strategic_planning:
                asyncio.create_task(self._strategic_planning_loop())
            
            # Start performance monitoring
            if self.config.enable_performance_analytics:
                asyncio.create_task(self._performance_monitoring_loop())
            
            # Start autonomous boardroom if enabled
            if self.config.enable_autonomous_boardroom:
                asyncio.create_task(self._autonomous_boardroom_loop())
            
            self.logger.info("Business processes started")
            
        except Exception as e:
            self.logger.error(f"Failed to start business processes: {e}")
            raise
    
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a strategic business decision across relevant agents
        
        Args:
            decision_context: Context and parameters for the decision
            
        Returns:
            Dict containing the collective decision and reasoning
        """
        try:
            # Determine relevant agents for this decision
            relevant_agents = self._determine_relevant_agents(decision_context)
            
            # Gather input from each agent
            agent_inputs = {}
            for agent_id in relevant_agents:
                agent = self.business_agents[agent_id]
                agent_inputs[agent_id] = await agent.analyze_business_context(decision_context)
            
            # Use workflow engine to orchestrate decision
            decision_result = await self.workflow_engine.orchestrate_decision(
                decision_context=decision_context,
                agent_inputs=agent_inputs,
                consensus_threshold=self.config.decision_consensus_threshold
            )
            
            # Record decision in analytics
            await self.analytics_engine.record_decision(decision_result)
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Strategic decision failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def execute_business_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific business workflow
        
        Args:
            workflow_name: Name of the workflow to execute
            parameters: Workflow-specific parameters
            
        Returns:
            Dict containing workflow execution results
        """
        return await self.workflow_engine.execute_workflow(workflow_name, parameters)
    
    async def get_business_analytics(self) -> Dict[str, Any]:
        """Get current business analytics and KPIs"""
        return await self.analytics_engine.generate_business_report()
    
    def _determine_relevant_agents(self, decision_context: Dict[str, Any]) -> List[str]:
        """Determine which agents should participate in a decision"""
        decision_type = decision_context.get("type", "general")
        
        # Business decision routing logic
        if decision_type in ["funding", "investment", "valuation"]:
            return ["cfo", "founder", "investor"]
        elif decision_type in ["product", "technology", "innovation"]:
            return ["ceo", "cto", "founder"]
        elif decision_type in ["strategy", "vision", "market"]:
            return ["ceo", "founder", "investor"]
        elif decision_type in ["operations", "finance", "resources"]:
            return ["ceo", "cfo", "cto"]
        else:
            return ["ceo", "cfo", "cto"]  # Default leadership team
    
    async def _strategic_planning_loop(self):
        """Continuous strategic planning process"""
        while True:
            try:
                await asyncio.sleep(self.config.strategic_planning_interval)
                
                # Execute strategic planning workflow
                planning_result = await self.workflow_engine.execute_workflow(
                    "strategic_planning",
                    {"business_context": self.business_context}
                )
                
                self.logger.info("Strategic planning cycle completed")
                
            except Exception as e:
                self.logger.error(f"Strategic planning loop error: {e}")
    
    async def _performance_monitoring_loop(self):
        """Continuous performance monitoring process"""
        while True:
            try:
                await asyncio.sleep(self.config.performance_review_interval)
                
                # Generate performance analytics
                performance_report = await self.analytics_engine.generate_performance_report()
                
                self.logger.info("Performance monitoring cycle completed")
                
            except Exception as e:
                self.logger.error(f"Performance monitoring loop error: {e}")
    
    async def _autonomous_boardroom_loop(self):
        """Continuous autonomous boardroom operations"""
        while True:
            try:
                await asyncio.sleep(3600)  # Hourly boardroom check
                
                # Check for autonomous decisions needed
                autonomous_items = await self._check_autonomous_decision_queue()
                
                for item in autonomous_items:
                    await self.make_strategic_decision(item)
                
            except Exception as e:
                self.logger.error(f"Autonomous boardroom loop error: {e}")
    
    async def _check_autonomous_decision_queue(self) -> List[Dict[str, Any]]:
        """Check for autonomous decisions that need to be made"""
        # Implementation would check various sources for pending decisions
        return []
    
    # Covenant Management API Methods
    
    async def publish_covenant(self) -> bool:
        """Publish the enterprise covenant to the global network"""
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot publish covenant - covenant not initialized")
            return False
        
        try:
            success = await self.covenant_manager.publish_covenant(self.covenant_id)
            if success:
                self.covenant_status = "pending"
                self.logger.info("Covenant published successfully")
            return success
        except Exception as e:
            self.logger.error(f"Failed to publish covenant: {e}")
            return False
    
    async def get_covenant_status(self) -> Dict[str, Any]:
        """Get current covenant status and compliance information"""
        if not self.covenant_manager or not self.covenant_id:
            return {
                "covenant_exists": False,
                "status": "not_created",
                "message": "No covenant initialized"
            }
        
        try:
            covenant = await self.covenant_manager.get_covenant(self.covenant_id)
            if not covenant:
                return {"covenant_exists": False, "status": "not_found"}
            
            return {
                "covenant_exists": True,
                "covenant_id": self.covenant_id,
                "status": self.covenant_status,
                "company_name": covenant.get("identity", {}).get("company_name"),
                "verification_status": covenant.get("identity", {}).get("linkedin_verification", {}).get("verification_status"),
                "recognition_count": covenant.get("provenance", {}).get("recognition_status", {}).get("recognition_count", 0),
                "bic_badge": covenant.get("provenance", {}).get("recognition_status", {}).get("bic_badge", {}),
                "last_validated": covenant.get("compliance_metadata", {}).get("last_validated"),
                "compliance_score": covenant.get("compliance_metadata", {}).get("validation_score", 0)
            }
        except Exception as e:
            self.logger.error(f"Failed to get covenant status: {e}")
            return {"error": str(e)}
    
    async def propose_covenant_amendment(self, changes: Dict[str, Any], rationale: str,
                                       proposer_agent: str = "ceo") -> Optional[str]:
        """Propose an amendment to the enterprise covenant"""
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot propose amendment - covenant not initialized")
            return None
        
        try:
            amendment_id = await self.covenant_manager.propose_amendment(
                self.covenant_id, proposer_agent, changes, rationale
            )
            self.logger.info(f"Amendment proposed: {amendment_id}")
            return amendment_id
        except Exception as e:
            self.logger.error(f"Failed to propose amendment: {e}")
            return None
    
    async def vote_on_amendment(self, amendment_id: str, agent_id: str, 
                              vote: str, rationale: str = None) -> bool:
        """Cast a vote on a covenant amendment"""
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot vote on amendment - covenant not initialized")
            return False
        
        try:
            success = await self.covenant_manager.vote_on_amendment(
                self.covenant_id, amendment_id, agent_id, vote, rationale
            )
            if success:
                self.logger.info(f"Vote cast by {agent_id} on amendment {amendment_id}: {vote}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to vote on amendment: {e}")
            return False
    
    async def discover_peer_boardrooms(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Discover peer boardrooms in the network"""
        if not self.network_discovery:
            self.logger.error("Network discovery not initialized")
            return []
        
        try:
            from .network.discovery import DiscoveryCriteria, DiscoveryType
            
            # Create discovery criteria
            discovery_criteria = DiscoveryCriteria(
                industry=criteria.get("industry") if criteria else self.config.industry,
                verification_required=True,
                max_results=criteria.get("max_results", 20) if criteria else 20
            )
            
            # Add capabilities if specified
            if criteria and "capabilities" in criteria:
                discovery_criteria.capabilities = set(criteria["capabilities"])
            
            # Discover boardrooms
            boardrooms = await self.network_discovery.discover_boardrooms(
                discovery_criteria, DiscoveryType.INDUSTRY
            )
            
            # Convert to simple dict format
            results = []
            for boardroom in boardrooms:
                results.append({
                    "node_id": boardroom.node_id,
                    "company_name": boardroom.enterprise_identity.company_name,
                    "industry": boardroom.enterprise_identity.industry,
                    "size": boardroom.enterprise_identity.size,
                    "location": boardroom.enterprise_identity.location,
                    "verification_status": boardroom.enterprise_identity.verification_status,
                    "capabilities": list(boardroom.capabilities),
                    "status": boardroom.status.value
                })
            
            self.logger.info(f"Discovered {len(results)} peer boardrooms")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to discover peer boardrooms: {e}")
            return []
    
    async def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get covenant compliance and network statistics"""
        if not self.covenant_manager:
            return {"error": "Covenant management not initialized"}
        
        try:
            stats = self.covenant_manager.get_compliance_statistics()
            
            # Add enterprise-specific information
            if self.covenant_id:
                covenant_status = await self.get_covenant_status()
                stats["enterprise_covenant"] = covenant_status
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get compliance statistics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown Business Infinity"""
        try:
            self.logger.info("Shutting down Business Infinity...")
            
            # Stop business processes
            # (asyncio tasks will be cancelled when the event loop stops)
            
            # Shutdown AOS infrastructure
            if self.aos:
                await self.aos.stop()
            
            self.business_context["status"] = "shutdown"
            self.logger.info("Business Infinity shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Factory functions for easy instantiation
def create_business_infinity(config: BusinessInfinityConfig = None) -> BusinessInfinity:
    """Create and initialize Business Infinity application"""
    return BusinessInfinity(config)

def create_default_business_infinity() -> BusinessInfinity:
    """Create Business Infinity with default configuration"""
    return BusinessInfinity(BusinessInfinityConfig())