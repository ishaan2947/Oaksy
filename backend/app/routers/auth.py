"""Email/password auth + optional Google sign-in."""
from __future__ import annotations

import logging
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..security import create_access_token, hash_password, verify_password

logger = logging.getLogger("oaksy.auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

_GOOGLE_TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"


@router.post("/signup", response_model=schemas.TokenOut, status_code=201)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.TokenOut(
        access_token=create_access_token(user.id), user=schemas.UserOut.model_validate(user)
    )


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return schemas.TokenOut(
        access_token=create_access_token(user.id), user=schemas.UserOut.model_validate(user)
    )


@router.get("/config", response_model=schemas.AuthConfigOut)
def auth_config():
    """Public client config so the frontend knows whether to show the Google
    button. The client ID is not a secret; the client secret is never used."""
    return schemas.AuthConfigOut(google_client_id=settings.google_client_id or None)


@router.post("/google", response_model=schemas.TokenOut)
def google_auth(payload: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    """Sign in with a Google ID token. We verify it with Google, then find or
    create the matching account and issue our own session token."""
    if not settings.google_client_id:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Google sign-in isn't configured")

    try:
        resp = httpx.get(_GOOGLE_TOKENINFO, params={"id_token": payload.credential}, timeout=10)
    except httpx.HTTPError as exc:
        logger.warning("Google tokeninfo unreachable: %s", exc)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Couldn't reach Google to verify sign-in")

    if resp.status_code != 200:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google sign-in")
    data = resp.json()

    if data.get("aud") != settings.google_client_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Google sign-in failed (wrong app)")
    if str(data.get("email_verified")).lower() != "true":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Your Google email isn't verified")
    email = (data.get("email") or "").lower()
    if not email:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Google didn't return an email")

    user = db.scalar(select(User).where(User.email == email))
    if not user:
        name = data.get("name") or data.get("given_name") or email.split("@")[0]
        user = User(
            email=email,
            display_name=name[:40],
            # Random unusable password — these accounts sign in via Google only.
            password_hash=hash_password(secrets.token_urlsafe(32)),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return schemas.TokenOut(
        access_token=create_access_token(user.id),
        user=schemas.UserOut.model_validate(user),
    )


@router.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(get_current_user)):
    return user
