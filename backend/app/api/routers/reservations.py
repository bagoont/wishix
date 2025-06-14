from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app import services
from app.api.deps import CurrentUser, UoWDep
from app.schemas.reservations import Reservation, ReservationAdd, ReservationUpdate
from app.schemas.utils import Message

router = APIRouter()


@router.post("/", response_model=Reservation)
async def reserve_wish(
    uow: UoWDep,
    current_user: CurrentUser,
    wish_id: UUID,
    reservation_in: ReservationAdd,
):
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")
    if wish.wishlist.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't reserve your own wish.",
        )
    if wish.reservation is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wish already reserved.",
        )

    return await services.reservations.add(uow, current_user.id, wish.id, reservation_in)


@router.patch("/", response_model=Reservation)
async def update_reservation(
    uow: UoWDep,
    current_user: CurrentUser,
    wish_id: UUID,
    reservation_in: ReservationUpdate,
):
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")
    if wish.reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not reserved.")
    if wish.reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    return await services.reservations.update(uow, wish.reservation, reservation_in)


@router.delete("/")
async def unreserve_wish(uow: UoWDep, current_user: CurrentUser, wish_id: UUID) -> Message:
    wish = await services.wishes.get_by_id(uow, wish_id)
    if wish is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found.")
    if wish.reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not reserved.")
    if wish.reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions.",
        )

    await services.reservations.delete(uow, wish.reservation)
    return Message(detail="Wish unreserved successfully.")
