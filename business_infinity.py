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

# Import AOS foundation - use AOS as the core infrastructure layer
try:
    from RealmOfAgents.AgentOperatingSystem.AgentOperatingSystem import AgentOperatingSystem
    from RealmOfAgents.AgentOperatingSystem.config import AOSConfig, default_config
    from RealmOfAgents.AgentOperatingSystem.storage.manager import UnifiedStorageManager
    from RealmOfAgents.AgentOperatingSystem.environment import UnifiedEnvManager
    from RealmOfAgents.AgentOperatingSystem.mcp_servicebus_client import MCPServiceBusClient
    from RealmOfAgents.AgentOperatingSystem.aos_auth import UnifiedAuthHandler
    from RealmOfAgents.AgentOperatingSystem.ml_pipeline_ops import trigger_lora_training, aml_infer
    from autonomous_boardroom import AutonomousBoardroom, create_autonomous_boardroom
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    logging.warning("AOS not available, using fallback implementations")

# Import local mentor mode implementation
try:
    from core.mentor_mode import MentorMode
    LOCAL_MENTOR_MODE_AVAILABLE = True
except ImportError:
    LOCAL_MENTOR_MODE_AVAILABLE = False
    logging.warning("Local mentor mode not available")

# MCP connectivity managed through AOS
# No direct Azure Service Bus imports needed - use AOS MCPServiceBusClient

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
    from mvp_agents import LeadershipAgent, AgentManager as MVPAgentManager


class BusinessInfinityConfig:
    """Configuration for Business Infinity autonomous boardroom"""
    
    def __init__(self):
        self.aos_config = default_config if AOS_AVAILABLE else None
        self.business_name = os.getenv("BUSINESS_NAME", "Business Infinity")
        self.industry = os.getenv("BUSINESS_INDUSTRY", "Technology")
        self.stage = os.getenv("BUSINESS_STAGE", "Growth")  # Startup, Growth, Mature
        self.market = os.getenv("TARGET_MARKET", "Global")
        
        # Autonomous Boardroom Configuration
        self.enable_autonomous_boardroom = True
        self.perpetual_operation = True
        self.session_frequency_hours = int(os.getenv("BOARDROOM_SESSION_FREQUENCY", "1"))
        
        # Legendary Expertise Configuration
        self.enable_lora_adapters = True
        self.mentor_mode_enabled = bool(os.getenv("MENTOR_MODE_ENABLED", "false").lower() == "true")
        self.legendary_profiles_path = os.getenv("LEGENDARY_PROFILES_PATH", "config/legendary_profiles.json")
        
        # MCP Server Configuration
        self.mcp_servers = {
            "linkedin": os.getenv("LINKEDIN_MCP_QUEUE", "bi-linkedin-mcp"),
            "reddit": os.getenv("REDDIT_MCP_QUEUE", "bi-reddit-mcp"),
            "erpnext": os.getenv("ERPNEXT_MCP_QUEUE", "bi-erpnext-mcp")
        }
        
        # Service Bus Configuration
        self.service_bus_connection = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
        
        # Operational configuration
        self.decision_threshold = float(os.getenv("DECISION_THRESHOLD", "0.7"))
        self.collaboration_mode = "legendary_consensus"  # legendary_consensus, delegation, hierarchy
        self.reporting_enabled = True
        self.metrics_collection = True
        self.performance_tracking = True


