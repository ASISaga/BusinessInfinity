"""
Example usage for PossibilityAgent
"""

from PossibilityAgent import PossibilityAgent
from executors.ERPExecutor import ERPExecutor
from executors.LinkedInExecutor import LinkedInExecutor
from executors.CRMExecutor import CRMExecutor

# Executors
erp_exec = ERPExecutor()
li_exec = LinkedInExecutor()
crm_exec = CRMExecutor()

tools = {"erp": erp_exec, "linkedin": li_exec, "crm": crm_exec}

# Instantiate the agent
agent = PossibilityAgent(tool_executors=tools)

# Example async usage (in an async context):
# result = await agent.declare_possibility("Invent a new market for AI-driven sustainability")
# print(result)
