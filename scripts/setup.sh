#!/usr/bin/env bash
# TokenForge — one-shot local setup script
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[info]${NC} $*"; }
success() { echo -e "${GREEN}[ok]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC} $*"; }
error()   { echo -e "${RED}[err]${NC}  $*"; exit 1; }

echo ""
echo "  ╔══════════════════════════════╗"
echo "  ║   TokenForge Setup Script    ║"
echo "  ╚══════════════════════════════╝"
echo ""

# ─── Prerequisites ────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || error "Python 3 not found. Install from https://python.org"
command -v node    >/dev/null 2>&1 || error "Node.js not found. Install from https://nodejs.org"
command -v ollama  >/dev/null 2>&1 || warn  "Ollama not found. Install from https://ollama.com — falling back to mock adapter."

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PY_VERSION detected"

# ─── .env ────────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  success ".env created from .env.example"
else
  info ".env already exists — skipping"
fi

# ─── Backend ─────────────────────────────────────────────────────────────────
info "Installing backend dependencies…"
pip install -r backend/requirements.txt -q
success "Backend dependencies installed"

# ─── Frontend ─────────────────────────────────────────────────────────────────
info "Installing frontend dependencies…"
(cd frontend && npm install --silent)
success "Frontend dependencies installed"

# ─── Ollama / Gemma ───────────────────────────────────────────────────────────
if command -v ollama >/dev/null 2>&1; then
  info "Checking for gemma3:4b model…"
  if ollama list | grep -q "gemma4"; then
    success "gemma4:latest already available"
  else
    info "Pulling gemma4:latest (this may take several minutes)…"
    ollama pull gemma4:latest
    success "gemma4:latest downloaded"
  fi
fi

echo ""
echo "  ─────────────────────────────────"
success "Setup complete!"
echo ""
echo "  Start the backend:"
echo "    uvicorn backend.main:app --reload"
echo ""
echo "  Start the frontend:"
echo "    cd frontend && npm run dev"
echo ""
echo "  Or with Docker:"
echo "    docker-compose up"
echo ""
