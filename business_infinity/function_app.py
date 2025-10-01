"""
BusinessInfinity Azure Functions App

Main entry point for the BusinessInfinity Azure Functions application.
Integrates with AOS infrastructure and provides business-specific API endpoints.
"""

import logging
import azure.functions as func
from typing import Optional

# Import new business infinity structure
try:
    from business_infinity.core.business_manager import create_business_manager, BusinessManager
    from business_infinity.routes.agents import create_agents_api
    from business_infinity.tools.audit_viewer import BusinessAuditViewer
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"New BusinessInfinity structure not available: {e}")
    BUSINESS_INFINITY_AVAILABLE = False

# Import legacy structure for backward compatibility
try:
    from routes.health import HealthEndpoint
    from routes.analytics import AnalyticsEndpoint
    from routes.workflows import WorkflowsEndpoint  
    from business_infinity import BusinessInfinity, BusinessInfinityConfig
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

# Import AOS components
try:
    from aos.monitoring.audit_trail import get_audit_manager
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False

# =========================
# Logging & Initialization
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
business_manager: Optional[BusinessManager] = None
agents_api = None
audit_viewer = None

async def initialize_business_infinity():
    """Initialize BusinessInfinity system"""
    global business_manager, agents_api, audit_viewer
    
    if not BUSINESS_INFINITY_AVAILABLE:
        logger.warning("New BusinessInfinity structure not available")
        return False
    
    try:
        # Initialize business manager
        business_manager = await create_business_manager()
        logger.info("BusinessManager initialized successfully")
        
        # Initialize API endpoints
        agents_api = create_agents_api(business_manager)
        
        # Initialize audit viewer
        if AOS_AVAILABLE:
            audit_manager = get_audit_manager()
            audit_viewer = BusinessAuditViewer(audit_manager)
        
        logger.info("BusinessInfinity system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize BusinessInfinity: {e}")
        return False

# Initialize legacy system for fallback
legacy_business_infinity = None
legacy_health_endpoint = None
legacy_analytics_endpoint = None
legacy_workflows_endpoint = None

if LEGACY_AVAILABLE:
    try:
        config = BusinessInfinityConfig()
        legacy_business_infinity = BusinessInfinity(config)
        legacy_health_endpoint = HealthEndpoint(legacy_business_infinity)
        legacy_analytics_endpoint = AnalyticsEndpoint(legacy_business_infinity)
        legacy_workflows_endpoint = WorkflowsEndpoint(legacy_business_infinity)
        logger.info("Legacy BusinessInfinity system initialized as fallback")
    except Exception as e:
        logger.error(f"Failed to initialize legacy BusinessInfinity: {e}")

# Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# =========================
# Startup Hook
# =========================
@app.function_name("startup")
@app.timer_trigger(schedule="0 0 0 1 1 *", arg_name="timer", run_on_startup=True)  # Run once on startup
async def startup_function(timer: func.TimerRequest) -> None:
    """Initialize BusinessInfinity on startup"""
    success = await initialize_business_infinity()
    if success:
        logger.info("BusinessInfinity startup completed successfully")
    else:
        logger.error("BusinessInfinity startup failed, running in degraded mode")

