from collections.abc import Sequence
from uuid import UUID

from app.db import UnitOfWork, models
from app.schemas.wishes import WishAdd, WishUpdate


async def get_by_id(uow: UnitOfWork, wish_id: UUID) -> models.Wish | None:
    async with uow:
        return await uow.wishes.get(wish_id)


async def list(uow: UnitOfWork, offset: int = 0, limit: int = 100) -> Sequence[models.Wish]:
    async with uow:
        return await uow.wishes.list(offset, limit)


async def add(uow: UnitOfWork, wishlist_id: UUID, data: WishAdd) -> models.Wish:
    wish_dict = data.model_dump()

    async with uow:
        new_wish = await uow.wishes.add(**wish_dict, wishlist_id=wishlist_id)
        await uow.commit()
        return new_wish


async def update(uow: UnitOfWork, wish: UUID | models.Wish, data: WishUpdate) -> models.Wish:
    async with uow:
        wish_dict = data.model_dump(exclude_unset=True)

        updated_wish = await uow.wishes.update(wish, **wish_dict)
        await uow.commit()
        return updated_wish


async def delete(uow: UnitOfWork, wish: UUID | models.Wish) -> None:
    async with uow:
        await uow.wishes.delete(wish)
        await uow.commit()


async def get_count(uow: UnitOfWork) -> int:
    async with uow:
        count = await uow.wishlists.count()
        if count is None:
            return 0
        return count
