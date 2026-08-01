from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class Favorite(Base):
    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_favorite_user_news"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
