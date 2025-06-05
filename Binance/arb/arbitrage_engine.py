# arb/arbitrage_engine.py

import asyncio
from data.websocket_client import PriceTick
from arb.risk_manager import RiskManager
from exec.order_executor import OrderExecutor


class ArbitrageEngine:
    def __init__(self, risk_manager: RiskManager, order_executor: OrderExecutor):
        self.risk = risk_manager
        self.executor = order_executor

    async def run(self, price_queue: asyncio.Queue):
        """
        Continuously consume PriceTick objects from price_queue.
        For each tick, calculate position size; if non‐zero, trigger a hedge.
        """
        while True:
            tick: PriceTick = await price_queue.get()

            size_asset = self.risk.calculate_position_size(tick)
            if size_asset > 0:
                # Launch the hedge asynchronously so that we don't block reading more ticks
                asyncio.create_task(self.executor.place_hedge(tick, size_asset))
