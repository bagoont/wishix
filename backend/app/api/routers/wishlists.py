from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app import services
from app.api.deps import CurrentUser, UoWDep
from app.core.cache import cache
from app.db.models import consts
from app.schemas.utils import Message
from app.schemas.wishlists import Wishlist, WishlistAdd, WishlistUpdate

router = APIRouter()


@router.get("/", response_model=list[Wishlist | None])
async def get_wishlists(uow: UoWDep, offset: int = 0, limit: int = 100):
    return await services.wishlists.list(uow, offset, limit)


@router.post("/")
async def post_wishlist(uow: UoWDep, current_user: CurrentUser, wishlist_in: WishlistAdd):
    wishlist = await services.wishlists.add(uow, current_user.id, wishlist_in)

    await cache.delete("wishlists:count")

    return wishlist


@router.get("/{wishlist_id}", response_model=Wishlist)
async def get_wishlist(uow: UoWDep, wishlist_id: UUID):
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")

    return wishlist


@router.patch("/{wishlist_id}")
async def patch_wishlist(
    uow: UoWDep,
    current_user: CurrentUser,
    wishlist_id: UUID,
    wishlist_in: WishlistUpdate,
):
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")
    if current_user.role != consts.UserRole.SUPERUSER and wishlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    return await services.wishlists.update(uow, wishlist, wishlist_in)


@router.delete("/{wishlist_id}")
async def delete_wishlist(uow: UoWDep, current_user: CurrentUser, wishlist_id: UUID) -> Message:
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")
    if current_user.role != consts.UserRole.SUPERUSER and wishlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    await services.wishlists.delete(uow, wishlist)

    await cache.delete("wishlists:count")

    return Message(detail="Wishlist deleted successfully.")


@router.get("/count/cached")
@cache(ttl="1h", key="wishlists:count")
async def get_cached_wishlists_count(uow: UoWDep):
    return await services.wishlists.get_count(uow)


@router.get("/count/no_cached")
async def get_no_cached_wishlists_count(uow: UoWDep):
    return await services.wishlists.get_count(uow)
