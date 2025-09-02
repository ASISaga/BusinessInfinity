"""
Authentication and Authorization Feature
Consolidates all authentication, authorization, and security functionality
"""
from .auth_handler import validate_jwt, UNAUTHORIZED_MSG

__all__ = ['validate_jwt', 'UNAUTHORIZED_MSG']