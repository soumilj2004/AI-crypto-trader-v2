from fastapi import APIRouter
from services.fetcher import fetch_prices_batch, fetch_single, COIN_IDS

router = APIRouter(tags=["prices"])


@router.get("/prices")
async def all_prices():
    data = await fetch_prices_batch(list(COIN_IDS.keys()))
    return {"data": data}


@router.get("/price/{coin_id}")
async def single_price(coin_id: str):
    return await fetch_single(coin_id.lower())


@router.get("/coins")
async def list_coins():
    return {"coins": [
        {"id": k, "symbol": v["symbol"], "name": v["name"], "color": v["color"]}
        for k, v in COIN_IDS.items()
    ]}
