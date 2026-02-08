from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    ensure_jwt,
    get_subject,
    validate_token_type,
    verify_password,
)
from app.db import models
from app.db.init_db import init_db
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.deps import get_current_user, get_db
from app.schemas import LoginRequest, RefreshRequest, TokenResponse, UserProfile

app = FastAPI(title="ph-admin-system")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(models.User).filter_by(email=payload.email).one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    roles = [role.name for role in user.roles]
    access_token = create_access_token(str(user.id), roles)
    refresh_token = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        decoded = ensure_jwt(payload.refresh_token)
        validate_token_type(decoded, "refresh")
        subject = get_subject(decoded)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.query(models.User).filter_by(id=int(subject)).one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    roles = [role.name for role in user.roles]
    access_token = create_access_token(str(user.id), roles)
    refresh_token = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.get("/me", response_model=UserProfile)
def me(current_user: models.User = Depends(get_current_user)) -> UserProfile:
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        roles=[role.name for role in current_user.roles],
    )
