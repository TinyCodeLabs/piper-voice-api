# syntax=docker/dockerfile:1


ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS base

LABEL org.opencontainers.image.source="https://github.com/TinyCodeLabs/piper-voice-api"
LABEL org.opencontainers.image.description="Python UNIX Socket wrapper for piper-tts"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---- user / group ----
ARG UID=10001
ARG GID=10001

RUN groupadd -g ${GID} appgroup \
 && useradd \
    --uid ${UID} \
    --gid ${GID} \
    --home /nonexistent \
    --shell /sbin/nologin \
    --no-create-home \
    appuser

# ---- directories that must be writable & shared ----
RUN mkdir -p /app/voices /app/out /app/run \
 && chown -R appuser:appgroup /app \
 && chown -R appuser:appgroup /app/run \
 && chmod 755 /app \
 && chmod 755 /app/run \
 && chmod 775 /app/voices /app/out

# ---- install deps ----
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# ---- app code ----
COPY --chown=appuser:appgroup . .

USER appuser

# optional but nice documentation
VOLUME ["/app/voices", "/app/out", "/app/run"]

CMD ["python", "src/main.py"]