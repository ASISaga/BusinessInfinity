"""
Agent Management Feature
Consolidated into core system - this module provides backward compatibility.
Use core.agent_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.agents import agent_manager as core_agent_manager, UnifiedAgentManager
    
    # Create aliases for backward compatibility - ensure we use the core agent_manager
    agent_manager = core_agent_manager
    manager = core_agent_manager
    AgentManager = UnifiedAgentManager
    
    __all__ = ['manager', 'agent_manager', 'AgentManager', 'UnifiedAgentManager']
except ImportError:
    # If core system not available, provide fallback
    class AgentManager:
        def __init__(self):
            pass
        def get_agent_profiles(self):
            return "[]"
    
    class UnifiedAgentManager:
        def __init__(self):
            pass
        def get_agent_profiles(self):
            return "[]"
    
    manager = AgentManager()
    agent_manager = manager
    
    __all__ = ['manager', 'agent_manager', 'AgentManager', 'UnifiedAgentManager']