from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

from config.db_conf import get_db
from crud import users
from models.users import STATUS_ACTIVE, User
from schemas.users import (
    AuthData,
    UserChangePwdRequest,
    UserInfoOut,
    UserLoginRequest,
    UserRegisterRequest,
    UserUpdateRequest,
)
from utils.auth import get_current_token, get_current_user
from utils.response import success_response
from utils.security import verify_password

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


@router.post("/login")
async def login(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, payload.username, payload.password)
    if user is None:
        # deliberately identical for unknown user and wrong password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if user.status != STATUS_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    user.last_login_at = datetime.now()
    await users.purge_expired_tokens(db, user_id=user.id)
    token = await users.create_token(db, user_id=user.id)

    return success_response(
        message="Logged in successfully",
        data=AuthData(token=token.access_token, user_info=UserInfoOut.model_validate(user)),
    )


@router.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    return success_response(data=UserInfoOut.model_validate(current_user))


@router.put("/update")
async def update_user_info(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # exclude_unset keeps absent keys from overwriting existing values with null
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated_user = await users.update_user(db, current_user, fields)

    return success_response(
        message="Updated successfully",
        data=UserInfoOut.model_validate(updated_user),
    )


@router.put("/password")
async def change_password(
    payload: UserChangePwdRequest,
    current_user: User = Depends(get_current_user),
    current_token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    await users.change_password(db, current_user, payload.new_password)
    # other devices are signed out; the one changing the password stays in
    await users.revoke_other_tokens(db, current_user.id, keep_access_token=current_token)

    return success_response(message="Password changed successfully")
