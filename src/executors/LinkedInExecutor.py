
# Try to import from runtime first
try:
    from runtime import RuntimeConfig
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False

# Import AOS executor base
try:
    from AgentOperatingSystem.executor.base_executor import BaseExecutor, WorkflowContext, handler
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    # Create placeholder if AOS not available
    class BaseExecutor:
        def __init__(self, name):
            self.name = name
    class WorkflowContext:
        pass
    def handler(func):
        return func


from ..mcp_clients.linkedin import create_linkedin_mcp_client  # You may need to adjust import path

class LinkedInExecutor(BaseExecutor):
    """Executor that delegates LinkedIn queries to an MCP LinkedIn server."""

    def __init__(self):
        super().__init__("LinkedInExecutor")
        self.mcp = create_linkedin_mcp_client()
        self.capabilities = {
            "profile_lookup": "profiles.lookup",
            "network_insights": "network.insights",
            "hiring_signals": "hiring.signals"
        }

    async def handle(self, intent: dict, ctx):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            if hasattr(ctx, 'yield_output'):
                await ctx.yield_output({"error": f"Unsupported LinkedIn capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "linkedin",
            "capability": capability,
            "result": result,
            "timestamp": getattr(ctx, 'now', lambda: None)()
        }
        if hasattr(ctx, 'yield_output'):
            await ctx.yield_output(output)