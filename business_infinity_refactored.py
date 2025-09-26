"""
Business Infinity - Enterprise Business Application

This module provides the main Business Infinity application built on top of the
Agent Operating System (AOS). It focuses purely on business logic, workflows,
and business-specific agent orchestration while leveraging AOS for all
infrastructure needs.

Architecture:
- BusinessInfinity: Main business application orchestrator
- BusinessAgents: Business-specific agents extending AOS LeadershipAgent
- Business Workflows: Strategic decision-making and operational processes
- Business Analytics: KPIs, metrics, and performance tracking
- Business Integration: External system connections via MCP
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
    BusinessCEO, BusinessCFO, BusinessCTO, 
    BusinessFounder, BusinessInvestor
)
from .business_workflows import BusinessWorkflowEngine
from .business_analytics import BusinessAnalyticsEngine


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
        
        # Business Decision Making
        self.decision_consensus_threshold = float(os.getenv("DECISION_THRESHOLD", "0.75"))
        self.strategic_planning_interval = int(os.getenv("STRATEGIC_PLANNING_INTERVAL", "86400"))  # daily
        self.performance_review_interval = int(os.getenv("PERFORMANCE_REVIEW_INTERVAL", "604800"))  # weekly
        
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
    
    Responsibilities:
    - Business agent management and orchestration
    - Strategic planning and decision-making workflows
    - Business performance analytics and KPI tracking
    - Integration with external business systems via MCP
    - Business process automation and optimization
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
        
        # Business agents registry
        self.business_agents = {}
        
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
            
            # Initialize business engines
            await self._initialize_business_engines()
            
            # Initialize business agents
            await self._initialize_business_agents()
            
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
            self.business_agents["ceo"] = BusinessCEO(
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