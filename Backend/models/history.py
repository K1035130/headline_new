from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models import Base


class History(Base):
    __tablename__ = "history"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_history_user_news"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    viewed_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
