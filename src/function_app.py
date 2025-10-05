# Ensure LEGACY_AVAILABLE is always defined for status reporting
LEGACY_AVAILABLE = False
# =========================
# BusinessInfinity Azure Functions App (from function_app1.py)
# =========================

# --- Imports for new business infinity structure and audit viewer ---
import logging
from typing import Optional
import azure.functions as func

from orchestration.business_manager import create_business_manager, BusinessManager

from routes.agents import create_agents_api
from routes.health import HealthEndpoint
from routes.agents import AgentsEndpoint
from routes.conversations import ConversationsEndpoint
from routes.decisions import DecisionsEndpoint
from routes.linkedin import LinkedInEndpoint
from routes.mentor import MentorEndpoint
from routes.network import NetworkEndpoint
from routes.onboarding import OnboardingEndpoint
from routes.workflows import WorkflowsEndpoint
from routes.analytics import AnalyticsEndpoint
from routes.audit import AuditEndpoint
from routes.business_service_bus import BusinessServiceBusHandlers

from tools.audit_viewer import BusinessAuditViewer
from tools import BusinessInfinity, BusinessInfinityConfig

# Import AOS components
from aos.monitoring.audit_trail import get_audit_manager

from agents import UnifiedAgentManager, get_unified_manager


# --- Global instances for new structure ---
business_manager: Optional['BusinessManager'] = None
agents_api = None
audit_viewer = None
audit_endpoint = None

async def initialize_business_infinity():
    """Initialize BusinessInfinity system (new structure)"""
    global business_manager, agents_api, audit_viewer
    try:
        # Initialize business manager
        global business_manager, agents_api, audit_viewer, audit_endpoint
        business_manager = await create_business_manager()
        logger.info("BusinessManager initialized successfully")
        # Initialize API endpoints
        agents_api = create_agents_api(business_manager)
        # Initialize audit viewer
        audit_manager = get_audit_manager()
        audit_viewer = BusinessAuditViewer(audit_manager)
        audit_endpoint = AuditEndpoint(audit_viewer)
        logger.info("BusinessInfinity system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize BusinessInfinity: {e}")
        return False

# --- Startup hook for Azure Functions (new structure) ---
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.function_name("startup")
@app.timer_trigger(schedule="0 0 0 1 1 *", arg_name="timer", run_on_startup=True)
async def startup_function(timer: func.TimerRequest) -> None:
    """Initialize BusinessInfinity on startup (new structure)"""
    success = await initialize_business_infinity()
    if success:
        logger.info("BusinessInfinity startup completed successfully")
    else:
        logger.error("BusinessInfinity startup failed, running in degraded mode")


# --- Health & Status Endpoints (refactored) ---
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.handle(req)

