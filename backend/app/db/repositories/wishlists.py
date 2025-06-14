from sqlalchemy import func, select

from app.db.models import Wishlist
from app.db.repositories import Repository


class WishlistRepository(Repository[Wishlist]):
    model = Wishlist

    async def count(self) -> int | None:
        statement = select(func.count()).select_from(self.model)
        result = await self.session.execute(statement)
        return result.scalar()
