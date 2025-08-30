import asyncio, json, os
import websockets
from protocol import MCPRequest, MCPResponse

STATE = {
    "blend_overrides": {},
    "adapter_overrides": {}
}

async def handler(ws):
    async for message in ws:
        req = MCPRequest(**json.loads(message))
        if req.method == "ping":
            resp = MCPResponse(result={"ok": True}, id=req.id)
        elif req.method == "set_blend":
            node_id, blend = req.params["node_id"], req.params["blend"]
            STATE["blend_overrides"][node_id] = blend
            resp = MCPResponse(result={"ack": True}, id=req.id)
        elif req.method == "switch_adapter":
            role, legend = req.params["role"], req.params["legend"]
            STATE["adapter_overrides"][role] = legend
            resp = MCPResponse(result={"ack": True}, id=req.id)
        else:
            resp = MCPResponse(error={"code": -32601, "message": "Method not found"}, id=req.id)
        await ws.send(resp.model_dump_json())

async def main():
    port = int(os.getenv("MCP_PORT", "8765"))
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())