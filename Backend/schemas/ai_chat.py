from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ChatRole = Literal["user", "assistant", "system"]


class ChatMessage(BaseModel):
    role: ChatRole
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    """Request body for POST /api/ai/chat — the whole conversation so far."""

    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


class ChatHistoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    create_at: datetime = Field(serialization_alias="createTime")


class ChatHistoryData(BaseModel):
    list: list[ChatHistoryItemOut]
    total: int
