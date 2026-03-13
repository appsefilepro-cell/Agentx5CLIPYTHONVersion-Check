import asyncio
import os
import sys

# Ensure agentx5/ root is on sys.path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.trading_agent import TradingAgent
from backend.wallets.wallet_manager import WalletManager


async def main():
    print("[Orchestrator] Starting AgentX5...")

    # Init wallet manager
    wm = WalletManager()
    wm.add_wallet("main", {"type": "sandbox", "currency": "USD"})
    print(f"[Orchestrator] Wallet loaded: {wm.get_balance('main')}")

    # Start trading agent
    agent = TradingAgent()
    print("[Orchestrator] Trading agent initialized. Running...")
    await agent.start()


if __name__ == "__main__":
    # Ensure DB exists before starting
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "trading.db")
    if not os.path.exists(db_path):
        print("[Orchestrator] DB not found — running init...")
        import subprocess
        init_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "init_db.py")
        subprocess.run([sys.executable, init_path], check=True)

    asyncio.run(main())
