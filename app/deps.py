from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TokenError, ensure_jwt, get_subject, validate_token_type
from app.db import models
from app.db.session import SessionLocal

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    token = credentials.credentials
    try:
        payload = ensure_jwt(token)
        validate_token_type(payload, "access")
        subject = get_subject(payload)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.query(models.User).filter_by(id=int(subject)).one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def require_roles(*roles: str) -> Callable[[models.User], models.User]:
    required = set(roles)

    def dependency(user: models.User = Depends(get_current_user)) -> models.User:
        user_roles: List[str] = [role.name for role in user.roles]
        if not required.intersection(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency
