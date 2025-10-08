# BoardroomOrchestrator.py
import asyncio

from agent_framework import WorkflowBuilder

# Agents (inheritance chain: ChatAgent → PossibilityAgent → BusinessAgent → RoleAgents)
from CEO import ChiefExecutiveOfficer
from CFO import ChiefFinancialOfficer
from CTO import ChiefTechnologyOfficer
from COO import ChiefOperatingOfficer
from CMO import ChiefMarketingOfficer
from CHRO import ChiefHumanResourcesOfficer
from CSO import ChiefStrategyOfficer
Founder import FounderAgent
from InvestorAgent import InvestorAgent

# MCP Executors
from executors.ERPExecutor import ERPExecutor
from executors.CRMExecutor import CRMExecutor
from executors.LinkedInExecutor import LinkedInExecutor

# Decision pipeline
from .DecisionIntegrator import DecisionIntegrator

# Semantic Kernel adapter (chat reasoning layer)
from SKLLM import SKChatClientAdapter
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion


class BoardroomOrchestrator:
    """
    Orchestrates the full boardroom workflow and produces structured DecisionArtifacts.
    """

    def __init__(self, api_key: str, mcp_clients: dict, governance_path: str = "boardroom.governance.yaml"):
        # --- Build Semantic Kernel chat client ---
        kernel = Kernel()
        kernel.add_service(OpenAIChatCompletion("gpt-4o-mini", api_key=api_key))
        sk_client = SKChatClientAdapter(kernel, instructions="Boardroom reasoning agent")

        # --- MCP Executors ---
        self.erp_exec = ERPExecutor(mcp_clients["erp"])
        self.crm_exec = CRMExecutor(mcp_clients["crm"])
        self.li_exec = LinkedInExecutor(mcp_clients["linkedin"])
        tool_executors = {"erp": self.erp_exec, "crm": self.crm_exec, "linkedin": self.li_exec}

        # --- Agents (all role agents inherit BusinessAgent → PossibilityAgent → ChatAgent) ---
        self.founder = FounderAgent(chat_client=sk_client, tool_executors=tool_executors)
        self.investor = InvestorAgent(chat_client=sk_client, tool_executors=tool_executors)
        self.ceo = ChiefExecutiveOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.cfo = ChiefFinancialOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.cto = ChiefTechnologyOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.coo = ChiefOperatingOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.cmo = ChiefMarketingOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.chro = ChiefHumanResourcesOfficer(chat_client=sk_client, tool_executors=tool_executors)
        self.cso = ChiefStrategyOfficer(chat_client=sk_client, tool_executors=tool_executors)

        # --- Decision Integrator (YAML-driven governance + ledger) ---
        self.decision_integrator = DecisionIntegrator(config_path=governance_path)

        # --- Workflow graph ---
        builder = WorkflowBuilder()

        f_node = builder.add_executor(self.founder)
        i_node = builder.add_executor(self.investor)
        ceo_node = builder.add_executor(self.ceo)
        cfo_node = builder.add_executor(self.cfo)
        cto_node = builder.add_executor(self.cto)
        coo_node = builder.add_executor(self.coo)
        cmo_node = builder.add_executor(self.cmo)
        chro_node = builder.add_executor(self.chro)
        cso_node = builder.add_executor(self.cso)
        di_node = builder.add_executor(self.decision_integrator)

        # Flow: Founder → Investor → CEO → CFO/CTO/COO → DecisionIntegrator → CEO
        builder.add_edge(f_node, i_node)
        builder.add_edge(i_node, ceo_node)
        builder.add_edge(ceo_node, [cfo_node, cto_node, coo_node, cmo_node, chro_node, cso_node])

        # Integrator collects from CFO, CTO, COO, CMO, CHRO, CSO, and Investor (could also collect ERP/CRM/LI evidence routed as messages)
        builder.add_edge([cfo_node, cto_node, coo_node, cmo_node, chro_node, cso_node, i_node], di_node)

        # CEO receives the final decision artifact for announcement or follow-up planning
        builder.add_edge(di_node, ceo_node)

        self.workflow = builder.set_start_executor(f_node).build()

    async def run_boardroom(self, topic: str):
        print(f"\n=== Boardroom Session: {topic} ===\n")
        result = await self.workflow.run(topic)
        print("\n=== Final Decision Artifact ===")
        print(result)
        return result


