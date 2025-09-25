"""
Business Infinity - Autonomous Boardroom

A perpetual, fully autonomous boardroom of agents comprising Investor, Founder, 
and C-Suite members. Each agent possesses legendary domain knowledge through 
LoRA adapters from FineTunedLLM AML, connected to AOS via Azure Service Bus.

The boardroom operates continuously, making strategic decisions, monitoring 
performance, and executing business operations through integration with 
conventional business systems via MCP servers.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Import AOS foundation
try:
    from RealmOfAgents.AgentOperatingSystem.AgentOperatingSystem import AgentOperatingSystem
    from RealmOfAgents.AgentOperatingSystem.config import AOSConfig, default_config
    from RealmOfAgents.AgentOperatingSystem.messaging import Message, MessageBus
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    logging.warning("AOS not available")
    
    # Create fallback AOSConfig for type annotations
    class AOSConfig:
        def __init__(self):
            pass

# Import audit trail system
from core.audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, 
    audit_log, get_audit_manager
)

# Import FineTunedLLM for LoRA adapters
try:
    from RealmOfAgents.FineTunedLLM.lora_manager import LoRAManager
    from RealmOfAgents.FineTunedLLM.domain_expertise import DomainExpertiseLoader
    FINETUNED_LLM_AVAILABLE = True
except ImportError:
    FINETUNED_LLM_AVAILABLE = False
    logging.warning("FineTunedLLM not available")

# Import local adapter system
try:
    from adapters import (
        initialize_adapter_system, 
        generate_boardroom_response,
        evaluate_boardroom_response,
        start_learning_cycle,
        get_system_status,
        adapter_orchestrator
    )
    LOCAL_ADAPTER_SYSTEM_AVAILABLE = True
except ImportError:
    LOCAL_ADAPTER_SYSTEM_AVAILABLE = False
    logging.warning("Local adapter system not available")

# Azure Service Bus for MCP connectivity
try:
    from azure.servicebus import ServiceBusClient, ServiceBusMessage
    from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
    AZURE_SERVICEBUS_AVAILABLE = True
except ImportError:
    AZURE_SERVICEBUS_AVAILABLE = False
    logging.warning("Azure Service Bus not available")


class BoardroomRole(Enum):
    """Roles in the autonomous boardroom"""
    FOUNDER = "Founder"
    INVESTOR = "Investor"
    CEO = "CEO"
    CFO = "CFO" 
    CTO = "CTO"
    CMO = "CMO"
    COO = "COO"
    CHRO = "CHRO"
    CSO = "CSO"  # Chief Strategy Officer


class DecisionType(Enum):
    """Types of boardroom decisions"""
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    INVESTMENT = "investment"
    PRODUCT = "product"
    MARKET = "market"
    GOVERNANCE = "governance"


class BoardroomState(Enum):
    """States of the autonomous boardroom"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IN_SESSION = "in_session"
    DELIBERATING = "deliberating"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class LegendaryExpertise:
    """Represents legendary domain knowledge loaded via LoRA adapters"""
    domain: str
    legend_profile: str  # e.g., "Warren Buffett", "Steve Jobs", etc.
    lora_adapter_id: str
    expertise_areas: List[str]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class BoardroomAgent:
    """Represents a boardroom member with legendary expertise and voting capability"""
    agent_id: str
    role: BoardroomRole
    legendary_expertise: LegendaryExpertise
    assigned_purpose: str  # Specific purpose/mandate for this role
    voting_weight: float = 1.0  # Weight of this agent's vote
    mcp_connections: List[str] = field(default_factory=list)  # Connected MCP servers
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    current_tasks: List[str] = field(default_factory=list)
    status: str = "active"


