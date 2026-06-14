"""Oaksy API — FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import settings
from .routers import auth, debates, picks, situations, users
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


@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "version": __version__,
        "ai_enabled": bool(settings.anthropic_api_key),
        "ai_model": settings.ai_model,
    }
