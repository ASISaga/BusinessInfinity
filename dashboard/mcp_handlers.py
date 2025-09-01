# mcp_handlers.py (append/extend)
import json, os
from datetime import datetime
from dashboard.state import founder_state, investor_state, finance_state, tech_state, ops_state
from dashboard.prompts import APPROVAL_PROMPT
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

kernel = Kernel()
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        kernel.add_service(OpenAIChatCompletion(service_id="openai", api_key=api_key, ai_model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini")))
except Exception as e:
    # OpenAI service not available, will handle in the function
    pass

async def run_prompt(prompt: str, input_text: str) -> str:
    func = kernel.create_semantic_function(prompt)
    result = await func.invoke_async(input_text)
    return str(result)

async def handle_mcp(body: dict):
    method = body.get("method")
    params = body.get("params", {})
    id_ = body.get("id")

    try:
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