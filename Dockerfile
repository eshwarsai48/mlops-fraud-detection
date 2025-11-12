# ---------- Base with system deps ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \          # Avoid creating .pyc files
    PYTHONUNBUFFERED=1 \                 # Ensure logs show up immediately
    PIP_NO_CACHE_DIR=1 \                 # Avoid pip cache bloat
    PIP_DISABLE_PIP_VERSION_CHECK=1      # Prevent version check messages

# Install essential build tools (only once in base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*       # Keep image size minimal

WORKDIR /app

# ---------- Builder: resolve and cache Python wheels ----------
FROM base AS builder
COPY requirements.txt /app/requirements.txt
RUN pip wheel --wheel-dir /app/.wheels -r /app/requirements.txt  # Pre-build dependencies into wheels for caching

# ---------- Runtime: minimal image ----------
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -u 10001 -m appuser
WORKDIR /app

# Copy pre-built dependency wheels from builder stage
COPY --from=builder /app/.wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels  # Install all deps then delete wheels to slim down

# ---------- COPY APPLICATION CODE ----------
# Only copy code and configs — NOT the model folder (model will be fetched at runtime)
COPY app /app/app                          # Application source code
COPY ML /app/ML                            # Any helper scripts or logic
COPY gunicorn_conf.py /app/gunicorn_conf.py


# Create a directory where model will be downloaded at runtime
RUN mkdir -p /model && chown -R appuser:appuser /model

# Fix ownership of app directory for non-root execution
RUN chown -R appuser:appuser /app && chmod -R 755 /app

# ---------- Environment configuration ----------
# FastAPI code now expects model to be under /model/pipeline.joblib
ENV MODEL_DIR=/model \
    MODEL_FILE=/model/pipeline.joblib \
    APP_VERSION=1.0.0 \
    PYTHONPATH=/app

# Optional: explicitly define default ports for better clarity
EXPOSE 8000

# ---------- Healthcheck ----------
# Calls the /healthcheck endpoint exposed by FastAPI (important for AKS readiness)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/healthcheck || exit 1

# ---------- Run as non-root user ----------
USER appuser

# ---------- Start the FastAPI app ----------
# Using Gunicorn with Uvicorn workers for production-grade async performance
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app.main:app"]