class BusinessInfinity:
    """
    Business Infinity - Perpetual Autonomous Boardroom
    
    A fully autonomous boardroom of legendary AI agents that operates perpetually,
    making strategic decisions and executing business operations. Each agent possesses
    legendary domain knowledge through LoRA adapters from FineTunedLLM AML.
    
    Connected to conventional business systems through MCP servers via Azure Service Bus.
    """
    
    def __init__(self, config: BusinessInfinityConfig = None):
        self.config = config or BusinessInfinityConfig()
        self.logger = logging.getLogger(__name__)
        
        # Core systems
        self.aos = None
        self.autonomous_boardroom = None
        self.lora_manager = None
        self.mentor_mode = None
        self.service_bus_client = None
        
        # Business context with legendary profiles
        self.business_context = {
            "name": self.config.business_name,
            "industry": self.config.industry,
            "stage": self.config.stage,
            "market": self.config.market,
            "autonomous_boardroom_enabled": self.config.enable_autonomous_boardroom,
            "legendary_expertise_enabled": self.config.enable_lora_adapters,
            "initialized_at": datetime.now()
        }
        
        # MCP-UI Dashboard configuration
        self.mcp_ui_config = {
            "admin_mode_enabled": True,
            "aos_monitoring_enabled": True,
            "mentor_mode_enabled": self.config.mentor_mode_enabled,
            "boardroom_monitoring_enabled": True
        }
        
        # Fallback MVP manager for degraded operation
        self.mvp_manager = None
        if not AOS_AVAILABLE:
            self.mvp_manager = MVPAgentManager()
        
        # Initialize systems
        asyncio.create_task(self._initialize_systems())
    
    async def _initialize_systems(self):
        """Initialize all core systems for the autonomous boardroom"""
        try:
            self.logger.info("Initializing Business Infinity autonomous systems...")
            
            # Initialize AOS foundation
            if AOS_AVAILABLE:
                self.aos = AgentOperatingSystem(self.config.aos_config)
                # Use AOS ML pipeline instead of direct FineTunedLLM
                self.storage_manager = UnifiedStorageManager()
                self.auth_handler = UnifiedAuthHandler()
                
                # Initialize mentor mode through AOS if enabled
                if self.config.mentor_mode_enabled:
                    if LOCAL_MENTOR_MODE_AVAILABLE:
                        self.mentor_mode = MentorMode()
                        await self.mentor_mode.initialize()
                        self.logger.info("Local Mentor Mode initialized")
                
                # Initialize MCP Service Bus through AOS
                if self.config.service_bus_connection:
                    self.service_bus_client = MCPServiceBusClient(
                        self.config.service_bus_connection,
                        self.config.service_bus_topic or "business-infinity"
                    )
                    self.logger.info("MCP Service Bus client initialized through AOS")
                
                self.logger.info("AOS initialized successfully")
            
            # Initialize Autonomous Boardroom
            if self.config.enable_autonomous_boardroom:
                self.autonomous_boardroom = create_autonomous_boardroom(self.config.aos_config)
                
                # Configure boardroom with LoRA manager
                if self.lora_manager:
                    self.autonomous_boardroom.lora_manager = self.lora_manager
                
                # Configure Service Bus client
                if self.service_bus_client:
                    self.autonomous_boardroom.service_bus_client = self.service_bus_client
                
                self.logger.info("Autonomous Boardroom initialized successfully")
            
            # Initialize MCP-UI Dashboard connections
            await self._initialize_mcp_ui_dashboard()
            
            self.logger.info("Business Infinity autonomous systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Infinity systems: {e}")
            raise
    
    async def _initialize_mcp_ui_dashboard(self):
        """Initialize MCP-UI dashboard for administration and monitoring"""
        try:
            # Configure MCP-UI for BI administration
            mcp_ui_config = {
                "boardroom_monitoring": {
                    "enabled": True,
                    "update_frequency": "real-time",
                    "metrics": ["agent_performance", "decision_confidence", "execution_status"]
                },
                "aos_administration": {
                    "enabled": True,
                    "admin_mode": True,
                    "monitoring_level": "detailed"
                },
                "mentor_mode": {
                    "enabled": self.config.mentor_mode_enabled,
                    "training_dashboard": True,
                    "lora_management": True
                },
                "mcp_servers": {
                    "linkedin": {"status": "monitoring", "queue": self.config.mcp_servers["linkedin"]},
                    "reddit": {"status": "monitoring", "queue": self.config.mcp_servers["reddit"]},
                    "erpnext": {"status": "monitoring", "queue": self.config.mcp_servers["erpnext"]}
                }
            }
            
            # Store configuration for MCP-UI integration
            self.mcp_ui_config.update(mcp_ui_config)
            
            self.logger.info("MCP-UI dashboard configuration initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP-UI dashboard: {e}")
    
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
    
    # Autonomous Boardroom Operations API
    async def make_strategic_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a strategic decision through the autonomous boardroom of legendary agents
        
        Args:
            decision_context: Context and parameters for the decision
            
        Returns:
            Decision result with legendary recommendations and rationale
        """
        try:
            if self.autonomous_boardroom:
                # Route decision through autonomous boardroom
                return await self.autonomous_boardroom._make_boardroom_decision(decision_context)
            
            elif self.aos:
                # Fallback to AOS decision orchestration
                return await self.aos.orchestrate_leadership_decision(decision_context)
            
            else:
                # Final fallback to collaborative decision
                return await self._collaborative_decision(decision_context)
                
        except Exception as e:
            self.logger.error(f"Error in strategic decision making: {e}")
            return {"status": "error", "error": str(e)}
    
    async def execute_legendary_consultation(self, consultation_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a consultation with legendary agents for specific expertise
        
        Args:
            consultation_request: Request for legendary expertise consultation
            
        Returns:
            Consultation results from legendary agents
        """
        if not self.autonomous_boardroom:
            return {"status": "error", "error": "Autonomous boardroom not available"}
        
        try:
            # Route consultation through specific legendary agents
            requested_roles = consultation_request.get("roles", [])
            expertise_areas = consultation_request.get("expertise", [])
            context = consultation_request.get("context", {})
            
            consultation_results = {}
            
            # Get consultation from each requested legendary agent
            for role_str in requested_roles:
                try:
                    from .autonomous_boardroom import BoardroomRole
                    role = BoardroomRole(role_str)
                    
                    if role in self.autonomous_boardroom.agents:
                        agent = self.autonomous_boardroom.agents[role]
                        legendary_advice = await self.autonomous_boardroom._get_legendary_recommendation(
                            agent, context
                        )
                        
                        consultation_results[role_str] = {
                            "legendary_profile": agent.legendary_expertise.legend_profile,
                            "domain": agent.legendary_expertise.domain,
                            "advice": legendary_advice,
                            "expertise_areas": agent.legendary_expertise.expertise_areas
                        }
                        
                except Exception as e:
                    consultation_results[role_str] = {"error": str(e)}
            
            return {
                "status": "completed",
                "consultation_results": consultation_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in legendary consultation: {e}")
            return {"status": "error", "error": str(e)}
    
    async def train_legendary_expertise(self, training_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train LoRA adapters for legendary expertise using Mentor Mode
        
        Args:
            training_request: Training parameters and data
            
        Returns:
            Training results and updated adapter information
        """
        if not self.mentor_mode:
            return {"status": "error", "error": "Mentor Mode not available"}
        
        try:
            legendary_profile = training_request.get("legendary_profile")
            domain = training_request.get("domain")
            training_data = training_request.get("training_data")
            
            # Start LoRA adapter training
            training_job = await self.mentor_mode.start_training(
                legend_name=legendary_profile,
                domain=domain,
                training_data=training_data
            )
            
            return {
                "status": "training_started",
                "training_job_id": training_job.id,
                "legendary_profile": legendary_profile,
                "domain": domain,
                "estimated_completion": training_job.estimated_completion
            }
            
        except Exception as e:
            self.logger.error(f"Error starting legendary expertise training: {e}")
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

    async def train_agent_adapter(self, agent_role: str, training_data: Dict[str, Any]) -> str:
        """Train LoRA adapter for an agent using AOS ML pipeline"""
        if not AOS_AVAILABLE:
            return "AOS not available for agent training"
            
        try:
            # Use AOS ML pipeline for training
            training_params = {
                "model_name": training_data.get("model_name", "gpt-4"),
                "data_path": training_data.get("data_path"),
                "output_dir": f"/models/{agent_role}_lora",
                "agent_role": agent_role
            }
            
            adapters = training_data.get("adapters", [])
            result = await trigger_lora_training(training_params, adapters)
            
            self.logger.info(f"Agent {agent_role} training initiated: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to train agent {agent_role}: {e}")
            return f"Training failed: {str(e)}"
    
    async def infer_with_agent(self, agent_role: str, prompt: str) -> Any:
        """Perform inference with an agent using AOS ML pipeline"""
        if not AOS_AVAILABLE:
            return "AOS not available for agent inference"
            
        try:
            result = await aml_infer(agent_role, prompt)
            return result
        except Exception as e:
            self.logger.error(f"Failed to infer with agent {agent_role}: {e}")
            return f"Inference failed: {str(e)}"
    
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