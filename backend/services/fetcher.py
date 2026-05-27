import httpx
import asyncio
import time
from datetime import datetime

# ── coin registry ──────────────────────────────────────────────────────────────
COIN_IDS: dict[str, dict] = {
    "bitcoin":      {"symbol": "BTC",  "name": "Bitcoin",       "color": "#F7931A"},
    "ethereum":     {"symbol": "ETH",  "name": "Ethereum",      "color": "#627EEA"},
    "solana":       {"symbol": "SOL",  "name": "Solana",        "color": "#9945FF"},
    "binancecoin":  {"symbol": "BNB",  "name": "BNB",           "color": "#F3BA2F"},
    "ripple":       {"symbol": "XRP",  "name": "XRP",           "color": "#00AAE4"},
    "cardano":      {"symbol": "ADA",  "name": "Cardano",       "color": "#0033AD"},
    "dogecoin":     {"symbol": "DOGE", "name": "Dogecoin",      "color": "#C2A633"},
    "avalanche-2":  {"symbol": "AVAX", "name": "Avalanche",     "color": "#E84142"},
    "chainlink":    {"symbol": "LINK", "name": "Chainlink",     "color": "#2A5ADA"},
    "polkadot":     {"symbol": "DOT",  "name": "Polkadot",      "color": "#E6007A"},
}

# ── shared cache ──────────────────────────────────────────────────────────────
_cache: dict = {}
_last_fetch: float = 0.0
_lock = asyncio.Lock()
CACHE_TTL = 12          # seconds — CoinGecko free tier allows ~30 req/min

# ── simulated micro-movement for sub-TTL ticks ────────────────────────────────
import random

def _nudge(price: float) -> float:
    """Tiny realistic ±0.03 % random walk to animate 1-second bars."""
    return price * (1 + random.gauss(0, 0.0003))


async def fetch_prices_batch(symbols: list[str]) -> dict:
    global _cache, _last_fetch
    async with _lock:
        now = time.monotonic()
        if now - _last_fetch >= CACHE_TTL:
            # Real fetch from CoinGecko
            ids = ",".join(s for s in symbols if s in COIN_IDS)
            url = (
                "https://api.coingecko.com/api/v3/simple/price"
                f"?ids={ids}&vs_currencies=usd"
                "&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
            )
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.get(url)
                    if r.status_code == 200:
                        raw = r.json()
                        new_cache = {}
                        for cid, meta in COIN_IDS.items():
                            if cid in raw:
                                d = raw[cid]
                                new_cache[cid] = {
                                    "id":         cid,
                                    "symbol":     meta["symbol"],
                                    "name":       meta["name"],
                                    "color":      meta["color"],
                                    "price":      d.get("usd", 0),
                                    "change_24h": round(d.get("usd_24h_change", 0), 4),
                                    "volume_24h": d.get("usd_24h_vol", 0),
                                    "market_cap": d.get("usd_market_cap", 0),
                                    "timestamp":  datetime.utcnow().isoformat(),
                                }
                        if new_cache:
                            _cache = new_cache
                            _last_fetch = now
            except Exception as e:
                print(f"[fetcher] CoinGecko error: {e}")
        else:
            # Sub-TTL tick: nudge prices slightly for live feel
            for cid in _cache:
                _cache[cid]["price"] = round(_nudge(_cache[cid]["price"]), 8)
                _cache[cid]["timestamp"] = datetime.utcnow().isoformat()

    return dict(_cache)


async def fetch_single(coin_id: str) -> dict:
    data = await fetch_prices_batch([coin_id])
    return data.get(coin_id, {})
