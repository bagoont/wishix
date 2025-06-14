from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base

T = TypeVar("T", bound=Base)


class _IRepository(Generic[T], ABC):
    @abstractmethod
    async def get(self, ident: UUID | T) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        offset: int,
        limit: int,
    ) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, **kwargs: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, ident: UUID | T, **kwargs: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, ident: UUID | T) -> None:
        raise NotImplementedError


class Repository(_IRepository[T], ABC):
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_obj(self, ident: UUID | T) -> T | None:
        if isinstance(ident, UUID):
            return await self.session.get(self.model, ident)
        if isinstance(ident, self.model):
            return ident
        msg = f"Invalid identifier type: {type(ident)}"
        raise ValueError(msg)

    async def get(self, ident: UUID | T) -> T | None:
        return await self._get_obj(ident)

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> Sequence[T]:
        statement = select(self.model).offset(offset).limit(limit)
        if order_by:
            statement = statement.order_by(order_by)
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

    async def add(self, **kwargs: Any) -> T:
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, ident: UUID | T, **kwargs: Any) -> T:
        entity = await self._get_obj(ident)
        if entity is None:
            msg = "Entity not found."
            raise ValueError(msg)
        for key, value in kwargs.items():
            setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, ident: UUID | T) -> None:
        entity = await self._get_obj(ident)
        if entity is None:
            msg = "Entity not found."
            raise ValueError(msg)
        await self.session.delete(entity)
        await self.session.flush()
