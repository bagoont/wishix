from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
RESET_PASSWORD_TOKEN_TYPE = "reset_password"
REGISTRATION_CONFIRMATION_TOKEN_TYPE = "registration_confirmation"


def create_token(subject: Any, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(tz=UTC) + expires_delta

    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}

    return jwt.encode(
        payload=to_encode,
        key=settings.token.private_key_path.read_text(),
        algorithm=settings.token.algorithm,
    )


def decode_token(token: str | bytes) -> dict[str, Any]:
    return jwt.decode(
        jwt=token,
        key=settings.token.public_key_path.read_text(),
        algorithms=[settings.token.algorithm],
    )
