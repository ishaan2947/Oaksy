"""Submit a call on a situation; returns the full reveal."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..deps import get_optional_user
from ..models import Pick, User

router = APIRouter(prefix="/api/picks", tags=["picks"])


@router.post("", response_model=schemas.RevealOut, status_code=201)
def submit_pick(
    payload: schemas.PickRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    situation = services.get_situation_cached(db, payload.situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")

    if not situation.option_text(payload.choice):
        raise HTTPException(400, "That option isn't available on this situation")

    if user is None and not payload.anon_id:
        raise HTTPException(400, "Provide anon_id when not logged in")

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
    try:
        # Insert directly; the unique constraint enforces one call per identity,
        # so we skip a pre-check query on the common (new-pick) path.
        db.commit()
    except IntegrityError:
        db.rollback()
        ident = (
            Pick.user_id == user.id if user else Pick.anon_id == payload.anon_id
        )
        existing = db.scalar(
            select(Pick).where(Pick.situation_id == situation.id, ident)
        )
        return services.build_reveal(db, situation, existing)

    services.invalidate_split(situation.id)  # so the submitter sees their own vote
    return services.build_reveal(db, situation, pick)
