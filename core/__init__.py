"""
BusinessInfinity Core Package

This is the core package for the BusinessInfinity application, providing:
- Agent management and orchestration
- Machine learning integrations  
- Storage and environment management
- Application framework components
- API and server functionality

Key modules:
- agents: Agent management and orchestration
- app: Application-level logic and models
- api: API components and handlers (some deprecated)
- framework: Framework-level infrastructure
- ml: Machine learning components
- storage: Data storage management
- environment: Environment and configuration management
"""

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