from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NewsCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class NewsItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: datetime


class NewsListData(BaseModel):
    list: list[NewsItemOut]
    total: int
    has_more: bool