# =========================
# Health & Status Endpoints
# =========================
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "timestamp": func.datetime.datetime.now().isoformat(),
            "components": {
                "business_manager": business_manager is not None,
                "aos_integration": AOS_AVAILABLE,
                "legacy_fallback": LEGACY_AVAILABLE
            }
        }
        
        # Get detailed health if business manager available
        if business_manager:
            business_health = await business_manager.health_check()
            status["business_health"] = business_health
        
        return func.HttpResponse(
            func.json.dumps(status),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        error_status = {
            "status": "error",
            "error": str(e),
            "timestamp": func.datetime.datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            func.json.dumps(error_status),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="status", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def system_status(req: func.HttpRequest) -> func.HttpResponse:
    """Detailed system status endpoint"""
    try:
        status = {
            "business_infinity_available": BUSINESS_INFINITY_AVAILABLE,
            "aos_available": AOS_AVAILABLE,
            "legacy_available": LEGACY_AVAILABLE,
            "components_initialized": {
                "business_manager": business_manager is not None,
                "agents_api": agents_api is not None,
                "audit_viewer": audit_viewer is not None
            }
        }
        
        # Add business metrics if available
        if business_manager:
            business_metrics = await business_manager.get_business_metrics()
            status["business_metrics"] = business_metrics
        
        return func.HttpResponse(
            func.json.dumps(status, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# =========================
# Agent Endpoints
# =========================
@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all available business agents"""
    if agents_api:
        return await agents_api.list_agents(req)
    elif legacy_health_endpoint:
        # Fallback to legacy endpoint
        return await legacy_health_endpoint.handle(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Agents service not available"}),
            mimetype="application/json",
            status_code=503
        )

@app.route(route="agents/{agent_id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_agent_details(req: func.HttpRequest) -> func.HttpResponse:
    """Get detailed information about a specific agent"""
    if agents_api:
        return await agents_api.get_agent_details(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Agents service not available"}),
            mimetype="application/json",
            status_code=503
        )

@app.route(route="agents/{agent_id}/ask", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Ask a question to a specific agent"""
    if agents_api:
        return await agents_api.ask_agent(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Agents service not available"}),
            mimetype="application/json",
            status_code=503
        )

@app.route(route="agents/{agent_id}/tasks", auth_level=func.AuthLevel.FUNCTION, methods=["GET", "POST"])
async def agent_tasks(req: func.HttpRequest) -> func.HttpResponse:
    """Get or assign tasks for an agent"""
    if not agents_api:
        return func.HttpResponse(
            func.json.dumps({"error": "Agents service not available"}),
            mimetype="application/json",
            status_code=503
        )
    
    if req.method == "GET":
        return await agents_api.get_agent_tasks(req)
    elif req.method == "POST":
        return await agents_api.assign_task(req)

# =========================
# Business Operations Endpoints
# =========================
@app.route(route="business/metrics", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def business_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """Get business metrics and analytics"""
    try:
        if business_manager:
            metrics = await business_manager.get_business_metrics()
            return func.HttpResponse(
                func.json.dumps(metrics, default=str),
                mimetype="application/json",
                status_code=200
            )
        elif legacy_analytics_endpoint:
            return await legacy_analytics_endpoint.get_analytics(req)
        else:
            return func.HttpResponse(
                func.json.dumps({"error": "Business metrics service not available"}),
                mimetype="application/json",
                status_code=503
            )
            
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="business/decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def initiate_decision(req: func.HttpRequest) -> func.HttpResponse:
    """Initiate a boardroom decision process"""
    try:
        if not business_manager:
            return func.HttpResponse(
                func.json.dumps({"error": "Business manager not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                func.json.dumps({"error": "Request body required"}),
                mimetype="application/json",
                status_code=400
            )
        
        topic = req_body.get("topic")
        decision_type = req_body.get("decision_type")
        context = req_body.get("context", {})
        
        if not topic or not decision_type:
            return func.HttpResponse(
                func.json.dumps({"error": "Topic and decision_type are required"}),
                mimetype="application/json",
                status_code=400
            )
        
        decision_id = await business_manager.initiate_boardroom_decision(topic, decision_type, context)
        
        return func.HttpResponse(
            func.json.dumps({
                "decision_id": decision_id,
                "topic": topic,
                "decision_type": decision_type,
                "status": "initiated",
                "timestamp": func.datetime.datetime.now().isoformat()
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# =========================
# Audit & Monitoring Endpoints
# =========================
@app.route(route="audit/report", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def audit_report(req: func.HttpRequest) -> func.HttpResponse:
    """Generate business audit report"""
    try:
        if not audit_viewer:
            return func.HttpResponse(
                func.json.dumps({"error": "Audit viewer not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        days = int(req.params.get("days", 7))
        report = await audit_viewer.generate_business_report(days)
        
        return func.HttpResponse(
            func.json.dumps(report, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="audit/decisions", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def audit_decisions(req: func.HttpRequest) -> func.HttpResponse:
    """Get audit trail of business decisions"""
    try:
        if not audit_viewer:
            return func.HttpResponse(
                func.json.dumps({"error": "Audit viewer not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        days = int(req.params.get("days", 7))
        end_date = func.datetime.datetime.now()
        start_date = end_date - func.datetime.timedelta(days=days)
        
        decisions = await audit_viewer.view_business_decisions(start_date, end_date)
        
        return func.HttpResponse(
            func.json.dumps({
                "decisions": decisions,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                },
                "total": len(decisions)
            }, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# =========================
# Legacy Fallback Endpoints
# =========================
@app.route(route="legacy/workflows", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def legacy_workflows(req: func.HttpRequest) -> func.HttpResponse:
    """Legacy workflows endpoint for backward compatibility"""
    if legacy_workflows_endpoint:
        return await legacy_workflows_endpoint.list_workflows(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Legacy workflows service not available"}),
            mimetype="application/json",
            status_code=503
        )

@app.route(route="legacy/analytics", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def legacy_analytics(req: func.HttpRequest) -> func.HttpResponse:
    """Legacy analytics endpoint for backward compatibility"""
    if legacy_analytics_endpoint:
        return await legacy_analytics_endpoint.get_analytics(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Legacy analytics service not available"}),
            mimetype="application/json",
            status_code=503
        )

# =========================
# Error Handlers
# =========================
@app.exception_handler(Exception)
async def global_exception_handler(req: func.HttpRequest, exc: Exception) -> func.HttpResponse:
    """Global exception handler"""
    logger.error(f"Unhandled exception in {req.url}: {exc}")
    
    return func.HttpResponse(
        func.json.dumps({
            "error": "Internal server error",
            "message": str(exc),
            "endpoint": req.url,
            "timestamp": func.datetime.datetime.now().isoformat()
        }),
        mimetype="application/json",
        status_code=500
    )

# =========================
# Main entry point for local development
# =========================
if __name__ == "__main__":
    import asyncio
    
    async def main():
        success = await initialize_business_infinity()
        if success:
            print("BusinessInfinity initialized successfully")
        else:
            print("BusinessInfinity initialization failed")
    
    asyncio.run(main())