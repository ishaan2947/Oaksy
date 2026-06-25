# Single-image deploy: builds the web app and serves it from the FastAPI backend,
# so the API and the site share one origin (relative /api calls just work).

# --- Stage 1: build the web app ---
FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend runtime ---
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ ./
# Drop the built site where the app serves static files from.
COPY --from=web /web/dist ./static
ENV STATIC_DIR=/app/static

EXPOSE 8000
# Bind to $PORT if provided (Render/Heroku), else 8000. WEB_CONCURRENCY controls
# worker processes — default 2; bump it on a larger instance for more headroom.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}"]
