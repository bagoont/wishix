from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tests.utils import random_string

from app import services
from app.__main__ import app
from app.core.config import settings
from app.db import UnitOfWork, initial_data
from app.schemas.users import UserAdd

TEST_USERS = {
    "Buzz": {
        "password": random_string(),
        "first_name": None,
        "last_name": None,
        "email": None,
    },
    "Jazz": {
        "password": random_string(),
        "first_name": "Ethan",
        "last_name": "Kim",
        "email": None,
    },
    "Nova": {
        "password": random_string(),
        "first_name": "Ava",
        "last_name": "Moreno",
        "email": "nova@email.com",
    },
    "Pixie": {
        "password": random_string(),
        "first_name": None,
        "last_name": None,
        "email": None,
    },
    "Sparky": {
        "password": random_string(),
        "first_name": None,
        "last_name": None,
        "email": "sparky@email.com",
    },
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def uow() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork() as uow:
        if await uow.users.list():
            pytest.skip("Database is not empty.")

        await initial_data()
        for username in TEST_USERS:
            await services.users.add(
                uow,
                UserAdd(
                    name=username,
                    password=TEST_USERS[username]["password"],
                    first_name=TEST_USERS[username]["first_name"],
                    last_name=TEST_USERS[username]["last_name"],
                    email=TEST_USERS[username]["email"],
                    is_active=True,
                ),
            )

        yield uow

        await uow.users.clean()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"{settings.app.protocol}://{settings.app.host}:{settings.app.port}",
    ) as ac:
        yield ac


async def get_token_headers(client: AsyncClient, username: str, password: str) -> dict[str, str]:
    login_data = {
        "username": username,
        "password": password,
    }
    r = await client.post(f"{settings.app.api.v1}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}


@pytest_asyncio.fixture(scope="session")
async def superuser_token_headers(client: AsyncClient) -> dict[str, str]:
    return await get_token_headers(client, settings.superuser.name, settings.superuser.password)


@pytest_asyncio.fixture(scope="session")
async def token_headers(client: AsyncClient) -> dict[str, dict[str, str]]:
    token_headers_dict = {}
    for username in TEST_USERS:
        token_headers_dict[username] = await get_token_headers(
            client,
            username,
            TEST_USERS[username]["password"],
        )
    return token_headers_dict
