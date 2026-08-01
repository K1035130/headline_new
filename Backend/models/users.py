from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models import Base

DEFAULT_AVATAR = "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"

STATUS_ACTIVE = "active"
STATUS_DISABLED = "disabled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, comment="User ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="Username")
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, comment="Email")
    hashed_password: Mapped[str] = mapped_column(String(255), comment="Hashed password")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="Display name")
    bio: Mapped[Optional[str]] = mapped_column(Text, comment="User bio")
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), default=DEFAULT_AVATAR, comment="Avatar URL"
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(10), comment="Gender: male / female / other"
    )
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_ACTIVE, nullable=False, comment="Account status"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="Last login time"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
