from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base, consts, uuid_pk

if TYPE_CHECKING:
    from app.db.models import Reservation, Wishlist


# TODO: Use email instead login for auth.
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(consts.USER_NAME_LENGTH), unique=True)
    email: Mapped[str | None] = mapped_column(
        String(consts.USER_EMAIL_LENGTH),
        unique=True,
        default=None,
    )
    first_name: Mapped[str | None] = mapped_column(String(consts.USER_NAME_LENGTH), default=None)
    last_name: Mapped[str | None] = mapped_column(String(consts.USER_NAME_LENGTH), default=None)
    hashed_password: Mapped[str] = mapped_column(String(consts.USER_HASHED_PASSWORD_LENGTH))
    is_active: Mapped[bool] = mapped_column(default=False)
    role: Mapped[consts.UserRole] = mapped_column(default=consts.UserRole.USER)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="user", lazy="joined")
    wishlists: Mapped[list["Wishlist"]] = relationship(back_populates="owner", lazy="joined")
