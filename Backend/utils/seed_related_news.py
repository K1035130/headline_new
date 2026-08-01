"""Seed the related_news table so news detail pages have recommendations.

Each article is linked to a few others: same-category ones first, then
nearby ids to fill the quota. Safe to re-run — existing pairs are skipped.

    python -m utils.seed_related_news
"""

import asyncio

from sqlalchemy import select

from config.db_conf import async_session, engine
from models.news import News
from models.news_category import NewsCategory  # noqa: F401 registers FK target
from models.related_news import RelatedNews
from models.users import User  # noqa: F401 registers FK target

RELATED_PER_NEWS = 3


def pick_related(news_obj, all_news):
    """Same-category articles first, then following ids, capped at the quota."""
    same_category = [n.id for n in all_news if n.category_id == news_obj.category_id and n.id != news_obj.id]

    others = [n.id for n in all_news if n.id not in same_category and n.id != news_obj.id]
    # start after the current article so each one gets a different mix
    start = next((i for i, nid in enumerate(others) if nid > news_obj.id), 0)
    rotated = others[start:] + others[:start]

    return (same_category + rotated)[:RELATED_PER_NEWS]


async def seed() -> None:
    async with async_session() as session:
        all_news = (await session.execute(select(News).order_by(News.id))).scalars().all()

        existing_pairs = {
            (r.news_id, r.related_news_id)
            for r in (await session.execute(select(RelatedNews))).scalars().all()
        }

        added = 0
        for news_obj in all_news:
            for related_id in pick_related(news_obj, all_news):
                if (news_obj.id, related_id) not in existing_pairs:
                    session.add(RelatedNews(news_id=news_obj.id, related_news_id=related_id))
                    existing_pairs.add((news_obj.id, related_id))
                    added += 1

        await session.commit()

        total = len((await session.execute(select(RelatedNews))).scalars().all())
        print(f"added {added} new pairs, {total} total")

        for news_obj in all_news[:3]:
            related = (
                await session.execute(
                    select(News.id, News.title)
                    .join(RelatedNews, RelatedNews.related_news_id == News.id)
                    .where(RelatedNews.news_id == news_obj.id)
                )
            ).all()
            print(f"News {news_obj.id} -> {[r.title for r in related]}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
