"""
BusinessInfinity Agents - Agent Coordinator

Coordinates agent interactions, task distribution, and agent lifecycle management
within the BusinessInfinity system.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Import AOS components for agent coordination
try:
    from AgentOperatingSystem.messaging import MessageBus
    from AgentOperatingSystem.orchestration import OrchestrationEngine
    from AgentOperatingSystem.monitoring import SystemMonitor
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    MessageBus = None
    OrchestrationEngine = None
    SystemMonitor = None


@dataclass 
class AgentQuery:
    """Represents a query to an agent"""
    query_id: str
    agent_id: str
    question: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: str = "medium"


@dataclass
class AgentResponse:
    """Represents an agent's response"""
    query_id: str
    agent_id: str
    answer: str
    confidence: float
    response_time: float
    sources: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]


class AgentCoordinator:
    """
    Coordinates agent interactions and task management
    
    Handles agent queries, task assignment, and coordination between
    business agents and the underlying AOS infrastructure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AOS integration
        self.conversation_system: Optional[AOSConversationSystem] = None
        self.orchestrator: Optional[Orchestrator] = None
        
        # Coordination state
        self.active_queries: Dict[str, AgentQuery] = {}
        self.query_history: List[AgentResponse] = []
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # Configuration
        self.config = {
            "max_concurrent_queries": 10,
            "query_timeout_seconds": 30,
            "response_cache_size": 100
        }
        
        self._initialize_agent_capabilities()
        self.logger.info("AgentCoordinator initialized")
    
    async def initialize(self):
        """Initialize the agent coordinator"""
        try:
            if AOS_AVAILABLE:
                self.conversation_system = AOSConversationSystem()
                await self.conversation_system.initialize()
                
                self.orchestrator = Orchestrator()
                await self.orchestrator.initialize()
                
                self.logger.info("AOS integration initialized for agent coordination")
            
            # Start background tasks
            await self._start_coordination_tasks()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AgentCoordinator: {e}")
            raise
    
    def _initialize_agent_capabilities(self):
        """Initialize agent capability mappings"""
        self.agent_capabilities = {
            "founder": [
                "strategic_planning", "vision_setting", "leadership", "fundraising",
                "investor_relations", "company_culture", "market_analysis"
            ],
            "ceo": [
                "executive_decisions", "team_management", "operations", "stakeholder_relations",
                "strategic_execution", "crisis_management", "performance_oversight"
            ],
            "cto": [
                "technical_architecture", "technology_strategy", "engineering", "product_development",
                "technical_recruitment", "infrastructure_planning", "security_oversight"
            ],
            "cfo": [
                "financial_planning", "budget_management", "financial_analysis", "investment_decisions",
                "risk_management", "financial_reporting", "cost_optimization"
            ],
            "coo": [
                "operations_management", "process_optimization", "supply_chain", "quality_assurance",
                "vendor_management", "operational_efficiency", "compliance_management"
            ],
            "cmo": [
                "marketing_strategy", "brand_management", "customer_acquisition", "market_research",
                "content_strategy", "digital_marketing", "customer_retention"
            ],
            "investor": [
                "investment_analysis", "due_diligence", "portfolio_management", "market_evaluation",
                "risk_assessment", "valuation_analysis", "exit_strategy"
            ]
        }
    
    async def ask_agent(self, agent_id: str, question: str, 
                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ask a question to a specific agent"""
        try:
            # Validate agent
            if agent_id not in self.agent_capabilities:
                raise ValueError(f"Unknown agent: {agent_id}")
            
            # Check if agent can handle this type of question
            agent_caps = self.agent_capabilities[agent_id]
            question_relevant = await self._assess_question_relevance(question, agent_caps)
            
            # Create query
            query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
            query = AgentQuery(
                query_id=query_id,
                agent_id=agent_id,
                question=question,
                context=context or {},
                timestamp=datetime.now()
            )
            
            # Check concurrency limits
            if len(self.active_queries) >= self.config["max_concurrent_queries"]:
                raise RuntimeError("Too many concurrent queries")
            
            self.active_queries[query_id] = query
            
            # Process query through appropriate channels
            if self.conversation_system:
                response = await self._process_query_via_aos(query)
            else:
                response = await self._process_query_direct(query)
            
            # Clean up active query
            if query_id in self.active_queries:
                del self.active_queries[query_id]
            
            # Store in history
            self.query_history.append(response)
            if len(self.query_history) > self.config["response_cache_size"]:
                self.query_history.pop(0)
            
            # Log the interaction
            if AOS_AVAILABLE:
                await audit_log(
                    AuditEventType.AGENT_ACTION,
                    f"Agent query processed: {agent_id}",
                    subject_id=agent_id,
                    subject_type="agent",
                    component="agent_coordinator",
                    severity=AuditSeverity.DEBUG,
                    metadata={
                        "query_id": query_id,
                        "question_length": len(question),
                        "confidence": response.confidence,
                        "response_time": response.response_time
                    }
                )
            
            return {
                "agent_id": response.agent_id,
                "question": question,
                "answer": response.answer,
                "confidence": response.confidence,
                "response_time": response.response_time,
                "timestamp": response.timestamp.isoformat(),
                "context_used": bool(context),
                "sources": response.sources,
                "query_id": query_id,
                "relevance_score": question_relevant
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process agent query: {e}")
            
            # Return error response
            return {
                "agent_id": agent_id,
                "question": question,
                "answer": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "confidence": 0.0,
                "response_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": True,
                "sources": []
            }
    
    async def assign_task(self, agent_id: str, task_description: str,
                         priority: str = "medium", deadline: Optional[datetime] = None,
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assign a task to an agent through coordination system"""
        try:
            # Validate agent
            if agent_id not in self.agent_capabilities:
                raise ValueError(f"Unknown agent: {agent_id}")
            
            # Check if agent is suitable for this task
            task_suitability = await self._assess_task_suitability(task_description, agent_id)
            
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
            
            # Create coordination workflow if AOS available
            workflow_id = None
            if self.orchestrator:
                workflow_id = await self.orchestrator.create_workflow(
                    name=f"Agent Task: {task_description[:50]}",
                    steps=[
                        {
                            "type": "agent_task",
                            "agent_id": agent_id,
                            "task_description": task_description,
                            "priority": priority
                        }
                    ],
                    metadata={
                        "task_type": "agent_assignment",
                        "business_context": context or {}
                    }
                )
            
            # Log task assignment
            if AOS_AVAILABLE:
                await audit_log(
                    AuditEventType.TASK_ASSIGNED,
                    f"Task assigned through coordinator: {task_description[:100]}",
                    subject_id=agent_id,
                    subject_type="agent",
                    component="agent_coordinator",
                    severity=AuditSeverity.INFO,
                    metadata={
                        "task_id": task_id,
                        "priority": priority,
                        "suitability_score": task_suitability,
                        "workflow_id": workflow_id
                    }
                )
            
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "task": task_description,
                "priority": priority,
                "status": "assigned",
                "assigned_at": datetime.now().isoformat(),
                "deadline": deadline.isoformat() if deadline else None,
                "workflow_id": workflow_id,
                "suitability_score": task_suitability,
                "coordination_method": "aos" if self.orchestrator else "direct"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assign task through coordinator: {e}")
            raise
    
    async def get_agent_tasks(self, agent_id: str, status_filter: Optional[str] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Get tasks for an agent (coordinated view)"""
        # This would integrate with the orchestrator to get actual task status
        # For now, return a coordinated view
        
        tasks = []
        
        if self.orchestrator:
            # Get workflows for this agent
            agent_workflows = await self.orchestrator.get_agent_workflows(agent_id)
            
            for workflow in agent_workflows:
                if workflow.get("metadata", {}).get("task_type") == "agent_assignment":
                    task_info = {
                        "task_id": workflow.get("metadata", {}).get("task_id", workflow["id"]),
                        "description": workflow["name"],
                        "status": workflow["status"],
                        "priority": workflow.get("priority", "medium"),
                        "assigned_at": workflow["created_at"],
                        "progress": workflow.get("progress", 0.0),
                        "workflow_id": workflow["id"]
                    }
                    
                    if not status_filter or task_info["status"] == status_filter:
                        tasks.append(task_info)
        
        # Sort and limit
        tasks.sort(key=lambda t: t["assigned_at"], reverse=True)
        return tasks[:limit]
    
    async def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get agent coordination metrics"""
        active_queries_count = len(self.active_queries)
        total_queries = len(self.query_history)
        
        # Calculate average response time and confidence
        if self.query_history:
            avg_response_time = sum(r.response_time for r in self.query_history) / len(self.query_history)
            avg_confidence = sum(r.confidence for r in self.query_history) / len(self.query_history)
        else:
            avg_response_time = 0.0
            avg_confidence = 0.0
        
        # Agent activity
        agent_activity = {}
        for response in self.query_history:
            agent_id = response.agent_id
            if agent_id not in agent_activity:
                agent_activity[agent_id] = {"queries": 0, "avg_confidence": 0.0}
            agent_activity[agent_id]["queries"] += 1
        
        return {
            "active_queries": active_queries_count,
            "total_queries_processed": total_queries,
            "average_response_time": avg_response_time,
            "average_confidence": avg_confidence,
            "agent_activity": agent_activity,
            "aos_integration": AOS_AVAILABLE,
            "conversation_system_active": self.conversation_system is not None,
            "orchestrator_active": self.orchestrator is not None
        }
    
    async def _assess_question_relevance(self, question: str, agent_capabilities: List[str]) -> float:
        """Assess how relevant a question is to an agent's capabilities"""
        # Simple keyword-based relevance (could be enhanced with ML)
        question_lower = question.lower()
        relevant_keywords = 0
        total_keywords = len(agent_capabilities)
        
        for capability in agent_capabilities:
            capability_words = capability.replace("_", " ").split()
            for word in capability_words:
                if word.lower() in question_lower:
                    relevant_keywords += 1
                    break
        
        return relevant_keywords / total_keywords if total_keywords > 0 else 0.0
    
    async def _assess_task_suitability(self, task_description: str, agent_id: str) -> float:
        """Assess how suitable an agent is for a task"""
        agent_caps = self.agent_capabilities.get(agent_id, [])
        return await self._assess_question_relevance(task_description, agent_caps)
    
    async def _process_query_via_aos(self, query: AgentQuery) -> AgentResponse:
        """Process query through AOS conversation system"""
        try:
            # Create a conversation for the query
            from aos.messaging.conversation_system import create_agent_coordination_conversation, ConversationRole
            
            conversation = await create_agent_coordination_conversation(
                title=f"Agent Query: {query.question[:50]}",
                description=f"Query to {query.agent_id}: {query.question}",
                champion=ConversationRole.SYSTEM,
                participants=[ConversationRole.AGENT],
                context={
                    "query_id": query.query_id,
                    "agent_id": query.agent_id,
                    "question": query.question,
                    "user_context": query.context
                }
            )
            
            conversation_id = await self.conversation_system.create_conversation(conversation)
            
            # Add the question as a message
            await self.conversation_system.add_message(
                conversation_id=conversation_id,
                sender_role=ConversationRole.SYSTEM,
                sender_name="Query System",
                content=query.question,
                message_type="question"
            )
            
            # Generate response (in a real implementation, this would invoke the actual agent)
            start_time = datetime.now()
            answer = await self._generate_agent_response(query)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Add response to conversation
            await self.conversation_system.add_message(
                conversation_id=conversation_id,
                sender_role=ConversationRole.AGENT,
                sender_name=f"{query.agent_id.title()} Agent",
                content=answer,
                message_type="response"
            )
            
            return AgentResponse(
                query_id=query.query_id,
                agent_id=query.agent_id,
                answer=answer,
                confidence=0.85,  # Would be calculated by actual agent
                response_time=response_time,
                sources=["knowledge_base", "conversation_context"],
                timestamp=datetime.now(),
                metadata={"conversation_id": conversation_id, "method": "aos"}
            )
            
        except Exception as e:
            self.logger.error(f"Error processing query via AOS: {e}")
            return await self._process_query_direct(query)
    
    async def _process_query_direct(self, query: AgentQuery) -> AgentResponse:
        """Process query directly (fallback method)"""
        start_time = datetime.now()
        answer = await self._generate_agent_response(query)
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            query_id=query.query_id,
            agent_id=query.agent_id,
            answer=answer,
            confidence=0.75,  # Lower confidence for direct method
            response_time=response_time,
            sources=["direct_processing"],
            timestamp=datetime.now(),
            metadata={"method": "direct"}
        )
    
    async def _generate_agent_response(self, query: AgentQuery) -> str:
        """Generate response from agent (mock implementation)"""
        # This would be replaced with actual agent inference
        agent_name = query.agent_id.title()
        capabilities = self.agent_capabilities.get(query.agent_id, [])
        
        response_templates = {
            "founder": f"As the Founder, I can help with {', '.join(capabilities[:3])}. Regarding your question about '{query.question[:50]}...', here's my perspective based on strategic vision and leadership experience.",
            "ceo": f"From an executive perspective, considering {', '.join(capabilities[:3])}, I would approach '{query.question[:50]}...' by focusing on operational excellence and stakeholder value.",
            "cto": f"From a technical standpoint, leveraging my expertise in {', '.join(capabilities[:3])}, I'd address '{query.question[:50]}...' through technology strategy and engineering best practices.",
            "cfo": f"From a financial perspective, considering {', '.join(capabilities[:3])}, I'd analyze '{query.question[:50]}...' through the lens of financial optimization and risk management.",
            "coo": f"From an operations standpoint, with expertise in {', '.join(capabilities[:3])}, I'd handle '{query.question[:50]}...' by focusing on process efficiency and execution.",
            "cmo": f"From a marketing perspective, leveraging {', '.join(capabilities[:3])}, I'd approach '{query.question[:50]}...' through customer-centric strategy and brand development.",
            "investor": f"From an investment perspective, considering {', '.join(capabilities[:3])}, I'd evaluate '{query.question[:50]}...' through risk-return analysis and market opportunity assessment."
        }
        
        base_response = response_templates.get(query.agent_id, f"As {agent_name}, I'll help with your question about '{query.question[:50]}...'")
        
        # Add context-specific information if available
        if query.context:
            base_response += f" Given the context you've provided, I recommend a tailored approach that considers your specific situation."
        
        return base_response
    
    async def _start_coordination_tasks(self):
        """Start background coordination tasks"""
        asyncio.create_task(self._cleanup_expired_queries())
    
    async def _cleanup_expired_queries(self):
        """Clean up expired queries"""
        while True:
            try:
                current_time = datetime.now()
                expired_queries = []
                
                for query_id, query in self.active_queries.items():
                    elapsed = (current_time - query.timestamp).total_seconds()
                    if elapsed > self.config["query_timeout_seconds"]:
                        expired_queries.append(query_id)
                
                for query_id in expired_queries:
                    del self.active_queries[query_id]
                    self.logger.warning(f"Query {query_id} expired due to timeout")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in query cleanup: {e}")
                await asyncio.sleep(60)
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of agent coordinator"""
        return {
            "status": "healthy",
            "active_queries": len(self.active_queries),
            "query_history_size": len(self.query_history),
            "aos_integration": AOS_AVAILABLE,
            "conversation_system": self.conversation_system is not None,
            "orchestrator": self.orchestrator is not None
        }