# =========================================================================
# NTRO Cyber Forensics Platform - Multi-Stage Production Dockerfile
# Problem Statement: SIH26148 | Authorized DFIR & Forensic DSL Platform
# =========================================================================

# Stage 1: Build Frontend Assets with Node.js
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend & Standalone Web Server
FROM python:3.11-slim AS production

LABEL maintainer="NTRO Cyber Forensics Team"
LABEL description="Cryptographically Governed Forensic Platform & DSL Engine (SIH26148)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    FORENSIC_DB_PATH=/app/backend/app/forensic_platform.db

WORKDIR /app

# Install system dependencies (build essentials for psutil / reportlab / sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code & forensic DSL engine
COPY backend/ ./backend/
COPY forensic_dsl/ ./forensic_dsl/
COPY sample_data/ ./sample_data/

# Copy built frontend assets from stage 1 into backend's dist directory
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create runtime directories for evidence vault, reports, and sample data
RUN mkdir -p /app/backend/app/reports_vault \
             /app/backend/app/evidence_vault \
             /app/sample_data

# Run database initialization and pre-seeding
RUN python -m backend.app.database

# Expose port (default 8000 or dynamic $PORT from cloud providers)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn in production mode
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
