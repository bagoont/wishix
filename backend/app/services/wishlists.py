from collections.abc import Sequence
from uuid import UUID

from app.db import UnitOfWork, models
from app.schemas.wishlists import WishlistAdd, WishlistUpdate


async def get_by_id(uow: UnitOfWork, wishlist_id: UUID) -> models.Wishlist | None:
    async with uow:
        return await uow.wishlists.get(wishlist_id)


async def list(uow: UnitOfWork, offset: int = 0, limit: int = 100) -> Sequence[models.Wishlist]:
    async with uow:
        return await uow.wishlists.list(offset, limit)


async def add(uow: UnitOfWork, user_id: UUID, data: WishlistAdd) -> models.Wishlist:
    wishlist_dict = data.model_dump()

    async with uow:
        new_wishlist = await uow.wishlists.add(**wishlist_dict, owner_id=user_id)
        await uow.commit()
        return new_wishlist


async def update(
    uow: UnitOfWork,
    wishlist: UUID | models.Wishlist,
    data: WishlistUpdate,
) -> models.Wishlist:
    async with uow:
        wishlist_dict = data.model_dump(exclude_unset=True)

        updated_wishlist = await uow.wishlists.update(wishlist, **wishlist_dict)
        await uow.commit()
        return updated_wishlist


async def delete(uow: UnitOfWork, wishlist: UUID | models.Wishlist) -> None:
    async with uow:
        await uow.wishlists.delete(wishlist)
        await uow.commit()


async def get_count(uow: UnitOfWork) -> int:
    async with uow:
        count = await uow.wishlists.count()
        if count is None:
            return 0
        return count
