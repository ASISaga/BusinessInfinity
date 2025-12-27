"""
BusinessInfinity Azure Functions App using Generic Runtime

This is an example of how BusinessInfinity uses the generic runtime.
The app is now primarily configuration-driven with minimal custom code.

Key principles:
1. Use generic runtime for all infrastructure
2. Configure via bi_config.py, not code
3. Register routes declaratively
4. Delegate to AgentOperatingSystem for all infrastructure
"""

import logging
from typing import Optional

# Import generic runtime
from runtime import create_runtime, RuntimeConfig, RouteRegistry, HttpMethod, AuthLevel

# Import BusinessInfinity-specific configuration
from src.bi_config import load_bi_config, BusinessInfinityConfig

# Import BusinessInfinity application (which now uses runtime)
from src.business_infinity import create_business_infinity, BusinessInfinity

# Import route handlers
from src.routes.health import HealthEndpoint
from src.routes.agents import AgentsEndpoint
from src.routes.conversations import ConversationsEndpoint
from src.routes.decisions import DecisionsEndpoint
from src.routes.workflows import WorkflowsEndpoint
from src.routes.analytics import AnalyticsEndpoint
from src.routes.mentor import MentorEndpoint
from src.routes.network import NetworkEndpoint
from src.routes.onboarding import OnboardingEndpoint
from src.routes.linkedin import LinkedInEndpoint
from src.routes.audit import AuditEndpoint

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
bi_app: Optional[BusinessInfinity] = None
bi_config: BusinessInfinityConfig = None


async def initialize_business_infinity():
    """Initialize BusinessInfinity application."""
    global bi_app, bi_config
    
    try:
        logger.info("Initializing BusinessInfinity...")
        
        # Load configuration
        bi_config = load_bi_config()
        
        # Create BusinessInfinity application
        bi_app = await create_business_infinity(bi_config)
        
        logger.info("BusinessInfinity initialized successfully")
        return bi_app
        
    except Exception as e:
        logger.error(f"Failed to initialize BusinessInfinity: {e}")
        raise


async def shutdown_business_infinity():
    """Shutdown BusinessInfinity application."""
    global bi_app
    
    if bi_app:
        await bi_app.shutdown()
        bi_app = None


