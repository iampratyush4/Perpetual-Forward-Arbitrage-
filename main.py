import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from database import TimescaleDB
from risk_engine import RiskEngine
from config import EXCHANGE_CONFIG

# -----------------------------------------
# 1. DATA COLLECTOR
# -----------------------------------------
class DataHandler:
    def __init__(self):
        self.db = TimescaleDB()
    
    async def update_live_data(self):
        while True:
            try:
                # Connect to Binance
                exchange = ccxt.binance({
                    'apiKey': EXCHANGE_CONFIG['binance']['apiKey'],
                    'secret': EXCHANGE_CONFIG['binance']['secret'],
                    'enableRateLimit': True,
                })
                
                # Fetch Bitcoin prices
                spot_price = (await exchange.fetch_ticker('BTC/USDT'))['last']
                perp_data = await exchange.fetch_funding_rate('BTC/USDT:USDT')
                
                # Save to database
                self.db.write('prices', {
                    'timestamp': pd.Timestamp.now(),
                    'exchange': 'binance',
                    'spot': spot_price,
                    'perp': perp_data['markPrice'],
                    'funding_rate': perp_data['fundingRate']
                })
                
                await exchange.close()
                await asyncio.sleep(60)  # Wait 1 minute
            
            except Exception as e:
                print(f"Error: {e}")

# -----------------------------------------
# 2. ARBITRAGE DETECTOR
# -----------------------------------------
class ArbitrageEngine:
    def __init__(self):
        self.db = TimescaleDB()
        self.risk_engine = RiskEngine()
    
    async def check_arbitrage(self):
        # Get latest Bitcoin price from database
        data = self.db.query("SELECT * FROM prices ORDER BY timestamp DESC LIMIT 1")
        if not data.empty:
            spot = data['spot'].iloc[0]
            perp = data['perp'].iloc[0]
            funding = data['funding_rate'].iloc[0]
            
            basis = (perp - spot) / spot * 100  # Basis in