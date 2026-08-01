from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    """Request body for POST /api/user/register."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, max_length=72, description="Password")


class UserInfoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None


class AuthData(BaseModel):
    """`data` payload returned by register / login."""

    token: str
    user_info: UserInfoOut = Field(serialization_alias="userInfo")
