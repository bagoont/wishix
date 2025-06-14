from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base, consts, uuid_pk

if TYPE_CHECKING:
    from app.db.models import User, Wish


class Wishlist(Base):
    __tablename__ = "wishlists"

    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(consts.WISHLIST_TITLE_LENGTH))
    description: Mapped[str | None] = mapped_column(String(consts.WISHLIST_DESCRIPTION_LENGTH))
    date: Mapped[datetime | None] = mapped_column(default=None)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship(back_populates="wishlists", lazy="joined")
    wishes: Mapped[list["Wish"]] = relationship(back_populates="wishlist", lazy="joined")
