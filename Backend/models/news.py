from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询速度
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),
        Index('idx_publish_time', 'publish_time'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="News ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="News title")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="News summary")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="News content")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="Cover image URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="Author")
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), comment="Author user ID")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_category.id"), comment="Category ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="View count")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="Publish time")

    def __repr__(self) -> str:
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
