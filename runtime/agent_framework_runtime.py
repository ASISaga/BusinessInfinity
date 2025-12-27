"""
Generic Microsoft Agent Framework Runtime Integration

Provides integration with Microsoft Agent Framework for applications
built on AgentOperatingSystem.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

try:
    # Try importing agent-framework
    from agent_framework import AgentFramework, AgentConfig
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    AgentFramework = None
    AgentConfig = None

from .config_loader import RuntimeConfig


class AgentFrameworkRuntime:
    """
    Generic Agent Framework runtime integration.
    
    Provides integration with Microsoft Agent Framework for:
    - Agent lifecycle management
    - Agent communication and coordination
    - Agent state management
    - Integration with Azure AI services
    """
    
    def __init__(
        self,
        config: RuntimeConfig,
        agent_factory: Optional[Callable[[], Any]] = None
    ):
        """
        Initialize Agent Framework runtime.
        
        Args:
            config: Runtime configuration
            agent_factory: Optional factory function to create agent instances
        """
        if not AGENT_FRAMEWORK_AVAILABLE:
            raise RuntimeError(
                "Microsoft Agent Framework is not installed. "
                "Install with: pip install agent-framework"
            )
        
        self.config = config
        self.agent_factory = agent_factory
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized Agent Framework runtime")
        
        # Agent Framework instance
        self._framework: Optional[Any] = None
        self._agents: Dict[str, Any] = {}
    
    def get_framework(self) -> Any:
        """
        Get or create the Agent Framework instance.
        
        Returns:
            Agent Framework instance
        """
        if self._framework is None:
            if self.config.agent_framework_endpoint:
                # Initialize with endpoint
                self._framework = AgentFramework(
                    endpoint=self.config.agent_framework_endpoint
                )
            else:
                # Initialize with default settings
                self._framework = AgentFramework()
            
            self.logger.info("Created Agent Framework instance")
        
        return self._framework
    
    async def create_agent(
        self,
        agent_id: str,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create a new agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_config: Optional agent configuration
            
        Returns:
            Created agent instance
        """
        framework = self.get_framework()
        
        if self.agent_factory:
            agent = await self.agent_factory()
        else:
            # Create agent using framework
            agent = framework.create_agent(agent_id, config=agent_config)
        
        self._agents[agent_id] = agent
        self.logger.info(f"Created agent: {agent_id}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents."""
        return self._agents.copy()
    
    async def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent.
        
        Args:
            agent_id: ID of the agent to remove
            
        Returns:
            True if agent was found and removed, False otherwise
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            self.logger.info(f"Removed agent: {agent_id}")
            return True
        return False


def create_agent_framework_runtime(
    config: RuntimeConfig,
    agent_factory: Optional[Callable[[], Any]] = None
) -> AgentFrameworkRuntime:
    """
    Factory function to create Agent Framework runtime.
    
    Args:
        config: Runtime configuration
        agent_factory: Optional factory function to create agent instances
        
    Returns:
        Configured AgentFrameworkRuntime instance
    """
    return AgentFrameworkRuntime(config=config, agent_factory=agent_factory)
