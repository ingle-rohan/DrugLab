# =========================================================
# DrugLab Production Multi-Stage Dockerfile
# Stage 1: Build React TypeScript Frontend SPA
# Stage 2: Serve Unified FastAPI + Static Assets on Python 3.11
# =========================================================

# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Backend & Static Serving
FROM python:3.11-slim AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install system runtime libraries for PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY app/ ./app/

# Copy built React frontend distribution from Stage 1
COPY --from=frontend-builder /build/dist ./frontend/dist

# Expose standard container port
EXPOSE 8000

# Start FastAPI application bound to cloud provider PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
