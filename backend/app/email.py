"""Transactional email via Resend. No-ops cleanly when unconfigured."""
from __future__ import annotations

import logging

import httpx

from .config import settings

logger = logging.getLogger("oaksy.email")

_RESEND_URL = "https://api.resend.com/emails"


def send_email(to: str, subject: str, html: str) -> bool:
    """Send one email. Returns True on success, False (logged) on any failure or
    when no RESEND_API_KEY is configured — so callers never crash on email."""
    if not settings.resend_api_key:
        return False
    try:
        resp = httpx.post(
            _RESEND_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={"from": settings.reminder_from, "to": [to], "subject": subject, "html": html},
            timeout=10,
        )
        if resp.status_code >= 300:
            logger.warning("Resend send failed (%s): %s", resp.status_code, resp.text[:300])
            return False
        return True
    except httpx.HTTPError as exc:
        logger.warning("Resend request error: %s", exc)
        return False
