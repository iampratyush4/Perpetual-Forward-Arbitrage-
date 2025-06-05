# db/db_async.py

import asyncpg
from typing import List
from data.websocket_client import PriceTick


class TimescaleDB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.pool.Pool = None

    async def connect(self):
        """
        Establish an asyncpg connection pool.
        """
        self.pool = await asyncpg.create_pool(dsn=self.dsn, max_size=10)

    async def write_batch(self, ticks: List[PriceTick]):
        """
        Bulk‐insert a list of PriceTick into the `prices` table.

        The `prices` table schema (in Postgres/TimescaleDB) is assumed to be:
            CREATE TABLE IF NOT EXISTS prices (
                timestamp  TIMESTAMPTZ NOT NULL,
                exchange   TEXT         NOT NULL,
                symbol     TEXT         NOT NULL,
                spot       DOUBLE PRECISION NOT NULL,
                perp       DOUBLE PRECISION NOT NULL,
                funding_rate DOUBLE PRECISION NOT NULL
            );
            -- Then convert to hypertable:
            SELECT create_hypertable('prices', 'timestamp', if_not_exists => TRUE);
        """
        if not ticks:
            return

        records = [
            (t.timestamp, 'binance', t.symbol, t.spot_price, t.perp_price, t.funding_rate)
            for t in ticks
        ]

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO prices(timestamp, exchange, symbol, spot, perp, funding_rate)
                    VALUES($1, $2, $3, $4, $5, $6)
                    """,
                    records
                )
