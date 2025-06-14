from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base, consts, uuid_pk

if TYPE_CHECKING:
    from app.db.models import Reservation, Wishlist


class Wish(Base):
    __tablename__ = "wishes"

    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(consts.WISH_TITLE_LENGTH))
    description: Mapped[str | None] = mapped_column(
        String(consts.WISH_DESCRIPTION_LENGTH),
        default=None,
    )
    price: Mapped[Numeric | None] = mapped_column(
        Numeric(consts.WISH_PRICE_PRECISION, consts.WISH_PRICE_SCALE),
        default=None,
    )
    wishlist_id: Mapped[UUID] = mapped_column(
        ForeignKey("wishlists.id", ondelete="CASCADE"),
    )

    wishlist: Mapped["Wishlist"] = relationship(back_populates="wishes", lazy="joined")
    reservation: Mapped[Optional["Reservation"]] = relationship(
        back_populates="wish",
        lazy="joined",
    )
