from routes.health import HealthEndpoint
from routes.agents import AgentsEndpoint
from routes.conversations import ConversationsEndpoint
from routes.decisions import DecisionsEndpoint
from routes.linkedin import LinkedInEndpoint
from routes.mentor import MentorEndpoint
from routes.network import NetworkEndpoint
from routes.onboarding import OnboardingEndpoint
from routes.workflows import WorkflowsEndpoint
from routes.business_health import BusinessHealthEndpoint
from routes.business_agents import BusinessAgentsEndpoint
from routes.business_decisions import BusinessDecisionsEndpoint
from routes.business_workflows import BusinessWorkflowsEndpoint
from routes.business_analytics import BusinessAnalyticsEndpoint

# Import new Business Infinity system (always available)
from business_infinity import BusinessInfinity, BusinessInfinityConfig
from core.agents import UnifiedAgentManager, get_unified_manager
BUSINESS_INFINITY_AVAILABLE = True

# Business Infinity Core (refactored) imports
try:
    from business_infinity_core import (
        BusinessInfinity as RefactoredBusinessInfinity,
        BusinessInfinityConfig as RefactoredBusinessInfinityConfig,
        create_business_infinity
    )
    REFACTORED_BI_AVAILABLE = True
except ImportError:
    REFACTORED_BI_AVAILABLE = False

# Refactored BI instance
refactored_bi = None
if REFACTORED_BI_AVAILABLE:
    try:
        refactored_bi_config = RefactoredBusinessInfinityConfig()
        refactored_bi = create_business_infinity(refactored_bi_config)
    except Exception:
        refactored_bi = None

# Refactored endpoints
business_health_endpoint = BusinessHealthEndpoint(refactored_bi, REFACTORED_BI_AVAILABLE)
business_agents_endpoint = BusinessAgentsEndpoint(refactored_bi, REFACTORED_BI_AVAILABLE)
business_decisions_endpoint = BusinessDecisionsEndpoint(refactored_bi, REFACTORED_BI_AVAILABLE)
business_workflows_endpoint = BusinessWorkflowsEndpoint(refactored_bi, REFACTORED_BI_AVAILABLE)
business_analytics_endpoint = BusinessAnalyticsEndpoint(refactored_bi, REFACTORED_BI_AVAILABLE)

# Create the Azure Functions app (must be before any @app.route)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# === Onboarding Endpoints ===
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

