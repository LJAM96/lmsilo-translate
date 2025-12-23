# Translate - Merged Docker Image  
# Contains: Frontend (nginx) + Backend (uvicorn with FastAPI) + Worker (celery)
# Multi-stage build with React frontend

# ============================================
# Stage 1: Build React Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN npm run build

# ============================================
# Stage 2: Python Backend + Nginx
# ============================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    nginx \
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

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create nginx config
RUN cat > /etc/nginx/sites-available/default <<'NGINX'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    
    client_max_body_size 500M;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
NGINX

# Create supervisord config
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/nginx.log
stderr_logfile=/var/log/supervisor/nginx_error.log

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

# Expose ports
EXPOSE 80 8000

# Default command runs supervisord (nginx + uvicorn)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
