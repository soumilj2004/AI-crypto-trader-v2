import aiosqlite
import os
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(__file__), "market.db")


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id   TEXT    NOT NULL,
                price     REAL    NOT NULL,
                volume    REAL    DEFAULT 0,
                ts        TEXT    NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_coin_ts ON ticks(coin_id, ts)")
        await db.commit()
    print("✅ DB ready")


async def save_prices(prices: dict):
    async with aiosqlite.connect(DB) as db:
        rows = [
            (c, d["price"], d.get("volume_24h", 0), d.get("timestamp", datetime.utcnow().isoformat()))
            for c, d in prices.items()
        ]
        await db.executemany(
            "INSERT INTO ticks (coin_id, price, volume, ts) VALUES (?,?,?,?)", rows
        )
        # Prune > 7 days
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        await db.execute("DELETE FROM ticks WHERE ts < ?", (cutoff,))
        await db.commit()


async def get_ticks(coin_id: str, since_minutes: int = 60) -> list[dict]:
    cutoff = (datetime.utcnow() - timedelta(minutes=since_minutes)).isoformat()
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT price, volume, ts FROM ticks WHERE coin_id=? AND ts>? ORDER BY ts ASC",
            (coin_id, cutoff)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_ohlcv(coin_id: str, minutes: int, bucket_seconds: int) -> list[dict]:
    """
    Aggregate raw ticks into OHLCV candles of `bucket_seconds` width.
    """
    ticks = await get_ticks(coin_id, since_minutes=minutes)
    if not ticks:
        return []

    candles: dict[int, dict] = {}
    for t in ticks:
        dt = datetime.fromisoformat(t["ts"])
        bucket = int(dt.timestamp() // bucket_seconds) * bucket_seconds
        if bucket not in candles:
            candles[bucket] = {"t": bucket, "o": t["price"], "h": t["price"],
                               "l": t["price"], "c": t["price"], "v": t["volume"]}
        else:
            c = candles[bucket]
            c["h"] = max(c["h"], t["price"])
            c["l"] = min(c["l"], t["price"])
            c["c"] = t["price"]
            c["v"] += t["volume"]

    return sorted(candles.values(), key=lambda x: x["t"])
