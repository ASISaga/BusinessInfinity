"""
Business Infinity - Azure Functions App (Refactored)

This module provides the Azure Functions HTTP API for Business Infinity,
built on the clean AOS/BI architecture. It focuses on business-specific
endpoints while leveraging AOS infrastructure.
"""

import json
import logging
import azure.functions as func
from datetime import datetime
from typing import Dict, Any, Optional

# Business Infinity Core (clean architecture)
try:
    from business_infinity_core import (
        BusinessInfinity,
        BusinessInfinityConfig,
        create_business_infinity
    )
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError as e:
    logging.error(f"Business Infinity core not available: {e}")
    BUSINESS_INFINITY_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Global Business Infinity instance
business_infinity: Optional[BusinessInfinity] = None

# Initialize Business Infinity
if BUSINESS_INFINITY_AVAILABLE:
    try:
        config = BusinessInfinityConfig()
        business_infinity = create_business_infinity(config)
        logger.info("Business Infinity initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Business Infinity: {e}")
        BUSINESS_INFINITY_AVAILABLE = False


# === Core Business Endpoints ===

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        health_status = {
            "service": "Business Infinity",
            "status": "healthy" if BUSINESS_INFINITY_AVAILABLE else "degraded",
            "aos_available": BUSINESS_INFINITY_AVAILABLE,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0-refactored"
        }
        
        if business_infinity:
            # Add business context if available
            health_status["business_context"] = business_infinity.business_context
        
        status_code = 200 if BUSINESS_INFINITY_AVAILABLE else 503
        
        return func.HttpResponse(
            json.dumps(health_status),
            status_code=status_code,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_business_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all available business agents"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization to complete
        await business_infinity._initialize_task
        
        agents_info = {}
        for agent_id, agent in business_infinity.business_agents.items():
            agents_info[agent_id] = {
                "id": agent_id,
                "role": agent.role,
                "domain": agent.domain,
                "expertise": agent.domain_expertise,
                "kpis": list(agent.business_kpis.keys()),
                "status": "active"
            }
        
        return func.HttpResponse(
            json.dumps({
                "agents": agents_info,
                "total_agents": len(agents_info),
                "timestamp": datetime.utcnow().isoformat()
            }),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/agents/{agent_role}/analyze", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def analyze_with_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Get analysis from a specific business agent"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        agent_role = req.route_params.get('agent_role')
        if not agent_role:
            return func.HttpResponse(
                json.dumps({"error": "Agent role is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Get request body
        try:
            request_json = req.get_json()
            context = request_json.get("context", {})
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Find the agent
        agent = business_infinity.business_agents.get(agent_role.lower())
        if not agent:
            return func.HttpResponse(
                json.dumps({"error": f"Agent '{agent_role}' not found"}),
                status_code=404,
                headers={"Content-Type": "application/json"}
            )
        
        # Get analysis from agent
        analysis = await agent.analyze_business_context(context)
        
        return func.HttpResponse(
            json.dumps(analysis),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Agent analysis failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_strategic_decision(req: func.HttpRequest) -> func.HttpResponse:
    """Make a strategic business decision using multi-agent collaboration"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Get request body
        try:
            request_json = req.get_json()
            decision_context = request_json.get("decision_context", {})
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Make strategic decision
        decision_result = await business_infinity.make_strategic_decision(decision_context)
        
        return func.HttpResponse(
            json.dumps(decision_result),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Strategic decision failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_business_workflow(req: func.HttpRequest) -> func.HttpResponse:
    """Execute a specific business workflow"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        workflow_name = req.route_params.get('workflow_name')
        if not workflow_name:
            return func.HttpResponse(
                json.dumps({"error": "Workflow name is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Get request body
        try:
            request_json = req.get_json()
            parameters = request_json.get("parameters", {})
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Execute workflow
        workflow_result = await business_infinity.execute_business_workflow(workflow_name, parameters)
        
        return func.HttpResponse(
            json.dumps(workflow_result),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/analytics", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_business_analytics(req: func.HttpRequest) -> func.HttpResponse:
    """Get current business analytics and KPIs"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Get analytics report
        analytics = await business_infinity.get_business_analytics()
        
        return func.HttpResponse(
            json.dumps(analytics),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Analytics request failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="business/performance", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_performance_report(req: func.HttpRequest) -> func.HttpResponse:
    """Get business performance report"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Get performance report from analytics engine
        if business_infinity.analytics_engine:
            performance_report = await business_infinity.analytics_engine.generate_performance_report()
        else:
            performance_report = {"error": "Analytics engine not available"}
        
        return func.HttpResponse(
            json.dumps(performance_report),
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Performance report failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


# === Service Bus Event Handlers ===

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="AzureServiceBusConnectionString"
)
async def business_decision_processor(msg: func.ServiceBusMessage) -> None:
    """Process business decisions from service bus"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            logger.warning("Business decision received but Business Infinity not available")
            return
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Parse message
        decision_context = json.loads(msg.get_body().decode('utf-8'))
        
        # Process decision asynchronously
        decision_result = await business_infinity.make_strategic_decision(decision_context)
        
        logger.info(f"Processed business decision: {decision_result.get('id', 'unknown')}")
    
    except Exception as e:
        logger.error(f"Business decision processing failed: {e}")


@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="business-infinity",
    connection="AzureServiceBusConnectionString"
)
async def business_event_processor(msg: func.ServiceBusMessage) -> None:
    """Process business events from service bus"""
    try:
        if not BUSINESS_INFINITY_AVAILABLE or not business_infinity:
            logger.warning("Business event received but Business Infinity not available")
            return
        
        # Wait for initialization
        await business_infinity._initialize_task
        
        # Parse event
        event_data = json.loads(msg.get_body().decode('utf-8'))
        event_type = event_data.get('type', 'unknown')
        
        logger.info(f"Processing business event: {event_type}")
        
        # Route event based on type
        if event_type == "performance_metric":
            await _process_performance_metric(event_data)
        elif event_type == "business_milestone":
            await _process_business_milestone(event_data)
        elif event_type == "external_integration":
            await _process_external_integration(event_data)
        
    except Exception as e:
        logger.error(f"Business event processing failed: {e}")


# === Helper Functions ===

async def _process_performance_metric(event_data: Dict[str, Any]) -> None:
    """Process performance metric events"""
    if business_infinity and business_infinity.analytics_engine:
        metric_name = event_data.get('metric_name')
        metric_value = event_data.get('metric_value')
        metric_unit = event_data.get('metric_unit', 'count')
        
        if metric_name and metric_value is not None:
            await business_infinity.analytics_engine.record_metric(
                name=metric_name,
                value=metric_value,
                unit=metric_unit,
                metric_type="external"
            )


async def _process_business_milestone(event_data: Dict[str, Any]) -> None:
    """Process business milestone events"""
    milestone = event_data.get('milestone')
    logger.info(f"Business milestone achieved: {milestone}")
    
    # Could trigger celebration workflow or stakeholder notifications


async def _process_external_integration(event_data: Dict[str, Any]) -> None:
    """Process external integration events"""
    integration_type = event_data.get('integration_type')
    logger.info(f"External integration event: {integration_type}")
    
    # Could trigger data synchronization or workflow updates