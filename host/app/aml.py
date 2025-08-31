import os, httpx
from typing import Dict, Any

# Map agentId → AML endpoint (scoring URI + key)
AML_ENDPOINTS = {
    "cmo": {
        "scoring_uri": os.getenv("AML_CMO_SCORING_URI", ""),
        "key": os.getenv("AML_CMO_KEY", "")
    },
    "cfo": {
        "scoring_uri": os.getenv("AML_CFO_SCORING_URI", ""),
        "key": os.getenv("AML_CFO_KEY", "")
    },
    "cto": {
        "scoring_uri": os.getenv("AML_CTO_SCORING_URI", ""),
        "key": os.getenv("AML_CTO_KEY", "")
    }
}

async def aml_infer(agent_id: str, prompt: str) -> Dict[str, Any]:
    cfg = AML_ENDPOINTS.get(agent_id)
    if not cfg or not cfg["scoring_uri"]:
        return {"error": f"No AML endpoint configured for {agent_id}"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['key']}"
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(cfg["scoring_uri"], headers=headers, json={"input": prompt})
        resp.raise_for_status()
        return resp.json()

async def aml_train(job_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # Stub: integrate AML Jobs REST or azure-ai-ml as needed
    # Return a fake job id for now
    return {"jobId": f"job-{job_name}", "status": "queued"}