from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.db.models import consts

MAX_PASSWORD_LENGTH = 64
MIN_PASSWORD_LENGTH = 8


# TODO: Frist name and Last name only AND not OR
class UserBase(BaseModel):
    name: str = Field(max_length=consts.USER_NAME_LENGTH)
    email: EmailStr | None = Field(max_length=consts.USER_EMAIL_LENGTH, default=None)
    first_name: str | None = Field(max_length=consts.USER_NAME_LENGTH, default=None)
    last_name: str | None = Field(max_length=consts.USER_NAME_LENGTH, default=None)

    class Config:
        from_attributes = True


class User(UserBase):
    id: UUID4
    hashed_password: str
    is_active: bool
    role: consts.UserRole

    created_at: datetime
    updated_at: datetime


class UserPublic(UserBase):
    id: UUID4
    role: consts.UserRole


class UserRegister(UserBase):
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)


class UserAdd(UserBase):
    email: EmailStr | None = Field(max_length=consts.USER_EMAIL_LENGTH, default=None)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    is_active: bool = False
    role: consts.UserRole = consts.UserRole.USER


class UserUpdate(UserBase):
    name: str | None = Field(max_length=consts.USER_NAME_LENGTH, default=None)
    email: EmailStr | None = Field(max_length=consts.USER_EMAIL_LENGTH, default=None)
    password: str | None = Field(
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        default=None,
    )
    is_active: bool | None = False
    role: consts.UserRole | None = consts.UserRole.USER


class UserUpdateMe(BaseModel):
    name: str | None = Field(max_length=consts.USER_NAME_LENGTH)
    email: EmailStr | None = Field(max_length=consts.USER_EMAIL_LENGTH)
    first_name: str | None = Field(max_length=consts.USER_NAME_LENGTH)
    last_name: str | None = Field(max_length=consts.USER_NAME_LENGTH)
