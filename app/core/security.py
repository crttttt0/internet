from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Пароли

pwd_context = CryptContext(["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Преобразует пароль в хеш с использованием bcrypt"""

    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли введённый пароль сохранtнному хешу"""

    return pwd_context.verify(plain_password, hashed_password)


# JWT


def create_access_token(data: dict) -> str:
    """Создает access JWT"""

    payload = data.copy()
    payload.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
    )

    return jwt.encode(
        payload, settings.jwt.SECRET_KEY.get_secret_value(), settings.jwt.ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    """Создает refresh JWT"""

    payload = data.copy()
    payload.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.jwt.REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh",
        }
    )

    return jwt.encode(
        payload, settings.jwt.SECRET_KEY.get_secret_value(), settings.jwt.ALGORITHM
    )


def decode_token(token: str) -> dict:
    """Декодирует JWT"""

    return jwt.decode(
        token, settings.jwt.SECRET_KEY.get_secret_value(), [settings.jwt.ALGORITHM]
    )
