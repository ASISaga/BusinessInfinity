"""
Unified Agent Management System
Consolidates functionality from:
- /agents/manager.py (UnifiedAgentManager with AML and Semantic Kernel support)
- /azure_functions/server/Operations/ (Individual agent classes)
- Various agent references throughout the codebase
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

# Optional imports with fallbacks
try:
    from semantic_kernel import Kernel
    from semantic_kernel.contents import ChatHistory
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False

try:
    from chromadb import Client as ChromaClient
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Import AML chat service
try:
    from ..agents.aml_chat_service import AmlChatService
except ImportError:
    try:
        from agents.aml_chat_service import AmlChatService
    except ImportError:
        AmlChatService = None

# Import environment manager
try:
    from ..environment import env_manager as env
except ImportError:
    env = None


class BaseAgent(ABC):
    """Base class for all agents - consolidates PurposeDrivenAgent functionality"""
    
    def __init__(self, agent_id: str, purpose: str, interval: int = 5):
        self.agent_id = agent_id
        self.purpose = purpose
        self.interval = interval
        self.active = False
        
    @abstractmethod
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        """Execute the agent's main task"""
        pass
    
    def get_profile(self) -> Dict[str, Any]:
        """Get agent profile information"""
        return {
            "agentId": self.agent_id,
            "name": self.agent_id.replace("_", " ").title(),
            "purpose": self.purpose,
            "interval": self.interval,
            "active": self.active
        }


