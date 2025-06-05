# main.py

import asyncio
import logging
import os

import ccxt.async_support as ccxt

from config import API_KEY, API_SECRET, DATABASE_URL, SYMBOL
from data.websocket_client import BinanceWebSocketClient, PriceTick
from db.db_async import TimescaleDB
from arb.risk_manager import RiskManager
from arb.arbitrage_engine import ArbitrageEngine
from exec.order_executor import OrderExecutor


async def main():
    # 1) Basic logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger()

    # 2) Connect to the database
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set in environment.")
        return
    db = TimescaleDB(dsn=DATABASE_URL)
    await db.connect()
    logger.info("Connected to TimescaleDB.")

    # 3) Create a single ccxt.binance instance (for both rest & user data WS)
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': False,  # we manage our own rate logic
    })
    await exchange.load_markets()
    logger.info("Connected to Binance via CCXT.")

    # 4) Initialize RiskManager and fetch fees
    risk_manager = RiskManager(initial_equity=100_000.0, max_alloc=float(os.getenv('MAX_ALLOC', 0.1)))
    await risk_manager.fetch_fees(exchange)
    logger.info(f"Fetched maker={risk_manager.maker_fee}, taker={risk_manager.taker_fee} fees.")

    # 5) Initialize OrderExecutor (attach risk_manager to exchange for collateral locking)
    order_executor = OrderExecutor(exchange)
    exchange.risk_manager = risk_manager  # so OrderExecutor can lock collateral
    # Spawn a task to listen for order updates
    asyncio.create_task(order_executor.listen_order_updates(risk_manager))
    logger.info("Order update listener started.")

    # 6) Initialize ArbitrageEngine
    arb_engine = ArbitrageEngine(risk_manager, order_executor)

    # 7) Initialize BinanceWebSocketClient
    ws_client = BinanceWebSocketClient()

    # 8) Create asyncio queues
    price_queue = asyncio.Queue(maxsize=1000)

    # 9) Start WebSocket listener (feeds price_queue)
    data_task = asyncio.create_task(ws_client.listen_price_ticks(price_queue, exchange))
    logger.info("WebSocket price listener started.")

    # 10) Start DB writer task (consumes price_queue in batches)
    async def db_writer():
        buffer = []
        while True:
            tick: PriceTick = await price_queue.get()
            buffer.append(tick)
            # If we have ≥100 ticks or ≥1 second since first tick, flush
            first_ts = buffer[0].timestamp.timestamp()
            now_ts = asyncio.get_event_loop().time()
            if len(buffer) >= 100 or (now_ts - first_ts) >= 1.0:
                await db.write_batch(buffer)
                buffer.clear()

    writer_task = asyncio.create_task(db_writer())
    logger.info("DB writer task started.")

    # 11) Start arbitrage engine (also consumes price_queue)
    arb_task = asyncio.create_task(arb_engine.run(price_queue))
    logger.info("Arbitrage engine started.")

    # 12) Run until cancelled
    await asyncio.gather(data_task, writer_task, arb_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested. Exiting...")
