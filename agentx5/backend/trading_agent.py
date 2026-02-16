import asyncio, random, sqlite3, datetime, os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

class TradingAgent:
    def __init__(self):
        self.symbol="BTC/USD"
        self.pos=0.0
        self.entry=0.0

    async def price_stream(self):
        price=30000.0
        while True:
            # simulate small random walk
            price += random.uniform(-150,150)
            yield round(price,2)
            await asyncio.sleep(1)

    async def start(self):
        print(f"Agent starting for {self.symbol}...")
        async for p in self.price_stream():
            await self.on_price(p)

    async def on_price(self, price):
        # very simple strategy: buy if price drops > 0.3% from last, sell if +0.5% gain
        # Adjust DB path to match where script is run from (assuming agentx5 root)
        db_path = "database/trading.db"
        
        conn=sqlite3.connect(db_path)
        c=conn.cursor()
        
        # Ensure balance table exists just in case
        try:
            bal_row = c.execute("SELECT amount FROM balance").fetchone()
            if bal_row is None:
                c.execute("INSERT INTO balance(amount) VALUES (500.0)")
                conn.commit()
                bal = 500.0
            else:
                bal = bal_row[0]
        except sqlite3.OperationalError:
             # DB might be locked or table missing if init didn't run
             print("DB Error: ensure init_db.py ran")
             return

        action=None
        if self.pos==0 and random.random()<0.2: # Increased buy probability for demo
            # buy small
            size = min(0.01, bal/price)
            if size*price < bal:
                self.pos += size; self.entry=price; bal -= size*price; action="BUY"
                c.execute("INSERT INTO trades(symbol,side,price,size,pnl,ts) VALUES (?,?,?,?,?,?)",
                          (self.symbol,"BUY",price,size,0.0,str(datetime.datetime.utcnow())))
                print(f"BUY at {price}")
        elif self.pos>0 and (price - self.entry)/self.entry > 0.005:
            # take profit
            pnl = (price - self.entry) * self.pos
            bal += price*self.pos
            c.execute("INSERT INTO trades(symbol,side,price,size,pnl,ts) VALUES (?,?,?,?,?,?)",
                      (self.symbol,"SELL",price,self.pos,pnl,str(datetime.datetime.utcnow())))
            self.pos=0; self.entry=0; action="SELL"
            print(f"SELL at {price} PnL={pnl}")

        c.execute("UPDATE balance SET amount = ?", (bal,))
        conn.commit(); conn.close()
        
        # log
        if action:
            with open("logs/trades.log","a") as f:
                f.write(f"{datetime.datetime.utcnow()} price={price} action={action} pos={self.pos}\n")
