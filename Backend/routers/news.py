from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from schemas.news import (
    NewsCategoryOut,
    NewsDetailOut,
    NewsItemOut,
    NewsListData,
    RelatedNewsItem,
)
from utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db, skip=skip, limit=limit)

    return success_response(
        message="Success",
        data=[NewsCategoryOut.model_validate(c) for c in categories],
    )


@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db),
):
    news_list, total, has_more = await news.get_news_by_category(
        db, category_id=category_id, page=page, page_size=page_size
    )

    return success_response(
        message="Success",
        data=NewsListData(
            list=[NewsItemOut.model_validate(item) for item in news_list],
            total=total,
            has_more=has_more,
        ),
    )


@router.get("/detail")
async def get_news_detail(id: int, db: AsyncSession = Depends(get_db)):
    result = await news.get_news_detail(db, news_id=id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )

    news_obj, related_news = result
    data = NewsDetailOut.model_validate(news_obj)
    data.related_news = [RelatedNewsItem.model_validate(item) for item in related_news]

    return success_response(message="Success", data=data)
