# data/websocket_client.py

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
import pytz
import websockets

from config import SYMBOL


BINANCE_WS_BASE = 'wss://stream.binance.com:9443/stream'
# Combine two streams: ticker (spot) + markPrice (perp)
STREAMS = f"{SYMBOL.lower()}@ticker/{SYMBOL.lower()}@markPrice"


@dataclass
class PriceTick:
    symbol: str
    timestamp: datetime
    spot_price: float
    perp_price: float
    funding_rate: float


class BinanceWebSocketClient:
    def __init__(self):
        # e.g. wss://stream.binance.com:9443/stream?streams=btcusdt@ticker/btcusdt@markPrice
        self.url = f"{BINANCE_WS_BASE}?streams={STREAMS}"
        self.spot_price: float = None
        self.perp_price: float = None
        self.funding_rate: float = None
        self._last_funding_fetch: datetime = None

    async def fetch_initial_funding_rate(self, exchange):
        """
        Fetch the most recent funding rate via REST. 
        Binance returns a list—take the last element's 'fundingRate'.
        """
        try:
            data = await exchange.fapiPublic_get_fundingRate({'symbol': SYMBOL})
            if isinstance(data, list) and data:
                last_entry = data[-1]
                self.funding_rate = float(last_entry.get('fundingRate', 0.0))
                self._last_funding_fetch = datetime.utcnow().replace(tzinfo=pytz.utc)
        except Exception as e:
            print(f"Error fetching initial funding rate: {e}")
            self.funding_rate = 0.0
            self._last_funding_fetch = datetime.utcnow().replace(tzinfo=pytz.utc)

    async def listen_price_ticks(self, price_queue: asyncio.Queue, exchange):
        """
        Connect to Binance WebSocket streams and push PriceTick objects into price_queue.
        Automatically refreshes funding rate every 8 hours.
        On any disconnect/error, waits 1 second and reconnects.
        """
        # On startup, fetch the current funding rate via REST
        await self.fetch_initial_funding_rate(exchange)

        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    while True:
                        msg = await ws.recv()
                        msg_json = json.loads(msg)
                        stream = msg_json.get('stream', '')
                        data = msg_json.get('data', {})

                        # Spot ticker updates
                        if stream.endswith('@ticker'):
                            # 'c' is last price
                            self.spot_price = float(data.get('c', 0.0))

                        # Perp mark price updates
                        elif stream.endswith('@markPrice'):
                            # 'p' is mark price
                            self.perp_price = float(data.get('p', 0.0))

                        # If both prices are available, build and send a tick
                        if self.spot_price is not None and self.perp_price is not None:
                            now = datetime.utcnow().replace(tzinfo=pytz.utc)

                            # If 8+ hours have passed since last funding fetch, refresh via REST
                            if (
                                self._last_funding_fetch is None
                                or (now - self._last_funding_fetch).total_seconds() >= 8 * 3600
                            ):
                                await self.fetch_initial_funding_rate(exchange)

                            tick = PriceTick(
                                symbol=SYMBOL,
                                timestamp=now,
                                spot_price=self.spot_price,
                                perp_price=self.perp_price,
                                funding_rate=self.funding_rate
                            )
                            await price_queue.put(tick)

            except Exception as e:
                print(f"WebSocket error: {e}. Reconnecting in 1s...")
                await asyncio.sleep(1)
              