"""
Agent management package
"""
from .aml_chat_service import AmlChatService
from .unified_agent_manager import UnifiedAgentManager

# Global instance - can be imported directly
agent_manager = UnifiedAgentManager()

__all__ = ['AmlChatService', 'UnifiedAgentManager', 'agent_manager']