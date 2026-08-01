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
