"""
Agent Management Feature
Consolidated into core system - this module provides backward compatibility.
Use core.agent_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.agents import agent_manager, UnifiedAgentManager
    
    # Create aliases for backward compatibility
    manager = agent_manager
    AgentManager = UnifiedAgentManager
    
    __all__ = ['manager', 'agent_manager', 'AgentManager', 'UnifiedAgentManager']
except ImportError:
    # If core system not available, provide fallback
    class AgentManager:
        def __init__(self):
            pass
    
    class UnifiedAgentManager:
        def __init__(self):
            pass
    
    manager = AgentManager()
    agent_manager = manager
    
    __all__ = ['manager', 'agent_manager', 'AgentManager', 'UnifiedAgentManager']