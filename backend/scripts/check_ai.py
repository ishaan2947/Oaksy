"""Verify the Claude AI verdict path end-to-end.

The AI integration is already wired (app/ai.py): when ANTHROPIC_API_KEY is set,
verdicts come from Claude; when it isn't, the app falls back to the stored
analytics note. This script confirms which path is active and, if a key is set,
makes one real call so you know the key + model work before relying on them.

Usage (from the backend/ directory):
    python scripts/check_ai.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402


def main() -> int:
    if not settings.anthropic_api_key:
        print("No ANTHROPIC_API_KEY set.")
        print("   Verdicts currently use the built-in fallback (the stored analytics note).")
        print("   To enable real Claude verdicts, add to backend/.env:")
        print("       ANTHROPIC_API_KEY=sk-ant-...")
        print(f"       AI_MODEL={settings.ai_model}   # optional")
        return 0

    print(f"Key found. Testing model '{settings.ai_model}' with one live call...")
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.ai_model,
            max_tokens=120,
            system="You are the analytics voice of Oaksy. Be punchy, no preamble.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Situation: 4th and 2 at midfield, up 3, two minutes left. "
                        "Coach punted; the data favored going for it. Give the verdict."
                    ),
                }
            ],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        print("\n[OK] Claude responded -- the AI verdict path is live.\n")
        print("   " + text.replace("\n", "\n   "))
        return 0
    except Exception as exc:  # auth, model, network
        print(f"\n[FAILED] Claude call failed: {exc}")
        print("   Check the key, the model id (AI_MODEL), and network access.")
        print("   The app still runs — it falls back to the analytics verdict.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
