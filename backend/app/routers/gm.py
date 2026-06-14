"""82-0 GM Mode — spin a player pool, build an all-era five, get a Claude verdict."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import ai, schemas, services
from ..database import get_db
from ..deps import get_optional_user
from ..models import GMSpin, GMTeam, User
from ..players import BY_ID, PLAYERS

router = APIRouter(prefix="/api/gm", tags=["gm"])


def _player_out(p: dict) -> schemas.PlayerOut:
    return schemas.PlayerOut(**{k: p[k] for k in ("id", "name", "pos", "era", "cost", "tag")})


def _share_line(team: list[dict], score: int) -> str:
    names = ", ".join(p["name"].split()[-1] for p in team)
    return f"My 82-0 team: {names}. Claude gave it a {score}/100. Can you beat it?"


@router.get("/players", response_model=list[schemas.PlayerOut])
def all_players():
    return [_player_out(p) for p in PLAYERS]


@router.post("/spin", response_model=schemas.SpinOut)
def spin(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    pool = services.gm_spin_pool()
    record = GMSpin(
        user_id=user.id if user else None,
        player_ids=[p["id"] for p in pool],
        cap=services.GM_CAP,
        roster_size=services.GM_ROSTER_SIZE,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.SpinOut(
        spin_id=record.id,
        cap=services.GM_CAP,
        roster_size=services.GM_ROSTER_SIZE,
        rules=services.GM_RULES,
        pool=[_player_out(p) for p in pool],
    )


@router.post("/submit", response_model=schemas.GMResultOut)
def submit(
    payload: schemas.GMSubmitRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    spin = db.get(GMSpin, payload.spin_id)
    if not spin:
        raise HTTPException(404, "Spin not found — spin the wheel again.")

    ok, err = services.validate_gm_roster(spin.player_ids, payload.player_ids)
    if not ok:
        raise HTTPException(400, err)

    team = [BY_ID[pid] for pid in payload.player_ids]
    total = sum(p["cost"] for p in team)
    score, verdict = ai.generate_gm_verdict(team, total, spin.cap)

    db.add(
        GMTeam(
            spin_id=spin.id,
            user_id=user.id if user else None,
            anon_id=None if user else payload.anon_id,
            player_ids=payload.player_ids,
            total_cost=total,
            score=score,
            verdict=verdict,
        )
    )
    db.commit()

    return schemas.GMResultOut(
        team=[_player_out(p) for p in team],
        total_cost=total,
        cap=spin.cap,
        score=score,
        verdict=verdict,
        share_line=_share_line(team, score),
    )
