"""
DEPRECATED: This module has been consolidated into core/ml.py
Use: from core.ml import ml_manager instead
"""
import warnings
from core.ml import UnifiedMLManager as MLClientManager

warnings.warn(
    "api.MLClientManager is deprecated. Use core.ml.ml_manager instead.",
    DeprecationWarning,
    stacklevel=2
)
