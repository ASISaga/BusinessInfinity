"""
Unified Feature Modules
Consolidates functionality from:
- /storage/manager.py (Storage management) - Now uses runtime abstractions
- /ml_pipeline/manager.py (ML operations)  
- /environment/manager.py (Environment variables)
- /api/orchestrator.py (API orchestration)

REFACTORED: Now imports from runtime abstractions with fallback to AOS
"""

from .storage import UnifiedStorageManager
# from .ml_pipeline import UnifiedMLManager  # Temporarily disabled - module missing

# Try to import from AOS for environment manager
try:
    from AgentOperatingSystem.environment import EnvironmentManager, env_manager as aos_env_manager
    env_manager = aos_env_manager
except ImportError:
    EnvironmentManager = None
    env_manager = None

# from .api import UnifiedAPIOrchestrator  # Temporarily disabled - module missing

# Create global instances
storage_manager = UnifiedStorageManager()
# ml_manager = UnifiedMLManager()  # Temporarily disabled - module missing
ml_manager = None  # Placeholder 
# api_orchestrator = UnifiedAPIOrchestrator()  # Temporarily disabled - module missing
api_orchestrator = None  # Placeholder

# Export all managers
__all__ = [
    'storage_manager', 
    'ml_manager',
    'env_manager', 
    'api_orchestrator',
    'UnifiedStorageManager',
    # 'UnifiedMLManager',  # Temporarily disabled - module missing
    'EnvironmentManager',
    # 'UnifiedAPIOrchestrator'  # Temporarily disabled - module missing
]