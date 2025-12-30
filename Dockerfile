# Translate - Backend Only
# API server + Celery worker for AI translation
# Frontend now served by Portal

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FastAPI stack and additional dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    python-multipart \
    celery[redis] \
    redis \
    sqlalchemy[asyncio] \
    asyncpg

# Pre-download NLLB model during build (for airgapped environments)
COPY backend/download_model.py .
RUN python download_model.py || echo "Model download skipped - will download at runtime"

# Copy backend code
COPY backend/ ./backend/

# Create supervisord config
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:uvicorn]
command=python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/uvicorn.log
stderr_logfile=/var/log/supervisor/uvicorn_error.log

[program:celery]
command=python -m celery -A backend.workers.celery_app worker -Q translate -c 1 --loglevel=info
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/celery.log
stderr_logfile=/var/log/supervisor/celery_error.log
EOF

# Create directories
RUN mkdir -p /app/models /app/uploads /tmp/translation_checkpoints

# Expose API port only
EXPOSE 8000

# Run supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
