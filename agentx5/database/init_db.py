import sqlite3, os

# Ensure database directory exists relative to current execution context if needed,
# but the script assumes "database" folder. 
# Adjusted to be robust regarding CWD if run from agentx5 root.

if __name__ == "__main__":
    db_folder = "database"
    if not os.path.exists(db_folder):
        os.makedirs(db_folder, exist_ok=True)
        
    conn = sqlite3.connect(f"{db_folder}/trading.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS trades(
      id integer primary key, symbol text, side text, price real, size real, pnl real, ts text)""")
    c.execute("CREATE TABLE IF NOT EXISTS balance(amount real);")
    if c.execute("SELECT count(*) FROM balance").fetchone()[0]==0:
        c.execute("INSERT INTO balance(amount) VALUES (500.0)")
    conn.commit()
    conn.close()
    print('DB initialized')
