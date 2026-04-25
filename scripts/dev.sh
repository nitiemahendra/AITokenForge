#!/usr/bin/env bash
# Start backend and frontend concurrently in dev mode
# Requires: concurrently (npm install -g concurrently) or manual two terminals
set -euo pipefail

if ! command -v concurrently &>/dev/null; then
  echo "Starting backend in background, frontend in foreground…"
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  trap "kill $BACKEND_PID" EXIT
  cd frontend && npm run dev
else
  concurrently \
    --prefix "[{name}]" \
    --names "backend,frontend" \
    --prefix-colors "cyan,magenta" \
    "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" \
    "cd frontend && npm run dev"
fi
