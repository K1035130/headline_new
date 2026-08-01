import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_token import UserToken
from models.users import User
from utils.security import hash_password

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
