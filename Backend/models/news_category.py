from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
