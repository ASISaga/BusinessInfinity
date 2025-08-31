import os
from typing import Dict
from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory, AuthorRole
from .aml_chat import AmlChatService

AGENT_CFG = {
    "cmo": {"scoring_uri": os.getenv("AML_CMO_SCORING_URI", ""), "key": os.getenv("AML_CMO_KEY", ""), "instructions": "You are the CMO. Produce actionable marketing plans."},
    "cfo": {"scoring_uri": os.getenv("AML_CFO_SCORING_URI", ""), "key": os.getenv("AML_CFO_KEY", ""), "instructions": "You are the CFO. Analyze ROI and budgets."},
    "cto": {"scoring_uri": os.getenv("AML_CTO_SCORING_URI", ""), "key": os.getenv("AML_CTO_KEY", ""), "instructions": "You are the CTO. Evaluate technical risk and architecture."}
}

def build_kernel(agent_id: str) -> Kernel:
    k = Kernel()
    cfg = AGENT_CFG[agent_id]
    k.add_service(AmlChatService(cfg["scoring_uri"], cfg["key"]))
    return k

async def run_agent(agent_id: str, user_input: str) -> str:
    k = build_kernel(agent_id)
    hist = ChatHistory()
    hist.add_system_message(AGENT_CFG[agent_id]["instructions"])
    hist.add_user_message(user_input)
    result = await k.get_required_service(AmlChatService).get_chat_message_contents(hist)
    return result[0].content if result else ""