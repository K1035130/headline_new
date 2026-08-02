from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import favorite
from models.news import News
from models.users import User
from schemas.favorite import (
    FavoriteAddData,
    FavoriteAddRequest,
    FavoriteCheckData,
    FavoriteItemOut,
    FavoriteListData,
)
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    favorited = await favorite.is_favorited(db, user_id=user.id, news_id=news_id)

    return success_response(data=FavoriteCheckData(is_favorite=favorited))


@router.post("/add")
async def add_favorite(
    payload: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # checked up front so a bad id gives a 404 instead of a foreign key error
    news = await db.get(News, payload.news_id)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )

    record = await favorite.add_favorite(db, user_id=user.id, news_id=payload.news_id)

    return success_response(
        message="Added to favorites",
        data=FavoriteAddData(
            id=record.id,
            user_id=record.user_id,
            news_id=record.news_id,
            create_time=record.create_at,
        ),
    )


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # removing something that isn't favorited leaves the user in the state they
    # asked for, so it counts as success
    await favorite.remove_favorite(db, user_id=user.id, news_id=news_id)

    return success_response(message="Removed from favorites")


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total, has_more = await favorite.get_favorite_list(
        db, user_id=user.id, page=page, page_size=page_size
    )

    items = [
        FavoriteItemOut(
            id=news.id,
            news_id=news.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            publish_time=news.publish_time,
            category_id=news.category_id,
            views=news.views,
            favorite_time=favorite_time,
        )
        for news, favorite_time in rows
    ]

    return success_response(
        data=FavoriteListData(list=items, total=total, has_more=has_more)
    )


@router.delete("/clear")
async def clear_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await favorite.clear_favorites(db, user_id=user.id)

    return success_response(message=f"Cleared {removed} favorite(s)")
