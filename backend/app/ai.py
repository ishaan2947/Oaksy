"""AI verdict layer.

Generates a punchy, 2-3 sentence verdict on a coaching decision using Claude
(model from settings, default claude-sonnet-4-6 as specified in the product spec).

If no ANTHROPIC_API_KEY is configured — or the API call fails — we fall back to
the situation's stored analytics verdict so the app always returns something
useful. This keeps the whole product runnable before a key is wired up.
"""
from __future__ import annotations

import logging

from .config import settings

logger = logging.getLogger("oaksy.ai")

_SYSTEM = (
    "You are the analytics voice of Oaksy, a sports app where fans out-coach real "
    "coaches. Given a real game decision, explain in 2-3 punchy sentences whether "
    "the data supported or contradicted the coach's call. Write for a passionate "
    "sports fan, not an analyst: confident, vivid, no hedging, no jargon dumps, no "
    "preamble. Never start with 'Here is' or 'Based on'. Do not use markdown."
)


def _prompt(
    *,
    situation: str,
    actual_call: str,
    best_call: str,
    outcome: str,
    analytics: str,
) -> str:
    return (
        f"Situation: {situation}\n"
        f"What the coach actually did: {actual_call}\n"
        f"What the data favored: {best_call}\n"
        f"What happened: {outcome}\n"
        f"Analytics note: {analytics}\n\n"
        "Give the verdict."
    )


def generate_verdict(
    *,
    situation: str,
    actual_call: str,
    best_call: str,
    outcome: str,
    analytics: str,
) -> str:
    """Return a fan-facing verdict. Falls back to `analytics` when AI is unavailable."""
    if not settings.anthropic_api_key:
        return analytics

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.ai_model,
            max_tokens=300,
            system=_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": _prompt(
                        situation=situation,
                        actual_call=actual_call,
                        best_call=best_call,
                        outcome=outcome,
                        analytics=analytics,
                    ),
                }
            ],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or analytics
    except Exception as exc:  # network, auth, rate limit — degrade gracefully
        logger.warning("AI verdict generation failed, using analytics fallback: %s", exc)
        return analytics
