# ---------- Base with system deps ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Optional: build tools for some wheels (scikit-learn, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/* # Delete cached packages for lean images

WORKDIR /app

# ---------- Builder: resolve and cache wheels ----------
FROM base AS builder
COPY requirements.txt /app/requirements.txt
RUN pip wheel --wheel-dir /app/.wheels -r /app/requirements.txt

# ---------- Runtime: minimal image ----------
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# don't create PYC files and write the STDERR/STDOUT without bufferring since we want realtime logs

# Create unprivileged user (since running as root in a container is bad-practice for production)
RUN useradd -u 10001 -m appuser
WORKDIR /app

# Install deps from cached wheels
COPY --from=builder /app/.wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels


# Copy app code and model assets
COPY app /app/app
COPY ML /app/ML
COPY model /app/model
COPY gunicorn_conf.py /app/gunicorn_conf.py

# Let the app know where the model artifact is (adjust if needed)
ENV MODEL_PATH=/app/model/pipeline.joblib

# Healthcheck hits /healthcheck (The health check route we defined in our FASTAPI app)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/healthcheck || exit 1

USER appuser
EXPOSE 8000

# Default: production server with Gunicorn+Uvicorn workers
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app.main:app"]
