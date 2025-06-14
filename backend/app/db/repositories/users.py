from sqlalchemy import delete, select

from app.db.models import User
from app.db.repositories import Repository


class UserRepository(Repository[User]):
    model = User

    async def get_by_name(self, username: str) -> User | None:
        statement = select(self.model).where(self.model.name == username)
        result = await self.session.execute(statement)
        return result.unique().scalar()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.model).where(self.model.email == email)
        result = await self.session.execute(statement)
        return result.unique().scalar()

    async def clean(self) -> None:
        statement = delete(self.model)
        await self.session.execute(statement)
