"""
DEPRECATED: This module has been consolidated into core/environment.py
Use: from core.environment import env_manager instead
"""
import warnings
from core.environment import UnifiedEnvManager as EnvManager

warnings.warn(
    "api.EnvManager is deprecated. Use core.environment.env_manager instead.",
    DeprecationWarning,
    stacklevel=2
)
