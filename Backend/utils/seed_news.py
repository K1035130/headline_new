"""Seed the news table with placeholder articles for testing.

Safe to re-run: existing rows are matched by id and updated in place.

    python -m utils.seed_news
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, text

from config.db_conf import async_session, engine
from models.news import News
from models.news_category import NewsCategory  # noqa: F401 registers news_category FK target
from models.users import User  # noqa: F401 registers users FK target

NEWS_PER_CATEGORY = 2
CATEGORY_IDS = range(1, 9)  # matches the 8 categories seeded by seed_categories.py


def build_news_rows():
    rows = []
    news_id = 1
    for category_id in CATEGORY_IDS:
        for _ in range(NEWS_PER_CATEGORY):
            rows.append(
                dict(
                    id=news_id,
                    title=f"News {news_id}",
                    description=f"here is description for news {news_id}",
                    content=f"This is placeholder content for News {news_id}.",
                    image=None,
                    author="Test Author",
                    author_id=None,
                    category_id=category_id,
                    views=(news_id * 137) % 5000,
                    publish_time=datetime.now() - timedelta(hours=news_id),
                )
            )
            news_id += 1
    return rows


async def seed() -> None:
    rows = build_news_rows()

    async with async_session() as session:
        for row in rows:
            existing = await session.get(News, row["id"])
            if existing is None:
                session.add(News(**row))
            else:
                for key, value in row.items():
                    if key != "id":
                        setattr(existing, key, value)
        await session.commit()

        # ids are assigned explicitly above, which leaves the SERIAL sequence
        # behind; move it past the seeded rows so later inserts don't collide
        await session.execute(
            text("select setval('news_id_seq', (select max(id) from news))")
        )
        await session.commit()

        result = await session.execute(select(News).order_by(News.id))
        for row in result.scalars():
            print(row)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
