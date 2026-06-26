"""Challenge a friend — head-to-head on a Daily Call or an 82-0 GM spin."""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..models import Challenge, GMSpin, Situation
from ..players import BY_ID

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


def _new_id() -> str:
    return secrets.token_urlsafe(6)


@router.post("", response_model=schemas.ChallengeCreated, status_code=201)
def create_challenge(payload: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    name = (payload.challenger_name or "A challenger").strip()[:40] or "A challenger"

    if payload.kind == "daily":
        if not payload.situation_id or not payload.choice:
            raise HTTPException(400, "Daily challenge needs a situation and a choice")
        situation = db.get(Situation, payload.situation_id)
        if not situation:
            raise HTTPException(404, "Situation not found")
        correct = payload.choice == situation.best_call
        ch = Challenge(
            id=_new_id(),
            kind="daily",
            challenger_name=name,
            situation_id=situation.id,
            choice=payload.choice,
            confidence=payload.confidence,
            correct=correct,
            beat_coach=correct and situation.actual_call != situation.best_call,
        )
    else:  # gm
        if not payload.spin_id or not payload.player_ids or payload.score is None:
            raise HTTPException(400, "GM challenge needs a spin, a roster, and a score")
        if not db.get(GMSpin, payload.spin_id):
            raise HTTPException(404, "Spin not found")
        ch = Challenge(
            id=_new_id(),
            kind="gm",
            challenger_name=name,
            spin_id=payload.spin_id,
            player_ids=payload.player_ids,
            score=payload.score,
        )

    db.add(ch)
    db.commit()
    return schemas.ChallengeCreated(id=ch.id)


@router.get("/{challenge_id}", response_model=schemas.ChallengeOut)
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    ch = db.get(Challenge, challenge_id)
    if not ch:
        raise HTTPException(404, "Challenge not found")

    out = schemas.ChallengeOut(id=ch.id, kind=ch.kind, challenger_name=ch.challenger_name)

    if ch.kind == "daily":
        situation = services.get_situation_cached(db, ch.situation_id)
        if not situation:
            raise HTTPException(404, "Situation not found")
        # The friend gets the blind situation + the challenger's CHOICE (not its
        # correctness) — they figure out who was right after their own pick.
        out.situation = services.situation_out(situation)
        out.challenger_choice = ch.choice
        out.challenger_confidence = ch.confidence
    else:  # gm — reuse the same spin pool so it's a fair head-to-head
        spin = db.get(GMSpin, ch.spin_id)
        if not spin:
            raise HTTPException(404, "Spin not found")
        pool = [BY_ID[pid] for pid in spin.player_ids if pid in BY_ID]
        out.spin = schemas.SpinOut(
            spin_id=spin.id,
            cap=spin.cap,
            roster_size=spin.roster_size,
            rules=services.GM_RULES,
            pool=[
                schemas.PlayerOut(**{k: p[k] for k in ("id", "name", "pos", "era", "cost", "tag")})
                for p in pool
            ],
        )
        out.challenger_score = ch.score

    return out
