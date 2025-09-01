"""
DEPRECATED: This module has been consolidated into core/agents.py
Use: from core.agents import agent_manager instead
"""
import warnings
from core.agents import UnifiedAgentManager as AgentManager

warnings.warn(
    "api.AgentManager is deprecated. Use core.agents.agent_manager instead.",
    DeprecationWarning,
    stacklevel=2
)
