from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.utils import get_current_token_payload, get_user_by_payload
from app.core.config import settings
from app.db import UnitOfWork
from app.db.models import User, consts
from app.utils.jwt import ACCESS_TOKEN_TYPE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.app.api.v1}/login/access-token")


UoWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]


async def get_current_user(
    uow: UoWDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    payload = get_current_token_payload(token)
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect token type.",
        )

    return await get_user_by_payload(uow, payload)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_superuser(user: CurrentUser) -> User:
    if user.role != consts.UserRole.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges.",
        )
    return user
