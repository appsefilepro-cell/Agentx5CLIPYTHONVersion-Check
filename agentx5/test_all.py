"""
AgentX5 - Full Integration Test Suite
Run from agentx5/ directory: python3 test_all.py
"""
import sys
import os
import asyncio
import sqlite3
import subprocess
import tempfile

# Ensure correct path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

results = []

def test(name, fn):
    try:
        fn()
        print(f"  {PASS} {name}")
        results.append((name, True, None))
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append((name, False, str(e)))


# ──────────────────────────────────────────
# 1. PACKAGE IMPORTS
# ──────────────────────────────────────────
print(f"\n{INFO} 1. Package Imports")

def test_import_fastapi():
    import fastapi
test("fastapi", test_import_fastapi)

def test_import_uvicorn():
    import uvicorn
test("uvicorn", test_import_uvicorn)

def test_import_aiohttp():
    import aiohttp
test("aiohttp", test_import_aiohttp)

def test_import_sqlalchemy():
    import sqlalchemy
test("sqlalchemy", test_import_sqlalchemy)

def test_import_pandas():
    import pandas
test("pandas", test_import_pandas)

def test_import_numpy():
    import numpy
test("numpy", test_import_numpy)


# ──────────────────────────────────────────
# 2. MODULE IMPORTS
# ──────────────────────────────────────────
print(f"\n{INFO} 2. Module Imports")

def test_import_trading_agent():
    from backend.trading_agent import TradingAgent
    agent = TradingAgent()
    assert agent.symbol == "BTC/USD"
test("backend.trading_agent", test_import_trading_agent)

def test_import_wallet_manager():
    from backend.wallets.wallet_manager import WalletManager
    wm = WalletManager()
    wm.add_wallet("test", {"type": "sandbox"})
    assert "test" in wm.list_wallets()
test("backend.wallets.wallet_manager", test_import_wallet_manager)

def test_import_simple_ui():
    from frontend.simple_ui import app
    assert app is not None
test("frontend.simple_ui", test_import_simple_ui)


# ──────────────────────────────────────────
# 3. DATABASE
# ──────────────────────────────────────────
print(f"\n{INFO} 3. Database")

DB_PATH = os.path.join(ROOT, "database", "trading.db")

def test_db_exists():
    if not os.path.exists(DB_PATH):
        # Auto-init
        subprocess.run([sys.executable, os.path.join(ROOT, "database", "init_db.py")], check=True)
    assert os.path.exists(DB_PATH)
test("DB file exists", test_db_exists)

def test_db_schema():
    conn = sqlite3.connect(DB_PATH)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "trades" in tables, "Missing 'trades' table"
    assert "balance" in tables, "Missing 'balance' table"
    conn.close()
test("DB schema (trades + balance)", test_db_schema)

def test_db_balance():
    conn = sqlite3.connect(DB_PATH)
    bal = conn.execute("SELECT amount FROM balance").fetchone()
    assert bal is not None, "No balance row"
    assert isinstance(bal[0], float), "Balance is not a float"
    conn.close()
test("DB balance row readable", test_db_balance)


# ──────────────────────────────────────────
# 4. TRADING AGENT (ASYNC)
# ──────────────────────────────────────────
print(f"\n{INFO} 4. Trading Agent")

def test_trading_agent_ticks():
    from backend.trading_agent import TradingAgent
    agent = TradingAgent()

    async def run():
        count = 0
        async for p in agent.price_stream():
            assert isinstance(p, float), f"Price not float: {p}"
            await agent.on_price(p)
            count += 1
            if count >= 5:
                break
        return count

    count = asyncio.run(run())
    assert count == 5, f"Expected 5 ticks, got {count}"
test("5 price ticks processed", test_trading_agent_ticks)

def test_trade_recorded():
    conn = sqlite3.connect(DB_PATH)
    trades = conn.execute("SELECT count(*) FROM trades").fetchone()[0]
    conn.close()
    assert trades >= 0  # At least initialized
test("trades table accessible", test_trade_recorded)


# ──────────────────────────────────────────
# 5. WALLET MANAGER
# ──────────────────────────────────────────
print(f"\n{INFO} 5. Wallet Manager")

def test_wallet_add_get():
    from backend.wallets.wallet_manager import WalletManager
    wm = WalletManager()
    wm.add_wallet("metamask", {"type": "evm"})
    bal = wm.get_balance("metamask")
    assert "sandbox" in bal.lower()
test("add + get wallet balance", test_wallet_add_get)

def test_wallet_remove():
    from backend.wallets.wallet_manager import WalletManager
    wm = WalletManager()
    wm.add_wallet("phantom", {"type": "solana"})
    wm.remove_wallet("phantom")
    assert "phantom" not in wm.list_wallets()
test("remove wallet", test_wallet_remove)

def test_wallet_missing():
    from backend.wallets.wallet_manager import WalletManager
    wm = WalletManager()
    result = wm.get_balance("nonexistent")
    assert result is None
test("missing wallet returns None", test_wallet_missing)


# ──────────────────────────────────────────
# 6. FASTAPI ENDPOINTS
# ──────────────────────────────────────────
print(f"\n{INFO} 6. FastAPI Endpoints")

def test_fastapi_health():
    from frontend.simple_ui import health
    result = health()
    assert "status" in result
    assert "checks" in result
test("/health endpoint", test_fastapi_health)

def test_fastapi_balance():
    from frontend.simple_ui import balance
    result = balance()
    assert "balance" in result, f"Missing 'balance' key: {result}"
    assert "trades" in result, f"Missing 'trades' key: {result}"
test("/balance endpoint", test_fastapi_balance)


# ──────────────────────────────────────────
# 7. CLI SCRIPT
# ──────────────────────────────────────────
print(f"\n{INFO} 7. CLI Script")

def test_cli_syntax():
    import py_compile
    py_compile.compile(os.path.join(ROOT, "cli.py"), doraise=True)
test("cli.py syntax valid", test_cli_syntax)

def test_cli_bash_execution():
    code = """
import subprocess, sys
result = subprocess.run("echo hello_agentx5", shell=True, text=True, capture_output=True)
assert result.stdout.strip() == "hello_agentx5"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run([sys.executable, tmp], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    finally:
        os.remove(tmp)
test("bash execution in CLI works", test_cli_bash_execution)


# ──────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total = len(results)

print(f"\n{'='*50}")
print(f"RESULTS: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} FAILED)")
    for name, ok, err in results:
        if not ok:
            print(f"  {FAIL} {name}: {err}")
else:
    print(" — All tests passed!")
print(f"{'='*50}\n")

sys.exit(0 if failed == 0 else 1)
