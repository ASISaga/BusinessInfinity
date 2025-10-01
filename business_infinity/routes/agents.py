"""
BusinessInfinity API Routes - Agents

Provides HTTP API endpoints for interacting with business agents
through the BusinessInfinity system.
"""

import json
import azure.functions as func
from datetime import datetime
from typing import Optional, Dict, Any

# Import business infinity core
try:
    from business_infinity.core.business_manager import BusinessManager
    from business_infinity.agents.agent_coordinator import AgentCoordinator
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError:
    BUSINESS_INFINITY_AVAILABLE = False
    print("Warning: BusinessInfinity core not available")


class AgentsAPI:
    """API endpoints for business agent operations"""
    
    def __init__(self, business_manager: Optional[BusinessManager] = None):
        self.business_manager = business_manager
        self.agent_coordinator = AgentCoordinator() if BUSINESS_INFINITY_AVAILABLE else None

    async def list_agents(self, req: func.HttpRequest) -> func.HttpResponse:
        """List all available business agents"""
        try:
            if not self.business_manager:
                agents = [
                    {
                        "id": "founder",
                        "name": "Founder Agent",
                        "role": "founder",
                        "status": "available",
                        "capabilities": ["strategic_planning", "vision_setting", "leadership"]
                    },
                    {
                        "id": "ceo", 
                        "name": "CEO Agent",
                        "role": "ceo",
                        "status": "available",
                        "capabilities": ["executive_decisions", "team_management", "operations"]
                    },
                    {
                        "id": "cto",
                        "name": "CTO Agent", 
                        "role": "cto",
                        "status": "available",
                        "capabilities": ["technical_architecture", "technology_strategy", "engineering"]
                    },
                    {
                        "id": "cfo",
                        "name": "CFO Agent",
                        "role": "cfo", 
                        "status": "available",
                        "capabilities": ["financial_planning", "budget_management", "financial_analysis"]
                    },
                    {
                        "id": "investor",
                        "name": "Investor Agent",
                        "role": "investor",
                        "status": "available", 
                        "capabilities": ["investment_analysis", "due_diligence", "portfolio_management"]
                    }
                ]
            else:
                agents = await self.business_manager.list_agents()
            
            return func.HttpResponse(
                json.dumps({
                    "agents": agents,
                    "total": len(agents),
                    "business_infinity_available": BUSINESS_INFINITY_AVAILABLE
                }),
                mimetype="application/json",
                status_code=200
            )
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def get_agent_details(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get detailed information about a specific agent"""
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            if self.business_manager:
                agent_details = await self.business_manager.get_agent_details(agent_id)
            else:
                # Mock agent details
                agent_details = {
                    "id": agent_id,
                    "name": f"{agent_id.title()} Agent",
                    "role": agent_id,
                    "status": "available",
                    "last_activity": datetime.now().isoformat(),
                    "performance_metrics": {
                        "tasks_completed": 42,
                        "success_rate": 0.95,
                        "avg_response_time": 1.2
                    },
                    "capabilities": ["general_business_operations"],
                    "current_workload": 0.3
                }
            
            if not agent_details:
                return func.HttpResponse(
                    json.dumps({"error": f"Agent {agent_id} not found"}),
                    mimetype="application/json",
                    status_code=404
                )

            return func.HttpResponse(
                json.dumps(agent_details),
                mimetype="application/json",
                status_code=200
            )
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def ask_agent(self, req: func.HttpRequest) -> func.HttpResponse:
        """Ask a specific agent a question"""
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Parse request body
            try:
                req_body = req.get_json()
                if not req_body:
                    raise ValueError("No JSON body")
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )

            question = req_body.get('question')
            context = req_body.get('context', {})
            
            if not question:
                return func.HttpResponse(
                    json.dumps({"error": "Question is required"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Process the request
            if self.agent_coordinator:
                response = await self.agent_coordinator.ask_agent(agent_id, question, context)
            else:
                # Mock response for development
                response = {
                    "agent_id": agent_id,
                    "question": question,
                    "answer": f"This is a mock response from {agent_id} agent. In production, this would be processed by the BusinessInfinity system.",
                    "confidence": 0.8,
                    "response_time": 0.5,
                    "timestamp": datetime.now().isoformat(),
                    "context_used": bool(context),
                    "sources": ["mock_knowledge_base"]
                }

            return func.HttpResponse(
                json.dumps(response),
                mimetype="application/json",
                status_code=200
            )
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def assign_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Assign a task to an agent"""
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Parse request body
            try:
                req_body = req.get_json()
                if not req_body:
                    raise ValueError("No JSON body")
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )

            task_description = req_body.get('task')
            priority = req_body.get('priority', 'medium')
            deadline = req_body.get('deadline')
            context = req_body.get('context', {})
            
            if not task_description:
                return func.HttpResponse(
                    json.dumps({"error": "Task description is required"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Process task assignment
            if self.agent_coordinator:
                task_result = await self.agent_coordinator.assign_task(
                    agent_id, task_description, priority, deadline, context
                )
            else:
                # Mock task assignment
                task_result = {
                    "task_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "agent_id": agent_id,
                    "task": task_description,
                    "priority": priority,
                    "status": "assigned",
                    "assigned_at": datetime.now().isoformat(),
                    "estimated_completion": None,
                    "deadline": deadline
                }

            return func.HttpResponse(
                json.dumps(task_result),
                mimetype="application/json",
                status_code=200
            )
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def get_agent_tasks(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get tasks assigned to an agent"""
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            status_filter = req.params.get('status')
            limit = int(req.params.get('limit', 50))

            if self.agent_coordinator:
                tasks = await self.agent_coordinator.get_agent_tasks(agent_id, status_filter, limit)
            else:
                # Mock tasks
                tasks = [
                    {
                        "task_id": "task_001",
                        "description": "Analyze market trends",
                        "status": "in_progress",
                        "priority": "high",
                        "assigned_at": "2024-01-15T09:00:00Z",
                        "progress": 0.7
                    },
                    {
                        "task_id": "task_002", 
                        "description": "Prepare quarterly report",
                        "status": "pending",
                        "priority": "medium",
                        "assigned_at": "2024-01-15T10:30:00Z",
                        "progress": 0.0
                    }
                ]
                
                if status_filter:
                    tasks = [t for t in tasks if t["status"] == status_filter]
                
                tasks = tasks[:limit]

            return func.HttpResponse(
                json.dumps({
                    "tasks": tasks,
                    "total": len(tasks),
                    "agent_id": agent_id,
                    "status_filter": status_filter
                }),
                mimetype="application/json",
                status_code=200
            )
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )


# Factory function for creating the API instance
def create_agents_api(business_manager: Optional[BusinessManager] = None) -> AgentsAPI:
    """Create and configure the Agents API"""
    return AgentsAPI(business_manager)


# Azure Functions entry points
async def list_agents_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler for listing agents"""
    api = create_agents_api()
    return await api.list_agents(req)


async def get_agent_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler for getting agent details"""
    api = create_agents_api()
    return await api.get_agent_details(req)


async def ask_agent_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler for asking agent questions"""
    api = create_agents_api()
    return await api.ask_agent(req)


async def assign_task_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler for assigning tasks"""
    api = create_agents_api()
    return await api.assign_task(req)


async def get_tasks_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler for getting agent tasks"""
    api = create_agents_api()
    return await api.get_agent_tasks(req)