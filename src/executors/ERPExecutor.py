
from runtime import RuntimeConfig
from AgentOperatingSystem.executor.base_executor import BaseExecutor, WorkflowContext, handler


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

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            await ctx.yield_output({"error": f"Unsupported ERP capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "erp",
            "capability": capability,
            "result": result,
            "timestamp": ctx.now()
        }
        await ctx.yield_output(output)