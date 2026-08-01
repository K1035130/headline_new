from sqlalchemy import DateTime

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    create_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now,
        comment = "Creation time")

    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment = "Update time")


# 在 Base 定义之后导入所有模型模块，让它们注册到同一份 metadata 上。
# 否则跨表外键（如 news.author_id -> users.id）在 flush 时会因为目标表
# 未注册而报 NoReferencedTableError。
from models import (  # noqa: E402,F401
    ai_chat,
    favorite,
    history,
    news,
    news_category,
    related_news,
    user_token,
    users,
)
