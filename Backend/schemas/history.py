from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HistoryAddRequest(BaseModel):
    """Request body for POST /api/history/add."""

    model_config = ConfigDict(populate_by_name=True)

    news_id: int = Field(alias="newsId", gt=0, description="News ID")


class HistoryAddData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int = Field(serialization_alias="userId")
    news_id: int = Field(serialization_alias="newsId")
    view_time: datetime = Field(serialization_alias="viewTime")


class HistoryItemOut(BaseModel):
    """A viewed article, flattened for the history page.

    `id` is the news id (used for navigation), `historyId` is the history row
    id — that's what the delete endpoint takes.
    """

    id: int
    history_id: int = Field(serialization_alias="historyId")
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: datetime = Field(serialization_alias="publishTime")
    category_id: int = Field(serialization_alias="categoryId")
    views: int
    view_time: datetime = Field(serialization_alias="viewTime")


class HistoryListData(BaseModel):
    list: list[HistoryItemOut]
    total: int
    has_more: bool = Field(serialization_alias="hasMore")
