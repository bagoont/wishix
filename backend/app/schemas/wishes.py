from datetime import datetime

from pydantic import UUID4, BaseModel, Field, NonNegativeFloat

from app.db.models import consts
from app.schemas.reservations import Reservation


class Wish(BaseModel):
    id: UUID4
    title: str
    description: str | None
    price: NonNegativeFloat | None
    reservation: Reservation | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WishAdd(BaseModel):
    title: str = Field(max_length=consts.WISH_TITLE_LENGTH)
    description: str | None = Field(max_length=consts.WISH_DESCRIPTION_LENGTH, default=None)
    price: NonNegativeFloat | None = None


class WishUpdate(BaseModel):
    title: str | None = Field(max_length=consts.WISH_TITLE_LENGTH, default=None)
    description: str | None = Field(max_length=consts.WISH_DESCRIPTION_LENGTH, default=None)
    price: NonNegativeFloat | None
