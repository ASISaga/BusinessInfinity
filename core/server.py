"""
Unified Server Module
Consolidates server functionality from:
- /azure_functions/server/server.py (Flask-based conversation API)
- /shared/framework/server/main.py (FastAPI decision engine)  
- /shared/framework/mcp/server.py (WebSocket MCP server)
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Body, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import websockets
from dotenv import load_dotenv

# Import shared framework components
try:
    from ..shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
    from ..shared.framework.server.decision_engine import DecisionEngine
    from ..shared.framework.mcp.protocol import MCPRequest, MCPResponse
except ImportError:
    # Fallback imports for development
    from shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
    from shared.framework.server.decision_engine import DecisionEngine
    from shared.framework.mcp.protocol import MCPRequest, MCPResponse

# Import dashboard MCP handlers
try:
    from ..dashboard.mcp_handlers import handle_mcp
except ImportError:
    from dashboard.mcp_handlers import handle_mcp

# Import conversation API
try:
    from ..azure_functions.server.conversation_api import get_conversation
except ImportError:
    async def get_conversation():
        return {"error": "Conversation API not available"}

load_dotenv()

class UnifiedServer:
    """
    Unified server that provides:
    1. FastAPI REST endpoints for decision engine
    2. WebSocket MCP server for real-time communication
    3. Static file serving for web client
    4. Conversation API endpoints
    """
    
    def __init__(self):
        self.app = FastAPI(title="Business Infinity Unified Server")
        self.mcp_state = {
            "blend_overrides": {},
            "adapter_overrides": {}
        }
        
        # Initialize decision engine
        try:
            self.principles = load_principles()
            self.tree = load_decision_tree()
            self.adapters = load_adapters()
            self.decision_engine = DecisionEngine(self.tree, self.adapters, self.principles)
        except Exception as e:
            print(f"Warning: Could not initialize decision engine: {e}")
            self.decision_engine = None
            
        self._setup_routes()
        self._setup_static_files()
    
    def _setup_routes(self):
        """Setup all REST API routes"""
        
        # Health check
        @self.app.get("/health")
        def health():
            return {"status": "ok", "services": {
                "decision_engine": self.decision_engine is not None,
                "mcp": True,
                "conversation": True
            }}
        
        # Decision engine endpoints
        if self.decision_engine:
            @self.app.post("/decisions/run")
            def run_decision(evidence: Evidence):
                return self.decision_engine.run(evidence.data)
            
            @self.app.post("/adapters/switch")
            def switch_adapter(payload: dict = Body(...)):
                # Update adapter overrides in MCP state
                role = payload.get("role")
                legend = payload.get("legend")
                if role and legend:
                    self.mcp_state["adapter_overrides"][role] = legend
                return {"status": "ack", "requested": payload}
        
        # MCP endpoint (consolidated from triggers/http_routes.py)
        @self.app.post("/mcp")
        async def mcp_endpoint(body: dict = Body(...)):
            """Unified MCP endpoint handler"""
            try:
                # Handle dashboard MCP methods
                response = await handle_mcp(body)
                if response.get("error", {}).get("code") != -32601:  # Method found
                    return response
                
                # Handle framework MCP methods
                method = body.get("method")
                params = body.get("params", {})
                id_ = body.get("id")
                
                if method == "ping":
                    return {"jsonrpc": "2.0", "id": id_, "result": {"ok": True}}
                elif method == "set_blend":
                    node_id, blend = params["node_id"], params["blend"]
                    self.mcp_state["blend_overrides"][node_id] = blend
                    return {"jsonrpc": "2.0", "id": id_, "result": {"ack": True}}
                elif method == "switch_adapter":
                    role, legend = params["role"], params["legend"]
                    self.mcp_state["adapter_overrides"][role] = legend
                    return {"jsonrpc": "2.0", "id": id_, "result": {"ack": True}}
                else:
                    return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": "Method not found"}}
                    
            except Exception as e:
                return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32000, "message": str(e)}}
        
        # Conversation API endpoint  
        @self.app.get("/api/conversation")
        async def conversation_route():
            return await get_conversation()
    
    def _setup_static_files(self):
        """Setup static file serving"""
        # Check for static directory from azure_functions/server structure
        static_dir = None
        possible_static_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "azure_functions", "businessinfinity.asisaga.com"),
            os.path.join(os.path.dirname(__file__), "..", "webclient"),
            os.path.join(os.path.dirname(__file__), "..", "static")
        ]
        
        for dir_path in possible_static_dirs:
            if os.path.exists(dir_path):
                static_dir = dir_path
                break
        
        if static_dir:
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")
            
            @self.app.get("/")
            def root():
                index_path = os.path.join(static_dir, "index.html")
                if os.path.exists(index_path):
                    return FileResponse(index_path)
                return {"message": "Business Infinity Unified Server", "static_dir": static_dir}
    
    async def start_mcp_websocket_server(self, host: str = "0.0.0.0", port: int = None):
        """Start the WebSocket MCP server"""
        port = port or int(os.getenv("MCP_PORT", "8765"))
        
        async def ws_handler(websocket):
            async for message in websocket:
                try:
                    req = MCPRequest(**json.loads(message))
                    
                    if req.method == "ping":
                        resp = MCPResponse(result={"ok": True}, id=req.id)
                    elif req.method == "set_blend":
                        node_id, blend = req.params["node_id"], req.params["blend"]
                        self.mcp_state["blend_overrides"][node_id] = blend
                        resp = MCPResponse(result={"ack": True}, id=req.id)
                    elif req.method == "switch_adapter":
                        role, legend = req.params["role"], req.params["legend"]
                        self.mcp_state["adapter_overrides"][role] = legend
                        resp = MCPResponse(result={"ack": True}, id=req.id)
                    else:
                        resp = MCPResponse(error={"code": -32601, "message": "Method not found"}, id=req.id)
                        
                    await websocket.send(resp.model_dump_json())
                except Exception as e:
                    error_resp = MCPResponse(error={"code": -32000, "message": str(e)}, id=getattr(req, 'id', None))
                    await websocket.send(error_resp.model_dump_json())
        
        async with websockets.serve(ws_handler, host, port):
            print(f"MCP WebSocket server started on ws://{host}:{port}")
            await asyncio.Future()  # Run forever


# Pydantic models
class Evidence(BaseModel):
    data: dict


# Create global server instance
unified_server = UnifiedServer()

# Export for use in function_app.py and other modules
app = unified_server.app

# For direct execution
if __name__ == "__main__":
    import uvicorn
    
    # Start both HTTP and WebSocket servers
    async def run_servers():
        # Start WebSocket server in background
        websocket_task = asyncio.create_task(
            unified_server.start_mcp_websocket_server()
        )
        
        # Start HTTP server
        config = uvicorn.Config(app, host="0.0.0.0", port=8000)
        server = uvicorn.Server(config)
        
        await asyncio.gather(
            websocket_task,
            server.serve()
        )
    
    asyncio.run(run_servers())