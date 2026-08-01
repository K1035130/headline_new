from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), 
                                      unique = True,
                                      nullable = False,
                                      comment = "Category name")
    sort_order: Mapped[int] = mapped_column(Integer,
                                            default = 0,
                                            nullable = False,
                                            comment = "Sort order")

    def __repr__(self) -> str:
        return f"<NewsCategory(id={self.id}, name={self.name}, sort_order={self.sort_order})>"