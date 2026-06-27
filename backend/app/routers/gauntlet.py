"""The Gauntlet — endless, sudden-death survival mode.

Random real calls back-to-back; you keep going until you miss. Grading is
stateless (no Pick is written) so runs are fast, repeatable, and kept separate
from your official daily record.
"""
from __future__ import annotations

import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..models import Situation
from ..seed_data import MATCHUPS, WIN_PROBS

router = APIRouter(prefix="/api/gauntlet", tags=["gauntlet"])


@router.get("/next", response_model=schemas.SituationOut)
def next_call(
    seen: str = Query(default=""),
    sport: str = Query(default=""),
    db: Session = Depends(get_db),
):
    """A random blind situation, avoiding ones already seen this run."""
    seen_ids = {s for s in seen.split(",") if s}
    q = select(Situation.id)
    if sport:
        q = q.where(Situation.sport == sport.upper())
    ids = list(db.scalars(q).all())
    if not ids:
        raise HTTPException(404, "No situations available")
    pool = [i for i in ids if i not in seen_ids] or ids  # reshuffle once exhausted
    situation = services.get_situation_cached(db, random.choice(pool))
    return services.situation_out(situation)


@router.post("/grade", response_model=schemas.GauntletResultOut)
def grade(payload: schemas.GauntletGradeRequest, db: Session = Depends(get_db)):
    """Grade a gauntlet call without recording a Pick."""
    situation = services.get_situation_cached(db, payload.situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")
    if not situation.option_text(payload.choice):
        raise HTTPException(400, "That option isn't available on this situation")

    return schemas.GauntletResultOut(
        situation_id=situation.id,
        your_choice=payload.choice,
        correct=payload.choice == situation.best_call,
        best_call=situation.best_call,
        best_call_label=situation.option_text(situation.best_call) or "",
        actual_call=situation.actual_call,
        actual_call_label=situation.option_text(situation.actual_call) or "",
        win_probabilities=WIN_PROBS.get(situation.game_id),
        ai_verdict=situation.ai_verdict or situation.analytics_verdict,
        outcome=situation.outcome,
        matchup=MATCHUPS.get(situation.game_id),
    )
