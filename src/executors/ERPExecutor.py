
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


from ..mcp_clients.erp import create_erp_mcp_client  # You may need to adjust import path

class ERPExecutor(BaseExecutor):
    """Executor that delegates ERP queries to an MCP ERP server."""

    def __init__(self):
        super().__init__("ERPExecutor")
        self.mcp = create_erp_mcp_client()
        self.capabilities = {
            "inventory_status": "inventory.status",
            "procurement_lead_time": "procurement.lead",
            "cogs": "finance.cogs"
        }

    async def handle(self, intent: dict, ctx):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            if hasattr(ctx, 'yield_output'):
                await ctx.yield_output({"error": f"Unsupported ERP capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "erp",
            "capability": capability,
            "result": result,
            "timestamp": getattr(ctx, 'now', lambda: None)()
        }
        if hasattr(ctx, 'yield_output'):
            await ctx.yield_output(output)