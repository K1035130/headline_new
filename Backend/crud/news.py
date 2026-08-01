from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from models.news_category import NewsCategory


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(NewsCategory).order_by(NewsCategory.sort_order).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_news_by_category(db: AsyncSession, category_id: int, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size

    result = await db.execute(
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    news_list = result.scalars().all()

    total_result = await db.execute(
        select(func.count()).select_from(News).where(News.category_id == category_id)
    )
    total = total_result.scalar()

    has_more = (offset + len(news_list)) < total

    return news_list, total, has_more
