"""Submit a call on a situation; returns the full reveal."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..deps import get_optional_user
from ..models import Pick, Situation, User

router = APIRouter(prefix="/api/picks", tags=["picks"])


@router.post("", response_model=schemas.RevealOut, status_code=201)
def submit_pick(
    payload: schemas.PickRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    situation = db.get(Situation, payload.situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")

    if payload.choice == "c" and not situation.option_c:
        raise HTTPException(400, "This situation has no third option")

    if user is None and not payload.anon_id:
        raise HTTPException(400, "Provide anon_id when not logged in")

    # One call per situation per identity — return the existing reveal if re-submitting.
    if user:
        existing = db.scalar(
            select(Pick).where(
                Pick.situation_id == situation.id, Pick.user_id == user.id
            )
        )
    else:
        existing = db.scalar(
            select(Pick).where(
                Pick.situation_id == situation.id, Pick.anon_id == payload.anon_id
            )
        )
    if existing:
        return services.build_reveal(db, situation, existing)

    correct = payload.choice == situation.best_call
    beat_coach = correct and situation.actual_call != situation.best_call

    pick = Pick(
        situation_id=situation.id,
        user_id=user.id if user else None,
        anon_id=None if user else payload.anon_id,
        choice=payload.choice,
        reasoning=(payload.reasoning or "").strip() or None,
        correct=correct,
        beat_coach=beat_coach,
    )
    db.add(pick)
    db.commit()
    db.refresh(pick)

    return services.build_reveal(db, situation, pick)
