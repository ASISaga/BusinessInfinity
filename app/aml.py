"""
DEPRECATED: This module has been consolidated into core/ml.py
Use: from core.ml import ml_manager instead
"""
import warnings
from core.ml import ml_manager

warnings.warn(
    "app.aml is deprecated. Use core.ml.ml_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backwards compatibility aliases
AML_ENDPOINTS = ml_manager.AML_ENDPOINTS
aml_infer = ml_manager.aml_infer
aml_train = ml_manager.aml_train