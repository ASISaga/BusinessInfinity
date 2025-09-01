"""
Environment management package
"""
from .unified_env_manager import UnifiedEnvManager
from .env_manager import EnvManager

# Convenience instance and backwards compatibility
env_manager = UnifiedEnvManager()

__all__ = ['UnifiedEnvManager', 'EnvManager', 'env_manager']