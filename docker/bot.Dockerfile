# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETPLATFORM

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -q -y --no-install-recommends install \
    build-essential \
    cmake \
    pkg-config \
    libffi-dev \
    zlib1g-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libfreetype6-dev \
    libwebp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip,id=pip-${TARGETPLATFORM} \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


FROM python:${PYTHON_VERSION}-slim AS runtime

ARG UID=10001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get -q -y --no-install-recommends install \
    libtiff6 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libfreetype6 \
    libwebp7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY --from=builder /opt/venv /opt/venv

COPY --chown=appuser:appuser . .

USER appuser

CMD ["python", "main.py"]