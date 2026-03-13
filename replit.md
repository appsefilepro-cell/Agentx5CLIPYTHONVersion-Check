# AgentX5 — Project Overview

## Architecture

This project has two coexisting parts:

### 1. Node.js / React App (port 5000)
- Entry: `server/index.ts` → `server/routes.ts`
- Frontend: `client/src/App.tsx` (React + Vite)
- Workflow: `Start application` → `npm run dev`

### 2. AgentX5 Python Project (`agentx5/`)
- Language: Python 3.11 (system-wide, no venv)
- All scripts run with `python3` from the `agentx5/` directory as CWD

## AgentX5 Structure

```
agentx5/
├── cli.py                    # Main CLI terminal (run: python3 agentx5/cli.py)
├── run_all.sh                # Launcher: test | ui | bot | cli
├── test_all.py               # Full integration test suite (21 tests)
├── requirements.txt          # Python deps
├── database/
│   ├── init_db.py            # SQLite DB initializer
│   └── trading.db            # SQLite DB (auto-created)
├── backend/
│   ├── trading_agent.py      # Async BTC/USD trading bot (random walk)
│   ├── orchestrator.py       # Async orchestrator (runs trading agent)
│   └── wallets/
│       └── wallet_manager.py # Wallet manager stub
├── frontend/
│   └── simple_ui.py          # FastAPI dashboard (port 8765)
└── logs/
    └── trades.log            # Trade event log
```

## Running AgentX5

```bash
# CLI terminal (interactive)
python3 agentx5/cli.py

# Full test suite
bash agentx5/run_all.sh test

# FastAPI dashboard
bash agentx5/run_all.sh ui

# Trading bot
bash agentx5/run_all.sh bot
```

## CLI Commands
- `/help` — show all commands
- `/python` — multiline Python execution
- `/bash <cmd>` — run shell command
- `/run <file.py>` — run a Python file
- `/balance` — show bot balance + trades
- `/bot` — run 5-tick trading bot demo
- `/test` — run full test suite
- `/ui` — launch FastAPI dashboard
- `/dbinit` — re-init the SQLite DB
- `/logs` — show recent trade logs

## Packages Installed (system-wide)
fastapi, uvicorn, pandas, numpy, aiohttp, sqlalchemy, aiosqlite

## Key Notes
- Run all Python scripts from `agentx5/` as the working directory
- DB path is relative: `database/trading.db`
- CLI keeps history in `agentx5/.cli_history`
- GitHub repos planned: /Startmanuswebhooks, /Agentx5, /Clawbots, /Ray1500 (pending auth)
