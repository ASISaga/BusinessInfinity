"""
Business Infinity Orchestrator
Consolidates orchestration functionality from:
- /api/orchestrator.py
- Decision engine coordination
- Agent coordination and workflow management
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

# Import core components
from .agents import agent_manager, UnifiedAgentManager
from .mcp import mcp_handler
try:
    from ..shared.framework.server.decision_engine import DecisionEngine
    from ..shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
    DECISION_ENGINE_AVAILABLE = True
except ImportError:
    DECISION_ENGINE_AVAILABLE = False
    DecisionEngine = None

# Import utilities
try:
    from ..utils.governance import validate_request, GovernanceError
except ImportError:
    def validate_request(request):
        return True
    
    class GovernanceError(Exception):
        pass

# Import storage and environment managers
try:
    from ..storage import storage_manager
except ImportError:
    storage_manager = None

try:
    from ..environment import env_manager
except ImportError:
    env_manager = None


class WorkflowStep:
    """Represents a single step in a workflow"""
    
    def __init__(self, step_id: str, agent_id: str, task: str, depends_on: List[str] = None):
        self.step_id = step_id
        self.agent_id = agent_id  
        self.task = task
        self.depends_on = depends_on or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None


class Workflow:
    """Represents a complete workflow with multiple steps"""
    
    def __init__(self, workflow_id: str, steps: List[WorkflowStep]):
        self.workflow_id = workflow_id
        self.steps = {step.step_id: step for step in steps}
        self.status = "pending"
        self.created_at = datetime.now(timezone.utc)
        self.started_at = None
        self.completed_at = None


class BusinessInfinityOrchestrator:
    """
    Main orchestrator that coordinates:
    1. Agent interactions and workflows
    2. Decision engine processes
    3. MCP communication
    4. Business process automation
    """
    
    def __init__(self):
        self.agent_manager = agent_manager
        self.mcp_handler = mcp_handler
        
        # Initialize decision engine if available
        self.decision_engine = None
        if DECISION_ENGINE_AVAILABLE:
            try:
                principles = load_principles()
                tree = load_decision_tree()
                adapters = load_adapters()
                self.decision_engine = DecisionEngine(tree, adapters, principles)
            except Exception as e:
                logging.warning(f"Could not initialize decision engine: {e}")
        
        # Workflow management
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_counter = 0
        
        # Event handlers
        self.event_handlers: Dict[str, List] = {}
    
    async def process_decision(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Process a decision using the decision engine"""
        if not self.decision_engine:
            return {"error": "Decision engine not available"}
        
        try:
            # Validate the request using governance
            if not validate_request(evidence):
                raise GovernanceError("Request validation failed")
            
            # Run the decision engine
            result = self.decision_engine.run(evidence)
            
            # Log the decision
            logging.info(f"Decision processed: {result}")
            
            return result
            
        except GovernanceError as e:
            return {"error": f"Governance error: {str(e)}"}
        except Exception as e:
            return {"error": f"Decision processing error: {str(e)}"}
    
    async def execute_agent_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """
        Execute a multi-agent workflow
        
        workflow_definition should contain:
        {
            "name": "workflow_name",
            "steps": [
                {
                    "id": "step1",
                    "agent": "agent_id", 
                    "task": "task_description",
                    "depends_on": ["step0"] // optional
                }
            ]
        }
        """
        workflow_id = f"workflow_{self.workflow_counter}"
        self.workflow_counter += 1
        
        # Create workflow steps
        steps = []
        for step_def in workflow_definition.get("steps", []):
            step = WorkflowStep(
                step_id=step_def["id"],
                agent_id=step_def["agent"],
                task=step_def["task"],
                depends_on=step_def.get("depends_on", [])
            )
            steps.append(step)
        
        # Create and store workflow
        workflow = Workflow(workflow_id, steps)
        self.workflows[workflow_id] = workflow
        
        # Execute workflow
        await self._execute_workflow(workflow)
        
        return workflow_id
    
    async def _execute_workflow(self, workflow: Workflow):
        """Execute a workflow by running steps in dependency order"""
        workflow.status = "running"
        workflow.started_at = datetime.now(timezone.utc)
        
        try:
            # Build dependency graph
            remaining_steps = set(workflow.steps.keys())
            
            while remaining_steps:
                # Find steps that can be executed (dependencies completed)
                ready_steps = []
                for step_id in remaining_steps:
                    step = workflow.steps[step_id]
                    if all(workflow.steps[dep_id].status == "completed" for dep_id in step.depends_on):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Circular dependency or failed dependency
                    for step_id in remaining_steps:
                        workflow.steps[step_id].status = "failed"
                        workflow.steps[step_id].error = "Dependency not satisfied"
                    break
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    tasks.append(self._execute_workflow_step(step))
                
                await asyncio.gather(*tasks)
                
                # Remove completed/failed steps
                for step in ready_steps:
                    remaining_steps.remove(step.step_id)
            
            # Check overall workflow status
            if all(step.status == "completed" for step in workflow.steps.values()):
                workflow.status = "completed"
            else:
                workflow.status = "failed"
                
        except Exception as e:
            workflow.status = "failed"
            logging.error(f"Workflow {workflow.workflow_id} failed: {e}")
        
        workflow.completed_at = datetime.now(timezone.utc)
    
    async def _execute_workflow_step(self, step: WorkflowStep):
        """Execute a single workflow step"""
        step.status = "running"
        step.started_at = datetime.now(timezone.utc)
        
        try:
            result = await self.agent_manager.execute_agent(step.agent_id, step.task)
            if result:
                step.result = result
                step.status = "completed"
            else:
                step.status = "failed"
                step.error = f"Agent {step.agent_id} not found or returned no result"
                
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            
        step.completed_at = datetime.now(timezone.utc)
    
    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate multiple agents for a complex task
        
        coordination_request should contain:
        {
            "task": "Overall task description",
            "agents": ["agent1", "agent2", "agent3"],
            "mode": "parallel" | "sequential" | "hierarchical"
        }
        """
        task = coordination_request.get("task", "")
        agents = coordination_request.get("agents", [])
        mode = coordination_request.get("mode", "parallel")
        
        if not agents:
            return {"error": "No agents specified"}
        
        results = {}
        
        try:
            if mode == "parallel":
                # Execute all agents in parallel
                tasks = []
                for agent_id in agents:
                    tasks.append(self.agent_manager.execute_agent(agent_id, task))
                
                agent_results = await asyncio.gather(*tasks)
                for i, agent_id in enumerate(agents):
                    results[agent_id] = agent_results[i]
                    
            elif mode == "sequential":
                # Execute agents one after another, passing results along
                context = task
                for agent_id in agents:
                    result = await self.agent_manager.execute_agent(agent_id, context)
                    results[agent_id] = result
                    if result:
                        context += f"\n\nPrevious result from {agent_id}: {result}"
                        
            elif mode == "hierarchical":
                # First agent coordinates, others execute
                if len(agents) < 2:
                    return {"error": "Hierarchical mode requires at least 2 agents"}
                
                coordinator = agents[0]
                workers = agents[1:]
                
                # Get coordination plan from first agent
                coord_task = f"Coordinate this task among these agents {workers}: {task}"
                coord_result = await self.agent_manager.execute_agent(coordinator, coord_task)
                results[coordinator] = coord_result
                
                # Execute worker agents with coordination input
                for agent_id in workers:
                    worker_task = f"Execute your part of this coordinated task:\nOriginal task: {task}\nCoordination guidance: {coord_result}"
                    worker_result = await self.agent_manager.execute_agent(agent_id, worker_task)
                    results[agent_id] = worker_result
            
            return {
                "status": "completed",
                "mode": mode,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "partial_results": results
            }
    
    async def handle_business_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle various business events and trigger appropriate responses"""
        event_type = event.get("type")
        event_data = event.get("data", {})
        
        # Process through MCP if applicable
        if event_type in ["mcp_request", "agent_communication"]:
            return await self.mcp_handler.handle_mcp_request(event_data)
        
        # Trigger agent responses based on event type
        if event_type == "budget_alert":
            return await self._handle_budget_alert(event_data)
        elif event_type == "quality_issue":
            return await self._handle_quality_issue(event_data)
        elif event_type == "market_change":
            return await self._handle_market_change(event_data)
        elif event_type == "operational_alert":
            return await self._handle_operational_alert(event_data)
        else:
            return {"status": "unknown_event_type", "event_type": event_type}
    
    async def _handle_budget_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget-related alerts"""
        # Coordinate between finance and operations agents
        return await self.coordinate_agents({
            "task": f"Budget alert: {data.get('message', 'Budget threshold exceeded')}",
            "agents": ["finance", "operations"],
            "mode": "hierarchical"
        })
    
    async def _handle_quality_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quality issues"""
        return await self.coordinate_agents({
            "task": f"Quality issue reported: {data.get('description', 'Quality threshold not met')}",
            "agents": ["quality", "operations", "purchase"],
            "mode": "hierarchical"
        })
    
    async def _handle_market_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market changes"""
        return await self.coordinate_agents({
            "task": f"Market change detected: {data.get('change', 'Significant market shift observed')}",
            "agents": ["marketing", "finance", "cmo"],
            "mode": "parallel"
        })
    
    async def _handle_operational_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operational alerts"""
        return await self.coordinate_agents({
            "task": f"Operational alert: {data.get('alert', 'Operational issue detected')}",
            "agents": ["operations", "hr"],
            "mode": "sequential"
        })
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": {
                step_id: {
                    "status": step.status,
                    "agent_id": step.agent_id,
                    "task": step.task,
                    "result": step.result,
                    "error": step.error,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None
                }
                for step_id, step in workflow.steps.items()
            }
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with their statuses"""
        return [self.get_workflow_status(wid) for wid in self.workflows.keys()]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {
                "count": self.agent_manager.get_agent_count(),
                "available": self.agent_manager.list_agent_ids()
            },
            "workflows": {
                "total": len(self.workflows),
                "active": sum(1 for w in self.workflows.values() if w.status == "running"),
                "completed": sum(1 for w in self.workflows.values() if w.status == "completed"),
                "failed": sum(1 for w in self.workflows.values() if w.status == "failed")
            },
            "decision_engine": self.decision_engine is not None,
            "mcp": {
                "active": True,
                "methods": len(self.mcp_handler.method_handlers)
            }
        }


# Create global orchestrator instance
orchestrator = BusinessInfinityOrchestrator()

# Export for backward compatibility
async def process_decision(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Process decision through orchestrator"""
    return await orchestrator.process_decision(evidence)

async def coordinate_agents(request: Dict[str, Any]) -> Dict[str, Any]:
    """Coordinate agents through orchestrator"""
    return await orchestrator.coordinate_agents(request)