import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import TEST_USERS
from tests.utils import random_string

from app import services
from app.core.config import settings
from app.db import UnitOfWork
from app.db.models import consts
from app.utils.passwords import verify_password

from pprint import pprint


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize("username", list(TEST_USERS))
async def test_user_get_me(
    username: str,
    client: AsyncClient,
    token_headers: dict[str, dict[str, str]],
) -> None:
    r = await client.get(
        f"{settings.app.api.v1}/users/me",
        headers=token_headers[username],
    )
    current_user = r.json()

    assert current_user
    assert current_user["name"] == username
    assert current_user["email"] == TEST_USERS[username]["email"]
    assert current_user["first_name"] == TEST_USERS[username]["first_name"]
    assert current_user["last_name"] == TEST_USERS[username]["last_name"]
    assert current_user["role"] == consts.UserRole.USER


@pytest.mark.asyncio(scope="session")
async def test_user_get_me_not_auth(client: AsyncClient) -> None:
    r = await client.get(f"{settings.app.api.v1}/users/me")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize("username", ["Buzz"])
async def test_user_update_me(
    username: str,
    client: AsyncClient,
    token_headers: dict[str, dict[str, str]],
    uow: UnitOfWork,
) -> None:
    r = await client.patch(
        f"{settings.app.api.v1}/users/me",
        headers=token_headers[username],
        json={"last_name": "Aiden", "first_name": "Patel"},
    )
    current_user = r.json()

    current_user_model = await services.users.get_by_name(uow, username)
    assert current_user_model

    assert current_user
    assert current_user["name"] == current_user_model.name
    assert current_user["first_name"] == current_user_model.first_name
    assert current_user["last_name"] == current_user_model.last_name

    TEST_USERS[username]["first_name"] = "Aiden"
    TEST_USERS[username]["last_name"] = "Patel"


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize("username", ["Buzz"])
async def test_user_get(
    username: str,
    client: AsyncClient,
    token_headers: dict[str, dict[str, str]],
    uow: UnitOfWork,
) -> None:
    another_user_model = await services.users.get_by_name(uow, settings.superuser.name)
    assert another_user_model

    r = await client.get(
        f"{settings.app.api.v1}/users/{another_user_model.id}",
        headers=token_headers[username],
    )
    another_user = r.json()

    assert another_user
    assert another_user["name"] == another_user_model.name
    assert another_user["role"] == another_user_model.role
    assert another_user["email"] == another_user_model.email
    assert another_user["first_name"] == another_user_model.first_name
    assert another_user["last_name"] == another_user_model.last_name


@pytest.mark.asyncio(scope="session")
async def test_superuser_get_me(
    client: AsyncClient,
    superuser_token_headers: dict[str, str],
) -> None:
    r = await client.get(f"{settings.app.api.v1}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user

    assert current_user["name"] == settings.superuser.name
    assert current_user["role"] == consts.UserRole.SUPERUSER


@pytest.mark.asyncio(scope="session")
async def test_superuser_get_users(
    username: str,
    client: AsyncClient,
    superuser_token_headers: dict[str, str],
    uow: UnitOfWork,
) -> None:
    user = await services.users.get_by_name(uow, username)
    assert user

    r = await client.get(f"{settings.app.api.v1}/users/", headers=superuser_token_headers)

    users = r.json()
    
    for username in TEST_USERS:
    assert user[0]


@pytest.mark.asyncio(scope="session")
async def test_superuser_get_users_default_user(
    client: AsyncClient,
    token_headers: dict[str, str],
) -> None:
    r = await client.get(f"{settings.app.api.v1}/users/", headers=token_headers)
    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio(scope="session")
async def test_superuser_create_user(
    client: AsyncClient,
    superuser_token_headers: dict[str, str],
    uow: UnitOfWork,
) -> None:
    data = {
        "name": random_string(),
        "email": None,
        "first_name": None,
        "last_name": None,
        "password": random_string(),
        "is_active": True,
        "role": consts.UserRole.SUPERUSER,
    }
    r = await client.post(
        f"{settings.app.api.v1}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()

    user = await services.users.get_by_name(uow, data["name"])
    assert user

    assert data["name"] == user["name"]
    assert data["email"] == user["email"]
    assert data["first_name"] == user["first_name"]
    assert data["last_name"] == user["last_name"]
    assert verify_password(data["password"], user["hashed_password"])
    assert data["is_active"] == user["is_active"]
    assert data["role"] == user["role"]


@pytest.mark.asyncio(scope="session")
async def test_superuser_update_user(
    client: AsyncClient,
    superuser_token_headers: dict[str, str],
    uow: UnitOfWork,
) -> None:
    another_user_model = await services.users.get_by_name(uow, TEST_USERNAME)
    assert another_user_model

    r = await client.patch(
        f"{settings.app.api.v1}/users/{another_user_model.id}",
        headers=superuser_token_headers,
        json={"last_name": TEST_LASTNAME},
    )
    current_user = r.json()

    assert current_user
    assert current_user["name"] == another_user_model.name
    assert current_user["role"] == another_user_model.role
    assert current_user["email"] == another_user_model.email
    assert current_user["first_name"] == another_user_model.first_name
    assert current_user["last_name"] == TEST_LASTNAME


@pytest.mark.asyncio(scope="session")
async def test_superuser_delete_user(
    client: AsyncClient,
    superuser_token_headers: dict[str, str],
    uow: UnitOfWork,
) -> None:
    another_user_model = await services.users.get_by_name(uow, TEST_USERNAME)
    assert another_user_model

    r = await client.delete(
        f"{settings.app.api.v1}/users/{another_user_model.id}",
        headers=superuser_token_headers,
    )

    assert r.status_code == status.HTTP_200_OK

    another_user_model = await services.users.get_by_name(uow, TEST_USERNAME)
    assert not another_user_model


@pytest.mark.asyncio(scope="session")
async def test_signup(client: AsyncClient, uow: UnitOfWork) -> None:
    data = {
        "name": "Zee",
        "password": random_string(),
    }
    r = await client.post(
        f"{settings.app.api.v1}/users/signup",
        json=data,
    )

    created_user = r.json()

    user = await services.users.get_by_name(uow, data["name"])
    assert user

    assert created_user["name"] == user.name
    assert created_user["email"] == user.email
    assert created_user["first_name"] == user.first_name
    assert created_user["last_name"] == user.last_name
    assert created_user["role"] == user.role
