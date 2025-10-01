"""
BusinessInfinity Core - Business Manager

Central manager for business operations, agent coordination, and workflow management.
This coordinates between the AOS infrastructure and business-specific logic.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Import AOS components
try:
    from aos.core.boardroom import AutonomousBoardroom
    from aos.messaging.conversation_system import AOSConversationSystem, ConversationType
    from aos.orchestration.orchestrator import Orchestrator
    from aos.monitoring.audit_trail import audit_log, AuditEventType, AuditSeverity
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    print("Warning: AOS not available")


@dataclass
class BusinessAgent:
    """Represents a business agent in the system"""
    id: str
    name: str
    role: str
    status: str = "available"
    capabilities: List[str] = field(default_factory=list)
    current_workload: float = 0.0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_activity: Optional[datetime] = None


@dataclass
class BusinessTask:
    """Represents a business task"""
    task_id: str
    agent_id: str
    description: str
    priority: str = "medium"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    progress: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)


class BusinessManager:
    """
    Central manager for BusinessInfinity operations
    
    Coordinates between AOS infrastructure and business-specific functionality.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AOS components
        self.boardroom: Optional[AutonomousBoardroom] = None
        self.conversation_system: Optional[AOSConversationSystem] = None
        self.orchestrator: Optional[Orchestrator] = None
        
        # Business state
        self.agents: Dict[str, BusinessAgent] = {}
        self.tasks: Dict[str, BusinessTask] = {}
        self.active_workflows: Dict[str, Any] = {}
        
        # Initialize default agents
        self._initialize_default_agents()
        
        self.logger.info("BusinessManager initialized")
    
    async def initialize(self):
        """Initialize the business manager and AOS integration"""
        try:
            if AOS_AVAILABLE:
                # Initialize AOS components
                from aos.core.boardroom import create_autonomous_boardroom
                
                self.boardroom = await create_autonomous_boardroom()
                self.conversation_system = AOSConversationSystem()
                await self.conversation_system.initialize()
                
                self.orchestrator = Orchestrator()
                await self.orchestrator.initialize()
                
                # Set up business-specific boardroom members
                await self._setup_boardroom_members()
                
                self.logger.info("AOS integration initialized")
            else:
                self.logger.warning("AOS not available, running in standalone mode")
            
            # Start background tasks
            await self._start_background_tasks()
            
            if AOS_AVAILABLE:
                await audit_log(
                    AuditEventType.COMPONENT_STARTED,
                    "BusinessManager initialized",
                    component="business_manager",
                    severity=AuditSeverity.INFO
                )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BusinessManager: {e}")
            raise
    
    def _initialize_default_agents(self):
        """Initialize default business agents"""
        default_agents = [
            BusinessAgent(
                id="founder",
                name="Founder Agent",
                role="founder",
                capabilities=["strategic_planning", "vision_setting", "leadership", "fundraising"]
            ),
            BusinessAgent(
                id="ceo",
                name="CEO Agent", 
                role="ceo",
                capabilities=["executive_decisions", "team_management", "operations", "stakeholder_relations"]
            ),
            BusinessAgent(
                id="cto",
                name="CTO Agent",
                role="cto", 
                capabilities=["technical_architecture", "technology_strategy", "engineering", "product_development"]
            ),
            BusinessAgent(
                id="cfo",
                name="CFO Agent",
                role="cfo",
                capabilities=["financial_planning", "budget_management", "financial_analysis", "investment_decisions"]
            ),
            BusinessAgent(
                id="coo",
                name="COO Agent",
                role="coo",
                capabilities=["operations_management", "process_optimization", "supply_chain", "quality_assurance"]
            ),
            BusinessAgent(
                id="cmo",
                name="CMO Agent", 
                role="cmo",
                capabilities=["marketing_strategy", "brand_management", "customer_acquisition", "market_research"]
            ),
            BusinessAgent(
                id="investor",
                name="Investor Agent",
                role="investor",
                capabilities=["investment_analysis", "due_diligence", "portfolio_management", "market_evaluation"]
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.id] = agent
    
    async def _setup_boardroom_members(self):
        """Set up boardroom members from business agents"""
        if not self.boardroom:
            return
        
        from aos.core.boardroom import BoardroomMember, BoardroomRole
        
        # Map business agents to boardroom members
        role_mapping = {
            "founder": BoardroomRole.FOUNDER,
            "ceo": BoardroomRole.CEO,
            "cto": BoardroomRole.CTO,
            "cfo": BoardroomRole.CFO,
            "coo": BoardroomRole.COO,
            "cmo": BoardroomRole.CMO,
            "investor": BoardroomRole.INVESTOR
        }
        
        for agent_id, agent in self.agents.items():
            if agent.role in role_mapping:
                member = BoardroomMember(
                    agent_id=agent_id,
                    role=role_mapping[agent.role],
                    expertise_domains=agent.capabilities,
                    lora_adapters=[f"{agent.role}_adapter"]
                )
                
                await self.boardroom.add_member(member)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all business agents"""
        agents_list = []
        for agent in self.agents.values():
            agents_list.append({
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "current_workload": agent.current_workload,
                "performance_metrics": agent.performance_metrics,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
            })
        return agents_list
    
    async def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Get additional details from AOS if available
        additional_metrics = {}
        if self.boardroom:
            boardroom_status = await self.boardroom.get_boardroom_status()
            if agent_id in boardroom_status.get("members", {}):
                member_info = boardroom_status["members"][agent_id] 
                additional_metrics.update({
                    "boardroom_status": member_info.get("status"),
                    "last_boardroom_activity": member_info.get("last_activity")
                })
        
        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "status": agent.status,
            "capabilities": agent.capabilities,
            "current_workload": agent.current_workload,
            "performance_metrics": {**agent.performance_metrics, **additional_metrics},
            "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
            "tasks": await self._get_agent_task_summary(agent_id)
        }
    
    async def assign_task(self, agent_id: str, task_description: str, 
                         priority: str = "medium", deadline: Optional[datetime] = None,
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assign a task to an agent"""
        try:
            agent = self.agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Create task
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
            task = BusinessTask(
                task_id=task_id,
                agent_id=agent_id,
                description=task_description,
                priority=priority,
                deadline=deadline,
                context=context or {}
            )
            
            self.tasks[task_id] = task
            
            # Update agent workload
            agent.current_workload += 0.1  # Simple workload calculation
            agent.last_activity = datetime.now()
            
            # If AOS is available, create orchestration workflow
            if self.orchestrator:
                workflow_id = await self.orchestrator.create_workflow(
                    name=f"Task: {task_description[:50]}",
                    steps=[
                        {
                            "name": "execute_task",
                            "agent_id": agent_id,
                            "task_id": task_id,
                            "description": task_description
                        }
                    ],
                    metadata={"business_task": task_id}
                )
                task.context["workflow_id"] = workflow_id
            
            if AOS_AVAILABLE:
                await audit_log(
                    AuditEventType.TASK_ASSIGNED,
                    f"Task assigned to {agent_id}: {task_description}",
                    subject_id=agent_id,
                    subject_type="agent",
                    component="business_manager",
                    severity=AuditSeverity.INFO,
                    metadata={
                        "task_id": task_id,
                        "priority": priority,
                        "agent_role": agent.role
                    }
                )
            
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "task": task_description,
                "priority": priority,
                "status": task.status,
                "assigned_at": task.created_at.isoformat(),
                "deadline": deadline.isoformat() if deadline else None,
                "workflow_id": task.context.get("workflow_id")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}")
            raise
    
    async def get_agent_tasks(self, agent_id: str, status_filter: Optional[str] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Get tasks for a specific agent"""
        agent_tasks = [
            task for task in self.tasks.values()
            if task.agent_id == agent_id
        ]
        
        if status_filter:
            agent_tasks = [task for task in agent_tasks if task.status == status_filter]
        
        # Sort by creation date (newest first)
        agent_tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply limit
        agent_tasks = agent_tasks[:limit]
        
        # Convert to dict format
        tasks_list = []
        for task in agent_tasks:
            tasks_list.append({
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "assigned_at": task.created_at.isoformat(),
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "progress": task.progress,
                "workflow_id": task.context.get("workflow_id")
            })
        
        return tasks_list
    
    async def initiate_boardroom_decision(self, topic: str, decision_type: str,
                                        context: Dict[str, Any]) -> str:
        """Initiate a boardroom decision process"""
        if not self.boardroom:
            raise RuntimeError("Boardroom not available")
        
        decision_id = await self.boardroom.initiate_decision(topic, decision_type, context)
        
        # Create conversation for tracking
        if self.conversation_system:
            from aos.messaging.conversation_system import create_decision_conversation, ConversationRole
            
            conversation = await create_decision_conversation(
                title=f"Boardroom Decision: {topic}",
                description=f"Decision process for: {topic}",
                champion=ConversationRole.SYSTEM,
                required_signers=[ConversationRole.AGENT],  # Will be updated based on decision type
                context={"decision_id": decision_id, "decision_type": decision_type}
            )
            
            await self.conversation_system.create_conversation(conversation)
        
        return decision_id
    
    async def get_business_metrics(self) -> Dict[str, Any]:
        """Get overall business metrics"""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status == "active"])
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        
        avg_workload = sum(a.current_workload for a in self.agents.values()) / total_agents if total_agents > 0 else 0
        
        boardroom_status = {}
        if self.boardroom:
            boardroom_status = await self.boardroom.get_boardroom_status()
        
        return {
            "agents": {
                "total": total_agents,
                "active": active_agents,
                "average_workload": avg_workload
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "boardroom": boardroom_status,
            "aos_available": AOS_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_agent_task_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get task summary for an agent"""
        agent_tasks = [t for t in self.tasks.values() if t.agent_id == agent_id]
        
        return {
            "total": len(agent_tasks),
            "pending": len([t for t in agent_tasks if t.status == "pending"]),
            "in_progress": len([t for t in agent_tasks if t.status == "in_progress"]),
            "completed": len([t for t in agent_tasks if t.status == "completed"]),
            "failed": len([t for t in agent_tasks if t.status == "failed"])
        }
    
    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        asyncio.create_task(self._update_agent_metrics())
        asyncio.create_task(self._monitor_task_progress())
    
    async def _update_agent_metrics(self):
        """Background task to update agent performance metrics"""
        while True:
            try:
                for agent in self.agents.values():
                    # Update performance metrics based on task completion, etc.
                    agent_tasks = [t for t in self.tasks.values() if t.agent_id == agent.id]
                    completed_tasks = [t for t in agent_tasks if t.status == "completed"]
                    
                    if agent_tasks:
                        success_rate = len(completed_tasks) / len(agent_tasks)
                        agent.performance_metrics["success_rate"] = success_rate
                        agent.performance_metrics["tasks_completed"] = len(completed_tasks)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating agent metrics: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_task_progress(self):
        """Background task to monitor task progress"""
        while True:
            try:
                # Check for overdue tasks, update progress, etc.
                now = datetime.now()
                for task in self.tasks.values():
                    if task.deadline and now > task.deadline and task.status not in ["completed", "failed"]:
                        task.status = "overdue"
                        if AOS_AVAILABLE:
                            await audit_log(
                                AuditEventType.SYSTEM_ERROR,
                                f"Task overdue: {task.task_id}",
                                subject_id=task.agent_id,
                                subject_type="agent",
                                component="business_manager",
                                severity=AuditSeverity.WARNING,
                                metadata={"task_id": task.task_id}
                            )
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring tasks: {e}")
                await asyncio.sleep(600)
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of business manager"""
        return {
            "status": "healthy",
            "agents_count": len(self.agents),
            "active_tasks": len([t for t in self.tasks.values() if t.status in ["pending", "in_progress"]]),
            "aos_integration": AOS_AVAILABLE,
            "boardroom_available": self.boardroom is not None,
            "conversation_system_available": self.conversation_system is not None
        }


# Factory function
async def create_business_manager() -> BusinessManager:
    """Create and initialize a business manager"""
    manager = BusinessManager()
    await manager.initialize()
    return manager