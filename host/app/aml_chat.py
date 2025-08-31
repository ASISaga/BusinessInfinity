import httpx, os
from typing import List
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory, StreamingChatMessageContent, ChatMessageContent, AuthorRole

class AmlChatService(ChatCompletionClientBase):
    def __init__(self, scoring_uri: str, key: str):
        self.scoring_uri = scoring_uri
        self.key = key

    async def get_chat_message_contents(self, messages: ChatHistory, **kwargs) -> List[ChatMessageContent]:
        prompt = "\n".join([f"{m.role.name}: {m.content}" for m in messages.messages])
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.scoring_uri, headers=headers, json={"input": prompt})
            resp.raise_for_status()
            data = resp.json()
        text = data.get("result") or data.get("output") or str(data)
        return [ChatMessageContent(role=AuthorRole.ASSISTANT, content=text)]

    async def get_streaming_chat_message_contents(self, messages: ChatHistory, **kwargs):
        # Simple non‑streaming fallback
        for item in await self.get_chat_message_contents(messages, **kwargs):
            yield StreamingChatMessageContent(item.role, item.content)