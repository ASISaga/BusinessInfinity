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



# Import orchestration primitives from AgentOperatingSystem
from RealmOfAgents.AgentOperatingSystem.orchestration import Workflow, WorkflowStep, OrchestrationEngine


class BusinessInfinityOrchestrator:

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.orchestration_engine.get_workflow_status(workflow_id)

    def list_workflows(self) -> List[Dict[str, Any]]:
        return self.orchestration_engine.list_workflows()

    async def get_system_status(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {
                "count": self.agent_manager.get_agent_count(),
                "available": self.agent_manager.list_agent_ids()
            },
            "workflows": {
                "total": len(self.orchestration_engine.workflows),
                "active": sum(1 for w in self.orchestration_engine.workflows.values() if w.status == "running"),
                "completed": sum(1 for w in self.orchestration_engine.workflows.values() if w.status == "completed"),
                "failed": sum(1 for w in self.orchestration_engine.workflows.values() if w.status == "failed")
            },
            "decision_engine": self.decision_engine is not None,
            "mcp": {
                "active": True,
                "methods": len(self.mcp_handler.method_handlers)
            }
        }
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
        return await self.orchestration_engine.execute_workflow(workflow_definition)

    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        return await self.orchestration_engine.coordinate_agents(coordination_request)


# Create global orchestrator instance
orchestrator = BusinessInfinityOrchestrator()

# Export for backward compatibility
async def process_decision(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Process decision through orchestrator"""
    return await orchestrator.process_decision(evidence)

async def coordinate_agents(request: Dict[str, Any]) -> Dict[str, Any]:
    """Coordinate agents through orchestrator"""
    return await orchestrator.coordinate_agents(request)