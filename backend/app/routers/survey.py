"""Temporary in-app user-study survey.

A richer feedback form than the quick poll: scale questions + open-ended ones.
Stores raw answers; the summary averages any numeric answers and returns recent
responses for the owner to read. Remove this router + the Survey tab when the
study is done.
"""
from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import SurveyResponse

router = APIRouter(prefix="/api/survey", tags=["survey"])


@router.post("", status_code=201)
def submit(payload: schemas.SurveyRequest, db: Session = Depends(get_db)):
    db.add(SurveyResponse(anon_id=payload.anon_id, answers=payload.answers))
    db.commit()
    return {"ok": True}


@router.get("/summary", response_model=schemas.SurveySummary)
def summary(db: Session = Depends(get_db)):
    rows = db.scalars(select(SurveyResponse).order_by(SurveyResponse.created_at.desc())).all()

    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        for key, val in (r.answers or {}).items():
            if isinstance(val, bool):
                continue
            if isinstance(val, (int, float)):
                sums[key] += val
                counts[key] += 1

    averages = {k: round(sums[k] / counts[k], 2) for k in sums if counts[k]}
    responses = [
        {"answers": r.answers, "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in rows[:50]
    ]
    return schemas.SurveySummary(count=len(rows), averages=averages, responses=responses)
