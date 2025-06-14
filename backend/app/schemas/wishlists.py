from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from app.db.models import consts


class Wishlist(BaseModel):
    id: UUID4
    title: str
    description: str | None
    date: datetime | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WishlistAdd(BaseModel):
    title: str = Field(max_length=consts.WISHLIST_TITLE_LENGTH)
    description: str | None = Field(max_length=consts.WISHLIST_DESCRIPTION_LENGTH)
    date: datetime | None = None


class WishlistUpdate(BaseModel):
    title: str | None = Field(max_length=consts.WISHLIST_TITLE_LENGTH)
    description: str | None = Field(max_length=consts.WISHLIST_DESCRIPTION_LENGTH)
    date: datetime | None
