"""
ERP Executor

Executor that delegates ERP queries to an MCP ERP server.
Part of the BusinessInfinity MCP integration layer.
"""

from typing import Dict, Any, Optional
import logging

# Try importing runtime and AOS
try:
    from runtime import RuntimeConfig
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False
    RuntimeConfig = None

try:
    from AgentOperatingSystem.executor.base_executor import BaseExecutor, WorkflowContext, handler
    AOS_EXECUTOR_AVAILABLE = True
except ImportError:
    AOS_EXECUTOR_AVAILABLE = False
    # Provide stubs
    class BaseExecutor:
        def __init__(self, name: str):
            self.name = name
    WorkflowContext = Any
    def handler(f): return f


logger = logging.getLogger(__name__)


class ERPExecutor(BaseExecutor):
    """Executor that delegates ERP queries to an MCP ERP server."""

    def __init__(self, mcp_client=None):
        super().__init__("ERPExecutor")
        self.mcp = mcp_client
        self.capabilities = {
            "inventory_status": "inventory.status",
            "procurement_lead_time": "procurement.lead",
            "cogs": "finance.cogs"
        }
        self.logger = logger

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext):
        capability = intent.get("capability")
        if capability not in self.capabilities:
            await ctx.yield_output({"error": f"Unsupported ERP capability: {capability}"})
            return

        if self.mcp:
            result = await self.mcp.call(self.capabilities[capability], intent.get("args", {}))
        else:
            result = {"mock": True, "capability": capability, "message": "MCP client not configured"}
        
        output = {
            "source": "erp",
            "capability": capability,
            "result": result,
        }
        await ctx.yield_output(output)