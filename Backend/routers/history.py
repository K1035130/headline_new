from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import history
from models.news import News
from models.users import User
from schemas.history import (
    HistoryAddData,
    HistoryAddRequest,
    HistoryItemOut,
    HistoryListData,
)
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    payload: HistoryAddRequest,
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

    record = await history.add_or_touch_history(db, user_id=user.id, news_id=payload.news_id)

    return success_response(
        message="Added to history",
        data=HistoryAddData(
            id=record.id,
            user_id=record.user_id,
            news_id=record.news_id,
            view_time=record.viewed_at,
        ),
    )


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total, has_more = await history.get_history_list(
        db, user_id=user.id, page=page, page_size=page_size
    )

    items = [
        HistoryItemOut(
            id=news.id,
            history_id=record.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            publish_time=news.publish_time,
            category_id=news.category_id,
            views=news.views,
            view_time=record.viewed_at,
        )
        for news, record in rows
    ]

    return success_response(data=HistoryListData(list=items, total=total, has_more=has_more))


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await history.delete_history(db, user_id=user.id, history_id=history_id)
    if removed == 0:
        # same answer whether the row is missing or owned by someone else
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found",
        )

    return success_response(message="Deleted successfully")


@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await history.clear_history(db, user_id=user.id)

    return success_response(message=f"Cleared {removed} history record(s)")
