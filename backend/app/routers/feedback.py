"""In-app feedback poll — quick 'would you play this daily?' signal from testers."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..deps import get_optional_user
from ..models import FeedbackEntry, User

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=schemas.FeedbackSummary, status_code=201)
def submit(
    payload: schemas.FeedbackRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    db.add(
        FeedbackEntry(
            rating=payload.rating,
            comment=(payload.comment or "").strip() or None,
            user_id=user.id if user else None,
            anon_id=None if user else payload.anon_id,
            source=(payload.source or "").strip() or None,
        )
    )
    db.commit()
    return _summary(db)


@router.get("/summary", response_model=schemas.FeedbackSummary)
def summary(db: Session = Depends(get_db)):
    return _summary(db)


def _summary(db: Session) -> schemas.FeedbackSummary:
    rows = db.execute(
        select(FeedbackEntry.rating, func.count(FeedbackEntry.id)).group_by(
            FeedbackEntry.rating
        )
    ).all()
    counts = {r: n for r, n in rows}
    yes, maybe, no = counts.get("yes", 0), counts.get("maybe", 0), counts.get("no", 0)
    return schemas.FeedbackSummary(yes=yes, maybe=maybe, no=no, total=yes + maybe + no)
