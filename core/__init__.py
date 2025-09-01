# Core functionality package

# Import all managers and classes for backward compatibility
from .agents import AmlChatService, UnifiedAgentManager, agent_manager
from .environment import UnifiedEnvManager, EnvManager, env_manager  
from .ml import AML_ENDPOINTS, UnifiedMLManager, ml_manager
from .storage import UnifiedStorageManager, storage_manager

__all__ = [
    # Agents
    'AmlChatService', 'UnifiedAgentManager', 'agent_manager',
    # Environment  
    'UnifiedEnvManager', 'EnvManager', 'env_manager',
    # ML
    'AML_ENDPOINTS', 'UnifiedMLManager', 'ml_manager',
    # Storage
    'UnifiedStorageManager', 'storage_manager'
]