"""
Core API package - provides API components and handlers

This package contains various API components. Note that some modules
are deprecated and redirected to the new unified structure.
"""

# Import available API components
try:
    from .orchestrator import Orchestrator
except ImportError:
    pass

try:
    from .AuthHandler import AuthHandler
except ImportError:
    pass

# For deprecated modules, we provide warnings
def __getattr__(name):
    """Provide warnings for deprecated imports"""
    import warnings
    
    if name == "EnvManager":
        warnings.warn(
            "api.EnvManager is deprecated. Use core.environment.env_manager instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from core.environment import UnifiedEnvManager as EnvManager
        return EnvManager
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'Orchestrator',
    'AuthHandler'
]