@app.route(route="status", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def system_status(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.system_status(req)

# --- Agent Endpoints (new structure) ---
@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all available business agents (new structure)"""
    if agents_api:
        return await agents_api.list_agents(req)
    else:
        return func.HttpResponse(
            func.json.dumps({"error": "Agents service not available"}),
            mimetype="application/json",
            status_code=503
        )

@app.route(route="agents/{agent_id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_agent_details(req: func.HttpRequest) -> func.HttpResponse:
    """Get detailed information about a specific agent (new structure)"""
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
    """Ask a question to a specific agent (new structure)"""
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
    """Get or assign tasks for an agent (new structure)"""
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

# --- Audit & Monitoring Endpoints (new structure) ---


# --- Audit & Monitoring Endpoints (refactored) ---
@app.route(route="audit/report", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def audit_report(req: func.HttpRequest) -> func.HttpResponse:
    """Generate business audit report (new structure)"""
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
    """Get audit trail of business decisions (new structure)"""
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
# Logging & Initialization
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Legacy/Primary Business Infinity system ---
business_infinity = None
unified_manager = None
try:
    config = BusinessInfinityConfig()
    business_infinity = BusinessInfinity(config)
    unified_manager = get_unified_manager()
    logger.info("Business Infinity system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Business Infinity: {e}")


# --- Endpoint instances (legacy/primary) ---
health_endpoint = HealthEndpoint(business_infinity)
agents_endpoint = AgentsEndpoint(business_infinity)
conversations_endpoint = ConversationsEndpoint(business_infinity)
decisions_endpoint = DecisionsEndpoint(business_infinity)
linkedin_endpoint = LinkedInEndpoint(business_infinity)
mentor_endpoint = MentorEndpoint(business_infinity)
network_endpoint = NetworkEndpoint(business_infinity)
onboarding_endpoint = OnboardingEndpoint(business_infinity)
workflows_endpoint = WorkflowsEndpoint(business_infinity)
analytics_endpoint = AnalyticsEndpoint(business_infinity)


# --- Legacy AuditEndpoint instantiation ---
from aos.monitoring.audit_trail import get_audit_manager
from tools.audit_viewer import BusinessAuditViewer
from routes.audit import AuditEndpoint
audit_manager_legacy = get_audit_manager()
audit_viewer_legacy = BusinessAuditViewer(audit_manager_legacy)
audit_endpoint_legacy = AuditEndpoint(audit_viewer_legacy)

# Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# =========================
# HTTP Endpoints (Legacy/Primary)
# =========================
# =========================
# HTTP Endpoints (Refactored/Alternate)
# =========================

# --- Business Infinity Refactored Endpoints ---
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def business_health(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.handle(req)

@app.route(route="business/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_business_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.list_business_agents(req)

@app.route(route="business/agents/{agent_role}/analyze", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def analyze_with_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.analyze_with_agent(req)

@app.route(route="business/decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_strategic_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await decisions_endpoint.make_strategic_decision(req)

@app.route(route="business/workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_business_workflow(req: func.HttpRequest) -> func.HttpResponse:
    return await workflows_endpoint.execute_business_workflow(req)

@app.route(route="business/analytics", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_business_analytics(req: func.HttpRequest) -> func.HttpResponse:
    return await analytics_endpoint.get_business_analytics(req)

@app.route(route="business/performance", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_performance_report(req: func.HttpRequest) -> func.HttpResponse:
    return await analytics_endpoint.get_performance_report(req)


# --- Onboarding Endpoints ---
@app.route(route="onboarding", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def onboarding_interface(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.onboarding_interface(req)

@app.route(route="api/onboarding/parse-website", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def parse_website(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.parse_website(req)

@app.route(route="api/onboarding/upload-deck", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def upload_deck(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.upload_deck(req)

@app.route(route="api/onboarding/upload-financials", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def upload_financials(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.upload_financials(req)

@app.route(route="api/onboarding/connect-system", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def connect_system(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.connect_system(req)

@app.route(route="api/onboarding/generate-voice-profile", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def generate_voice_profile(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.generate_voice_profile(req)

@app.route(route="api/onboarding/quick-action", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def handle_quick_action(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.handle_quick_action(req)

@app.route(route="api/onboarding/audit-trail", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.get_audit_trail(req)

@app.route(route="api/onboarding/export-data", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def export_customer_data(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.export_customer_data(req)

@app.route(route="api/onboarding/request-deletion", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def request_data_deletion(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.request_data_deletion(req)

@app.route(route="api/onboarding/rbac", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_rbac_info(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.get_rbac_info(req)

@app.route(route="api/onboarding/incident-contact", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_incident_contact_info(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.get_incident_contact_info(req)

@app.route(route="api/onboarding/retention-policy", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.get_retention_policy(req)

# --- Conversations Endpoints ---
@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_conversations(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.list_conversations(req)

@app.route(route="conversations/{conversation_id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_conversation(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.get_conversation(req)

@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def create_conversation(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.create_conversation(req)

@app.route(route="conversations/{conversation_id}/sign", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def sign_conversation(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.sign_conversation(req)

@app.route(route="conversations/a2a", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def create_a2a_communication(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.create_a2a_communication(req)

@app.route(route="conversations/{conversation_id}/events", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_conversation_events(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.get_conversation_events(req)

@app.route(route="conversations/dashboard", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def conversations_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.conversations_dashboard(req)

# --- Workflows Endpoints ---
@app.route(route="workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_workflow(req: func.HttpRequest) -> func.HttpResponse:
    return await workflows_endpoint.execute_workflow(req)

# --- Mentor Endpoints ---
@app.route(route="mentor/agents/chat", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_chat_with_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_chat_with_agent(req)

@app.route(route="mentor/agents/fine-tune", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_fine_tune_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_fine_tune_agent(req)

@app.route(route="mentor/agents/training-logs", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_get_training_logs(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_get_training_logs(req)

@app.route(route="mentor/agents/deploy-adapter", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_deploy_adapter(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_deploy_adapter(req)

@app.route(route="mentor/mode-ui", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_mode_ui(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_mode_ui(req)

@app.route(route="mentor/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_list_agents(req)

# --- Network Endpoints ---
@app.route(route="network/join", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def join_network(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.join_network(req)

@app.route(route="network/discover-boardrooms", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def discover_boardrooms(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.discover_boardrooms(req)

@app.route(route="network/negotiations", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def handle_negotiations(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.handle_negotiations(req)

@app.route(route="network/agreements", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def handle_agreements(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.handle_agreements(req)

@app.route(route="network/sign-agreement", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def sign_agreement(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.sign_agreement(req)

@app.route(route="network/verification-status", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_verification_status(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.get_verification_status(req)

@app.route(route="network/activity", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_network_activity(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.get_network_activity(req)

@app.route(route="network/heartbeat", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def send_heartbeat(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.send_heartbeat(req)

@app.route(route="network/stats", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_network_stats(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.get_network_stats(req)

@app.route(route="network/status", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_network_status(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.get_network_status(req)

# --- Agents Endpoints ---
@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.list_agents(req)

@app.route(route="agents/{agent_role}/ask", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.ask_agent(req)

# --- Decisions Endpoints ---
@app.route(route="decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await decisions_endpoint.make_decision(req)

# --- LinkedIn Endpoints ---
@app.route(route="api/linkedin/auth", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def linkedin_auth_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    return await linkedin_endpoint.linkedin_auth_endpoint(req)

# --- Analytics Endpoints ---
# (Add analytics endpoints here if needed)


# --- Health Endpoint (Legacy/Primary) ---
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.handle(req)


# =========================
# Service Bus Event Handlers (Legacy/Primary)
# =========================
service_bus_handlers = BusinessServiceBusHandlers(business_infinity, logger)

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="AzureServiceBusConnectionString"
)
async def business_decision_processor(msg: func.ServiceBusMessage) -> None:
    await service_bus_handlers.business_decision_processor(msg)

@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="business-infinity",
    connection="AzureServiceBusConnectionString"
)
async def business_event_processor(msg: func.ServiceBusMessage) -> None:
    await service_bus_handlers.business_event_processor(msg)

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="AzureServiceBusConnectionString"
)
async def business_decision_processor_refactored(msg: func.ServiceBusMessage) -> None:
    await service_bus_handlers.business_decision_processor(msg)

@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="business-infinity",
    connection="AzureServiceBusConnectionString"
)
async def business_event_processor_refactored(msg: func.ServiceBusMessage) -> None:
    await service_bus_handlers.business_event_processor(msg)

if __name__ == "__main__":
    logger.info("Azure Functions app initialized with Business Infinity architecture")