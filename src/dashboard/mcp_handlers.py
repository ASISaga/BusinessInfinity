# mcp_handlers.py (append/extend)
import json, os
from datetime import datetime
from .state import founder_state, investor_state, finance_state, tech_state, ops_state
from .prompts import APPROVAL_PROMPT
import logging

from runtime import RuntimeConfig
from AgentOperatingSystem import AgentFrameworkSystem

# Import MCP Access Control
try:
    from ..core.utils import validate_mcp_request, MCPAccessDeniedError
    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    ACCESS_CONTROL_AVAILABLE = False
    logging.warning("MCP Access Control not available in dashboard handlers")

# Initialize AOS Agent Framework system for prompt processing
agent_framework_system = None
try:
    agent_framework_system = AgentFrameworkSystem()
except Exception as e:
    # Agent Framework system not available, will handle in the function
    pass

async def run_prompt(prompt: str, input_text: str) -> str:
    """Run a prompt using AOS Agent Framework system"""
    if agent_framework_system:
        try:
            # Initialize the system if not already done
            if not agent_framework_system.is_initialized:
                await agent_framework_system.initialize()
            
            # Create a temporary agent for prompt processing
            temp_agent = await agent_framework_system.create_agent(
                "PromptProcessor",
                prompt,
                ["prompt_processing"]
            )
            
            # Use the agent framework system to process the prompt
            result = await agent_framework_system.run_multi_agent_conversation(
                input_text, ["PromptProcessor"]
            )
            
            # Clean up the temporary agent
            await agent_framework_system.remove_agent("PromptProcessor")
            
            if result.get("success", False):
                return result.get("result", str(result))
            else:
                return f"Error processing prompt: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"Agent Framework processing failed: {str(e)}"
    else:
        # Fallback to simple text processing if Agent Framework not available
        return f"Processed (fallback): {prompt}\nInput: {input_text}"

async def handle_mcp(body: dict, user_context: dict = None):
    """
    Handle MCP requests with integrated access control
    
    Args:
        body: MCP request body
        user_context: User context containing user_id and role for access control
    """
    method = body.get("method")
    params = body.get("params", {})
    id_ = body.get("id")

    # Extract user information for access control
    user_id = (user_context or {}).get("user_id", "unknown")
    user_role = (user_context or {}).get("role", "Employee")

    try:
        # Map MCP methods to servers and operations for access control
        mcp_method_mapping = {
            "founder.approvePlan": ("businessinfinity_config", "update"),
            "cfo.approveBudget": ("erpnext", "update"),
            "cfo.getLiquidity": ("erpnext", "read"),
            "cto.getIncidentSummary": ("businessinfinity_config", "read"),
            "coo.acknowledgeAlert": ("businessinfinity_config", "update"),
            "investor.getRiskBreakdown": ("erpnext", "read")
        }
        
        # Check access control if available
        if ACCESS_CONTROL_AVAILABLE and method in mcp_method_mapping:
            mcp_server, operation = mcp_method_mapping[method]
            try:
                validate_mcp_request(user_id, user_role, mcp_server, operation)
            except MCPAccessDeniedError as e:
                return {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": {
                        "code": -32001,
                        "message": "Access Denied",
                        "data": {
                            "reason": str(e),
                            "user_role": user_role,
                            "required_permission": f"{mcp_server}.{operation}"
                        }
                    }
                }

        # CEO/Founder
        if method == "founder.approvePlan":
            plan = founder_state["plans"].get(params["planId"])
            if not plan: raise ValueError("Plan not found")
            eval_json = await run_prompt(APPROVAL_PROMPT, plan["title"])
            decision = json.loads(eval_json).get("decision", "approve")
            if decision == "approve":
                plan["status"] = "approved"
                return {"jsonrpc":"2.0","id":id_,"result":{"status":"approved","timestamp":datetime.utcnow().isoformat()}}
            return {"jsonrpc":"2.0","id":id_,"result":{"status":"error","timestamp":datetime.utcnow().isoformat(),"decision":decision}}

        # CFO
        if method == "cfo.approveBudget":
            b = finance_state["budgets"].get(params["budgetId"])
            if not b: raise ValueError("Budget not found")
            b["status"] = "approved"
            b["amount"] = params["amount"]
            return {"jsonrpc":"2.0","id":id_,"result":{"status":"approved","timestamp":datetime.utcnow().isoformat()}}

        if method == "cfo.getLiquidity":
            days = int(params.get("windowDays", 7))
            cash = finance_state["liquidity"]["cash"]
            burn = finance_state["liquidity"]["monthly_burn"]
            runway_months = max(0, round(cash / max(1, burn), 2))
            return {"jsonrpc":"2.0","id":id_,"result":{"days":days,"cash":cash,"runwayMonths":runway_months}}

        # CTO
        if method == "cto.getIncidentSummary":
            open_count = sum(1 for i in tech_state["incidents"] if i["status"]=="open")
            sev1 = sum(1 for i in tech_state["incidents"] if i["status"]=="open" and i["sev"]==1)
            sev2 = sum(1 for i in tech_state["incidents"] if i["status"]=="open" and i["sev"]==2)
            return {"jsonrpc":"2.0","id":id_,"result":{"open":open_count,"sev1":sev1,"sev2":sev2}}

        # COO
        if method == "coo.acknowledgeAlert":
            alert = next((a for a in ops_state["alerts"] if a["id"]==params["alertId"]), None)
            if not alert: raise ValueError("Alert not found")
            alert["status"] = "acknowledged"
            return {"jsonrpc":"2.0","id":id_,"result":{"acknowledged":True,"timestamp":datetime.utcnow().isoformat()}}

        # Investor (existing)
        if method == "investor.getRiskBreakdown":
            pid = params["portfolioId"]
            if pid not in investor_state["risk"]: raise ValueError("Portfolio not found")
            return {"jsonrpc":"2.0","id":id_,"result":{"uiResourceUri":"ui://boardroom/investor-risk"}}

        return {"jsonrpc":"2.0","id":id_,"error":{"code":-32601,"message":f"Method not found: {method}"}}

    except Exception as e:
        return {"jsonrpc":"2.0","id":id_,"error":{"code":-32000,"message":str(e)}}