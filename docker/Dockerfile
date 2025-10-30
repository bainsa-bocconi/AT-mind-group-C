ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Unprivileged user
ARG UID=10001
RUN useradd -r -u "${UID}" -g root -d /nonexistent -s /usr/sbin/nologin appuser

# Modern pip for PEP 517/518 builds
RUN python -m pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
COPY at_mind ./at_mind
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --no-cache-dir .

COPY . .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "at_mind.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
