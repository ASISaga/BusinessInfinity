import json
from datetime import datetime
from state import founder_state, investor_state
from prompts import APPROVAL_PROMPT
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os

kernel = Kernel()
kernel.add_service(
    OpenAIChatCompletion(
        service_id="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model_id="gpt-4o-mini"
    )
)

async def run_prompt(prompt: str, input_text: str) -> str:
    func = kernel.create_semantic_function(prompt)
    result = await func.invoke_async(input_text)
    return str(result)

async def handle_mcp(body: dict):
    method = body.get("method")
    params = body.get("params", {})
    id_ = body.get("id")

    try:
        if method == "founder.approvePlan":
            plan_id = params["planId"]
            approved_by = params["approvedBy"]
            plan = founder_state["plans"].get(plan_id)
            if not plan:
                raise ValueError("Plan not found")

            eval_json = await run_prompt(APPROVAL_PROMPT, plan["title"])
            decision = json.loads(eval_json).get("decision", "approve")
            if decision == "approve":
                plan["status"] = "approved"
                result = {"status": "approved", "timestamp": datetime.utcnow().isoformat()}
            else:
                result = {"status": "error", "timestamp": datetime.utcnow().isoformat(), "decision": decision}
            return {"jsonrpc": "2.0", "id": id_, "result": result}

        elif method == "founder.addComment":
            comment_id = f"c-{datetime.utcnow().timestamp()}"
            founder_state["comments"].append({
                "commentId": comment_id,
                "planId": params["planId"],
                "comment": params["comment"],
                "author": params["author"],
                "timestamp": datetime.utcnow().isoformat()
            })
            return {"jsonrpc": "2.0", "id": id_, "result": {"commentId": comment_id, "timestamp": datetime.utcnow().isoformat()}}

        elif method == "investor.getRiskBreakdown":
            portfolio_id = params["portfolioId"]
            if portfolio_id not in investor_state["risk"]:
                raise ValueError("Portfolio not found")
            return {"jsonrpc": "2.0", "id": id_, "result": {"uiResourceUri": "ui://boardroom/investor-risk"}}

        else:
            return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": "Method not found"}}

    except Exception as e:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32000, "message": str(e)}}