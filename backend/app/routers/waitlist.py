"""Waitlist signups for the landing page (pre-launch / mobile beta)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import WaitlistEntry

router = APIRouter(prefix="/api/waitlist", tags=["waitlist"])


def _count(db: Session) -> int:
    return db.scalar(select(func.count(WaitlistEntry.id))) or 0


@router.post("", response_model=schemas.WaitlistOut, status_code=201)
def join(payload: schemas.WaitlistRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    existing = db.scalar(select(WaitlistEntry).where(WaitlistEntry.email == email))
    if existing:
        return schemas.WaitlistOut(ok=True, already=True, count=_count(db))

    db.add(WaitlistEntry(email=email, source=(payload.source or "").strip() or None))
    db.commit()
    return schemas.WaitlistOut(ok=True, already=False, count=_count(db))


@router.get("/count", response_model=schemas.WaitlistCount)
def count(db: Session = Depends(get_db)):
    return schemas.WaitlistCount(count=_count(db))
