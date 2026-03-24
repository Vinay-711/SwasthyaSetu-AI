#!/bin/bash
# SwasthyaSetu AI — Project Startup Script
# Usage: ./run.sh [--install]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$PROJECT_ROOT/backend"
FRONTEND="$PROJECT_ROOT/frontend"
VENV="$PROJECT_ROOT/.venv"
ENV_FILE="$PROJECT_ROOT/.env"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║        SwasthyaSetu AI  🏥               ║"
echo "║  AI-Powered Healthcare Platform          ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Env file ──────────────────────────────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  No .env found. Copying from .env.example (Databricks features disabled).${NC}"
    cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
fi

# ── Virtual environment ────────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
    echo -e "${GREEN}▶ Creating virtual environment…${NC}"
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

# ── Install dependencies ───────────────────────────────────────────────────
if [[ "$1" == "--install" ]] || [ ! -f "$VENV/.installed_marker" ]; then
    echo -e "${GREEN}▶ Installing backend dependencies…${NC}"
    pip install -q --upgrade pip
    pip install -q -r "$BACKEND/requirements.txt"

    echo -e "${GREEN}▶ Installing frontend dependencies…${NC}"
    pip install -q -r "$FRONTEND/requirements.txt"

    touch "$VENV/.installed_marker"
    echo -e "${GREEN}✅ Dependencies installed.${NC}"
fi

# ── Start backend ──────────────────────────────────────────────────────────
echo -e "${GREEN}▶ Starting FastAPI backend on http://localhost:8000 …${NC}"
cd "$BACKEND"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 3

# ── Start frontend ─────────────────────────────────────────────────────────
echo -e "${GREEN}▶ Starting Streamlit frontend on http://localhost:8501 …${NC}"
cd "$FRONTEND"
streamlit run app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗"
echo -e "║  🚀 SwasthyaSetu AI is running!                     ║"
echo -e "║                                                      ║"
echo -e "║  Frontend  →  http://localhost:8501                  ║"
echo -e "║  Backend   →  http://localhost:8000                  ║"
echo -e "║  API Docs  →  http://localhost:8000/docs             ║"
echo -e "╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Press Ctrl+C to stop both services."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" SIGINT SIGTERM
wait
