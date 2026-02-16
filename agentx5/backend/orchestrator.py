import asyncio, uvicorn, os, sys

# Add the current directory to sys.path so we can import modules
sys.path.append(os.getcwd())

from backend.trading_agent import TradingAgent

async def main():
    print("Orchestrator starting (sandbox)")
    agent = TradingAgent()
    await agent.start()

if __name__=="__main__":
    # Ensure DB is initialized
    import database.init_db as _init
    if not os.path.exists("database/trading.db"):
         print("Initializing DB...")
         # Trigger the init logic if it was in a function, but it's top level in the provided file
         # The import above runs the top level code.
         pass
         
    asyncio.run(main())
