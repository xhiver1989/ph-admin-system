from datetime import datetime, timedelta
from typing import Any, Dict, List

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, roles: List[str]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


class TokenError(Exception):
    pass


def validate_token_type(payload: Dict[str, Any], token_type: str) -> None:
    if payload.get("type") != token_type:
        raise TokenError("Invalid token type")


def get_subject(payload: Dict[str, Any]) -> str:
    subject = payload.get("sub")
    if not subject:
        raise TokenError("Missing subject")
    return subject


def ensure_jwt(token: str) -> Dict[str, Any]:
    try:
        return decode_token(token)
    except JWTError as exc:
        raise TokenError("Invalid token") from exc
