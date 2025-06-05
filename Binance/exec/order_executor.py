# exec/order_executor.py

import asyncio
import json
import logging
import ccxt.async_support as ccxt
import websockets

from arb.risk_manager import RiskManager
from data.websocket_client import PriceTick


class OrderExecutor:
    def __init__(self, exchange: ccxt.binance):
        self.exchange = exchange
        self.user_ws_url: str = None

    async def place_hedge(self, tick: PriceTick, size_asset: float):
        """
        Given a PriceTick and an asset size, place two market orders:
          1. Spot side
          2. Perp side
        We assume: 
          - If perp > spot → Long spot, Short perp
          - Else → Short spot, Long perp
        After placing both legs, lock collateral in RiskManager.
        """
        symbol = tick.symbol
        perp_symbol = f"{symbol}"

        try:
            if tick.perp_price > tick.spot_price:
                # 1) Long spot
                spot_order = await self._place_market_order(symbol, 'BUY', size_asset, market_type='spot')
                # 2) Short perp
                perp_order = await self._place_market_order(perp_symbol, 'SELL', size_asset, market_type='perp')

            else:
                # 1) Short spot (convert to USDT‐margin syntax via createOrder)
                spot_order = await self._place_market_order(symbol, 'SELL', size_asset, market_type='spot')
                # 2) Long perp
                perp_order = await self._place_market_order(perp_symbol, 'BUY', size_asset, market_type='perp')

            # Estimate locked collateral (simple: assume 1% margin for perp)
            locked_usd = size_asset * tick.spot_price * 0.01
            self.exchange.risk_manager.lock_collateral(symbol, locked_usd)

            logging.info(f"Hedge placed: spot={spot_order}, perp={perp_order}")

        except Exception as e:
            logging.error(f"Error placing hedge for {symbol}: {e}")

    async def _place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        market_type: str = 'spot'
    ) -> dict:
        """
        market_type: 'spot' or 'perp'.
        For 'spot', use standard create_order.
        For 'perp', use the futures REST endpoint via ccxt.
        """
        if market_type == 'spot':
            order = await self.exchange.create_order(symbol, 'MARKET', side, quantity)

        else:  # 'perp'
            # Binance USDT‐margined perpetual uses fapiPrivate_post_order
            order = await self.exchange.fapiPrivate_post_order({
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': quantity,
            })

        return order

    async def listen_order_updates(self, risk_manager: RiskManager):
        """
        Listen to Binance User Data Stream for order/trade updates.
        Whenever an ORDER_TRADE_UPDATE event arrives, parse it and call
        `risk_manager.record_trade_outcome(...)` with realized PnL.
        """
        try:
            # 1) Get listenKey for futures user data
            resp = await self.exchange.fapiPrivate_post_listenKey()
            listen_key = resp.get('listenKey')
            self.user_ws_url = f"wss://fstream.binance.com/ws/{listen_key}"

            async with websockets.connect(self.user_ws_url) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if data.get('e') == 'ORDER_TRADE_UPDATE':
                        o = data['o']
                        symbol = o['s']  # e.g. "BTCUSDT"
                        executed_qty = float(o.get('z', 0.0))
                        avg_price = float(o.get('L', 0.0))
                        # PnL calculation for a basis arbitrage is not trivial here.
                        # For demonstration, assume we only care about whether the trade filled
                        # and we compute a pseudo‐PnL: executed_qty * (avg_price - last_spot).
                        # In practice, you'd need to reconcile both legs' fills.
                        # We'll fetch last_spot from data layer (omitted) or pass it in.
                        # Here, just record a 0 PnL placeholder and release collateral.
                        pnl = 0.0
                        risk_manager.record_trade_outcome(symbol, pnl)

        except Exception as e:
            logging.error(f"Order WS disconnected: {e}. Reconnecting in 1s...")
            await asyncio.sleep(1)
            await self.listen_order_updates(risk_manager)
