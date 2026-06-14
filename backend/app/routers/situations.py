"""The Daily Call — fetch today's situation and its reveal."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..deps import get_optional_user
from ..models import Pick, Situation, User

router = APIRouter(prefix="/api/situations", tags=["situations"])


@router.get("/daily", response_model=schemas.SituationOut)
def daily_call(
    sport: str = Query(default="NFL"),
    db: Session = Depends(get_db),
):
    """Today's Daily Call for a sport. Answer fields are never included here."""
    situation = services.get_or_assign_daily(db, sport, date.today())
    if not situation:
        raise HTTPException(404, f"No situations available for {sport.upper()}")
    return services.situation_out(situation)


@router.get("/{situation_id}", response_model=schemas.SituationOut)
def get_situation(situation_id: str, db: Session = Depends(get_db)):
    situation = db.get(Situation, situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")
    return services.situation_out(situation)


@router.get("/{situation_id}/reveal", response_model=schemas.RevealOut)
def reveal(
    situation_id: str,
    anon_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """The full verdict + community split. Includes the viewer's result if they picked."""
    situation = db.get(Situation, situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")

    viewer_pick: Pick | None = None
    if user:
        viewer_pick = db.scalar(
            select(Pick).where(
                Pick.situation_id == situation_id, Pick.user_id == user.id
            )
        )
    elif anon_id:
        viewer_pick = db.scalar(
            select(Pick).where(
                Pick.situation_id == situation_id, Pick.anon_id == anon_id
            )
        )
    return services.build_reveal(db, situation, viewer_pick)
