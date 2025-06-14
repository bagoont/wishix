from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import services
from app.api.deps import UoWDep
from app.api.utils import get_current_token_payload, get_user_by_payload
from app.core.config import settings
from app.schemas.users import UserUpdate
from app.schemas.utils import Message, TokenInfo
from app.utils.email import send_email
from app.utils.jwt import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    RESET_PASSWORD_TOKEN_TYPE,
    create_token,
)
from app.utils.passwords import verify_password
from app.utils.templates import render_template

router = APIRouter()


@router.post("/login/access-token")
async def login(
    uow: UoWDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenInfo:
    user = await services.users.get_by_name(uow, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")

    access_token_timedelta = timedelta(minutes=settings.token.access_expire_minutes)
    access_token = create_token(user.id, access_token_timedelta, ACCESS_TOKEN_TYPE)

    refresh_token_timedelta = timedelta(minutes=settings.token.refresh_expire_minutes)
    refresh_token = create_token(user.id, refresh_token_timedelta, REFRESH_TOKEN_TYPE)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh(
    uow: UoWDep,
    refresh_token: Annotated[str, Form()],
) -> TokenInfo:
    payload = get_current_token_payload(refresh_token)
    if payload.get("type") != REFRESH_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect token type.",
        )

    user = await get_user_by_payload(uow, payload)

    access_token_timedelta = timedelta(minutes=settings.token.access_expire_minutes)
    access_token = create_token(user.id, access_token_timedelta, ACCESS_TOKEN_TYPE)

    refresh_token_timedelta = timedelta(minutes=settings.token.refresh_expire_minutes)
    refresh_token = create_token(user.id, refresh_token_timedelta, REFRESH_TOKEN_TYPE)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/password-recovery/{email}")
async def recover_password(uow: UoWDep, email: str) -> Message:
    if settings.email is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sending is disabled.",
        )

    user = await uow.users.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    if user.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User doesn't have an email associated with their account.",
        )

    token_timedelta = timedelta(minutes=settings.token.reset_password_expire_minutes)
    token = create_token(user.id, token_timedelta, RESET_PASSWORD_TOKEN_TYPE)

    subject = f"{settings.app.name} - Password recovery for user {email}"
    email_data = render_template(
        "reset_password.html",
        app_name=settings.app.name,
        username=user.name,
        email=user.email,
        valid_time=settings.token.reset_password_expire_minutes,
        link=f"{settings.app.protocol}://{settings.app.host}:{settings.app.port}/reset-password?token={token}",
    )

    send_email(email_to=user.email, subject=subject, html_content=email_data)

    return Message(detail="Password recovery message sent.")


@router.post("/reset-password")
async def reset_password(uow: UoWDep, token: str, new_password: str) -> Message:
    payload = get_current_token_payload(token)
    if payload.get("type") != RESET_PASSWORD_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect token type.",
        )

    user = await get_user_by_payload(uow, payload)

    await services.users.update(uow, user, UserUpdate(password=new_password))

    return Message(detail="Password updated successfully.")