# === Conversations Endpoints ===
@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_conversations(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.list_conversations(req)

# Add more conversation routes as needed (e.g., get_conversation, create_conversation, etc.)

# === Additional Conversations Endpoints ===
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

# === Workflows Endpoints ===
@app.route(route="workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_workflow(req: func.HttpRequest) -> func.HttpResponse:
    return await workflows_endpoint.execute_workflow(req)

# === Mentor Endpoints ===

# === Additional Mentor Endpoints ===
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

# === Network Endpoints ===

# === Additional Network Endpoints ===
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

# === Agents Endpoints ===
@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.list_agents(req)

@app.route(route="agents/{agent_role}/ask", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.ask_agent(req)

# === Decisions Endpoints ===
@app.route(route="decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await decisions_endpoint.make_decision(req)

# === LinkedIn Endpoints ===
@app.route(route="api/linkedin/auth", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def linkedin_auth_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    return await linkedin_endpoint.linkedin_auth_endpoint(req)

# === Health Endpoint ===

# === Business Infinity Refactored Endpoints ===
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def business_health(req: func.HttpRequest) -> func.HttpResponse:
    return await business_health_endpoint.handle(req)

@app.route(route="business/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_business_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await business_agents_endpoint.list_business_agents(req)

@app.route(route="business/agents/{agent_role}/analyze", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def analyze_with_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await business_agents_endpoint.analyze_with_agent(req)

@app.route(route="business/decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_strategic_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await business_decisions_endpoint.make_strategic_decision(req)

@app.route(route="business/workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_business_workflow(req: func.HttpRequest) -> func.HttpResponse:
    return await business_workflows_endpoint.execute_business_workflow(req)

@app.route(route="business/analytics", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_business_analytics(req: func.HttpRequest) -> func.HttpResponse:
    return await business_analytics_endpoint.get_business_analytics(req)

@app.route(route="business/performance", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_performance_report(req: func.HttpRequest) -> func.HttpResponse:
    return await business_analytics_endpoint.get_performance_report(req)
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.handle(req)

import logging
import azure.functions as func



"""
Business Infinity - Azure Functions App
Updated to use the new AOS-based Business Infinity architecture
"""
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Business Infinity system
business_infinity = None
unified_manager = None
try:
    config = BusinessInfinityConfig()
    business_infinity = BusinessInfinity(config)
    unified_manager = get_unified_manager()
    logger.info("Business Infinity system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Business Infinity: {e}")

# === Core Business Infinity Endpoints ===
health_endpoint = HealthEndpoint(business_infinity)
agents_endpoint = AgentsEndpoint(business_infinity)
conversations_endpoint = ConversationsEndpoint(business_infinity)
decisions_endpoint = DecisionsEndpoint(business_infinity)
linkedin_endpoint = LinkedInEndpoint(business_infinity)
mentor_endpoint = MentorEndpoint(business_infinity)
network_endpoint = NetworkEndpoint(business_infinity)
onboarding_endpoint = OnboardingEndpoint(business_infinity)
workflows_endpoint = WorkflowsEndpoint(business_infinity)

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    return await health_endpoint.handle(req)

@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.list_agents(req)

@app.route(route="agents/{agent_role}/ask", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    return await agents_endpoint.ask_agent(req)

@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_conversations(req: func.HttpRequest) -> func.HttpResponse:
    return await conversations_endpoint.list_conversations(req)

@app.route(route="decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_decision(req: func.HttpRequest) -> func.HttpResponse:
    return await decisions_endpoint.make_decision(req)

@app.route(route="api/linkedin/auth", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def linkedin_auth_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    return await linkedin_endpoint.linkedin_auth_endpoint(req)

@app.route(route="mentor/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_list_agents(req: func.HttpRequest) -> func.HttpResponse:
    return await mentor_endpoint.mentor_list_agents(req)

@app.route(route="network/status", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_network_status(req: func.HttpRequest) -> func.HttpResponse:
    return await network_endpoint.get_network_status(req)

@app.route(route="onboarding", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def onboarding_interface(req: func.HttpRequest) -> func.HttpResponse:
    return await onboarding_endpoint.onboarding_interface(req)

@app.route(route="workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_workflow(req: func.HttpRequest) -> func.HttpResponse:
    return await workflows_endpoint.execute_workflow(req)

# Export the app for Azure Functions runtime
from routes.business_service_bus import BusinessServiceBusHandlers

# Register Service Bus Handlers after all core variables are defined
business_service_bus_handlers = BusinessServiceBusHandlers(business_infinity, BUSINESS_INFINITY_AVAILABLE, logger)

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="AzureServiceBusConnectionString"
)
async def business_decision_processor(msg: func.ServiceBusMessage) -> None:
    await business_service_bus_handlers.business_decision_processor(msg)

@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="business-infinity",
    connection="AzureServiceBusConnectionString"
)
async def business_event_processor(msg: func.ServiceBusMessage) -> None:
    await business_service_bus_handlers.business_event_processor(msg)
if __name__ == "__main__":
    logger.info("Azure Functions app initialized with Business Infinity architecture")

# === Service Bus Event Handlers (via class) ===
from routes.business_service_bus import BusinessServiceBusHandlers

# Register Service Bus Handlers after all core variables are defined
business_service_bus_handlers = BusinessServiceBusHandlers(business_infinity, BUSINESS_INFINITY_AVAILABLE, logger)

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="AzureServiceBusConnectionString"
)
async def business_decision_processor(msg: func.ServiceBusMessage) -> None:
    await business_service_bus_handlers.business_decision_processor(msg)

@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="business-infinity",
    connection="AzureServiceBusConnectionString"
)
async def business_event_processor(msg: func.ServiceBusMessage) -> None:
    await business_service_bus_handlers.business_event_processor(msg)