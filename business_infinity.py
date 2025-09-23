"""
Business Infinity - Business Application Layer

This module provides the main Business Infinity application that runs on top
of the Agent Operating System (AOS). It orchestrates C-Suite agents, Founder,
and Investor agents to handle business operations, decision-making, and 
strategic planning.

Business Infinity Architecture:
- Built on AOS foundation from RealmOfAgents
- C-Suite agents for operational leadership
- Founder agent for vision and innovation
- Investor agent for funding and growth decisions
- Business-specific workflows and orchestration
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import AOS foundation
try:
    from RealmOfAgents.AgentOperatingSystem.AgentOperatingSystem import AgentOperatingSystem
    from RealmOfAgents.AgentOperatingSystem.config import AOSConfig, default_config
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    logging.warning("AOS not available, using fallback implementations")

# Import C-Suite agents
try:
    from RealmOfAgents.CEO.ChiefExecutiveOfficer import ChiefExecutiveOfficer
    from RealmOfAgents.CFO.ChiefFinancialOfficer import ChiefFinancialOfficer  
    from RealmOfAgents.CTO.ChiefTechnologyOfficer import ChiefTechnologyOfficer
    from RealmOfAgents.CMO.ChiefMarketingOfficer import ChiefMarketingOfficer
    from RealmOfAgents.COO.ChiefOperatingOfficer import ChiefOperatingOfficer
    from RealmOfAgents.CHRO.ChiefHumanResourcesOfficer import ChiefHumanResourcesOfficer
    from RealmOfAgents.CSO.ChiefStrategyOfficer import ChiefStrategyOfficer
    C_SUITE_AVAILABLE = True
except ImportError:
    C_SUITE_AVAILABLE = False
    logging.warning("C-Suite agents not available, using fallback implementations")

# Import Founder and Investor agents
try:
    from RealmOfAgents.Founder.FounderAgent import FounderAgent
    from RealmOfAgents.Investor.InvestorAgent import InvestorAgent
    STAKEHOLDER_AGENTS_AVAILABLE = True
except ImportError:
    STAKEHOLDER_AGENTS_AVAILABLE = False
    logging.warning("Stakeholder agents not available, using fallback implementations")

# Fallback imports from MVP implementation
if not C_SUITE_AVAILABLE or not STAKEHOLDER_AGENTS_AVAILABLE:
    from .mvp_agents import LeadershipAgent, AgentManager as MVPAgentManager


class BusinessInfinityConfig:
    """Configuration for Business Infinity application"""
    
    def __init__(self):
        self.aos_config = default_config if AOS_AVAILABLE else None
        self.business_name = os.getenv("BUSINESS_NAME", "Business Infinity")
        self.industry = os.getenv("BUSINESS_INDUSTRY", "Technology")
        self.stage = os.getenv("BUSINESS_STAGE", "Growth")  # Startup, Growth, Mature
        self.market = os.getenv("TARGET_MARKET", "Global")
        
        # Business-specific configuration
        self.enable_c_suite = True
        self.enable_founder = True
        self.enable_investor = True
        self.enable_board = False  # Future feature
        
        # Operational configuration
        self.decision_threshold = 0.7  # Confidence threshold for decisions
        self.collaboration_mode = "consensus"  # consensus, delegation, hierarchy
        self.reporting_enabled = True
        self.metrics_collection = True


class BusinessInfinity:
    """
    Business Infinity - The business application layer built on AOS
    
    This class orchestrates business operations through C-Suite agents,
    Founder, and Investor agents, providing strategic decision-making,
    operational execution, and growth management capabilities.
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AOS foundation
        self.aos = None
        if AOS_AVAILABLE:
            self.aos = AgentOperatingSystem(self.config.aos_config)
        
        # Business agents
        self.c_suite = {}
        self.founder = None
        self.investor = None
        
        # Business state
        self.business_context = {
            "name": self.config.business_name,
            "industry": self.config.industry,
            "stage": self.config.stage,
            "market": self.config.market,
            "initialized_at": datetime.now()
        }
        
        # Fallback MVP manager if agents not available
        self.mvp_manager = None
        if not C_SUITE_AVAILABLE:
            self.mvp_manager = MVPAgentManager()
        
        # Initialize business agents
        asyncio.create_task(self._initialize_business_agents())
    
    async def _initialize_business_agents(self):
        """Initialize all business agents"""
        try:
            if C_SUITE_AVAILABLE and self.config.enable_c_suite:
                await self._initialize_c_suite()
            
            if STAKEHOLDER_AGENTS_AVAILABLE:
                if self.config.enable_founder:
                    await self._initialize_founder()
                
                if self.config.enable_investor:
                    await self._initialize_investor()
            
            self.logger.info("Business Infinity agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing business agents: {e}")
    
    async def _initialize_c_suite(self):
        """Initialize C-Suite agents"""
        c_suite_roles = {
            "CEO": ChiefExecutiveOfficer,
            "CFO": ChiefFinancialOfficer,
            "CTO": ChiefTechnologyOfficer,
            "CMO": ChiefMarketingOfficer,
            "COO": ChiefOperatingOfficer,
            "CHRO": ChiefHumanResourcesOfficer,
            "CSO": ChiefStrategyOfficer
        }
        
        for role, agent_class in c_suite_roles.items():
            try:
                # Create agent instance
                agent = agent_class()
                
                # Register with AOS if available
                if self.aos:
                    success = await self.aos.register_leadership_agent(role, {
                        "business_context": self.business_context,
                        "agent_class": agent_class.__name__
                    })
                    if success:
                        self.c_suite[role] = self.aos.get_leadership_agent(role)
                else:
                    self.c_suite[role] = agent
                
                self.logger.info(f"Initialized {role} agent")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {role}: {e}")
    
    async def _initialize_founder(self):
        """Initialize Founder agent"""
        try:
            self.founder = FounderAgent()
            
            # Register with AOS if available
            if self.aos:
                await self.aos.register_leadership_agent("Founder", {
                    "business_context": self.business_context,
                    "agent_class": "FounderAgent"
                })
                self.founder = self.aos.get_leadership_agent("Founder")
            
            self.logger.info("Initialized Founder agent")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Founder: {e}")
    
    async def _initialize_investor(self):
        """Initialize Investor agent"""
        try:
            self.investor = InvestorAgent()
            
            # Register with AOS if available  
            if self.aos:
                await self.aos.register_leadership_agent("Investor", {
                    "business_context": self.business_context,
                    "agent_class": "InvestorAgent"
                })
                self.investor = self.aos.get_leadership_agent("Investor")
            
            self.logger.info("Initialized Investor agent")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Investor: {e}")
    
    # Business Operations API
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a strategic business decision involving relevant stakeholders
        
        Args:
            decision_context: Context and parameters for the decision
            
        Returns:
            Decision result with recommendations and rationale
        """
        try:
            # Use AOS decision orchestration if available
            if self.aos:
                return await self.aos.orchestrate_leadership_decision(decision_context)
            
            # Fallback to collaborative decision making
            return await self._collaborative_decision(decision_context)
            
        except Exception as e:
            self.logger.error(f"Error in strategic decision making: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _collaborative_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback collaborative decision making"""
        # Determine which agents should participate
        participants = []
        decision_type = decision_context.get("type", "general")
        
        # Add relevant C-Suite members
        if decision_type in ["strategic", "general"]:
            participants.extend(["CEO", "CFO", "CSO"])
        if decision_type in ["technical", "product"]:
            participants.extend(["CTO", "CMO"])
        if decision_type in ["operational", "people"]:
            participants.extend(["COO", "CHRO"])
        if decision_type in ["financial", "investment"]:
            participants.extend(["CFO", "Investor"])
        if decision_type in ["vision", "innovation"]:
            participants.extend(["Founder", "CEO"])
        
        # Collect input from participants
        inputs = {}
        for role in participants:
            agent = self.get_agent(role)
            if agent:
                try:
                    if hasattr(agent, 'process_message'):
                        response = await agent.process_message(
                            f"Please provide your perspective on this decision: {decision_context}",
                            decision_context
                        )
                        inputs[role] = response
                except Exception as e:
                    self.logger.error(f"Error getting input from {role}: {e}")
        
        # Simple consensus logic
        return {
            "status": "completed",
            "decision_type": decision_type,
            "participants": participants,
            "inputs": inputs,
            "recommendation": "Proceed with collaborative approach based on stakeholder input",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_business_workflow(self, workflow_name: str, workflow_params: Dict[str, Any]) -> str:
        """Execute a business-specific workflow"""
        try:
            if self.aos:
                # Use AOS workflow orchestration
                workflow_definition = self._get_business_workflow_definition(workflow_name, workflow_params)
                return await self.aos.orchestrate_workflow(workflow_definition)
            
            # Fallback workflow execution
            return await self._execute_fallback_workflow(workflow_name, workflow_params)
            
        except Exception as e:
            self.logger.error(f"Error executing business workflow {workflow_name}: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    def _get_business_workflow_definition(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get business workflow definition for AOS orchestration"""
        workflows = {
            "product_launch": {
                "id": f"product_launch_{datetime.now().timestamp()}",
                "name": "Product Launch",
                "steps": [
                    {"id": "market_analysis", "agent": "CMO", "action": "analyze_market"},
                    {"id": "product_strategy", "agent": "CEO", "action": "define_strategy"}, 
                    {"id": "tech_implementation", "agent": "CTO", "action": "plan_development"},
                    {"id": "financial_planning", "agent": "CFO", "action": "budget_allocation"},
                    {"id": "operational_readiness", "agent": "COO", "action": "prepare_operations"},
                    {"id": "launch_execution", "agent": "CEO", "action": "coordinate_launch"}
                ],
                "params": params
            },
            "funding_round": {
                "id": f"funding_round_{datetime.now().timestamp()}",
                "name": "Funding Round",
                "steps": [
                    {"id": "financial_assessment", "agent": "CFO", "action": "assess_finances"},
                    {"id": "investor_outreach", "agent": "Investor", "action": "identify_investors"},
                    {"id": "pitch_preparation", "agent": "Founder", "action": "prepare_pitch"},
                    {"id": "due_diligence", "agent": "CEO", "action": "prepare_dd"},
                    {"id": "negotiation", "agent": "Founder", "action": "negotiate_terms"},
                    {"id": "closing", "agent": "CFO", "action": "close_round"}
                ],
                "params": params
            }
        }
        
        return workflows.get(workflow_name, {
            "id": f"generic_{datetime.now().timestamp()}",
            "name": workflow_name,
            "steps": [{"id": "execute", "agent": "CEO", "action": "coordinate"}],
            "params": params
        })
    
    async def _execute_fallback_workflow(self, workflow_name: str, params: Dict[str, Any]) -> str:
        """Fallback workflow execution without AOS"""
        self.logger.info(f"Executing fallback workflow: {workflow_name}")
        return f"fallback_{workflow_name}_{datetime.now().timestamp()}"
    
    def get_agent(self, role: str):
        """Get agent by role"""
        # Check C-Suite
        if role in self.c_suite:
            return self.c_suite[role]
        
        # Check special roles
        if role == "Founder":
            return self.founder
        elif role == "Investor":
            return self.investor
        
        # Fallback to MVP manager
        if self.mvp_manager:
            return self.mvp_manager.get_agent(role.lower())
        
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available business agents"""
        agents = []
        
        # Add C-Suite agents
        for role, agent in self.c_suite.items():
            agents.append({
                "role": role,
                "type": "C-Suite",
                "status": "active" if agent else "inactive"
            })
        
        # Add Founder
        if self.founder:
            agents.append({
                "role": "Founder",
                "type": "Stakeholder", 
                "status": "active"
            })
        
        # Add Investor
        if self.investor:
            agents.append({
                "role": "Investor",
                "type": "Stakeholder",
                "status": "active" 
            })
        
        return agents
    
    async def ask_agent(self, role: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Ask a specific agent a question"""
        agent = self.get_agent(role)
        if not agent:
            return f"Agent {role} not available"
        
        try:
            if hasattr(agent, 'process_message'):
                return await agent.process_message(message, context or self.business_context)
            else:
                return f"Agent {role} does not support message processing"
                
        except Exception as e:
            self.logger.error(f"Error asking agent {role}: {e}")
            return f"Error communicating with {role}: {e}"
    
    async def get_business_status(self) -> Dict[str, Any]:
        """Get comprehensive business status"""
        status = {
            "business_context": self.business_context,
            "agents": self.list_agents(),
            "aos_available": AOS_AVAILABLE,
            "c_suite_available": C_SUITE_AVAILABLE,
            "stakeholder_agents_available": STAKEHOLDER_AGENTS_AVAILABLE,
            "system_type": "BusinessInfinity",
            "version": "2.0"
        }
        
        # Add AOS status if available
        if self.aos:
            aos_status = await self.aos.get_aos_status()
            status["aos_status"] = aos_status
        
        return status
    
    async def shutdown(self):
        """Graceful shutdown of Business Infinity"""
        try:
            self.logger.info("Shutting down Business Infinity...")
            
            # Shutdown AOS if available
            if self.aos and hasattr(self.aos, 'shutdown'):
                await self.aos.shutdown()
            
            self.logger.info("Business Infinity shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Factory function for easy instantiation
def create_business_infinity(config: BusinessInfinityConfig = None) -> BusinessInfinity:
    """Create and initialize Business Infinity instance"""
    return BusinessInfinity(config)


# Global instance for backward compatibility
business_infinity = None

def get_business_infinity() -> BusinessInfinity:
    """Get global Business Infinity instance"""
    global business_infinity
    if business_infinity is None:
        business_infinity = create_business_infinity()
    return business_infinity