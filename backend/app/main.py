"""Oaksy API — FastAPI application entrypoint."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import settings
from .routers import (
    auth,
    challenges,
    debates,
    feedback,
    gm,
    picks,
    reminders,
    scores,
    situations,
    users,
    waitlist,
)
from .seed import create_tables, seed_situations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oaksy")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure schema exists and the app has content on first boot.
    create_tables()
    try:
        added = seed_situations()
        if added:
            logger.info("Seeded %d situation(s) on startup.", added)
    except Exception as exc:  # never block startup on seeding
        logger.warning("Startup seeding skipped: %s", exc)
    yield


app = FastAPI(title="Oaksy API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(situations.router)
app.include_router(picks.router)
app.include_router(users.router)
app.include_router(debates.router)
app.include_router(gm.router)
app.include_router(waitlist.router)
app.include_router(feedback.router)
app.include_router(scores.router)
app.include_router(challenges.router)
app.include_router(reminders.router)


@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "version": __version__,
        "ai_enabled": bool(settings.anthropic_api_key),
        "ai_model": settings.ai_model,
    }


# Serve the built web app from the same origin as the API (single-service deploy).
# In production we copy frontend/dist into the image and set STATIC_DIR; in local
# dev this is skipped and you use the Vite dev server instead. Mounted LAST so all
# /api routes and /docs take precedence.
_static_dir = os.environ.get("STATIC_DIR") or str(
    Path(__file__).resolve().parents[2] / "frontend" / "dist"
)
if Path(_static_dir).is_dir():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
    logger.info("Serving web app from %s", _static_dir)
