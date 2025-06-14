from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from app.db import session_maker
from app.db.repositories import (
    ReservationRepository,
    UserRepository,
    WishlistRepository,
    WishRepository,
)


class _IUnitOfWork(ABC):
    users: UserRepository
    wishes: WishRepository
    reservations: ReservationRepository
    wishlists: WishlistRepository

    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(_IUnitOfWork):
    async def __aenter__(self) -> Self:
        self.session = session_maker()
        self.users = UserRepository(self.session)
        self.wishes = WishRepository(self.session)
        self.reservations = ReservationRepository(self.session)
        self.wishlists = WishlistRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
