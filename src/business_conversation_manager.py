"""
BusinessConversationManager - Handles conversation system integration for Business Infinity
"""
from typing import Dict, Any, List, Optional
import logging

class BusinessConversationManager:
    def __init__(self, autonomous_boardroom, logger=None):
        self.autonomous_boardroom = autonomous_boardroom
        self.logger = logger or logging.getLogger(__name__)

    async def create_boardroom_conversation(self, conversation_type: str, champion_role: str, title: str, content: str, context: Dict[str, Any] = None) -> Optional[str]:
        if not self.autonomous_boardroom:
            self.logger.error("Autonomous boardroom not available")
            return None
        return await self.autonomous_boardroom.create_boardroom_conversation(conversation_type, champion_role, title, content, context)

    async def initiate_a2a_communication(self, from_agent: str, to_agent: str, conversation_type: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        if not self.autonomous_boardroom:
            self.logger.error("Autonomous boardroom not available")
            return None
        return await self.autonomous_boardroom.initiate_a2a_communication(from_agent, to_agent, conversation_type, message, context)

    async def get_agent_conversations(self, agent_role: str) -> Dict[str, Any]:
        if not self.autonomous_boardroom:
            return {"error": "Autonomous boardroom not available"}
        return await self.autonomous_boardroom.get_agent_conversations(agent_role)

    async def sign_conversation(self, conversation_id: str, signer_role: str, signer_name: str) -> bool:
        if not self.autonomous_boardroom:
            self.logger.error("Autonomous boardroom not available")
            return False
        return await self.autonomous_boardroom.sign_conversation(conversation_id, signer_role, signer_name)

    async def list_conversation_types(self) -> List[str]:
        try:
            from conversations.conversation_system import ConversationType
            return [conv_type.value for conv_type in ConversationType]
        except ImportError:
            return []

    async def list_conversation_roles(self) -> List[str]:
        try:
            from conversations.conversation_system import ConversationRole
            return [role.value for role in ConversationRole]
        except ImportError:
            return []

    async def get_conversation_templates(self) -> Dict[str, Any]:
        try:
            from conversations.conversation_system import ConversationTemplateManager
            template_manager = ConversationTemplateManager()
            templates = {}
            for conv_type in template_manager.templates:
                templates[conv_type.value] = template_manager.get_template(conv_type)
            return templates
        except ImportError:
            return {}
