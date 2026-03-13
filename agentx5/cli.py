"""
AgentX5 CLI Terminal
A general-purpose terminal for running Python/bash tasks pasted from LLMs.
Run: python3 agentx5/cli.py
"""
import os
import sys
import subprocess
import tempfile
import sqlite3
import readline  # enables arrow keys + history

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "database", "trading.db")

BANNER = """
\033[92m
  ▄▄▄       ▄████ ▓█████  ███▄    █ ▄▄▄█████▓ ▒██   ██▒ ██████
 ▒████▄    ██▒ ▀█▒▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒▒▒ █ █ ▒░▒██    ▒
 ▒██  ▀█▄ ▒██░▄▄▄░▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░░░  █   ░░ ▓██▄
 ░██▄▄▄▄██░▓█  ██▓▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░  ░ █ █ ▒   ▒   ██▒
  ▓█   ▓██▒░▒▓███▀▒░▒████▒▒██░   ▓██░  ▒██▒ ░ ▒██▒ ▒██▒▒██████▒▒
  ▒▒   ▓▒█░ ░▒   ▒ ░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░   ▒▒ ░ ░▓ ░▒ ▒▓▒ ▒ ░
   ▒   ▒▒ ░  ░   ░  ░ ░  ░░ ░░   ░ ▒░    ░    ░░   ░▒ ░░ ░▒  ░ ░
   ░   ▒   ░ ░   ░    ░      ░   ░ ░   ░      ░    ░  ░  ░  ░
       ░  ░      ░    ░  ░         ░            ░    ░        ░
\033[0m
  \033[94mAgentX5 CLI Terminal — Type /help for commands\033[0m
"""

HELP = """
\033[93mAvailable Commands:\033[0m
  \033[92m/help\033[0m              Show this help
  \033[92m/clear\033[0m             Clear the screen
  \033[92m/exit\033[0m              Exit the CLI

  \033[94m--- Code Execution ---\033[0m
  \033[92m/python\033[0m            Enter multiline Python mode (type /end to run)
  \033[92m/bash <cmd>\033[0m        Run a single bash command
  \033[92m/run <file.py>\033[0m     Run a Python file

  \033[94m--- AgentX5 ---\033[0m
  \033[92m/balance\033[0m           Show trading bot balance + recent trades
  \033[92m/bot\033[0m               Start trading bot (5 ticks demo)
  \033[92m/test\033[0m              Run full test suite
  \033[92m/ui\033[0m                Launch FastAPI dashboard (port 8765)
  \033[92m/dbinit\033[0m            Re-initialize the SQLite database
  \033[92m/logs\033[0m              Show recent trade logs

  \033[94m--- Anything else ---\033[0m
  Type any shell command directly (no slash needed)
"""


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def run_bash(cmd, cwd=ROOT):
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=cwd)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(color(result.stderr, "91"), end="")
    except Exception as e:
        print(color(f"Error: {e}", "91"))

def run_python_multiline():
    print(color("Multiline Python mode. Type /end on a new line to execute, /cancel to abort.", "94"))
    lines = []
    while True:
        try:
            line = input(color("... ", "93"))
        except (EOFError, KeyboardInterrupt):
            print()
            print(color("Cancelled.", "91"))
            return
        if line.strip() == "/end":
            break
        if line.strip() == "/cancel":
            print(color("Cancelled.", "91"))
            return
        lines.append(line)

    code = "\n".join(lines)
    if not code.strip():
        return

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=ROOT) as f:
        f.write(code)
        tmp = f.name
    try:
        print(color("--- Output ---", "90"))
        result = subprocess.run([sys.executable, tmp], text=True, capture_output=True, cwd=ROOT)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(color(result.stderr, "91"), end="")
        print(color("--------------", "90"))
    finally:
        os.remove(tmp)

