"""
Azure ML management package
"""
from .endpoints import AML_ENDPOINTS
from .unified_ml_manager import UnifiedMLManager

# Global instance
ml_manager = UnifiedMLManager()

__all__ = ['AML_ENDPOINTS', 'UnifiedMLManager', 'ml_manager']