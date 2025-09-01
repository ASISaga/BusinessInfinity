"""
ML Pipeline Feature
Consolidates all machine learning, training, and inference functionality
"""
from .manager import UnifiedMLManager

# Create singleton instance
ml_manager = UnifiedMLManager()

__all__ = ['ml_manager', 'UnifiedMLManager']