def run_file(path):
    if not os.path.exists(path):
        abs_path = os.path.join(ROOT, path)
        if not os.path.exists(abs_path):
            print(color(f"File not found: {path}", "91"))
            return
        path = abs_path
    print(color(f"Running: {path}", "94"))
    result = subprocess.run([sys.executable, path], text=True, capture_output=True, cwd=ROOT)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(color(result.stderr, "91"), end="")

def show_balance():
    try:
        conn = sqlite3.connect(DB_PATH)
        bal = conn.execute("SELECT amount FROM balance").fetchone()
        trades = conn.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
        print(color(f"\n  Balance: ${round(bal[0], 4) if bal else '?'} USD", "92"))
        if trades:
            print(color("  Recent trades:", "94"))
            for t in trades:
                side_color = "92" if t[2] == "BUY" else "91"
                print(f"    {color(t[2], side_color)} {t[1]} @ ${t[3]:.2f}  size={t[4]}  pnl={t[5]:.4f}  {t[6]}")
        else:
            print("  No trades yet.")
        print()
    except Exception as e:
        print(color(f"DB Error: {e}", "91"))

def run_bot_demo():
    import asyncio
    sys.path.insert(0, ROOT)
    from backend.trading_agent import TradingAgent

    async def demo():
        agent = TradingAgent()
        print(color("Running 5 price ticks...", "94"))
        count = 0
        async for p in agent.price_stream():
            print(color(f"  Tick {count+1}: ${p}", "93"))
            await agent.on_price(p)
            count += 1
            if count >= 5:
                break
        print(color("Done.", "92"))

    asyncio.run(demo())

def show_logs():
    log_file = os.path.join(ROOT, "logs", "trades.log")
    if not os.path.exists(log_file):
        print(color("No trade logs found yet.", "91"))
        return
    with open(log_file) as f:
        lines = f.readlines()[-20:]
    print(color("--- Last 20 log entries ---", "90"))
    for line in lines:
        print(" ", line, end="")
    print(color("---------------------------", "90"))

def cmd_ui():
    print(color("Starting FastAPI dashboard on port 8765...", "94"))
    print(color("Visit: http://localhost:8765", "92"))
    print(color("Press Ctrl+C to stop.", "93"))
    try:
        subprocess.run(
            ["uvicorn", "frontend.simple_ui:app", "--host", "0.0.0.0", "--port", "8765", "--reload"],
            cwd=ROOT
        )
    except KeyboardInterrupt:
        print(color("\nFastAPI server stopped.", "91"))


# ──────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────

def main():
    print(BANNER)

    # Enable persistent history
    history_file = os.path.join(ROOT, ".cli_history")
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass
    readline.set_history_length(500)

    while True:
        try:
            raw = input(color("\nAgentX5> ", "92")).strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print(color("\n(Ctrl+C — type /exit to quit)", "93"))
            continue

        if not raw:
            continue

        readline.write_history_file(history_file)

        if raw == "/exit":
            print(color("Goodbye.", "92"))
            break
        elif raw == "/help":
            print(HELP)
        elif raw == "/clear":
            os.system("clear")
        elif raw == "/python":
            run_python_multiline()
        elif raw.startswith("/bash "):
            run_bash(raw[6:])
        elif raw.startswith("/run "):
            run_file(raw[5:])
        elif raw == "/balance":
            show_balance()
        elif raw == "/bot":
            run_bot_demo()
        elif raw == "/test":
            run_bash(f"python3 {os.path.join(ROOT, 'test_all.py')}")
        elif raw == "/ui":
            cmd_ui()
        elif raw == "/dbinit":
            run_bash(f"python3 {os.path.join(ROOT, 'database', 'init_db.py')}")
        elif raw == "/logs":
            show_logs()
        elif raw.startswith("/"):
            print(color(f"Unknown command: {raw} — type /help for list", "91"))
        else:
            # Treat as a direct shell command
            run_bash(raw)


if __name__ == "__main__":
    main()
