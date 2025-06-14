from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base, uuid_pk

if TYPE_CHECKING:
    from app.db.models import User, Wish


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    wish_id: Mapped[UUID] = mapped_column(ForeignKey("wishes.id", ondelete="CASCADE"), unique=True)
    is_private: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="reservations", lazy="joined")
    wish: Mapped["Wish"] = relationship(back_populates="reservation", lazy="joined")
