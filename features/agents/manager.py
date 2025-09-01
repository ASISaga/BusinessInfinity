"""
Unified Agent Management System
Consolidates functionality from api/AgentManager.py and app/agents.py
"""
import os
import json
from typing import Dict, Any, List, Optional

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

from .aml_chat_service import AmlChatService


class UnifiedAgentManager:
    """
    Unified agent management system that consolidates:
    - Semantic Kernel agent functionality
    - Azure ML endpoint integration  
    - Agent profile management
    - ChromaDB knowledge integration
    """
    
    # Default agent configurations
    DEFAULT_AGENT_CFG = {
        "cmo": {
            "scoring_uri": os.getenv("AML_CMO_SCORING_URI", ""),
            "key": os.getenv("AML_CMO_KEY", ""),
            "instructions": "You are the CMO. Produce actionable marketing plans."
        },
        "cfo": {
            "scoring_uri": os.getenv("AML_CFO_SCORING_URI", ""),
            "key": os.getenv("AML_CFO_KEY", ""),
            "instructions": "You are the CFO. Analyze ROI and budgets."
        },
        "cto": {
            "scoring_uri": os.getenv("AML_CTO_SCORING_URI", ""),
            "key": os.getenv("AML_CTO_KEY", ""),
            "instructions": "You are the CTO. Evaluate technical risk and architecture."
        }
    }

    def __init__(self, agent_dirs=None, domain_know=None, ml_url=None, ml_key=None):
        self.ml_url = ml_url or os.getenv("MLENDPOINT_URL")
        self.ml_key = ml_key or os.getenv("MLENDPOINT_KEY")
        
        # Initialize environment manager if available
        try:
            from core.api.EnvManager import EnvManager
            env = EnvManager()
            self.agent_profile_blob = env.get_required("AGENTPROFILESBLOB")
            self.agent_directives_blob = env.get_required("AGENTDIRECTIVESBLOB")
        except (ImportError, Exception):
            self.agent_profile_blob = None
            self.agent_directives_blob = None
        
        # Agent storage
        self.agents = {}
        self.agent_profiles = {}
        
        # Initialize agents if provided
        if agent_dirs and domain_know:
            self.init_semantic_agents(agent_dirs, domain_know)
        
        # Always initialize AML agents
        self.init_aml_agents()

    def get_default_agent_cfg(self):
        """Get default agent configuration (backwards compatibility)"""
        return self.__class__.DEFAULT_AGENT_CFG

    def init_aml_agents(self):
        """Initialize Azure ML-based agents"""
        for agent_id, config in self.__class__.DEFAULT_AGENT_CFG.items():
            if config["scoring_uri"]:
                self.agents[agent_id] = self._create_aml_agent(agent_id, config)

    def init_semantic_agents(self, agent_dirs, domain_know):
        """Initialize Semantic Kernel-based agents with ChromaDB"""
        for domain in agent_dirs.keys():
            self.agents[domain] = self._create_semantic_agent(domain, agent_dirs, domain_know)

    def _create_aml_agent(self, agent_id: str, config: Dict[str, str]):
        """Create an AML-based agent function"""
        async def aml_agent_func(user_input: str, context: dict = None) -> str:
            if not SEMANTIC_KERNEL_AVAILABLE:
                return f"Error: semantic_kernel not available for agent {agent_id}"
                
            k = Kernel()
            k.add_service(AmlChatService(config["scoring_uri"], config["key"]))
            hist = ChatHistory()
            hist.add_system_message(config["instructions"])
            hist.add_user_message(user_input)
            result = await k.get_required_service(AmlChatService).get_chat_message_contents(hist)
            return result[0].content if result else ""
        
        return aml_agent_func

    def _create_semantic_agent(self, domain: str, agent_dirs, domain_know):
        """Create a Semantic Kernel agent with ChromaDB integration"""
        if not CHROMADB_AVAILABLE:
            async def error_agent_func(user_input: str, context: dict = None) -> str:
                return f"Error: ChromaDB not available for semantic agent {domain}"
            return error_agent_func
            
        dirs = agent_dirs[domain]
        sys_block = "\n".join([f"Purpose: {dirs['purpose']}", *dirs["context"]])
        cfg = domain_know[domain]["chromaconfig"]
        chroma = ChromaClient(cfg["client_kwargs"])
        collection = chroma.get_collection(cfg["collection"])

        async def semantic_agent_func(user_input: str, context: dict = None) -> str:
            docs = collection.query(query_texts=[user_input], n_results=5)
            snippets = "\n".join(f"- {s}" for s in docs["documents"][0])
            
            # Use a simple prompt-based approach since semantic function creation varies
            if SEMANTIC_KERNEL_AVAILABLE:
                kernel = Kernel()
            prompt = f"""{sys_block}

Context Snippets:
{snippets}

Task: {user_input}
Response:"""
            
            # For now, return formatted response - can be enhanced with actual LLM call
            return f"Agent {domain} processing: {user_input}\nContext: {snippets[:200]}..."

        return semantic_agent_func

    async def ask_agent(self, domain: str, question: str) -> Optional[str]:
        """Ask an agent a question and return JSON response"""
        agent_func = self.get_agent(domain)
        if not agent_func:
            return None
        
        try:
            answer = await agent_func(question, {})
            return json.dumps({"answer": answer})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_agent(self, domain: str):
        """Return the agent function for a given domain, or None if not found"""
        return self.agents.get(domain)

    def get_agent_profile(self, agent_id: str) -> Optional[str]:
        """Return a single agent profile as a JSON string by agent_id, or None if not found"""
        if hasattr(self, 'agent_profiles') and self.agent_profiles:
            profiles = self.agent_profiles
        else:
            # Fallback to default profiles
            profiles = {aid: {"name": aid.upper(), "profile": cfg["instructions"], "domains": [aid]} 
                       for aid, cfg in self.__class__.DEFAULT_AGENT_CFG.items()}
        
        prof = profiles.get(agent_id)
        if prof is not None:
            return json.dumps(prof)
        return None

    def get_agent_profiles(self) -> str:
        """Return a JSON string of agent profiles for API responses"""
        if hasattr(self, 'agent_profiles') and self.agent_profiles:
            profiles = self.agent_profiles
        else:
            # Fallback to default profiles 
            profiles = {aid: {"name": aid.upper(), "profile": cfg["instructions"], "domains": [aid]}
                       for aid, cfg in self.__class__.DEFAULT_AGENT_CFG.items()}
        
        agents = []
        for aid, prof in profiles.items():
            agents.append({
                "agentId": aid,
                "name": prof.get("name"),
                "profile": prof.get("profile"),
                "photo": prof.get("photo"),
                "domains": prof.get("domains", [aid])
            })
        return json.dumps(agents)

    def list_agent_ids(self) -> List[str]:
        """Return list of available agent IDs"""
        return list(self.agents.keys())

    async def run_agent(self, agent_id: str, user_input: str) -> str:
        """Run a specific agent with input (alternative interface)"""
        agent_func = self.get_agent(agent_id)
        if not agent_func:
            return f"Agent {agent_id} not found"
        
        try:
            return await agent_func(user_input, {})
        except Exception as e:
            return f"Error running agent {agent_id}: {str(e)}"