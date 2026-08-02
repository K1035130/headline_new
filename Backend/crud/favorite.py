from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def get_favorite(db: AsyncSession, user_id: int, news_id: int) -> Optional[Favorite]:
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    return result.scalar_one_or_none()


async def is_favorited(db: AsyncSession, user_id: int, news_id: int) -> bool:
    return await get_favorite(db, user_id, news_id) is not None


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> Favorite:
    """Favorite an article. Already favorited is a no-op, not an error."""
    existing = await get_favorite(db, user_id, news_id)
    if existing is not None:
        return existing

    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> int:
    """Un-favorite an article, returning how many rows went away (0 or 1)."""
    result = await db.execute(
        delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    return result.rowcount


async def clear_favorites(db: AsyncSession, user_id: int) -> int:
    """Drop every favorite of this user, returning how many were removed."""
    result = await db.execute(delete(Favorite).where(Favorite.user_id == user_id))
    return result.rowcount


async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    """Return (rows, total, has_more); each row is (News, favorited_at)."""
    offset = (page - 1) * page_size

    result = await db.execute(
        select(News, Favorite.create_at.label("favorite_time"))
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.create_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = result.all()

    total_result = await db.execute(
        select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
    )
    total = total_result.scalar()

    has_more = (offset + len(rows)) < total

    return rows, total, has_more
