from collections.abc import Sequence
from uuid import UUID

from app.db import UnitOfWork, models
from app.schemas.users import UserAdd, UserUpdate, UserUpdateMe
from app.utils.passwords import hash_password


async def get_by_id(uow: UnitOfWork, user_id: UUID) -> models.User | None:
    async with uow:
        return await uow.users.get(user_id)


async def get_by_name(uow: UnitOfWork, username: str) -> models.User | None:
    async with uow:
        return await uow.users.get_by_name(username)


async def get_by_email(uow: UnitOfWork, email: str) -> models.User | None:
    async with uow:
        return await uow.users.get_by_email(email)


async def list(uow: UnitOfWork, offset: int = 0, limit: int = 100) -> Sequence[models.User]:
    async with uow:
        return await uow.users.list(offset, limit, models.User.name)


async def add(uow: UnitOfWork, data: UserAdd) -> models.User:
    user_dict = data.model_dump()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

    async with uow:
        new_user = await uow.users.add(**user_dict)
        await uow.commit()
        return new_user


async def update(
    uow: UnitOfWork,
    user: UUID | models.User,
    data: UserUpdate | UserUpdateMe,
) -> models.User:
    user_dict = data.model_dump(exclude_unset=True)
    if "password" in user_dict:
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

    async with uow:
        updated_user = await uow.users.update(user, **user_dict)
        await uow.commit()
        return updated_user


async def delete(uow: UnitOfWork, user: UUID | models.User) -> None:
    async with uow:
        await uow.users.delete(user)
        await uow.commit()
