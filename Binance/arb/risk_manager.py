# arb/risk_manager.py

import ccxt.async_support as ccxt
from collections import deque
from typing import Dict
from data.websocket_client import PriceTick


class RiskManager:
    def __init__(self, initial_equity: float = 100_000.0, max_alloc: float = 0.1):
        self.equity: float = initial_equity
        self.open_positions: Dict[str, Dict] = {}  # Track collateral & entry for each symbol
        self.historical_outcomes = deque(maxlen=500)  # 1 for win, 0 for loss
        self.maker_fee: float = 0.0
        self.taker_fee: float = 0.0
        self.max_alloc: float = max_alloc

    async def fetch_fees(self, exchange: ccxt.binance):
        """
        Fetch maker/taker fees for SYMBOL from Binance REST.
        If Binance does not return a per‐symbol breakdown, default to 0.001 (0.1%).
        """
        try:
            fees_resp = await exchange.fetch_trading_fees()
            # fetch_trading_fees() returns a dict: { 'BTC/USDT': {'maker': 0.0002, 'taker': 0.0004}, ... }
            key = exchange.market_id(SYMBOL) if hasattr(exchange, 'market_id') else SYMBOL
            symbol_fees = fees_resp.get(key, {})
            self.maker_fee = float(symbol_fees.get('maker', 0.001))
            self.taker_fee = float(symbol_fees.get('taker', 0.001))
        except Exception:
            # Fallback defaults
            self.maker_fee = 0.001
            self.taker_fee = 0.001

    def estimate_win_prob(self) -> float:
        """
        Estimate empirical win probability from historical outcomes.
        If not enough data, default to 0.6.
        """
        if not self.historical_outcomes:
            return 0.6
        return sum(self.historical_outcomes) / len(self.historical_outcomes)

    def available_equity(self) -> float:
        """
        Subtract all locked collateral for open positions from total equity.
        """
        locked = sum(pos.get('locked_collateral', 0.0) for pos in self.open_positions.values())
        return self.equity - locked

    def calculate_position_size(self, tick: PriceTick) -> float:
        """
        Use a half‐Kelly formula to determine how much USD to allocate,
        then convert to asset units (spot side size).
        Returns size in units of the asset (e.g. BTC).
        """
        # 1. Compute basis in decimal (e.g., 0.007 for 0.7%)
        basis_pct = (tick.perp_price - tick.spot_price) / tick.spot_price

        # 2. Fee + slippage cushion (taker fee + 1 bps)
        fee_slippage = self.taker_fee + 0.0001

        # 3. Effective edge
        edge = abs(basis_pct) - fee_slippage

        # 4. Empirical win probability
        win_prob = self.estimate_win_prob()

        if edge <= 0 or win_prob < 0.51:
            return 0.0

        # 5. Kelly fraction: (p * b - q) / b
        b = edge  # assuming if we win, we make `edge` fraction (e.g., 0.005)
        q = 1 - win_prob
        kelly = (win_prob * b - q) / b
        # Use half‐Kelly for safety
        kelly *= 0.5

        # 6. Constrain by max_alloc
        kelly = max(0.0, min(kelly, self.max_alloc))

        # 7. Determine USD to allocate
        usd_alloc = self.available_equity() * kelly

        # 8. Convert to asset units
        size_asset = usd_alloc / tick.spot_price

        return max(0.0, size_asset)

    def lock_collateral(self, symbol: str, locked_usd: float):
        """
        Register locked collateral for an open position.
        """
        self.open_positions[symbol] = {
            'locked_collateral': locked_usd
        }

    def record_trade_outcome(self, symbol: str, pnl_usd: float):
        """
        Called whenever a completed arbitrage trade yields PnL.
        Updates equity, historical outcomes (1 = win, 0 = loss), and releases collateral.
        """
        if pnl_usd > 0:
            self.historical_outcomes.append(1)
        else:
            self.historical_outcomes.append(0)

        self.equity += pnl_usd

        # Remove collateral lock if position is closed
        if symbol in self.open_positions:
            del self.open_positions[symbol]
