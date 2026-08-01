from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class UserToken(Base):
    __tablename__ = "user_token"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Row ID")
    # not unique: a user may hold several valid tokens (one per device)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, comment="Owner user ID")
    token_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, comment="Token identifier (uuid)"
    )
    access_token: Mapped[str] = mapped_column(String(500), comment="Access token")
    refresh_token: Mapped[Optional[str]] = mapped_column(String(500), comment="Refresh token")
    expires_at: Mapped[datetime] = mapped_column(DateTime, comment="Expiry time")
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether the token was revoked"
    )

    def __repr__(self) -> str:
        return f"<UserToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
