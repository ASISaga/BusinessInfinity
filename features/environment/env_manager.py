"""
Environment Management
Consolidated from core.api.EnvManager - use features.environment instead
"""
import warnings
from .manager import UnifiedEnvManager as EnvManager

warnings.warn(
    "environment.env_manager is deprecated. Use features.environment.env_manager instead.",
    DeprecationWarning,
    stacklevel=2
)
