from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal["male", "female", "other", "unknown"]


class UserRegisterRequest(BaseModel):
    """Request body for POST /api/user/register."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, max_length=72, description="Password")


class UserLoginRequest(BaseModel):
    """Request body for POST /api/user/login."""

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


class UserUpdateRequest(BaseModel):
    """Request body for PUT /api/user/update — every field is optional.

    Only the keys actually present in the request are written, so sending
    {"bio": "..."} leaves the other columns untouched.
    """

    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = Field(default=None, max_length=255)
    gender: Optional[Gender] = None
    bio: Optional[str] = Field(default=None, max_length=2000)


class UserChangePwdRequest(BaseModel):
    """Request body for PUT /api/user/password."""

    model_config = ConfigDict(populate_by_name=True)

    old_password: str = Field(alias="oldPassword", min_length=6, max_length=72)
    new_password: str = Field(alias="newPassword", min_length=6, max_length=72)


class AuthData(BaseModel):
    """`data` payload returned by register / login."""

    token: str
    user_info: UserInfoOut = Field(serialization_alias="userInfo")
