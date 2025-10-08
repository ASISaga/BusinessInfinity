"""
Unified Feature Modules
Consolidates functionality from:
- /storage/manager.py (Storage management)
- /ml_pipeline/manager.py (ML operations)  
- /environment/manager.py (Environment variables)
- /api/orchestrator.py (API orchestration)
"""

from .storage import UnifiedStorageManager
from .ml_pipeline import UnifiedMLManager  
from AgentOperatingSystem.environment import EnvironmentManager, env_manager
from .api import UnifiedAPIOrchestrator

# Create global instances
storage_manager = UnifiedStorageManager()
ml_manager = UnifiedMLManager()
env_manager = env_manager
api_orchestrator = UnifiedAPIOrchestrator()

# Export all managers
__all__ = [
    'storage_manager', 
    'ml_manager',
    'env_manager', 
    'api_orchestrator',
    'UnifiedStorageManager',
    'UnifiedMLManager', 
    'EnvironmentManager',
    'UnifiedAPIOrchestrator'
]