import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_token import UserToken
from models.users import User
from utils.security import hash_password, verify_password

TOKEN_TTL = timedelta(days=7)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password: str) -> User:
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    # assigns the primary key without ending the transaction, so the caller
    # can immediately issue a token for this user
    await db.flush()
    return user


async def get_user_by_token(db: AsyncSession, access_token: str) -> Optional[User]:
    """Resolve an access token to its owner, ignoring revoked/expired ones."""
    result = await db.execute(
        select(User)
        .join(UserToken, UserToken.user_id == User.id)
        .where(
            UserToken.access_token == access_token,
            UserToken.is_revoked.is_(False),
            UserToken.expires_at > datetime.now(),
        )
    )
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Return the user when the credentials match, otherwise None.

    The caller reports a single generic error for both "no such user" and
    "wrong password" so the endpoint can't be used to enumerate usernames.
    """
    user = await get_user_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def purge_expired_tokens(db: AsyncSession, user_id: int) -> None:
    """Drop this user's expired tokens so the table doesn't grow forever."""
    await db.execute(
        delete(UserToken).where(
            UserToken.user_id == user_id,
            UserToken.expires_at < datetime.now(),
        )
    )


async def create_token(db: AsyncSession, user_id: int) -> UserToken:
    token = UserToken(
        user_id=user_id,
        token_id=str(uuid.uuid4()),
        access_token=str(uuid.uuid4()),
        expires_at=datetime.now() + TOKEN_TTL,
    )
    db.add(token)
    await db.flush()
    return token


async def update_user(db: AsyncSession, user: User, fields: dict) -> User:
    """Apply the given fields to the user. Callers pass only what was sent."""
    for name, value in fields.items():
        setattr(user, name, value)
    await db.flush()
    return user


async def change_password(db: AsyncSession, user: User, new_password: str) -> None:
    user.hashed_password = hash_password(new_password)
    await db.flush()


async def revoke_other_tokens(db: AsyncSession, user_id: int, keep_access_token: str) -> None:
    """Sign the user out everywhere except the device making the request."""
    await db.execute(
        update(UserToken)
        .where(
            UserToken.user_id == user_id,
            UserToken.access_token != keep_access_token,
        )
        .values(is_revoked=True)
    )
