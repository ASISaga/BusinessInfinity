"""
Environment and Configuration Management Feature  
Consolidates all environment variable and configuration management
"""
from .manager import UnifiedEnvManager

# Create singleton instance
env_manager = UnifiedEnvManager()

__all__ = ['env_manager', 'UnifiedEnvManager']