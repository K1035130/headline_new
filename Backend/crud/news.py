from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from models.news_category import NewsCategory

RELATED_NEWS_LIMIT = 3


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


async def get_news_detail(db: AsyncSession, news_id: int):
    """Return (news, related_news) for the given id, or None when it doesn't exist.

    Related news are simply the latest other articles in the same category.
    Viewing the detail counts as a read, so the view counter is bumped here.
    """
    news_obj = await db.get(News, news_id)
    if news_obj is None:
        return None

    news_obj.views += 1

    related_result = await db.execute(
        select(News)
        .where(News.category_id == news_obj.category_id, News.id != news_id)
        .order_by(News.publish_time.desc())
        .limit(RELATED_NEWS_LIMIT)
    )
    related_news = related_result.scalars().all()

    return news_obj, related_news
