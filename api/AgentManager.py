import os
import json
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import HttpChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from chromadb import Client as ChromaClient

class AgentManager:
    async def ask_agent(self, domain, question):
        agent_func = self.get_agent(domain)
        if not agent_func:
            return None
        answer = await agent_func(question, {})
        return json.dumps({"answer": answer})
    def get_agent(self, domain):
        """Return the agent function for a given domain, or None if not found."""
        return self.AGENTS.get(domain)
    def get_agent_profile(self, agent_id):
        """Return a single agent profile as a JSON string by agent_id, or None if not found."""
        if hasattr(self, 'agent_profiles') and self.agent_profiles:
            profiles = self.agent_profiles
        else:
            profiles = {}
        prof = profiles.get(agent_id)
        if prof is not None:
            return json.dumps(prof)
        return None
    def get_agent_profiles(self):
        """Return a JSON string of agent profiles for API responses."""
        if hasattr(self, 'agent_profiles') and self.agent_profiles:
            profiles = self.agent_profiles
        else:
            profiles = {}
        agents = []
        for aid, prof in profiles.items():
            agents.append({
                "agentId": aid,
                "name": prof.get("name"),
                "profile": prof.get("profile"),
                "photo": prof.get("photo"),
                "domains": prof.get("domains")
            })
        return json.dumps(agents)
    def __init__(self, agent_dirs=None, domain_know=None, ml_url=None, ml_key=None):
        self.ml_url = ml_url or os.getenv("MLENDPOINT_URL")
        self.ml_key = ml_key or os.getenv("MLENDPOINT_KEY")
        from .EnvManager import EnvManager
        env = EnvManager()
        self.agent_profile_blob = env.get_required("AGENTPROFILESBLOB")
        self.agent_directives_blob = env.get_required("AGENTDIRECTIVESBLOB")
        self.AGENTS = {}
        if agent_dirs and domain_know:
            self.init_agents(agent_dirs, domain_know)

    def create_agent(self, domain: str, agent_dirs, domain_know):
        dirs = agent_dirs[domain]
        sys_block = "\n".join([f"Purpose: {dirs['purpose']}", *dirs["context"]])
        cfg = domain_know[domain]["chromaconfig"]
        chroma = ChromaClient(cfg["client_kwargs"])
        collection = chroma.get_collection(cfg["collection"])

        @self.kernel.createsemanticfunction(
          name=f"{domain}_skill",
          description=f"{domain} domain agent",
          prompt_template=PromptTemplateConfig(
            prompt=(
              "{system}\n\n"
              "Context Snippets:\n"
              "{snippets}\n\n"
              "Task: {user_input}\n"
              "Response:"
            )
          )
        )
        async def agent_func(userinput: str, context: dict) -> str:
            docs = collection.query(query_texts=[userinput], n_results=5)
            snippets = "\n".join(f"- {s}" for s in docs["documents"][0])
            inputs = {"system": sys_block,
                      "snippets": snippets,
                      "user_input": userinput}
            result = await self.kernel.run_async("llm.chat", input=inputs)
            return result

        return agent_func

    def init_agents(self, agent_dirs, domain_know):
        self.AGENTS = {d: self.create_agent(d, agent_dirs, domain_know) for d in agent_dirs.keys()}
