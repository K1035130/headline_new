from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class RelatedNews(Base):
    __tablename__ = "related_news"
    __table_args__ = (UniqueConstraint("news_id", "related_news_id", name="uq_related_news_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    related_news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
