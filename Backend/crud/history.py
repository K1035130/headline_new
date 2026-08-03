from datetime import datetime
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def get_history(db: AsyncSession, user_id: int, news_id: int) -> Optional[History]:
    result = await db.execute(
        select(History).where(History.user_id == user_id, History.news_id == news_id)
    )
    return result.scalar_one_or_none()


async def add_or_touch_history(db: AsyncSession, user_id: int, news_id: int) -> History:
    """Record a view.

    An article appears at most once per user: viewing it again refreshes
    `viewed_at` instead of adding a second row, so the list shows each article
    once, ordered by the most recent visit.
    """
    existing = await get_history(db, user_id, news_id)
    if existing is not None:
        existing.viewed_at = datetime.now()
        await db.flush()
        return existing

    record = History(user_id=user_id, news_id=news_id, viewed_at=datetime.now())
    db.add(record)
    await db.flush()
    return record


async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    """Return (rows, total, has_more); each row is (News, History)."""
    offset = (page - 1) * page_size

    result = await db.execute(
        select(News, History)
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.viewed_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = result.all()

    total_result = await db.execute(
        select(func.count()).select_from(History).where(History.user_id == user_id)
    )
    total = total_result.scalar()

    has_more = (offset + len(rows)) < total

    return rows, total, has_more


async def delete_history(db: AsyncSession, user_id: int, history_id: int) -> int:
    """Delete one entry. Scoped to the owner so nobody can delete another
    user's history by guessing ids. Returns how many rows went away.
    """
    result = await db.execute(
        delete(History).where(History.id == history_id, History.user_id == user_id)
    )
    return result.rowcount


async def clear_history(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(delete(History).where(History.user_id == user_id))
    return result.rowcount
