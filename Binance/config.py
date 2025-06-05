import os
from dotenv import load_dotenv

load_dotenv()

# Binance API credentials
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Database connection URL (Postgres/Timescale)
# e.g. "postgres://user:password@host:port/dbname"
DATABASE_URL = os.getenv('DATABASE_URL')

# Symbol to trade (defaults to BTCUSDT if not set)
SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')

# Maximum allocation fraction of available equity per trade (e.g., 0.1 → 10%)
MAX_ALLOC = float(os.getenv('MAX_ALLOC', '0.1'))
