

from AgentOperatingSystem.executor.base_executor import BaseExecutor, WorkflowContext, handler


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

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext[dict]):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            await ctx.yield_output({"error": f"Unsupported CRM capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "crm",
            "capability": capability,
            "result": result,
            "timestamp": ctx.now()
        }
        await ctx.yield_output(output)