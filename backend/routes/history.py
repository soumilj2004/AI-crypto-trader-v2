from fastapi import APIRouter, Query
from db.database import get_ticks, get_ohlcv

router = APIRouter(tags=["history"])

# interval label → (lookback_minutes, bucket_seconds)
INTERVALS = {
    "1s":  (10,    1),
    "5s":  (30,    5),
    "15s": (60,   15),
    "30s": (120,  30),
    "1m":  (240,  60),
    "5m":  (720,  300),
    "15m": (1440, 900),
    "1h":  (4320, 3600),
    "4h":  (10080, 14400),
    "1d":  (10080, 86400),
}


@router.get("/history/{coin_id}")
async def history(
    coin_id: str,
    interval: str = Query(default="1m", description="One of: " + ", ".join(INTERVALS)),
):
    coin_id = coin_id.lower()
    if interval not in INTERVALS:
        return {"error": f"Unknown interval. Choose from: {list(INTERVALS)}"}
    minutes, bucket = INTERVALS[interval]
    candles = await get_ohlcv(coin_id, minutes, bucket)
    ticks   = await get_ticks(coin_id, since_minutes=minutes)
    return {
        "coin_id":  coin_id,
        "interval": interval,
        "candles":  candles,
        "ticks":    ticks,
    }


@router.get("/intervals")
async def list_intervals():
    return {"intervals": list(INTERVALS.keys())}
