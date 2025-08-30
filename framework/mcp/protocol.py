from pydantic import BaseModel
from typing import Any, Optional

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: Optional[str | int] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Any | None = None
    error: Any | None = None
    id: Optional[str | int] = None