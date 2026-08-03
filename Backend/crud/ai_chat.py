from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ai_chat import AIChat


async def save_exchange(
    db: AsyncSession, user_id: int, question: str, answer: str
) -> None:
    """Store one question/answer pair as two rows, matching the chat layout."""
    db.add(AIChat(user_id=user_id, role="user", content=question))
    db.add(AIChat(user_id=user_id, role="assistant", content=answer))
    await db.flush()


async def get_chat_history(db: AsyncSession, user_id: int, limit: int = 50):
    """Most recent messages first, returned oldest-first for replay."""
    result = await db.execute(
        select(AIChat)
        .where(AIChat.user_id == user_id)
        .order_by(AIChat.id.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))

    total_result = await db.execute(
        select(func.count()).select_from(AIChat).where(AIChat.user_id == user_id)
    )
    return messages, total_result.scalar()


async def clear_chat_history(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(delete(AIChat).where(AIChat.user_id == user_id))
    return result.rowcount
