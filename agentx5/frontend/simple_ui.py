import os
import sys
import sqlite3

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="AgentX5 Dashboard")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "trading.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head><title>AgentX5 Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { font-family: monospace; background: #0d0d0d; color: #00ff88; padding: 20px; }
      h1 { color: #00ff88; }
      a { color: #00aaff; text-decoration: none; }
      .box { border: 1px solid #00ff88; padding: 16px; margin: 12px 0; border-radius: 6px; }
    </style>
    </head>
    <body>
      <h1>AgentX5 Dashboard</h1>
      <div class="box"><a href="/balance">/balance</a> — Trading bot balance &amp; recent trades</div>
      <div class="box"><a href="/health">/health</a> — System health check</div>
      <div class="box"><a href="/docs">/docs</a> — API docs (Swagger UI)</div>
    </body>
    </html>
    """


@app.get("/balance")
def balance():
    try:
        conn = get_db()
        bal = conn.execute("SELECT amount FROM balance").fetchone()
        trades = [dict(row) for row in conn.execute(
            "SELECT * FROM trades ORDER BY id DESC LIMIT 10"
        ).fetchall()]
        conn.close()
        return {
            "balance": round(bal[0], 4) if bal else 500.0,
            "currency": "USD",
            "trades": trades
        }
    except Exception as e:
        return {"error": str(e), "balance": None, "trades": []}


@app.get("/health")
def health():
    checks = {}
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        checks["database"] = "OK"
    except Exception as e:
        checks["database"] = f"ERROR: {e}"
    return {"status": "ok" if all(v == "OK" for v in checks.values()) else "degraded", "checks": checks}
