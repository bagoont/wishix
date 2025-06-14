from datetime import datetime

from pydantic import UUID4, BaseModel


class Reservation(BaseModel):
    id: UUID4
    user_id: UUID4
    wish_id: UUID4
    is_private: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservationAdd(BaseModel):
    is_private: bool = False


class ReservationUpdate(BaseModel):
    is_private: bool | None = None
