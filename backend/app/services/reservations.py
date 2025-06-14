from uuid import UUID

from app.db import UnitOfWork, models
from app.schemas.reservations import ReservationAdd, ReservationUpdate


async def add(
    uow: UnitOfWork,
    user_id: UUID,
    wish_id: UUID,
    data: ReservationAdd,
) -> models.Reservation:
    async with uow:
        reservation = await uow.reservations.add(
            user_id=user_id,
            wish_id=wish_id,
            **data.model_dump(),
        )
        await uow.commit()

        return reservation


async def update(
    uow: UnitOfWork,
    reservation: UUID | models.Reservation,
    data: ReservationUpdate,
) -> models.Reservation:
    async with uow:
        reservation_dict = data.model_dump(exclude_unset=True)
        return await uow.reservations.update(reservation, **reservation_dict)


async def delete(uow: UnitOfWork, reservation: UUID | models.Reservation) -> None:
    async with uow:
        await uow.reservations.delete(reservation)
        await uow.commit()
