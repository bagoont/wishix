from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status

from app import services
from app.api.deps import CurrentUser, UoWDep, get_current_superuser
from app.api.utils import get_current_token_payload, get_user_by_payload
from app.core.config import settings
from app.schemas.users import User, UserAdd, UserPublic, UserRegister, UserUpdate, UserUpdateMe
from app.schemas.utils import Message
from app.schemas.wishlists import Wishlist
from app.utils.email import send_email
from app.utils.jwt import REGISTRATION_CONFIRMATION_TOKEN_TYPE, create_token
from app.utils.passwords import verify_password
from app.utils.templates import render_template

router = APIRouter()


@router.post("/signup", response_model=UserPublic)
async def signup(uow: UoWDep, user_in: UserRegister):
    if settings.app.registration is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration is disabled.",
        )

    user = await services.users.get_by_name(uow, user_in.name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this name already exists.",
        )

    user_add = UserAdd.model_validate(user_in)
    user = await services.users.add(uow, user_add)

    if settings.email and user.email:
        token_timedelta = timedelta(
            minutes=settings.token.registration_confirmation_expire_minutes,
        )
        token = create_token(user.id, token_timedelta, REGISTRATION_CONFIRMATION_TOKEN_TYPE)

        subject = f"{settings.app.name} - Registration confirmation."
        email_data = render_template(
            "registration_confirmation.html",
            app_name=settings.app.name,
            username=user_in.name,
            email=user_in.email,
            valid_time=settings.token.reset_password_expire_minutes,
            link=f"{settings.app.protocol}://{settings.app.host}:{settings.app.port}/registration-confirm?token={token}",
        )

        send_email(email_to=user.email, subject=subject, html_content=email_data)

    return user


@router.post("/registration-confirm", response_model=UserPublic)
async def registration_confirmation(uow: UoWDep, token: str):
    payload = get_current_token_payload(token)
    if payload.get("type") != REGISTRATION_CONFIRMATION_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect token type.",
        )

    user = await get_user_by_payload(uow, payload)

    await services.users.update(uow, user, UserUpdate(is_active=True))

    return Message(detail="Registration confirmation complete. Your account is now active.")


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_me(uow: UoWDep, current_user: CurrentUser, user_in: UserUpdateMe):
    if user_in.name:
        user = await services.users.get_by_name(uow, user_in.name)
        if user and user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this name already exists.",
            )

    await services.users.update(uow, current_user.id, user_in)

    return await services.users.update(uow, current_user.id, user_in)


@router.patch("/me/password")
async def update_password_me(
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    uow: UoWDep,
    current_user: CurrentUser,
) -> Message:
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password.")
    if current_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one.",
        )

    await services.users.update(uow, current_user.id, UserUpdate(password=new_password))
    return Message(detail="Password updated successfully.")


@router.delete("/me")
async def delete_me(uow: UoWDep, current_user: CurrentUser) -> Message:
    await services.users.delete(uow, current_user.id)
    return Message(detail="User deleted successfully.")


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(uow: UoWDep, user_id: UUID):
    user = await services.users.get_by_id(uow, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user


@router.get("/{user_id}/wishlists", response_model=list[Wishlist | None])
async def get_user_wishlists(
    uow: UoWDep,
    user_id: UUID,
):
    user = await services.users.get_by_id(uow, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user.wishlists


@router.get("/", dependencies=[Depends(get_current_superuser)], response_model=list[User])
async def get_users(uow: UoWDep, offset: int = 0, limit: int = 100):
    return await services.users.list(uow, offset, limit)


@router.post("/", dependencies=[Depends(get_current_superuser)], response_model=User)
async def post_user(uow: UoWDep, user_in: UserAdd):
    user = await services.users.get_by_name(uow, user_in.name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this name already exists.",
        )

    return await services.users.add(uow, user_in)


@router.patch("/{user_id}", dependencies=[Depends(get_current_superuser)], response_model=User)
async def update_user(uow: UoWDep, user_id: UUID, user_in: UserUpdate):
    user = await services.users.get_by_id(uow, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user_in.name:
        user = await services.users.get_by_name(uow, user_in.name)
        if user and user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this name already exists.",
            )

    return await services.users.update(uow, user_id, user_in)


@router.delete("/{user_id}", dependencies=[Depends(get_current_superuser)])
async def delete_user(uow: UoWDep, user_id: UUID) -> Message:
    user = await services.users.get_by_id(uow, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    await services.users.delete(uow, user_id)
    return Message(detail="User deleted successfully.")
