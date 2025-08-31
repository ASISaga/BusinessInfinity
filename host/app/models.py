from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal
import time, uuid

MessageType = Literal["chat","toolResult","status","error"]

class Envelope(BaseModel):
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlationId: str
    traceId: str
    boardroomId: str
    conversationId: str
    senderAgentId: str
    role: str
    scope: Literal["local","network"]
    messageType: MessageType
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=lambda: time.time())
    schemaVersion: str = "1.0.0"

class UiAction(BaseModel):
    boardroomId: str
    conversationId: str
    agentId: str
    action: str
    args: Dict[str, Any]
    scope: Literal["local","network"] = "local"
    correlationId: Optional[str] = None

class MessagesQuery(BaseModel):
    boardroomId: str
    conversationId: str
    since: Optional[str] = None  # RowKey (ULID/timestamp) high-watermark