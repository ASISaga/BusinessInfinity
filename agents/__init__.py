"""
Agent Management Feature
Consolidates all agent management, AI interactions, and semantic kernel functionality
"""
from .manager import UnifiedAgentManager

# Create singleton instance
agent_manager = UnifiedAgentManager()

__all__ = ['agent_manager', 'UnifiedAgentManager']