@dataclass
class BoardroomVote:
    """Represents a single boardroom member's vote"""
    voter_id: str
    voter_role: BoardroomRole
    vote_value: float  # -1.0 to 1.0 (against to for)
    confidence: float  # 0.0 to 1.0
    reasoning: str
    lora_adapter_score: float  # Domain expertise score from LoRA adapter
    purpose_alignment: float  # How well the proposal aligns with voter's purpose
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BoardroomDecision:
    """Represents a boardroom decision with voting-based results"""
    decision_id: str
    proposal: str
    decision_type: DecisionType
    proposed_by: str
    votes: List[BoardroomVote] = field(default_factory=list)
    voting_results: Dict[str, Any] = field(default_factory=dict)
    final_decision: str = ""
    rationale: str = ""
    confidence_score: float = 0.0
    consensus_score: float = 0.0  # How aligned the votes were
    implementation_plan: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class AutonomousBoardroom:
    """
    The core autonomous boardroom that operates perpetually, making strategic
    decisions and executing business operations through legendary AI agents.
    """
    
    def __init__(self, aos_config: AOSConfig = None):
        self.config = aos_config or (default_config if AOS_AVAILABLE else AOSConfig())
        self.logger = logging.getLogger(__name__)
        
        # Initialize audit trail manager
        self.audit_manager = get_audit_manager()
        
        # Core systems
        self.aos = None
        self.lora_manager = None
        self.service_bus_client = None
        self.message_bus = None
        
        # Boardroom state
        self.state = BoardroomState.INITIALIZING
        self.agents: Dict[BoardroomRole, BoardroomAgent] = {}
        self.active_decisions: Dict[str, BoardroomDecision] = {}
        self.decision_history: List[BoardroomDecision] = []
        
        # MCP server connections
        self.mcp_servers = {
            "linkedin": "bi-linkedin-mcp",
            "reddit": "bi-reddit-mcp", 
            "erpnext": "bi-erpnext-mcp"
        }
        
        # Perpetual operation
        self.is_running = False
        self.session_frequency = timedelta(hours=1)  # Board sessions every hour
        self.last_session = None
        
        # Log boardroom initialization
        self.audit_manager.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            subject_id="autonomous_boardroom",
            subject_type="system",
            action="Autonomous Boardroom initialized",
            severity=AuditSeverity.MEDIUM,
            context={
                "session_frequency_hours": self.session_frequency.total_seconds() / 3600,
                "mcp_servers": list(self.mcp_servers.keys())
            },
            compliance_tags={"system_lifecycle", "business_governance"}
        )
        
        # Initialize systems
        asyncio.create_task(self._initialize_systems())
    
    async def _initialize_systems(self):
        """Initialize all core systems for the autonomous boardroom"""
        try:
            self.logger.info("Initializing Autonomous Boardroom systems...")
            
            # Initialize AOS
            if AOS_AVAILABLE:
                self.aos = AgentOperatingSystem(self.config)
                self.message_bus = self.aos.message_bus
                self.logger.info("AOS initialized successfully")
            
            # Initialize LoRA Managers (external and/or local)
            if FINETUNED_LLM_AVAILABLE:
                self.lora_manager = LoRAManager()
                await self.lora_manager.initialize()
                self.logger.info("FineTunedLLM LoRA Manager initialized")
            
            # Initialize Conversation System
            try:
                from conversations.boardroom_conversations import get_conversation_manager
                self.conversation_manager = get_conversation_manager()
                self.logger.info("Boardroom Conversation System initialized")
            except ImportError as e:
                self.logger.warning(f"Failed to initialize conversation system: {e}")
                self.conversation_manager = None
            
            # Initialize local adapter system
            if LOCAL_ADAPTER_SYSTEM_AVAILABLE:
                try:
                    self.adapter_orchestrator = await initialize_adapter_system()
                    self.logger.info("Local LoRA Adapter System initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize local adapter system: {e}")
                    self.adapter_orchestrator = None
            else:
                self.adapter_orchestrator = None
            
            # Initialize Azure Service Bus
            if AZURE_SERVICEBUS_AVAILABLE:
                connection_string = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
                if connection_string:
                    self.service_bus_client = AsyncServiceBusClient.from_connection_string(connection_string)
                    self.logger.info("Azure Service Bus client initialized")
            
            # Initialize legendary agents
            await self._initialize_legendary_agents()
            
            # Start perpetual operation
            self.state = BoardroomState.ACTIVE
            await self._start_perpetual_operation()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Autonomous Boardroom: {e}")
            self.state = BoardroomState.ERROR
    
    async def _initialize_legendary_agents(self):
        """Initialize all boardroom agents with legendary expertise"""
        # Define legendary profiles for each role
        legendary_profiles = {
            BoardroomRole.FOUNDER: {
                "legend": "Steve Jobs",
                "domain": "Innovation & Vision",
                "expertise": ["product_vision", "innovation", "brand_building", "market_disruption"]
            },
            BoardroomRole.INVESTOR: {
                "legend": "Warren Buffett",
                "domain": "Investment Strategy", 
                "expertise": ["value_investing", "market_analysis", "risk_assessment", "portfolio_management"]
            },
            BoardroomRole.CEO: {
                "legend": "Jack Welch",
                "domain": "Executive Leadership",
                "expertise": ["strategic_leadership", "organizational_transformation", "stakeholder_management"]
            },
            BoardroomRole.CFO: {
                "legend": "Jamie Dimon",
                "domain": "Financial Leadership",
                "expertise": ["financial_strategy", "risk_management", "capital_allocation", "governance"]
            },
            BoardroomRole.CTO: {
                "legend": "Satya Nadella",
                "domain": "Technology Leadership",
                "expertise": ["technology_strategy", "digital_transformation", "innovation_management"]
            },
            BoardroomRole.CMO: {
                "legend": "Seth Godin",
                "domain": "Marketing Excellence",
                "expertise": ["brand_strategy", "customer_engagement", "market_positioning", "growth_hacking"]
            },
            BoardroomRole.COO: {
                "legend": "Sheryl Sandberg",
                "domain": "Operational Excellence",
                "expertise": ["operations_optimization", "process_improvement", "scaling", "execution"]
            },
            BoardroomRole.CHRO: {
                "legend": "Patty McCord",
                "domain": "People Leadership",
                "expertise": ["talent_strategy", "culture_building", "performance_management", "leadership_development"]
            },
            BoardroomRole.CSO: {
                "legend": "Michael Porter",
                "domain": "Strategic Planning",
                "expertise": ["competitive_strategy", "strategic_planning", "market_analysis", "value_creation"]
            }
        }
        
        # Initialize each agent with legendary expertise
        for role, profile in legendary_profiles.items():
            try:
                # Load LoRA adapter for legendary expertise
                lora_adapter_id = None
                if self.lora_manager:
                    lora_adapter_id = await self.lora_manager.load_legendary_adapter(
                        legend_name=profile["legend"],
                        domain=profile["domain"]
                    )
                
                # Create legendary expertise profile
                expertise = LegendaryExpertise(
                    domain=profile["domain"],
                    legend_profile=profile["legend"],
                    lora_adapter_id=lora_adapter_id or f"fallback_{role.value.lower()}",
                    expertise_areas=profile["expertise"]
                )
                
                # Create boardroom agent
                agent = BoardroomAgent(
                    role=role,
                    agent_id=f"{role.value.lower()}_agent_{datetime.now().timestamp()}",
                    legendary_expertise=expertise,
                    mcp_connections=list(self.mcp_servers.keys())  # Connect to all MCP servers
                )
                
                # Register with AOS if available
                if self.aos:
                    await self.aos.register_leadership_agent(role.value, {
                        "legendary_profile": profile["legend"],
                        "domain": profile["domain"],
                        "lora_adapter": lora_adapter_id
                    })
                
                self.agents[role] = agent
                self.logger.info(f"Initialized {role.value} agent with {profile['legend']} legendary expertise")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {role.value} agent: {e}")
    
    async def _start_perpetual_operation(self):
        """Start the perpetual autonomous operation"""
        self.is_running = True
        self.logger.info("Starting perpetual autonomous boardroom operation")
        
        # Start background tasks
        asyncio.create_task(self._perpetual_session_loop())
        asyncio.create_task(self._monitor_business_environment())
        asyncio.create_task(self._execute_decisions())
        asyncio.create_task(self._maintain_mcp_connections())
    
    async def _perpetual_session_loop(self):
        """Main loop for perpetual boardroom sessions"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check if it's time for a new session
                if (self.last_session is None or 
                    current_time - self.last_session >= self.session_frequency):
                    
                    await self._conduct_boardroom_session()
                    self.last_session = current_time
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in perpetual session loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _conduct_boardroom_session(self):
        """Conduct an autonomous boardroom session"""
        self.logger.info("Conducting autonomous boardroom session")
        self.state = BoardroomState.IN_SESSION
        
        try:
            # Gather business intelligence from MCP servers
            business_intelligence = await self._gather_business_intelligence()
            
            # Analyze current business state
            business_state = await self._analyze_business_state(business_intelligence)
            
            # Identify decisions needed
            required_decisions = await self._identify_required_decisions(business_state)
            
            # Make decisions through legendary agent collaboration
            for decision_context in required_decisions:
                await self._make_boardroom_decision(decision_context)
            
            # Update agent performance metrics
            await self._update_agent_performance()
            
            self.state = BoardroomState.ACTIVE
            self.logger.info("Boardroom session completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during boardroom session: {e}")
            self.state = BoardroomState.ERROR
    
    async def _gather_business_intelligence(self) -> Dict[str, Any]:
        """Gather business intelligence from MCP servers"""
        intelligence = {}
        
        for server_name, queue_name in self.mcp_servers.items():
            try:
                # Query MCP server for business data
                query_message = {
                    "type": "business_intelligence_query",
                    "server": server_name,
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "metrics": ["performance", "engagement", "opportunities", "risks"],
                        "timeframe": "last_24h"
                    }
                }
                
                # Send query via Service Bus
                if self.service_bus_client:
                    await self._send_mcp_query(queue_name, query_message)
                
                # For now, simulate response data
                intelligence[server_name] = {
                    "status": "active",
                    "metrics": self._simulate_business_metrics(server_name),
                    "alerts": [],
                    "opportunities": []
                }
                
            except Exception as e:
                self.logger.error(f"Failed to gather intelligence from {server_name}: {e}")
                intelligence[server_name] = {"status": "error", "error": str(e)}
        
        return intelligence
    
    def _simulate_business_metrics(self, server_name: str) -> Dict[str, Any]:
        """Simulate business metrics from different sources"""
        import random
        
        base_metrics = {
            "linkedin": {
                "connections": random.randint(5000, 15000),
                "engagement_rate": round(random.uniform(2.5, 8.5), 2),
                "lead_generation": random.randint(10, 50),
                "brand_mentions": random.randint(100, 500)
            },
            "reddit": {
                "brand_mentions": random.randint(50, 200),
                "sentiment_score": round(random.uniform(0.3, 0.8), 2),
                "community_engagement": random.randint(20, 100),
                "trending_topics": ["ai", "automation", "business"]
            },
            "erpnext": {
                "revenue": round(random.uniform(100000, 1000000), 2),
                "expenses": round(random.uniform(50000, 500000), 2),
                "customer_satisfaction": round(random.uniform(4.0, 5.0), 1),
                "operational_efficiency": round(random.uniform(0.7, 0.95), 2)
            }
        }
        
        return base_metrics.get(server_name, {})
    
    async def _analyze_business_state(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current business state using legendary agent expertise"""
        analysis = {
            "overall_health": "good",
            "key_metrics": {},
            "risks": [],
            "opportunities": [],
            "recommendations": {}
        }
        
        # Each agent analyzes from their legendary perspective
        for role, agent in self.agents.items():
            if agent.is_active:
                agent_analysis = await self._get_agent_analysis(agent, intelligence)
                analysis["recommendations"][role.value] = agent_analysis
        
        return analysis
    
    async def _get_agent_analysis(self, agent: BoardroomAgent, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis from a specific legendary agent"""
        # This would use the LoRA adapter to get legendary expertise
        # For now, simulate based on role and expertise
        
        expertise = agent.legendary_expertise
        analysis = {
            "legend_perspective": f"Analysis from {expertise.legend_profile} perspective",
            "key_insights": [],
            "recommendations": [],
            "confidence": 0.85
        }
        
        # Role-specific analysis based on legendary expertise
        if agent.role == BoardroomRole.INVESTOR:
            analysis["key_insights"] = [
                "Market valuation appears strong based on performance metrics",
                "Risk-adjusted returns show positive trajectory", 
                "Investment opportunities identified in growth segments"
            ]
            analysis["recommendations"] = [
                "Consider strategic investment in emerging market segments",
                "Diversify portfolio to reduce concentration risk",
                "Monitor cash flow patterns for optimization opportunities"
            ]
        
        elif agent.role == BoardroomRole.FOUNDER:
            analysis["key_insights"] = [
                "Product-market fit indicators showing positive signals",
                "Innovation pipeline needs acceleration",
                "Brand differentiation opportunities exist"
            ]
            analysis["recommendations"] = [
                "Invest in breakthrough innovation projects",
                "Strengthen brand positioning in key markets",
                "Build strategic partnerships for market expansion"
            ]
        
        # Add more role-specific analysis...
        
        return analysis
    
    async def _identify_required_decisions(self, business_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify decisions that need to be made"""
        decisions = []
        
        # Analyze business state to identify decision points
        recommendations = business_state.get("recommendations", {})
        
        # Strategic decisions from CEO/CSO
        if "CEO" in recommendations or "CSO" in recommendations:
            decisions.append({
                "type": DecisionType.STRATEGIC,
                "context": "Strategic planning and direction based on current market analysis",
                "urgency": "medium",
                "participants": [BoardroomRole.CEO, BoardroomRole.CSO, BoardroomRole.FOUNDER]
            })
        
        # Financial decisions from CFO/Investor
        if "CFO" in recommendations or "Investor" in recommendations:
            decisions.append({
                "type": DecisionType.FINANCIAL,
                "context": "Financial strategy and investment allocation",
                "urgency": "high",
                "participants": [BoardroomRole.CFO, BoardroomRole.INVESTOR, BoardroomRole.CEO]
            })
        
        # Add more decision identification logic...
        
        return decisions
    
    async def _make_boardroom_decision(self, decision_context: Dict[str, Any]) -> BoardroomDecision:
        """Make a boardroom decision through voting by legendary agents with LoRA adapter scoring"""
        self.state = BoardroomState.DELIBERATING
        
        decision_id = f"decision_{datetime.now().timestamp()}"
        proposal = decision_context.get("proposal", "")
        decision_type = DecisionType(decision_context["type"])
        
        # Log decision initiation
        self.audit_manager.log_event(
            event_type=AuditEventType.AGENT_PROPOSAL,
            subject_id=decision_context.get("proposed_by", "system"),
            subject_type="agent" if decision_context.get("proposed_by", "system") != "system" else "system",
            action=f"Initiated boardroom decision: {decision_type.value}",
            context={
                "decision_id": decision_id,
                "proposal": proposal,
                "decision_type": decision_type.value
            },
            rationale=f"Decision proposed: {proposal}",
            severity=AuditSeverity.HIGH,
            compliance_tags={"business_governance", "decision_making"}
        )
        
        decision = BoardroomDecision(
            decision_id=decision_id,
            proposal=proposal,
            decision_type=decision_type,
            proposed_by=decision_context.get("proposed_by", "system")
        )
        
        # Collect votes from all active boardroom members
        decision.votes = await self._collect_boardroom_votes(proposal, decision_type)
        
        # Calculate voting results with weighted scoring
        decision.voting_results = await self._calculate_voting_results(decision.votes)
        
        # Make final decision based on voting outcomes
        decision.final_decision = await self._determine_final_decision(decision.votes, decision.voting_results)
        
        # Generate comprehensive rationale based on all votes
        decision.rationale = await self._generate_voting_rationale(decision.votes, decision.voting_results)
        
        # Calculate confidence and consensus scores
        decision.confidence_score = decision.voting_results.get("confidence_score", 0.0)
        decision.consensus_score = decision.voting_results.get("consensus_score", 0.0)
        
        # Create implementation plan based on decision
        decision.implementation_plan = await self._create_implementation_plan(
            decision.final_decision, decision_type
        )
        
        # Determine status based on voting threshold and consensus
        decision.status = await self._determine_decision_status(decision.voting_results)
        
        # Store decision
        self.active_decisions[decision_id] = decision
        
        # Log comprehensive boardroom decision
        self.audit_manager.log_boardroom_decision(
            decision_id=decision_id,
            decision_type=decision_type.value,
            proposed_by=decision.proposed_by,
            final_decision=decision.final_decision,
            rationale=decision.rationale,
            votes=[{
                "voter_id": vote.voter_id,
                "voter_role": vote.voter_role.value,
                "vote_value": vote.vote_value,
                "confidence": vote.confidence,
                "rationale": vote.rationale
            } for vote in decision.votes],
            confidence_score=decision.confidence_score,
            consensus_score=decision.consensus_score
        )
        
        self.logger.info(f"Boardroom decision made via voting: {decision_id} - Status: {decision.status}")
        return decision
    
    async def _collect_boardroom_votes(self, proposal: str, decision_type: DecisionType) -> List[BoardroomVote]:
        """Collect votes from all active boardroom members using LoRA adapter scoring"""
        try:
            votes = []
            
            # Get all active boardroom agents
            active_agents = [agent for agent in self.agents.values() if agent.status == "active"]
            
            for agent in active_agents:
                vote = await self._get_agent_vote(agent, proposal, decision_type)
                if vote:
                    votes.append(vote)
            
            self.logger.info(f"Collected {len(votes)} votes for proposal: {proposal[:50]}...")
            return votes
            
        except Exception as e:
            self.logger.error(f"Failed to collect boardroom votes: {e}")
            return []
    
    async def _get_agent_vote(self, agent: BoardroomAgent, proposal: str, decision_type: DecisionType) -> Optional[BoardroomVote]:
        """Get a single agent's vote based on their LoRA adapter scoring and assigned purpose"""
        try:
            # Get LoRA adapter score using legendary expertise
            lora_score = await self._get_lora_adapter_score(agent, proposal, decision_type)
            
            # Calculate purpose alignment score
            purpose_alignment = await self._calculate_purpose_alignment(agent, proposal, decision_type)
            
            # Combine scores to determine vote value
            vote_value = await self._calculate_vote_value(lora_score, purpose_alignment, agent.role)
            
            # Calculate confidence based on LoRA adapter performance and purpose clarity
            confidence = await self._calculate_vote_confidence(lora_score, purpose_alignment, agent)
            
            # Generate reasoning using legendary expertise
            reasoning = await self._generate_vote_reasoning(agent, proposal, lora_score, purpose_alignment)
            
            vote = BoardroomVote(
                voter_id=agent.agent_id,
                voter_role=agent.role,
                vote_value=vote_value,
                confidence=confidence,
                reasoning=reasoning,
                lora_adapter_score=lora_score,
                purpose_alignment=purpose_alignment
            )
            
            # Log individual agent vote with comprehensive audit information
            self.audit_manager.log_agent_vote(
                voter_id=agent.agent_id,
                voter_role=agent.role.value,
                decision_id="",  # Will be set by calling method
                vote_value=vote_value,
                rationale=reasoning,
                evidence=[f"LoRA adapter score: {lora_score}", f"Purpose alignment: {purpose_alignment}"],
                confidence=confidence
            )
            
            self.logger.debug(f"Agent {agent.agent_id} voted {vote_value:.2f} with {confidence:.2f} confidence")
            return vote
            
        except Exception as e:
            self.logger.error(f"Failed to get vote from agent {agent.agent_id}: {e}")
            
            # Log voting failure
            self.audit_manager.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                subject_id=agent.agent_id,
                subject_type="agent",
                subject_role=agent.role.value,
                action="Failed to cast vote",
                severity=AuditSeverity.HIGH,
                context={
                    "proposal": proposal[:100] + "..." if len(proposal) > 100 else proposal,
                    "decision_type": decision_type.value,
                    "error": str(e)
                },
                compliance_tags={"business_governance", "system_error"}
            )
            return None
    
    async def _synthesize_decision(self, decision: BoardroomDecision) -> str:
        """Synthesize final decision from all legendary recommendations"""
        # Use AOS decision engine if available
        if self.aos:
            synthesis_result = await self.aos.make_decision({
                "type": decision.decision_type.value,
                "context": decision.context,
                "recommendations": decision.recommendations
            })
            return synthesis_result.get("decision", "No consensus reached")
        
        # Fallback synthesis
        return f"Synthesized decision based on {len(decision.recommendations)} legendary perspectives"
    
    def _calculate_decision_confidence(self, decision: BoardroomDecision) -> float:
        """Calculate confidence score for the decision"""
        # Simple confidence calculation based on number of participants and consensus
        base_confidence = len(decision.recommendations) / len(BoardroomRole) * 0.8
        return min(base_confidence + 0.2, 1.0)
    
    async def _send_mcp_query(self, queue_name: str, message: Dict[str, Any]):
        """Send query to MCP server via Service Bus"""
        # Determine which MCP server based on queue name
        mcp_server = None
        for server, queue in self.mcp_servers.items():
            if queue == queue_name:
                mcp_server = server
                break
        
        # Log MCP interaction attempt
        self.audit_manager.log_mcp_interaction(
            mcp_server=mcp_server or queue_name,
            operation=message.get("type", "unknown"),
            subject_id="autonomous_boardroom",
            subject_type="system",
            success=False,  # Will update if successful
            request_data=message
        )
        
        try:
            if self.service_bus_client:
                async with self.service_bus_client:
                    sender = self.service_bus_client.get_queue_sender(queue_name=queue_name)
                    async with sender:
                        message_body = json.dumps(message)
                        sb_message = ServiceBusMessage(message_body)
                        await sender.send_messages(sb_message)
                
                # Log successful MCP interaction
                self.audit_manager.log_mcp_interaction(
                    mcp_server=mcp_server or queue_name,
                    operation=message.get("type", "unknown"),
                    subject_id="autonomous_boardroom",
                    subject_type="system",
                    success=True,
                    request_data=message
                )
        except Exception as e:
            # Log failed MCP interaction
            self.audit_manager.log_mcp_interaction(
                mcp_server=mcp_server or queue_name,
                operation=message.get("type", "unknown"),
                subject_id="autonomous_boardroom",
                subject_type="system",
                success=False,
                request_data=message,
                error_details=str(e)
            )
            raise
    
    async def _monitor_business_environment(self):
        """Continuously monitor the business environment"""
        while self.is_running:
            try:
                # Monitor for critical business events
                await self._check_business_alerts()
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring business environment: {e}")
                await asyncio.sleep(60)
    
    async def _execute_decisions(self):
        """Execute approved boardroom decisions"""
        while self.is_running:
            try:
                self.state = BoardroomState.EXECUTING
                
                # Execute pending decisions
                for decision_id, decision in list(self.active_decisions.items()):
                    if decision.execution_status == "pending":
                        await self._execute_decision(decision)
                
                self.state = BoardroomState.MONITORING
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error executing decisions: {e}")
                await asyncio.sleep(60)
    
    async def _execute_decision(self, decision: BoardroomDecision):
        """Execute a specific decision"""
        # Log decision execution start
        self.audit_manager.log_event(
            event_type=AuditEventType.BUSINESS_TRANSACTION,
            subject_id="autonomous_boardroom",
            subject_type="system",
            action=f"Executing decision: {decision.decision_type.value}",
            target=decision.decision_id,
            severity=AuditSeverity.HIGH,
            context={
                "decision_id": decision.decision_id,
                "decision_type": decision.decision_type.value,
                "final_decision": decision.final_decision,
                "implementation_plan": decision.implementation_plan
            },
            rationale=decision.rationale,
            metrics={
                "confidence_score": decision.confidence_score,
                "consensus_score": decision.consensus_score
            },
            compliance_tags={"business_execution", "decision_implementation"}
        )
        
        try:
            # Send execution instructions to relevant MCP servers
            execution_context = {
                "decision_id": decision.decision_id,
                "type": decision.decision_type.value,
                "action": decision.final_decision,
                "timestamp": datetime.now().isoformat()
            }
            
            # Route to appropriate MCP servers based on decision type
            target_servers = self._get_execution_servers(decision.decision_type)
            
            executed_successfully = []
            execution_errors = []
            
            for server in target_servers:
                if server in self.mcp_servers:
                    try:
                        await self._send_mcp_query(self.mcp_servers[server], {
                            "type": "execute_decision",
                            "context": execution_context
                        })
                        executed_successfully.append(server)
                        
                        # Log individual server execution
                        self.audit_manager.log_business_action(
                            system=server,
                            operation="execute_decision",
                            agent_id="autonomous_boardroom",
                            business_entity=decision.decision_id,
                            transaction_data=execution_context
                        )
                        
                    except Exception as server_error:
                        execution_errors.append({"server": server, "error": str(server_error)})
            
            # Determine overall execution status
            if executed_successfully and not execution_errors:
                decision.execution_status = "completed"
                execution_success = True
            elif executed_successfully and execution_errors:
                decision.execution_status = "partially_completed"
                execution_success = True
            else:
                decision.execution_status = "failed"
                execution_success = False
            
            decision.executed_at = datetime.now()
            
            # Log execution completion
            self.audit_manager.log_event(
                event_type=AuditEventType.BUSINESS_TRANSACTION,
                subject_id="autonomous_boardroom",
                subject_type="system",
                action=f"Decision execution {decision.execution_status}",
                target=decision.decision_id,
                severity=AuditSeverity.HIGH if execution_success else AuditSeverity.CRITICAL,
                context={
                    "decision_id": decision.decision_id,
                    "execution_status": decision.execution_status,
                    "executed_successfully": executed_successfully,
                    "execution_errors": execution_errors,
                    "target_servers": target_servers
                },
                compliance_tags={"business_execution", "decision_implementation"}
            )
            
            self.logger.info(f"Executed decision: {decision.decision_id} - Status: {decision.execution_status}")
            
        except Exception as e:
            decision.execution_status = "failed"
            
            # Log execution failure
            self.audit_manager.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                subject_id="autonomous_boardroom",
                subject_type="system",
                action="Decision execution failed",
                target=decision.decision_id,
                severity=AuditSeverity.CRITICAL,
                context={
                    "decision_id": decision.decision_id,
                    "error": str(e),
                    "decision_type": decision.decision_type.value
                },
                compliance_tags={"business_execution", "system_error"}
            )
            
            self.logger.error(f"Failed to execute decision {decision.decision_id}: {e}")
    
    def _get_execution_servers(self, decision_type: DecisionType) -> List[str]:
        """Get MCP servers relevant for decision execution"""
        server_mapping = {
            DecisionType.FINANCIAL: ["erpnext"],
            DecisionType.MARKETING: ["linkedin", "reddit"],
            DecisionType.OPERATIONAL: ["erpnext"],
            DecisionType.STRATEGIC: ["linkedin", "reddit", "erpnext"],
            DecisionType.INVESTMENT: ["erpnext"],
            DecisionType.PRODUCT: ["reddit"],
            DecisionType.GOVERNANCE: ["erpnext"]
        }
        
        return server_mapping.get(decision_type, ["erpnext"])
    
    async def _maintain_mcp_connections(self):
        """Maintain connections to MCP servers"""
        while self.is_running:
            try:
                # Check health of MCP server connections
                for server_name, queue_name in self.mcp_servers.items():
                    await self._check_mcp_server_health(server_name, queue_name)
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error maintaining MCP connections: {e}")
                await asyncio.sleep(300)
    
    async def _check_mcp_server_health(self, server_name: str, queue_name: str):
        """Check health of an MCP server"""
        try:
            health_check = {
                "type": "health_check",
                "timestamp": datetime.now().isoformat(),
                "server": server_name
            }
            
            await self._send_mcp_query(queue_name, health_check)
            self.logger.debug(f"Health check sent to {server_name}")
            
        except Exception as e:
            self.logger.warning(f"Health check failed for {server_name}: {e}")
    
    async def _check_business_alerts(self):
        """Check for critical business alerts that require immediate attention"""
        # This would check for critical business conditions
        # For now, simulate alert checking
        pass
    
    async def _update_agent_performance(self):
        """Update performance metrics for all agents"""
        for role, agent in self.agents.items():
            # Update performance based on recent decisions and outcomes
            performance_update = {
                "timestamp": datetime.now().isoformat(),
                "decisions_participated": len([d for d in self.active_decisions.values() 
                                             if role in d.participants]),
                "average_confidence": self._calculate_agent_confidence(agent),
                "legendary_effectiveness": 0.85  # Would be calculated from actual outcomes
            }
            
            agent.performance_history.append(performance_update)
            
            # Keep only recent performance history
            if len(agent.performance_history) > 100:
                agent.performance_history = agent.performance_history[-100:]
    
    def _calculate_agent_confidence(self, agent: BoardroomAgent) -> float:
        """Calculate average confidence for an agent's contributions"""
        # This would analyze actual decision outcomes
        return 0.85  # Placeholder
    
    async def get_boardroom_status(self) -> Dict[str, Any]:
        """Get comprehensive boardroom status"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "agents": {
                role.value: {
                    "legendary_profile": agent.legendary_expertise.legend_profile,
                    "domain": agent.legendary_expertise.domain,
                    "is_active": agent.is_active,
                    "current_tasks": len(agent.current_tasks),
                    "performance_score": self._calculate_agent_confidence(agent)
                }
                for role, agent in self.agents.items()
            },
            "active_decisions": len(self.active_decisions),
            "total_decisions": len(self.decision_history),
            "last_session": self.last_session.isoformat() if self.last_session else None,
            "mcp_servers": list(self.mcp_servers.keys()),
            "system_health": {
                "aos_available": AOS_AVAILABLE,
                "finetuned_llm_available": FINETUNED_LLM_AVAILABLE,
                "azure_servicebus_available": AZURE_SERVICEBUS_AVAILABLE
            }
        }
    
    async def shutdown(self):
        """Graceful shutdown of the autonomous boardroom"""
        self.logger.info("Shutting down Autonomous Boardroom...")
        self.is_running = False
        
        if self.service_bus_client:
            await self.service_bus_client.close()
        
        if self.aos:
            await self.aos.shutdown()
        
        self.state = BoardroomState.PAUSED
        self.logger.info("Autonomous Boardroom shutdown completed")

    # Voting-based Decision Making Methods
    
    async def _get_lora_adapter_score(self, agent: BoardroomAgent, proposal: str, decision_type: DecisionType) -> float:
        """Get LoRA adapter scoring for the proposal based on legendary expertise"""
        try:
            # Try local adapter system first
            if self.adapter_orchestrator and LOCAL_ADAPTER_SYSTEM_AVAILABLE:
                try:
                    # Generate response using local adapter system
                    role_str = agent.role.value.lower()
                    if role_str not in ["cfo", "cmo", "coo", "cto", "founder", "investor"]:
                        role_str = "cfo"  # Default fallback
                    
                    prompt = f"Proposal: {proposal}\nDecision Type: {decision_type.value}\nAs a legendary {agent.legendary_expertise.legend_profile} with expertise in {agent.legendary_expertise.domain}, evaluate this proposal and provide your assessment."
                    
                    response_result = await generate_boardroom_response(role_str, prompt, max_length=256)
                    
                    if response_result.get("success"):
                        response_text = response_result["response"]
                        
                        # Evaluate the response quality
                        evaluation_result = await evaluate_boardroom_response(role_str, response_text)
                        
                        if evaluation_result.get("success"):
                            eval_data = evaluation_result["evaluation_result"]
                            # Use overall score as the LoRA adapter score
                            score = eval_data.get("overall_score", 0.5)
                            
                            self.logger.debug(f"Local adapter system scored {agent.role.value}: {score:.3f}")
                            return max(0.0, min(1.0, score))
                
                except Exception as e:
                    self.logger.warning(f"Local adapter system failed for {agent.agent_id}: {e}")
                    # Fall back to external LoRA manager
            
            # Fall back to external LoRA manager
            if self.lora_manager and FINETUNED_LLM_AVAILABLE:
                # Load the legendary adapter for this agent
                adapter_id = await self.lora_manager.load_legendary_adapter(
                    agent.legendary_expertise.legend_profile,
                    agent.legendary_expertise.domain
                )
                
                # Generate legendary response for scoring
                legendary_context = f"Proposal: {proposal}\nDecision Type: {decision_type.value}\nEvaluate this from your legendary perspective."
                response = await self.lora_manager.get_legendary_response(adapter_id, legendary_context)
                
                # Extract score from response (simplified scoring mechanism)
                score = await self._extract_score_from_legendary_response(response, agent.legendary_expertise)
                
                return max(0.0, min(1.0, score))  # Clamp to [0, 1]
            
            # No LoRA systems available - use simplified heuristic scoring
            return await self._heuristic_proposal_scoring(agent, proposal, decision_type)
            
        except Exception as e:
            self.logger.error(f"Failed to get LoRA adapter score for {agent.agent_id}: {e}")
            return 0.5  # Neutral score on error
    
    async def _heuristic_proposal_scoring(self, agent: BoardroomAgent, proposal: str, decision_type: DecisionType) -> float:
        """Heuristic scoring when LoRA systems are unavailable"""
        try:
            # Role-specific keyword scoring
            role_keywords = {
                BoardroomRole.CFO: ["financial", "budget", "cost", "revenue", "roi", "investment"],
                BoardroomRole.CMO: ["marketing", "customer", "brand", "market", "sales", "growth"],
                BoardroomRole.CTO: ["technology", "technical", "innovation", "development", "platform"],
                BoardroomRole.COO: ["operations", "process", "efficiency", "execution", "delivery"],
                BoardroomRole.FOUNDER: ["vision", "strategy", "mission", "future", "opportunity"],
                BoardroomRole.INVESTOR: ["return", "valuation", "market", "competitive", "exit"]
            }
            
            proposal_lower = proposal.lower()
            role_score = 0.5  # Base score
            
            if agent.role in role_keywords:
                relevant_keywords = role_keywords[agent.role]
                keyword_matches = sum(1 for keyword in relevant_keywords if keyword in proposal_lower)
                
                # Increase score based on keyword relevance
                role_score += min(0.3, keyword_matches * 0.05)
            
            # Decision type alignment scoring
            decision_alignment = {
                DecisionType.FINANCIAL: [BoardroomRole.CFO, BoardroomRole.INVESTOR],
                DecisionType.STRATEGIC: [BoardroomRole.FOUNDER, BoardroomRole.CEO, BoardroomRole.CSO],
                DecisionType.OPERATIONAL: [BoardroomRole.COO, BoardroomRole.CTO],
                DecisionType.MARKET: [BoardroomRole.CMO, BoardroomRole.FOUNDER],
                DecisionType.PRODUCT: [BoardroomRole.CTO, BoardroomRole.CMO],
                DecisionType.INVESTMENT: [BoardroomRole.INVESTOR, BoardroomRole.CFO]
            }
            
            if decision_type in decision_alignment and agent.role in decision_alignment[decision_type]:
                role_score += 0.1  # Bonus for aligned decision type
            
            return max(0.2, min(0.8, role_score))  # Keep in reasonable range
            
        except Exception as e:
            self.logger.error(f"Heuristic scoring failed for {agent.agent_id}: {e}")
            return 0.5
    
    async def _extract_score_from_legendary_response(self, response: str, expertise: LegendaryExpertise) -> float:
        """Extract scoring from legendary response (simplified implementation)"""
        try:
            positive_indicators = ["strongly support", "recommend", "excellent", "valuable", "strategic advantage"]
            negative_indicators = ["oppose", "risky", "avoid", "problematic", "decline"]
            
            response_lower = response.lower()
            positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
            
            # Base score calculation
            if positive_count > negative_count:
                base_score = 0.6 + (positive_count - negative_count) * 0.1
            elif negative_count > positive_count:
                base_score = 0.4 - (negative_count - positive_count) * 0.1
            else:
                base_score = 0.5
            
            # Apply expertise performance weighting
            performance_modifier = expertise.performance_metrics.get("accuracy", 0.8)
            final_score = base_score * performance_modifier
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            self.logger.error(f"Failed to extract score from legendary response: {e}")
            return 0.5
    
    async def _calculate_purpose_alignment(self, agent: BoardroomAgent, proposal: str, decision_type: DecisionType) -> float:
        """Calculate how well the proposal aligns with the agent's assigned purpose"""
        try:
            # Define role-specific purposes and their alignment with decision types
            role_purpose_alignment = {
                BoardroomRole.INVESTOR: {
                    DecisionType.INVESTMENT: 0.9, DecisionType.FINANCIAL: 0.9, DecisionType.STRATEGIC: 0.8
                },
                BoardroomRole.CEO: {
                    DecisionType.STRATEGIC: 0.9, DecisionType.GOVERNANCE: 0.9, DecisionType.OPERATIONAL: 0.8
                },
                BoardroomRole.CFO: {
                    DecisionType.FINANCIAL: 0.9, DecisionType.INVESTMENT: 0.8, DecisionType.OPERATIONAL: 0.6
                }
            }
            
            # Get base alignment for role and decision type
            base_alignment = role_purpose_alignment.get(agent.role, {}).get(decision_type, 0.5)
            
            return base_alignment
            
        except Exception as e:
            self.logger.error(f"Failed to calculate purpose alignment for {agent.agent_id}: {e}")
            return 0.5
    
    async def _calculate_vote_value(self, lora_score: float, purpose_alignment: float, role: BoardroomRole) -> float:
        """Calculate vote value combining LoRA adapter score and purpose alignment"""
        try:
            # Weighted combination of LoRA score and purpose alignment
            lora_weight = 0.7  # 70% weight to legendary expertise
            purpose_weight = 0.3  # 30% weight to purpose alignment
            
            combined_score = (lora_score * lora_weight) + (purpose_alignment * purpose_weight)
            
            # Convert to vote value (-1 to 1 range)
            if combined_score >= 0.6:
                vote_value = (combined_score - 0.6) / 0.4  # Maps 0.6-1.0 to 0.0-1.0
            elif combined_score <= 0.4:
                vote_value = (combined_score - 0.4) / 0.4  # Maps 0.0-0.4 to -1.0-0.0
            else:
                vote_value = (combined_score - 0.5) / 0.1 * 0.2  # Neutral zone
            
            return max(-1.0, min(1.0, vote_value))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate vote value: {e}")
            return 0.0
    
    async def _calculate_vote_confidence(self, lora_score: float, purpose_alignment: float, agent: BoardroomAgent) -> float:
        """Calculate confidence in the vote based on various factors"""
        try:
            adapter_confidence = agent.legendary_expertise.performance_metrics.get("accuracy", 0.8)
            alignment_confidence = purpose_alignment
            historical_confidence = self._calculate_agent_confidence(agent)
            
            # Weighted average
            combined_confidence = (adapter_confidence * 0.4 + alignment_confidence * 0.3 + historical_confidence * 0.3)
            
            return max(0.0, min(1.0, combined_confidence))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate vote confidence for {agent.agent_id}: {e}")
            return 0.5
    
    async def _generate_vote_reasoning(self, agent: BoardroomAgent, proposal: str, lora_score: float, purpose_alignment: float) -> str:
        """Generate reasoning for the vote using legendary expertise"""
        try:
            legend_name = agent.legendary_expertise.legend_profile
            role = agent.role.value
            
            reasoning = f"As {legend_name} serving as {role}, I evaluate this proposal with {lora_score:.2f} legendary expertise score and {purpose_alignment:.2f} purpose alignment."
            
            if lora_score > 0.6:
                reasoning += " I support this proposal based on proven strategic principles."
            elif lora_score < 0.4:
                reasoning += " I have concerns about this proposal based on historical patterns."
            else:
                reasoning += " This requires careful consideration of trade-offs."
            
            return reasoning
            
        except Exception as e:
            self.logger.error(f"Failed to generate vote reasoning for {agent.agent_id}: {e}")
            return f"Vote cast by {agent.role.value} based on {agent.legendary_expertise.domain} expertise."
    
    async def _calculate_voting_results(self, votes: List[BoardroomVote]) -> Dict[str, Any]:
        """Calculate comprehensive voting results with weighted scoring"""
        try:
            if not votes:
                return {"error": "No votes collected"}
            
            total_weighted_votes = 0.0
            total_weight = 0.0
            
            for vote in votes:
                agent = next((a for a in self.agents.values() if a.agent_id == vote.voter_id), None)
                weight = agent.voting_weight if agent else 1.0
                
                weighted_vote = vote.vote_value * weight * vote.confidence
                total_weighted_votes += weighted_vote
                total_weight += weight
            
            # Calculate final score
            final_score = total_weighted_votes / total_weight if total_weight > 0 else 0.0
            
            # Calculate consensus
            vote_values = [vote.vote_value for vote in votes]
            consensus_score = 1.0 - (max(vote_values) - min(vote_values)) / 2.0 if vote_values else 0.0
            
            # Calculate overall confidence
            confidence_score = sum(vote.confidence for vote in votes) / len(votes) if votes else 0.0
            
            return {
                "final_score": final_score,
                "consensus_score": consensus_score,
                "confidence_score": confidence_score,
                "total_votes": len(votes),
                "approval_threshold": final_score > 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate voting results: {e}")
            return {"error": str(e)}
    
    async def _determine_final_decision(self, votes: List[BoardroomVote], voting_results: Dict[str, Any]) -> str:
        """Determine final decision based on voting results"""
        try:
            final_score = voting_results.get("final_score", 0.0)
            consensus_score = voting_results.get("consensus_score", 0.0)
            
            if voting_results.get("error"):
                return "Decision deferred due to voting system error"
            
            if final_score > 0.6 and consensus_score > 0.7:
                return "APPROVED - Strong consensus in favor"
            elif final_score > 0.0:
                return "APPROVED - Majority support"
            elif final_score < -0.6:
                return "REJECTED - Strong opposition"
            elif consensus_score < 0.4:
                return "DEFERRED - Lack of consensus"
            else:
                return "REVIEW REQUIRED - Mixed signals"
                
        except Exception as e:
            self.logger.error(f"Failed to determine final decision: {e}")
            return "SYSTEM ERROR - Unable to determine decision"
    
    async def _generate_voting_rationale(self, votes: List[BoardroomVote], voting_results: Dict[str, Any]) -> str:
        """Generate comprehensive rationale based on all votes"""
        try:
            if voting_results.get("error"):
                return "Unable to generate rationale due to voting system error"
            
            final_score = voting_results.get("final_score", 0.0)
            consensus_score = voting_results.get("consensus_score", 0.0)
            total_votes = voting_results.get("total_votes", 0)
            
            rationale = f"Based on {total_votes} votes with final score {final_score:.2f} and consensus {consensus_score:.2f}. "
            
            # Add key votes summary
            supporting_votes = [v for v in votes if v.vote_value > 0.3]
            opposing_votes = [v for v in votes if v.vote_value < -0.3]
            
            if supporting_votes:
                rationale += f"Support from {len(supporting_votes)} members. "
            if opposing_votes:
                rationale += f"Opposition from {len(opposing_votes)} members. "
            
            return rationale
            
        except Exception as e:
            self.logger.error(f"Failed to generate voting rationale: {e}")
            return "Unable to generate comprehensive rationale due to system error"
    
    async def _determine_decision_status(self, voting_results: Dict[str, Any]) -> str:
        """Determine decision status based on voting results"""
        try:
            if voting_results.get("error"):
                return "error"
            
            final_score = voting_results.get("final_score", 0.0)
            
            if final_score > 0.0:
                return "approved"
            elif final_score < -0.3:
                return "rejected"
            else:
                return "review_required"
                
        except Exception as e:
            self.logger.error(f"Failed to determine decision status: {e}")
            return "error"
    
    # === Conversation System Integration ===
    
    async def create_boardroom_conversation(self, conversation_type: str, champion_role: str, 
                                          title: str, content: str, context: Dict[str, Any] = None) -> str:
        """Create a new boardroom conversation"""
        if not self.conversation_manager:
            self.logger.error("Conversation system not available")
            return None
            
        try:
            from conversations.conversation_system import ConversationType, ConversationRole
            
            # Map string parameters to enums
            conv_type = ConversationType(conversation_type)
            champion = ConversationRole(champion_role)
            
            conversation_id = await self.conversation_manager.create_conversation(
                conversation_type=conv_type,
                champion=champion,
                title=title,
                content=content,
                context=context or {}
            )
            
            # Log conversation creation
            self.audit_manager.log_event(
                event_type=AuditEventType.CONVERSATION_CREATED,
                subject_id=conversation_id,
                subject_type="conversation",
                action=f"Created {conversation_type} conversation",
                severity=AuditSeverity.MEDIUM,
                context={
                    "conversation_type": conversation_type,
                    "champion": champion_role,
                    "title": title
                },
                compliance_tags={"governance", "conversation_management"}
            )
            
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Failed to create boardroom conversation: {e}")
            return None
    
    async def initiate_a2a_communication(self, from_agent: str, to_agent: str, 
                                       conversation_type: str, message: str, 
                                       context: Dict[str, Any] = None) -> str:
        """Initiate Agent-to-Agent communication"""
        if not self.conversation_manager:
            self.logger.error("Conversation system not available")
            return None
            
        try:
            from conversations.conversation_system import ConversationType, ConversationRole
            
            from_role = ConversationRole(from_agent)
            to_role = ConversationRole(to_agent)
            conv_type = ConversationType(conversation_type)
            
            conversation_id = await self.conversation_manager.create_a2a_communication(
                from_agent=from_role,
                to_agent=to_role,
                conversation_type=conv_type,
                message_content=message,
                context=context or {}
            )
            
            # Log A2A communication
            self.audit_manager.log_event(
                event_type=AuditEventType.A2A_COMMUNICATION,
                subject_id=conversation_id,
                subject_type="a2a_conversation",
                action=f"A2A communication: {from_agent} → {to_agent}",
                severity=AuditSeverity.MEDIUM,
                context={
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "conversation_type": conversation_type,
                    "is_external": to_agent in ["Customer", "Partner", "Supplier", "Regulator"]
                },
                compliance_tags={"governance", "a2a_communication"}
            )
            
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Failed to initiate A2A communication: {e}")
            return None
    
    async def get_agent_conversations(self, agent_role: str) -> Dict[str, Any]:
        """Get conversations for a specific agent"""
        if not self.conversation_manager:
            return {"error": "Conversation system not available"}
            
        try:
            from conversations.conversation_system import ConversationRole
            
            role = ConversationRole(agent_role)
            conversations = await self.conversation_manager.list_conversations_by_agent(role)
            
            # Convert conversations to serializable format
            result = {}
            for category, conv_list in conversations.items():
                result[category] = [conv.to_dict() for conv in conv_list]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get agent conversations for {agent_role}: {e}")
            return {"error": str(e)}
    
    async def sign_conversation(self, conversation_id: str, signer_role: str, signer_name: str) -> bool:
        """Sign a conversation"""
        if not self.conversation_manager:
            self.logger.error("Conversation system not available")
            return False
            
        try:
            from conversations.conversation_system import ConversationRole
            
            role = ConversationRole(signer_role)
            success = await self.conversation_manager.sign_conversation(conversation_id, role, signer_name)
            
            if success:
                # Log conversation signature
                self.audit_manager.log_event(
                    event_type=AuditEventType.CONVERSATION_SIGNED,
                    subject_id=conversation_id,
                    subject_type="conversation",
                    action=f"Conversation signed by {signer_name}[{signer_role}]",
                    severity=AuditSeverity.MEDIUM,
                    context={
                        "signer_role": signer_role,
                        "signer_name": signer_name,
                        "conversation_id": conversation_id
                    },
                    compliance_tags={"governance", "conversation_signature"}
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to sign conversation {conversation_id}: {e}")
            return False


# Factory function
def create_autonomous_boardroom(config: AOSConfig = None) -> AutonomousBoardroom:
    """Create and initialize the Autonomous Boardroom"""
    return AutonomousBoardroom(config)


# Global instance
autonomous_boardroom = None

def get_autonomous_boardroom() -> AutonomousBoardroom:
    """Get global Autonomous Boardroom instance"""
    global autonomous_boardroom
    if autonomous_boardroom is None:
        autonomous_boardroom = create_autonomous_boardroom()
    return autonomous_boardroom