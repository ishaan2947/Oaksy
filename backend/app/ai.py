"""AI verdict layer.

Generates a punchy, 2-3 sentence verdict on a coaching decision using Claude
(model from settings, default claude-sonnet-4-6 as specified in the product spec).

If no ANTHROPIC_API_KEY is configured — or the API call fails — we fall back to
the situation's stored analytics verdict so the app always returns something
useful. This keeps the whole product runnable before a key is wired up.
"""
from __future__ import annotations

import logging
import re

from .config import settings
from .players import SHOOTERS

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


# ---------------------------------------------------------------------------
# 82-0 GM Mode team verdict
# ---------------------------------------------------------------------------
_GM_SYSTEM = (
    "You are Claude, the GM-Mode judge for Oaksy. A fan has assembled an all-era "
    "NBA starting five and claims it would go 82-0. Rate the team out of 100 and "
    "explain, like a sharp basketball mind, whether it could really go undefeated — "
    "weigh shot creation, spacing, defense, rim protection, playmaking, and how the "
    "eras fit together. Be opinionated and fun, not an analyst. Respond in EXACTLY "
    "this format:\nSCORE: <integer 0-100>\n<2-3 punchy sentences>"
)


def _gm_heuristic(players: list[dict], total_cost: int) -> tuple[int, str]:
    positions = {p["pos"] for p in players}
    eras = {p["era"] for p in players}
    has_shooter = any(p["id"] in SHOOTERS for p in players)
    names = ", ".join(p["name"].split()[-1] for p in players)

    score = 24 + total_cost * 1.4  # star power (capped spend → bounded)
    if "C" in positions:
        score += 5  # rim protection
    if "G" in positions:
        score += 4  # primary creation
    if len(positions) == 3:
        score += 5  # true positional balance
    if has_shooter:
        score += 7  # floor spacing matters most
    if len(eras) >= 3:
        score += 3  # versatility across styles
    score = max(40, min(99, round(score)))

    spacing = "with real floor spacing" if has_shooter else "but it's cramped for spacing"
    balance = "a balanced lineup" if len(positions) == 3 else "a lopsided rotation"
    verdict = (
        f"{names} is {balance} {spacing}. The star power is real, but undefeated is a "
        f"different animal — one cold night and the streak's gone. Strong build, not flawless."
    )
    return score, verdict


def generate_gm_verdict(players: list[dict], total_cost: int, cap: int) -> tuple[int, str]:
    """Return (score 0-100, verdict). Falls back to a heuristic without a key."""
    if not settings.anthropic_api_key:
        return _gm_heuristic(players, total_cost)

    roster = "\n".join(
        f"- {p['name']} ({p['pos']}, {p['era']}, cost {p['cost']})" for p in players
    )
    user = (
        f"Salary cap: {cap}. Team cost: {total_cost}.\nStarting five:\n{roster}\n\n"
        "Could this team go 82-0?"
    )
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.ai_model,
            max_tokens=350,
            system=_GM_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        m = re.search(r"SCORE:\s*(\d{1,3})", text, re.IGNORECASE)
        if not m:
            return _gm_heuristic(players, total_cost)
        score = max(0, min(100, int(m.group(1))))
        verdict = text[m.end():].strip().lstrip(".:\n ").strip() or _gm_heuristic(
            players, total_cost
        )[1]
        return score, verdict
    except Exception as exc:
        logger.warning("GM verdict generation failed, using heuristic: %s", exc)
        return _gm_heuristic(players, total_cost)
