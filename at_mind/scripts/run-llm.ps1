# scripts/run-llm.ps1
# Purpose: On Windows, start exactly one LLM backend:
# - GPU present  -> vLLM (compose profile: gpu)
# - No GPU       -> Ollama (compose profile: cpu)

$ErrorActionPreference = "Stop"

function Get-ComposeCmd {
  # Prefer modern "docker compose", fall back to legacy "docker-compose"
  if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
      docker compose version | Out-Null
      return "docker compose"
    } catch { }
  }
  if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    return "docker-compose"
  }
  throw "Docker Compose not found. Install Docker Desktop or docker-compose."
}

function Has-NvidiaGpu {
  # Fast path: nvidia-smi present
  if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) { return $true }
  # Fallback: check WMI for NVIDIA adapter
  try {
    $gpus = Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name
    return ($gpus -match "NVIDIA").Count -gt 0
  } catch {
    return $false
  }
}

$compose = Get-ComposeCmd

if (Has-NvidiaGpu) {
  Write-Host "[AT-Mind] GPU detected → starting vLLM (gpu profile)"
  iex "$compose --profile gpu up -d"
} else {
  Write-Host "[AT-Mind] No GPU detected → starting Ollama (cpu profile)"
  iex "$compose --profile cpu up -d"
}

iex "$compose ps"

try {
  $services = & $compose ps --format json | ConvertFrom-Json
  if ($services | Where-Object { $_.Service -eq "vllm" -and $_.State -match "running" }) {
    $env:LLM_BASE_URL = "http://localhost:8000/v1"
  } else {
    $env:LLM_BASE_URL = "http://localhost:11434/v1"
  }
  Write-Host "[AT-Mind] LLM_BASE_URL set to $($env:LLM_BASE_URL)"
} catch { }
