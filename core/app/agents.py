"""
DEPRECATED: This module has been consolidated into core/agents.py
Use: from core.agents import agent_manager instead
"""
import warnings
from core.agents import agent_manager

warnings.warn(
    "app.agents is deprecated. Use core.agents.agent_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backwards compatibility aliases
AGENT_CFG = agent_manager.DEFAULT_AGENT_CFG
build_kernel = agent_manager._create_aml_agent
run_agent = agent_manager.run_agent