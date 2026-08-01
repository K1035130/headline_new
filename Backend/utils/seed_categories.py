"""Seed the news_category table with the default set of categories.

Safe to re-run: existing rows are matched by id and updated in place.

    python -m utils.seed_categories
"""

import asyncio

from sqlalchemy import select, text

from config.db_conf import async_session, engine
from models.news_category import NewsCategory

CATEGORIES = [
    (1, "Society", 1),
    (2, "World", 2),
    (3, "Domestic", 3),
    (4, "Entertainment", 4),
    (5, "Sports", 5),
    (6, "Technology", 6),
    (7, "Finance", 7),
    (8, "Health", 8),
]


async def seed() -> None:
    async with async_session() as session:
        for category_id, name, sort_order in CATEGORIES:
            existing = await session.get(NewsCategory, category_id)
            if existing is None:
                session.add(NewsCategory(id=category_id, name=name, sort_order=sort_order))
            else:
                existing.name = name
                existing.sort_order = sort_order
        await session.commit()

        # ids are assigned explicitly above, which leaves the SERIAL sequence
        # behind; move it past the seeded rows so later inserts don't collide
        await session.execute(
            text("select setval('news_category_id_seq', (select max(id) from news_category))")
        )
        await session.commit()

        rows = await session.execute(select(NewsCategory).order_by(NewsCategory.sort_order))
        for row in rows.scalars():
            print(row)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
