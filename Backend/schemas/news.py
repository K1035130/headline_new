from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int = Field(serialization_alias="sortOrder")


class NewsItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(serialization_alias="categoryId")
    views: int
    publish_time: datetime = Field(serialization_alias="publishTime")


class NewsListData(BaseModel):
    list: list[NewsItemOut]
    total: int
    has_more: bool = Field(serialization_alias="hasMore")


class RelatedNewsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image: Optional[str] = None


class NewsDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: datetime = Field(serialization_alias="publishTime")
    category_id: int = Field(serialization_alias="categoryId")
    views: int
    related_news: list[RelatedNewsItem] = Field(
        default_factory=list, serialization_alias="relatedNews"
    )