def register_bi_routes(registry: RouteRegistry, bi_app: BusinessInfinity):
    """
    Register BusinessInfinity routes to the route registry.
    
    This is where BusinessInfinity-specific routes are defined.
    All routes are registered declaratively using the generic route registry.
    """
    # Create endpoint handlers
    health_endpoint = HealthEndpoint(bi_app)
    agents_endpoint = AgentsEndpoint(bi_app)
    conversations_endpoint = ConversationsEndpoint(bi_app)
    decisions_endpoint = DecisionsEndpoint(bi_app)
    workflows_endpoint = WorkflowsEndpoint(bi_app)
    analytics_endpoint = AnalyticsEndpoint(bi_app)
    mentor_endpoint = MentorEndpoint(bi_app)
    network_endpoint = NetworkEndpoint(bi_app)
    onboarding_endpoint = OnboardingEndpoint(bi_app)
    linkedin_endpoint = LinkedInEndpoint(bi_app)
    
    # Register routes
    # Health & Status
    registry.register(
        "health",
        health_endpoint.handle,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.ANONYMOUS,
        description="Health check endpoint",
        tags=["health", "monitoring"]
    )
    
    # Agents
    registry.register(
        "business/agents",
        agents_endpoint.list_business_agents,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="List all business agents",
        tags=["agents"]
    )
    
    registry.register(
        "business/agents/{agent_role}/analyze",
        agents_endpoint.analyze_with_agent,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Analyze with specific agent",
        tags=["agents"]
    )
    
    registry.register(
        "agents",
        agents_endpoint.list_agents,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="List agents",
        tags=["agents"]
    )
    
    registry.register(
        "agents/{agent_role}/ask",
        agents_endpoint.ask_agent,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Ask agent a question",
        tags=["agents"]
    )
    
    # Conversations
    registry.register(
        "conversations",
        conversations_endpoint.list_conversations,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="List conversations",
        tags=["conversations"]
    )
    
    registry.register(
        "conversations",
        conversations_endpoint.create_conversation,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Create conversation",
        tags=["conversations"]
    )
    
    # Decisions
    registry.register(
        "business/decisions",
        decisions_endpoint.make_strategic_decision,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Make strategic decision",
        tags=["decisions"]
    )
    
    registry.register(
        "decisions",
        decisions_endpoint.make_decision,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Make decision",
        tags=["decisions"]
    )
    
    # Workflows
    registry.register(
        "business/workflows/{workflow_name}",
        workflows_endpoint.execute_business_workflow,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Execute business workflow",
        tags=["workflows"]
    )
    
    registry.register(
        "workflows/{workflow_name}",
        workflows_endpoint.execute_workflow,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Execute workflow",
        tags=["workflows"]
    )
    
    # Analytics
    registry.register(
        "business/analytics",
        analytics_endpoint.get_business_analytics,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="Get business analytics",
        tags=["analytics"]
    )
    
    registry.register(
        "business/performance",
        analytics_endpoint.get_performance_report,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="Get performance report",
        tags=["analytics"]
    )
    
    # Mentor Mode
    if bi_config.mentor_mode_enabled:
        registry.register(
            "mentor/agents/chat",
            mentor_endpoint.mentor_chat_with_agent,
            methods=[HttpMethod.POST],
            auth_level=AuthLevel.FUNCTION,
            description="Chat with agent in mentor mode",
            tags=["mentor"]
        )
        
        registry.register(
            "mentor/agents/fine-tune",
            mentor_endpoint.mentor_fine_tune_agent,
            methods=[HttpMethod.POST],
            auth_level=AuthLevel.FUNCTION,
            description="Fine-tune agent",
            tags=["mentor"]
        )
    
    # Network
    if bi_config.network_discovery_enabled:
        registry.register(
            "network/join",
            network_endpoint.join_network,
            methods=[HttpMethod.POST],
            auth_level=AuthLevel.FUNCTION,
            description="Join network",
            tags=["network"]
        )
        
        registry.register(
            "network/discover-boardrooms",
            network_endpoint.discover_boardrooms,
            methods=[HttpMethod.GET],
            auth_level=AuthLevel.FUNCTION,
            description="Discover peer boardrooms",
            tags=["network"]
        )
    
    # Onboarding
    if bi_config.onboarding_enabled:
        registry.register(
            "onboarding",
            onboarding_endpoint.onboarding_interface,
            methods=[HttpMethod.GET],
            auth_level=AuthLevel.ANONYMOUS,
            description="Onboarding interface",
            tags=["onboarding"]
        )
        
        registry.register(
            "api/onboarding/parse-website",
            onboarding_endpoint.parse_website,
            methods=[HttpMethod.POST],
            auth_level=AuthLevel.ANONYMOUS,
            description="Parse website for onboarding",
            tags=["onboarding"]
        )
    
    # LinkedIn
    if bi_config.linkedin_verification_enabled:
        registry.register(
            "api/linkedin/auth",
            linkedin_endpoint.linkedin_auth_endpoint,
            methods=[HttpMethod.POST],
            auth_level=AuthLevel.ANONYMOUS,
            description="LinkedIn authentication",
            tags=["linkedin"]
        )


# Load configuration
bi_config = load_bi_config()

# Create runtime configuration from BI config
runtime_config = bi_config.to_runtime_config()

# Create route registry
route_registry = RouteRegistry()

# Create runtime with BusinessInfinity initialization
runtime = create_runtime(
    config=runtime_config,
    route_registry=route_registry,
    app_initializer=initialize_business_infinity,
    app_shutdown=shutdown_business_infinity,
    register_default_routes=True  # This adds /health endpoint
)

# Register BusinessInfinity-specific routes
# Note: We can't register routes that depend on bi_app until it's initialized
# So we'll do this in a startup hook or use lazy registration

# Get Azure Functions app
app = runtime.get_func_app()

# Register routes to Azure Functions
runtime.register_routes_to_azure_functions()

# Create startup function
runtime.create_startup_function()

# Add a post-startup hook to register BI routes after initialization
@app.function_name("register_bi_routes_startup")
@app.timer_trigger(schedule="0 0 0 1 1 *", arg_name="timer", run_on_startup=True)
async def register_bi_routes_on_startup(timer) -> None:
    """Register BusinessInfinity routes after app initialization."""
    global bi_app, route_registry
    
    if bi_app:
        # Register all BusinessInfinity routes
        register_bi_routes(route_registry, bi_app)
        
        # Re-register routes to Azure Functions
        runtime.register_routes_to_azure_functions()
        
        logger.info("BusinessInfinity routes registered successfully")


logger.info("BusinessInfinity Azure Functions app initialized with generic runtime")