class OperationsAgent(BaseAgent):
    """Operations management agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Operations Management: Oversee business operations, process optimization, and operational efficiency.
        Supply Chain: Monitor supply chain processes and vendor relationships.
        Quality Assurance: Ensure quality standards and continuous improvement.
        """
        super().__init__("operations", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        # Implement operations-specific logic
        return f"Operations Agent processing: {input_data}"


class FinanceAgent(BaseAgent):
    """Finance and accounting agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Financial Analysis: Analyze financial data, ROI, and budgets.
        Risk Management: Assess financial risks and recommend mitigation strategies.
        Reporting: Generate financial reports and insights.
        """
        super().__init__("finance", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Finance Agent processing: {input_data}"


class MarketingAgent(BaseAgent):
    """Marketing and customer engagement agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Marketing Strategy: Develop and execute marketing campaigns.
        Customer Analytics: Analyze customer behavior and market trends.
        Brand Management: Maintain brand consistency and reputation.
        """
        super().__init__("marketing", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Marketing Agent processing: {input_data}"


class HRAgent(BaseAgent):
    """Human Resources agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Talent Management: Recruit, develop, and retain talent.
        Employee Relations: Handle employee concerns and engagement.
        Policy Management: Maintain HR policies and compliance.
        """
        super().__init__("hr", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"HR Agent processing: {input_data}"


class AccountsAgent(BaseAgent):
    """Accounts and financial operations agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Accounts Management: Handle accounts payable/receivable.
        Financial Operations: Process transactions and financial data.
        Compliance: Ensure financial compliance and audit readiness.
        """
        super().__init__("accounts", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Accounts Agent processing: {input_data}"


class QualityAgent(BaseAgent):
    """Quality assurance agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Quality Control: Monitor and ensure quality standards.
        Process Improvement: Identify and implement improvements.
        Testing: Oversee testing processes and validation.
        """
        super().__init__("quality", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Quality Agent processing: {input_data}"


class PurchaseAgent(BaseAgent):
    """Purchasing and procurement agent"""
    
    def __init__(self, interval: int = 5):
        purpose = """
        Procurement: Handle purchasing decisions and vendor management.
        Cost Optimization: Optimize purchasing costs and contracts.
        Supplier Relations: Manage supplier relationships and negotiations.
        """
        super().__init__("purchase", purpose, interval)
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        return f"Purchase Agent processing: {input_data}"


class AMLAgent(BaseAgent):
    """Azure ML-powered agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, str]):
        super().__init__(agent_id, config.get("instructions", ""), 0)
        self.scoring_uri = config.get("scoring_uri", "")
        self.key = config.get("key", "")
        self.instructions = config.get("instructions", "")
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        if not AmlChatService or not self.scoring_uri:
            return f"Error: AML service not available for agent {self.agent_id}"
            
        if not SEMANTIC_KERNEL_AVAILABLE:
            return f"Error: semantic_kernel not available for agent {self.agent_id}"
            
        try:
            k = Kernel()
            k.add_service(AmlChatService(self.scoring_uri, self.key))
            hist = ChatHistory()
            hist.add_system_message(self.instructions)
            hist.add_user_message(input_data)
            result = await k.get_required_service(AmlChatService).get_chat_message_contents(hist)
            return result[0].content if result else ""
        except Exception as e:
            return f"Error in AML agent {self.agent_id}: {str(e)}"


class SemanticAgent(BaseAgent):
    """Semantic Kernel agent with ChromaDB integration"""
    
    def __init__(self, agent_id: str, agent_dirs: dict, domain_know: dict):
        dirs = agent_dirs[agent_id]
        purpose = f"Purpose: {dirs['purpose']}\n" + "\n".join(dirs["context"])
        super().__init__(agent_id, purpose, 0)
        
        self.sys_block = purpose
        if CHROMADB_AVAILABLE:
            cfg = domain_know[agent_id]["chromaconfig"]
            self.chroma = ChromaClient(cfg["client_kwargs"])
            self.collection = self.chroma.get_collection(cfg["collection"])
        else:
            self.chroma = None
            self.collection = None
    
    async def execute_task(self, input_data: str, context: dict = None) -> str:
        if not self.collection:
            return f"Error: ChromaDB not available for semantic agent {self.agent_id}"
            
        try:
            docs = self.collection.query(query_texts=[input_data], n_results=5)
            snippets = "\n".join(f"- {s}" for s in docs["documents"][0])
            
            # Enhanced prompt with context
            prompt = f"""{self.sys_block}

Context Snippets:
{snippets}

Task: {input_data}
Response:"""
            
            # For now, return formatted response - can be enhanced with actual LLM call
            return f"Agent {self.agent_id} processing: {input_data}\\nContext: {snippets[:200]}..."
        except Exception as e:
            return f"Error in semantic agent {self.agent_id}: {str(e)}"


class UnifiedAgentManager:
    """
    Unified agent management system that consolidates all agent functionality
    """
    
    # Default AML agent configurations
    DEFAULT_AML_AGENTS = {
        "cmo": {
            "scoring_uri": os.getenv("AML_CMO_SCORING_URI", ""),
            "key": os.getenv("AML_CMO_KEY", ""),
            "instructions": "You are the CMO. Produce actionable marketing plans and analyze market trends."
        },
        "cfo": {
            "scoring_uri": os.getenv("AML_CFO_SCORING_URI", ""),
            "key": os.getenv("AML_CFO_KEY", ""),
            "instructions": "You are the CFO. Analyze ROI, budgets, and financial performance."
        },
        "cto": {
            "scoring_uri": os.getenv("AML_CTO_SCORING_URI", ""),
            "key": os.getenv("AML_CTO_KEY", ""),
            "instructions": "You are the CTO. Evaluate technical risks, architecture, and technology decisions."
        }
    }

    def __init__(self, agent_dirs=None, domain_know=None, ml_url=None, ml_key=None):
        self.ml_url = ml_url or os.getenv("MLENDPOINT_URL")
        self.ml_key = ml_key or os.getenv("MLENDPOINT_KEY")
        
        # Initialize environment manager if available
        if env:
            try:
                self.agent_profile_blob = env.get_required("AGENTPROFILESBLOB")
                self.agent_directives_blob = env.get_required("AGENTDIRECTIVESBLOB")
            except Exception:
                self.agent_profile_blob = None
                self.agent_directives_blob = None
        else:
            self.agent_profile_blob = None
            self.agent_directives_blob = None
        
        # Agent storage
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_profiles = {}
        
        # Initialize all agent types
        self._init_operational_agents()
        self._init_aml_agents()
        
        if agent_dirs and domain_know:
            self._init_semantic_agents(agent_dirs, domain_know)

    def _init_operational_agents(self):
        """Initialize operational agents (from azure_functions/server/Operations)"""
        operational_agents = [
            OperationsAgent(),
            FinanceAgent(),
            MarketingAgent(),
            HRAgent(),
            AccountsAgent(),
            QualityAgent(),
            PurchaseAgent()
        ]
        
        for agent in operational_agents:
            self.agents[agent.agent_id] = agent

    def _init_aml_agents(self):
        """Initialize Azure ML-based agents"""
        for agent_id, config in self.DEFAULT_AML_AGENTS.items():
            if config["scoring_uri"]:
                self.agents[agent_id] = AMLAgent(agent_id, config)

    def _init_semantic_agents(self, agent_dirs, domain_know):
        """Initialize Semantic Kernel-based agents with ChromaDB"""
        for domain in agent_dirs.keys():
            self.agents[domain] = SemanticAgent(domain, agent_dirs, domain_know)

    async def execute_agent(self, agent_id: str, input_data: str, context: dict = None) -> Optional[str]:
        """Execute an agent task and return result"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        try:
            return await agent.execute_task(input_data, context or {})
        except Exception as e:
            return f"Error executing agent {agent_id}: {str(e)}"

    async def ask_agent(self, domain: str, question: str) -> Optional[str]:
        """Ask an agent a question and return JSON response (backward compatibility)"""
        result = await self.execute_agent(domain, question)
        if result is None:
            return None
        
        return json.dumps({"answer": result})

    def get_agent(self, domain: str) -> Optional[BaseAgent]:
        """Return the agent instance for a given domain"""
        return self.agents.get(domain)

    def get_agent_profile(self, agent_id: str) -> Optional[str]:
        """Return a single agent profile as JSON string"""
        agent = self.agents.get(agent_id)
        if agent:
            return json.dumps(agent.get_profile())
        return None

    def get_agent_profiles(self) -> str:
        """Return JSON string of all agent profiles"""
        profiles = []
        for agent_id, agent in self.agents.items():
            profile = agent.get_profile()
            profiles.append(profile)
        
        return json.dumps(profiles)

    def list_agent_ids(self) -> List[str]:
        """Return list of available agent IDs"""
        return list(self.agents.keys())

    async def run_agent(self, agent_id: str, user_input: str) -> str:
        """Run a specific agent with input (alternative interface)"""
        result = await self.execute_agent(agent_id, user_input)
        if result is None:
            return f"Agent {agent_id} not found"
        return result

    def get_agent_count(self) -> int:
        """Get total number of registered agents"""
        return len(self.agents)

    def get_agents_by_type(self, agent_type: str) -> List[str]:
        """Get agents by type (operational, aml, semantic)"""
        if agent_type == "operational":
            return [aid for aid, agent in self.agents.items() if isinstance(agent, BaseAgent) and not isinstance(agent, (AMLAgent, SemanticAgent))]
        elif agent_type == "aml":
            return [aid for aid, agent in self.agents.items() if isinstance(agent, AMLAgent)]
        elif agent_type == "semantic":
            return [aid for aid, agent in self.agents.items() if isinstance(agent, SemanticAgent)]
        else:
            return []

    async def broadcast_to_agents(self, message: str, agent_filter: Optional[List[str]] = None) -> Dict[str, str]:
        """Broadcast a message to multiple agents"""
        results = {}
        target_agents = agent_filter or list(self.agents.keys())
        
        for agent_id in target_agents:
            if agent_id in self.agents:
                result = await self.execute_agent(agent_id, message)
                results[agent_id] = result or f"No response from {agent_id}"
        
        return results


# Create global agent manager instance
agent_manager = UnifiedAgentManager()

# Export for backward compatibility
def get_default_agent_cfg():
    return UnifiedAgentManager.DEFAULT_AML_AGENTS