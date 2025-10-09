
from AgentOperatingSystem.executor.base_executor import BaseExecutor, WorkflowContext, handler


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

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext[dict]):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            await ctx.yield_output({"error": f"Unsupported LinkedIn capability: {capability}"})
            return

        result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        output = {
            "source": "linkedin",
            "capability": capability,
            "result": result,
            "timestamp": ctx.now()
        }
        await ctx.yield_output(output)