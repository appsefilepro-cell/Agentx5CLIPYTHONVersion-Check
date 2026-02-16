from fastapi import FastAPI
import sqlite3, json

app=FastAPI()

@app.get("/balance")
def balance():
    db_path = "database/trading.db"
    conn=sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Better dict conversion
    
    try:
        bal=conn.execute("SELECT amount FROM balance").fetchone()[0]
        trades = [dict(row) for row in conn.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 10").fetchall()]
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
        
    return {"balance":bal,"trades":trades}

@app.get("/")
def home():
    return {"message": "Trading Bot UI. Go to /balance to see status."}
