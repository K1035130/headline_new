from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.news_category import NewsCategory


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(NewsCategory).offset(skip).limit(limit))
    return result.scalars().all()