# example_boardroom_orchestrator.py
"""
Example usage for BoardroomOrchestrator.
"""
import os
import asyncio
from .BoardroomOrchestrator import BoardroomOrchestrator

# Minimal MCP client stubs (replace with real MCP clients)
class DummyMCP:
    async def call(self, capability, args):
        return {"capability": capability, "args": args, "data": "dummy"}

mcp_clients = {
    "erp": DummyMCP(),
    "crm": DummyMCP(),
    "linkedin": DummyMCP(),
}

if __name__ == "__main__":
    orchestrator = BoardroomOrchestrator(
        api_key=os.getenv("OPENAI_API_KEY", "sk-test"),
        mcp_clients=mcp_clients,
        governance_path="boardroom.governance.yaml",
    )
    asyncio.run(orchestrator.run_boardroom("Should we expand into renewable energy markets?"))
