"""
Business Infinity Conversations Module

This module implements the boardroom conversation system as specified in 
conversations/specification.md. It provides structured conversation types,
agent-to-agent (A2A) communication, and delegation/signature flows.
"""

from .conversation_system import (
    ConversationSystem,
    ConversationType,
    ConversationRole,
    Conversation,
    ConversationStatus
)

from .boardroom_conversations import (
    BoardroomConversationManager,
    create_conversation,
    get_conversation,
    list_conversations_by_agent,
    sign_conversation
)

__all__ = [
    "ConversationSystem",
    "ConversationType", 
    "ConversationRole",
    "Conversation",
    "ConversationStatus",
    "BoardroomConversationManager",
    "create_conversation",
    "get_conversation", 
    "list_conversations_by_agent",
    "sign_conversation"
]