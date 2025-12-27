
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


from ..mcp_clients.crm import create_crm_mcp_client  # You may need to adjust import path

class CRMExecutor(BaseExecutor):
    """Executor that delegates CRM queries to an MCP CRM server."""

    def __init__(self):
        super().__init__("CRMExecutor")
        self.mcp = create_crm_mcp_client()
        self.capabilities = {
            "pipeline_health": "pipeline.health",
            "churn_risk": "customers.churn",
            "account_activity": "accounts.activity"
        }

    async def handle(self, intent: dict, ctx):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            if hasattr(ctx, 'yield_output'):
                await ctx.yield_output({"error": f"Unsupported CRM capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "crm",
            "capability": capability,
            "result": result,
            "timestamp": getattr(ctx, 'now', lambda: None)()
        }
        if hasattr(ctx, 'yield_output'):
            await ctx.yield_output(output)