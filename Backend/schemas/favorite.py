from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FavoriteAddRequest(BaseModel):
    """Request body for POST /api/favorite/add."""

    model_config = ConfigDict(populate_by_name=True)

    news_id: int = Field(alias="newsId", gt=0, description="News ID")


class FavoriteCheckData(BaseModel):
    is_favorite: bool = Field(serialization_alias="isFavorite")


class FavoriteAddData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int = Field(serialization_alias="userId")
    news_id: int = Field(serialization_alias="newsId")
    create_time: datetime = Field(serialization_alias="createTime")


class FavoriteItemOut(BaseModel):
    """A favorited article, flattened for the list page.

    `id` and `newsId` both carry the news id: the spec uses `id`, while the
    frontend's Favorite.vue navigates and deletes by `newsId`.
    """

    id: int
    news_id: int = Field(serialization_alias="newsId")
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: datetime = Field(serialization_alias="publishTime")
    category_id: int = Field(serialization_alias="categoryId")
    views: int
    favorite_time: datetime = Field(serialization_alias="favoriteTime")


class FavoriteListData(BaseModel):
    list: list[FavoriteItemOut]
    total: int
    has_more: bool = Field(serialization_alias="hasMore")
