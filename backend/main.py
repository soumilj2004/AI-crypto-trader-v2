import asyncio
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routes.prices  import router as prices_router
from routes.ask     import router as ask_router
from routes.history import router as history_router
from services.fetcher    import fetch_prices_batch, COIN_IDS
from services.broadcaster import manager
from db.database import init_db, save_prices


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(price_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="CryptoTrader v2 API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices_router, prefix="/api")
app.include_router(ask_router,    prefix="/api")
app.include_router(history_router, prefix="/api")

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND):
    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(FRONTEND, "index.html"))

    @app.get("/{path:path}")
    async def catch_all(path: str):
        f = os.path.join(FRONTEND, path)
        if os.path.isfile(f):
            return FileResponse(f)
        return FileResponse(os.path.join(FRONTEND, "index.html"))


@app.websocket("/ws/prices")
async def ws_prices(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ── price broadcast loop ──────────────────────────────────────────────────────
_intervals = [1, 5, 15, 30, 60]          # seconds
_tick_counter = 0

async def price_loop():
    global _tick_counter
    SYMBOLS = list(COIN_IDS.keys())
    while True:
        try:
            prices = await fetch_prices_batch(SYMBOLS)
            if prices:
                await save_prices(prices)
                payload = json.dumps({"type": "prices", "data": prices,
                                      "ts": _tick_counter})
                await manager.broadcast(payload)
                _tick_counter += 1
        except Exception as e:
            print(f"[loop] {e}")
        await asyncio.sleep(1)          # tick every 1 s; clients filter by their chosen interval
