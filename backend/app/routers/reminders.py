"""Streak reminder emails.

A daily batch (triggered by an external cron, e.g. a scheduled GitHub Action,
since Render free instances sleep) emails opted-in users whose streak is alive
but at risk — i.e. they played yesterday but not yet today. Config-gated: does
nothing until RESEND_API_KEY + REMINDERS_TOKEN are set.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..email import send_email
from ..models import Pick, User
from .users import _streaks

logger = logging.getLogger("oaksy.reminders")
router = APIRouter(prefix="/api/reminders", tags=["reminders"])


def _sig(user_id: str) -> str:
    return hmac.new(
        settings.secret_key.encode(), user_id.encode(), hashlib.sha256
    ).hexdigest()[:32]


def unsubscribe_url(user_id: str) -> str:
    return f"{settings.app_base_url}/api/reminders/unsubscribe?u={user_id}&t={_sig(user_id)}"


def _email_html(name: str, streak: int, user_id: str) -> str:
    streak_line = (
        f"Your <b>{streak}-day streak</b> is on the line."
        if streak > 1
        else "Keep your streak alive."
    )
    return f"""
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:520px;margin:0 auto;color:#1d1d1f">
      <div style="font-size:22px;font-weight:800">Oaksy<span style="color:#ff5a1f">.</span></div>
      <h1 style="font-size:24px;margin:18px 0 8px">Don't break the chain, {name}. ⚡</h1>
      <p style="font-size:16px;line-height:1.5;color:#444">
        {streak_line} Today's Daily Call is live — make the coach's call in 30 seconds
        before the day ends.
      </p>
      <p style="margin:24px 0">
        <a href="{settings.app_base_url}"
           style="background:#ff5a1f;color:#1a0c04;font-weight:800;text-decoration:none;
                  padding:13px 26px;border-radius:999px;font-size:16px">
          Make today's call →
        </a>
      </p>
      <p style="font-size:12px;color:#999;margin-top:28px">
        You're getting this because you have an Oaksy account.
        <a href="{unsubscribe_url(user_id)}" style="color:#999">Turn off reminders</a>.
      </p>
    </div>
    """


@router.post("/run")
def run_reminders(
    x_reminders_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Send today's streak-at-risk emails. Protected by a shared token."""
    if not settings.reminders_token:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Reminders not configured")
    if not x_reminders_token or not hmac.compare_digest(
        x_reminders_token, settings.reminders_token
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad reminders token")
    if not settings.resend_api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Email isn't configured")

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    users = db.scalars(select(User).where(User.reminders.isnot(False))).all()
    eligible = sent = 0
    for u in users:
        dates = [
            dt.date()
            for dt in db.scalars(
                select(Pick.created_at).where(Pick.user_id == u.id)
            ).all()
            if dt
        ]
        if not dates or max(dates) != yesterday:
            continue  # never played, already played today, or streak already dead
        eligible += 1
        streak, _ = _streaks(dates, today=today)
        subject = (
            f"⚡ Your {streak}-day Oaksy streak ends tonight"
            if streak > 1
            else "⚡ Keep your Oaksy streak alive"
        )
        if send_email(u.email, subject, _email_html(u.display_name, streak, u.id)):
            sent += 1

    logger.info("Reminders run: %d eligible, %d sent", eligible, sent)
    return {"eligible": eligible, "sent": sent}


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(u: str = Query(...), t: str = Query(...), db: Session = Depends(get_db)):
    user = db.get(User, u)
    ok = user is not None and hmac.compare_digest(t, _sig(u))
    if ok:
        user.reminders = False
        db.commit()
        body = "You're unsubscribed from Oaksy streak reminders. You can re-enable them anytime in your Coach Score."
    else:
        body = "That unsubscribe link isn't valid."
    return HTMLResponse(
        f"""<html><body style="font-family:-apple-system,sans-serif;text-align:center;padding:60px 20px;color:#1d1d1f">
        <div style="font-size:24px;font-weight:800">Oaksy<span style="color:#ff5a1f">.</span></div>
        <p style="font-size:17px;max-width:420px;margin:18px auto;color:#444">{body}</p>
        <a href="{settings.app_base_url}" style="color:#ff5a1f;font-weight:700">Back to Oaksy →</a>
        </body></html>""",
        status_code=200 if ok else 400,
    )
