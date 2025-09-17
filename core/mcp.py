"""
Unified MCP (Multi-Agent Communication Protocol) System
Consolidates MCP functionality from:
- /shared/framework/mcp/server.py (WebSocket MCP server)
- /dashboard/mcp_handlers.py (Dashboard MCP handlers)
- MCP endpoints in /triggers/http_routes.py
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import websockets

# Import protocol classes
try:
    from ..shared.framework.mcp.protocol import MCPRequest, MCPResponse
except ImportError:
    try:
        from shared.framework.mcp.protocol import MCPRequest, MCPResponse
    except ImportError:
        from pydantic import BaseModel
        
        class MCPRequest(BaseModel):
            method: str
            params: dict = {}
            id: Optional[str] = None
            
        class MCPResponse(BaseModel):
            result: Optional[dict] = None
            error: Optional[dict] = None
            id: Optional[str] = None

# Import dashboard state and prompts
try:
    from ..dashboard.state import founder_state, investor_state, finance_state, tech_state, ops_state
    from ..dashboard.prompts import APPROVAL_PROMPT
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    # Create fallback state objects
    founder_state = {"plans": {}}
    investor_state = {"risk": {}}
    finance_state = {"budgets": {}, "liquidity": {"cash": 100000, "monthly_burn": 10000}}
    tech_state = {"incidents": []}
    ops_state = {"alerts": []}
    APPROVAL_PROMPT = "Evaluate this plan and return JSON with 'decision' field (approve/reject): {input}"

# Optional semantic kernel import
try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False


class UnifiedMCPHandler:
    """
    Unified MCP handler that manages all MCP communication methods:
    1. WebSocket server for real-time communication
    2. HTTP endpoint handlers for REST API integration
    3. Dashboard-specific MCP methods
    4. Framework-level MCP methods
    """
    
    def __init__(self):
        self.state = {
            "blend_overrides": {},
            "adapter_overrides": {}
        }
        
        self.kernel = None
        if SEMANTIC_KERNEL_AVAILABLE:
            self.kernel = Kernel()
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.kernel.add_service(
                        OpenAIChatCompletion(
                            service_id="openai",
                            api_key=api_key,
                            ai_model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                        )
                    )
            except Exception:
                pass
        
        # Method registry for extensibility
        self.method_handlers: Dict[str, Callable] = {
            # Framework methods
            "ping": self._handle_ping,
            "set_blend": self._handle_set_blend,
            "switch_adapter": self._handle_switch_adapter,
            
            # Dashboard methods
            "founder.approvePlan": self._handle_founder_approve_plan,
            "cfo.approveBudget": self._handle_cfo_approve_budget,
            "cfo.getLiquidity": self._handle_cfo_get_liquidity,
            "cto.getIncidentSummary": self._handle_cto_get_incident_summary,
            "coo.acknowledgeAlert": self._handle_coo_acknowledge_alert,
            "investor.getRiskBreakdown": self._handle_investor_get_risk_breakdown,
        }
    
    async def run_prompt(self, prompt: str, input_text: str) -> str:
        """Run semantic kernel prompt if available"""
        if not self.kernel or not SEMANTIC_KERNEL_AVAILABLE:
            # Fallback response
            return json.dumps({"decision": "approve", "reason": "Semantic kernel not available"})
        
        try:
            func = self.kernel.create_semantic_function(prompt)
            result = await func.invoke_async(input_text)
            return str(result)
        except Exception as e:
            return json.dumps({"decision": "error", "reason": str(e)})
    
    # Framework method handlers
    async def _handle_ping(self, params: dict, id_: str) -> dict:
        """Handle ping method"""
        return {"jsonrpc": "2.0", "id": id_, "result": {"ok": True}}
    
    async def _handle_set_blend(self, params: dict, id_: str) -> dict:
        """Handle set_blend method"""
        node_id = params.get("node_id")
        blend = params.get("blend")
        if node_id and blend:
            self.state["blend_overrides"][node_id] = blend
        return {"jsonrpc": "2.0", "id": id_, "result": {"ack": True}}
    
    async def _handle_switch_adapter(self, params: dict, id_: str) -> dict:
        """Handle switch_adapter method"""
        role = params.get("role")
        legend = params.get("legend")
        if role and legend:
            self.state["adapter_overrides"][role] = legend
        return {"jsonrpc": "2.0", "id": id_, "result": {"ack": True}}
    
    # Dashboard method handlers
    async def _handle_founder_approve_plan(self, params: dict, id_: str) -> dict:
        """Handle founder.approvePlan method"""
        plan_id = params.get("planId")
        if not plan_id:
            raise ValueError("planId is required")
            
        plan = founder_state["plans"].get(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        eval_json = await self.run_prompt(APPROVAL_PROMPT, plan["title"])
        try:
            decision_data = json.loads(eval_json)
            decision = decision_data.get("decision", "approve")
        except:
            decision = "approve"  # Fallback
        
        if decision == "approve":
            plan["status"] = "approved"
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "result": {
                    "status": "approved",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "status": "rejected",
                "timestamp": datetime.utcnow().isoformat(),
                "decision": decision
            }
        }
    
    async def _handle_cfo_approve_budget(self, params: dict, id_: str) -> dict:
        """Handle cfo.approveBudget method"""
        budget_id = params.get("budgetId")
        amount = params.get("amount")
        
        if not budget_id:
            raise ValueError("budgetId is required")
            
        budget = finance_state["budgets"].get(budget_id)
        if not budget:
            raise ValueError("Budget not found")
        
        budget["status"] = "approved"
        if amount:
            budget["amount"] = amount
            
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "status": "approved",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def _handle_cfo_get_liquidity(self, params: dict, id_: str) -> dict:
        """Handle cfo.getLiquidity method"""
        days = int(params.get("windowDays", 7))
        cash = finance_state["liquidity"]["cash"]
        burn = finance_state["liquidity"]["monthly_burn"]
        runway_months = max(0, round(cash / max(1, burn), 2))
        
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "days": days,
                "cash": cash,
                "runwayMonths": runway_months
            }
        }
    
    async def _handle_cto_get_incident_summary(self, params: dict, id_: str) -> dict:
        """Handle cto.getIncidentSummary method"""
        open_count = sum(1 for i in tech_state["incidents"] if i.get("status") == "open")
        sev1 = sum(1 for i in tech_state["incidents"] if i.get("status") == "open" and i.get("sev") == 1)
        sev2 = sum(1 for i in tech_state["incidents"] if i.get("status") == "open" and i.get("sev") == 2)
        
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "open": open_count,
                "sev1": sev1,
                "sev2": sev2
            }
        }
    
    async def _handle_coo_acknowledge_alert(self, params: dict, id_: str) -> dict:
        """Handle coo.acknowledgeAlert method"""
        alert_id = params.get("alertId")
        if not alert_id:
            raise ValueError("alertId is required")
            
        alert = next((a for a in ops_state["alerts"] if a.get("id") == alert_id), None)
        if not alert:
            raise ValueError("Alert not found")
        
        alert["status"] = "acknowledged"
        
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "acknowledged": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def _handle_investor_get_risk_breakdown(self, params: dict, id_: str) -> dict:
        """Handle investor.getRiskBreakdown method"""
        portfolio_id = params.get("portfolioId")
        if not portfolio_id:
            raise ValueError("portfolioId is required")
            
        if portfolio_id not in investor_state["risk"]:
            raise ValueError("Portfolio not found")
        
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "uiResourceUri": "ui://boardroom/investor-risk"
            }
        }
    
    async def handle_mcp_request(self, body: dict) -> dict:
        """
        Main MCP request handler - consolidates all MCP functionality
        """
        method = body.get("method")
        params = body.get("params", {})
        id_ = body.get("id")
        
        if not method:
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "error": {"code": -32600, "message": "Invalid request - method required"}
            }
        
        try:
            # Check if we have a handler for this method
            handler = self.method_handlers.get(method)
            if handler:
                return await handler(params, id_)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "error": {"code": -32000, "message": str(e)}
            }
    
    async def handle_websocket_message(self, websocket, message: str):
        """Handle WebSocket MCP message"""
        try:
            # Parse the message as MCP request
            body = json.loads(message)
            req = MCPRequest(**body)
            
            # Process the request
            if req.method in self.method_handlers:
                result = await self.method_handlers[req.method](req.params, req.id)
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "error": {"code": -32601, "message": "Method not found"}
                }
            
            # Send response
            await websocket.send(json.dumps(result))
            
        except json.JSONDecodeError:
            error_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
            await websocket.send(json.dumps(error_resp))
            
        except Exception as e:
            error_resp = {
                "jsonrpc": "2.0",
                "id": getattr(req, 'id', None) if 'req' in locals() else None,
                "error": {"code": -32000, "message": str(e)}
            }
            await websocket.send(json.dumps(error_resp))
    
    async def start_websocket_server(self, host: str = "0.0.0.0", port: int = None):
        """Start WebSocket MCP server"""
        port = port or int(os.getenv("MCP_PORT", "8765"))
        
        async def websocket_handler(websocket):
            async for message in websocket:
                await self.handle_websocket_message(websocket, message)
        
        print(f"Starting MCP WebSocket server on ws://{host}:{port}")
        async with websockets.serve(websocket_handler, host, port):
            await asyncio.Future()  # Run forever
    
    def register_method(self, method_name: str, handler: Callable):
        """Register a custom MCP method handler"""
        self.method_handlers[method_name] = handler
    
    def get_state(self) -> Dict[str, Any]:
        """Get current MCP state"""
        return self.state.copy()
    
    def update_state(self, updates: Dict[str, Any]):
        """Update MCP state"""
        self.state.update(updates)


# Create global MCP handler instance
mcp_handler = UnifiedMCPHandler()

# Export functions for backward compatibility
async def handle_mcp(body: dict) -> dict:
    """Backward compatibility function"""
    return await mcp_handler.handle_mcp_request(body)

def get_mcp_state() -> Dict[str, Any]:
    """Get MCP state"""
    return mcp_handler.get_state()

# For direct execution - start WebSocket server
if __name__ == "__main__":
    asyncio.run(mcp_handler.start_websocket_server())