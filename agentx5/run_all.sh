#!/bin/bash
# AgentX5 - Full stack launcher
# Usage: bash agentx5/run_all.sh [mode]
# Modes: test | ui | bot | cli (default: cli)

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MODE="${1:-cli}"

echo "=============================="
echo "  AgentX5 Launcher — $MODE"
echo "=============================="

# Init DB if not present
if [ ! -f database/trading.db ]; then
  echo "[*] Initializing database..."
  python3 database/init_db.py
fi

case "$MODE" in
  test)
    echo "[*] Running full test suite..."
    python3 test_all.py
    ;;
  ui)
    echo "[*] Starting FastAPI dashboard on port 8765..."
    echo "    Open: http://localhost:8765"
    uvicorn frontend.simple_ui:app --host 0.0.0.0 --port 8765 --reload
    ;;
  bot)
    echo "[*] Starting trading bot orchestrator..."
    python3 backend/orchestrator.py
    ;;
  cli)
    echo "[*] Starting AgentX5 CLI terminal..."
    python3 cli.py
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Usage: bash run_all.sh [test|ui|bot|cli]"
    exit 1
    ;;
esac
