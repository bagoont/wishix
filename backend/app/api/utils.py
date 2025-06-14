from uuid import UUID

from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, ExpiredSignatureError, MissingRequiredClaimError

from app import services
from app.db import UnitOfWork
from app.db.models import User
from app.utils.jwt import decode_token


def get_current_token_payload(token: str) -> dict:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your token has expired.",
        ) from e
    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error when decoding the token.",
        ) from e
    except MissingRequiredClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is no required field in your token.",
        ) from e

    return payload


async def get_user_by_payload(uow: UnitOfWork, payload: dict) -> User:
    user_id = payload.get("sub")
    if user_id is None:
        msg = '"User ID not found in payload."'
        raise ValueError(msg)
    user = await services.users.get_by_id(uow, UUID(user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")

    return user
