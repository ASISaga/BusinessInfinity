"""
Azure ML Chat Service for Semantic Kernel
"""
import httpx
from typing import List

try:
    from semantic_kernel.contents import ChatHistory, ChatMessageContent, AuthorRole, StreamingChatMessageContent
    from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    # Create dummy base class if semantic_kernel is not available
    ChatCompletionClientBase = object
    SEMANTIC_KERNEL_AVAILABLE = False


class AmlChatService(ChatCompletionClientBase):
    """Azure ML chat completion service for Semantic Kernel"""
    
    def __init__(self, scoring_uri: str, key: str):
        self.scoring_uri = scoring_uri
        self.key = key

    async def get_chat_message_contents(self, messages, **kwargs):
        if not SEMANTIC_KERNEL_AVAILABLE:
            raise ImportError("semantic_kernel is required for AmlChatService")
            
        prompt = "\n".join([f"{m.role.name}: {m.content}" for m in messages.messages])
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.scoring_uri, headers=headers, json={"input": prompt})
            resp.raise_for_status()
            data = resp.json()
        text = data.get("result") or data.get("output") or str(data)
        return [ChatMessageContent(role=AuthorRole.ASSISTANT, content=text)]

    async def get_streaming_chat_message_contents(self, messages, **kwargs):
        if not SEMANTIC_KERNEL_AVAILABLE:
            raise ImportError("semantic_kernel is required for AmlChatService")
            
        # Simple non-streaming fallback
        for item in await self.get_chat_message_contents(messages, **kwargs):
            yield StreamingChatMessageContent(item.role, item.content)