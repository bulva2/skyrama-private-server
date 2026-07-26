FROM python:3.13-slim

# PYTHONUNBUFFERED so logs reach `docker compose logs` immediately instead of
# sitting in a pipe buffer. PYTHONDONTWRITEBYTECODE keeps the layer clean.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# No build-essential / libpq-dev needed: psycopg[binary] and bcrypt both ship
# manylinux wheels, so nothing is compiled from source. `curl` is only here for
# the container healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Only the application code is copied. assets/, data/, templates/, stub/ and
# config.cfg are bind-mounted read-only by docker-compose.yml so that game data
# and config can be changed without rebuilding the image.
COPY server.py state.py bundle.py setup_database.py ./
COPY src/ ./src/
COPY routers/ ./routers/
COPY commands/ ./commands/

# Run unprivileged. The server never writes to disk (all state lives in
# Postgres), so no writable paths are required.
RUN useradd --create-home --uid 10001 skyrama && chown -R skyrama:skyrama /app
USER skyrama

EXPOSE 3800

HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=5 \
    CMD curl -fsS http://127.0.0.1:3800/crossdomain.xml || exit 1

CMD ["sh", "-c", "exec uvicorn server:app \
    --host 0.0.0.0 \
    --port 3800 \
    --workers 1 \
    --proxy-headers \
    --forwarded-allow-ips='*'"]
