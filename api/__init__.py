"""
API and Orchestration Feature
Consolidated into core system - this module is deprecated.
Use core.api_orchestrator instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.features.api import UnifiedAPIOrchestrator
    
    # Create alias for backward compatibility
    Orchestrator = UnifiedAPIOrchestrator
    
    __all__ = ['Orchestrator']
except ImportError:
    # If core system not available, provide empty placeholder
    class Orchestrator:
        pass
    
    __all__ = ['Orchestrator']