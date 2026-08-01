from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users
from schemas.users import AuthData, UserInfoOut, UserRegisterRequest
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register")
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await users.get_user_by_username(db, payload.username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = await users.create_user(db, username=payload.username, password=payload.password)
    token = await users.create_token(db, user_id=user.id)

    return success_response(
        message="Registered successfully",
        data=AuthData(token=token.access_token, user_info=UserInfoOut.model_validate(user)),
    )
