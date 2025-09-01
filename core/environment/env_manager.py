"""
Backwards compatibility wrapper for EnvManager
"""
from .unified_env_manager import UnifiedEnvManager


class EnvManager(UnifiedEnvManager):
    """Backwards compatibility wrapper"""
    pass