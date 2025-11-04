#!/usr/bin/env bash
set -euo pipefail
# for older docker instances
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
  $DOCKER_COMPOSE -f docker/docker-compose.yml --profile gpu up -d
elif command -v docker-compose &>/dev/null; then
  $DOCKER_COMPOSE -f docker/docker-compose.yml --profile gpu up -d
else
  echo "Docker Compose not found." >&2
  exit 1
fi

# GPU detection - will run ollama if cpu only
if command -v nvidia-smi &>/dev/null; then
  echo "[AT-Mind] GPU detected -> starting vLLM (gpu profile)"
  $DOCKER_COMPOSE -f docker/docker-compose.yml --profile gpu up -d
else
  echo "[AT-Mind] No GPU detected -> starting Ollama (cpu profile)"
  $DOCKER_COMPOSE -f docker/docker-compose.yml --profile gpu up -d
fi
$DOCKER_COMPOSE ps
