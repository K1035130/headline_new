"""Authentication dependency for endpoints that need a signed-in user."""

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users
from models.users import STATUS_ACTIVE, User


def extract_token(authorization: Optional[str]) -> str:
    """Pull the token out of the Authorization header.

    The frontend sends the raw token, but "Bearer <token>" is accepted too so
    the API keeps working if that ever changes.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return token


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = extract_token(authorization)

    user = await users.get_user_by_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if user.status != STATUS_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    return user


async def get_current_token(authorization: Optional[str] = Header(default=None)) -> str:
    """The raw token of the current request, for endpoints that revoke others."""
    return extract_token(authorization)
