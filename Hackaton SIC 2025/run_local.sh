#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=8001

echo "[init] Backend: $BACKEND_PORT | Frontend: $FRONTEND_PORT"
echo "[info] Asegúrate de instalar dependencias: pip install -r backend/requirements.txt"

start_backend() {
  cd "$BACKEND"
  if [ -d ".venv" ]; then
    source .venv/bin/activate
  fi
  uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
}

start_frontend() {
  cd "$FRONTEND"
  python3 -m http.server "$FRONTEND_PORT"
}

start_frontend &
FRONT_PID=$!
echo "[ok] Frontend sirviendo en http://localhost:$FRONTEND_PORT"

trap 'echo "[stop] Cerrando servicios"; kill $FRONT_PID 2>/dev/null || true' EXIT

start_backend
