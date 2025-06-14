from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app import services
from app.api.deps import CurrentUser, UoWDep
from app.core.cache import cache
from app.db.models import consts
from app.schemas.utils import Message
from app.schemas.wishes import Wish, WishAdd, WishUpdate

router = APIRouter()


@router.get("/", response_model=list[Wish | None])
async def get_wishes(uow: UoWDep, wishlist_id: UUID):
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")

    return wishlist.wishes


@router.post("/", response_model=Wish)
async def post_wish(
    uow: UoWDep,
    current_user: CurrentUser,
    wishlist_id: UUID,
    wish_in: WishAdd,
):
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")
    if current_user.role != consts.UserRole.SUPERUSER and wishlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    wish = await services.wishes.add(uow, wishlist_id, wish_in)

    await cache.delete("wishes:count")

    return wish


@router.post("/bulk", response_model=list[Wish])
async def post_wishes(
    uow: UoWDep,
    current_user: CurrentUser,
    wishlist_id: UUID,
    wishes_in: list[WishAdd],
):
    wishlist = await services.wishlists.get_by_id(uow, wishlist_id)
    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found.")
    if current_user.role != consts.UserRole.SUPERUSER and wishlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    wishes = [await services.wishes.add(uow, wishlist_id, wish_in) for wish_in in wishes_in]

    await cache.delete("wishes:count")

    return wishes


@router.get("/{wish_id}", response_model=Wish)
async def get_wish(uow: UoWDep, wish_id: UUID):
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")

    return wish


@router.patch("/{wish_id}", response_model=Wish)
async def updtae_wish(
    uow: UoWDep,
    current_user: CurrentUser,
    wish_id: UUID,
    wish_in: WishUpdate,
):
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")
    if (
        current_user.role != consts.UserRole.SUPERUSER
        and wish.wishlist.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    return await services.wishes.update(uow, wish, wish_in)


@router.delete("/{wish_id}")
async def delete_wish(uow: UoWDep, current_user: CurrentUser, wish_id: UUID) -> Message:
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")
    if (
        current_user.role != consts.UserRole.SUPERUSER
        and wish.wishlist.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    await services.wishes.delete(uow, wish)

    await cache.delete("wishes:count")

    return Message(detail="Wish deleted successfully.")


@router.get("/count/cached")
@cache(ttl="1h", key="wishes:count")
async def get_cached_wishlists_count(uow: UoWDep):
    return await services.wishes.get_count(uow)


@router.get("/count/no_cached")
async def get_no_cached_wishlists_count(uow: UoWDep):
    return await services.wishes.get_count(uow)
