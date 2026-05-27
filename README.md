# CryptoTrader v2 — Professional Crypto Terminal

A production-grade, real-time cryptocurrency trading terminal built with FastAPI and vanilla JS. Inspired by TradingView and Zerodha Kite.

---

## Quickstart (one command)

```bash
python start.py
```

The launcher automatically creates a virtual environment, installs all dependencies, and opens the app in your browser. No manual setup needed.

---

## Features

| | Feature |
|---|---|
| 📡 | **WebSocket live feed** — prices update every second via WebSocket |
| 📊 | **Professional chart** — line / area modes with MA20, MA50, Bollinger Bands |
| ⏱ | **10 time intervals** — 1s, 5s, 15s, 30s, 1m, 5m, 15m, 1h, 4h, 1D |
| 🪙 | **10 assets** — BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, LINK, DOT |
| 📈 | **Compare mode** — overlay multiple coins on one chart |
| 📉 | **Volume panel** — live volume bars below price chart |
| 📋 | **Order book** — live simulated order book with depth bars |
| 🧮 | **Stats panel** — price, market cap, volume, RSI estimate, volatility |
| 🤖 | **Nexus AI** — streaming AI assistant powered by Ollama (Mistral) |
| 💾 | **SQLite history** — 7 days of price history stored locally, auto-purged |
| 🎯 | **Watchlist** — searchable sidebar, click any asset to chart it |

---

## Project Structure

```
crypto-trader-v2/
├── start.py                   ← ONE-CLICK LAUNCHER
├── .env.example               ← Config template
├── .gitignore
├── README.md
│
├── backend/
│   ├── main.py                ← FastAPI app + WebSocket price loop
│   ├── requirements.txt
│   ├── routes/
│   │   ├── prices.py          ← GET /api/prices, /api/price/{id}, /api/coins
│   │   ├── ask.py             ← POST /api/ask  (streaming SSE)
│   │   └── history.py         ← GET /api/history/{id}?interval=1m
│   ├── services/
│   │   ├── fetcher.py         ← CoinGecko client + cache + micro-movement
│   │   ├── broadcaster.py     ← WebSocket connection manager
│   │   └── ollama_service.py  ← Streaming Ollama client
│   └── db/
│       └── database.py        ← aiosqlite: tick storage + OHLCV aggregation
│
└── frontend/
    └── index.html             ← Full SPA — zero build step
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/prices` | All 10 coin prices |
| `GET` | `/api/price/{coin_id}` | Single coin |
| `GET` | `/api/coins` | Coin registry |
| `GET` | `/api/history/{coin_id}?interval=1m` | OHLCV candle history |
| `GET` | `/api/intervals` | List valid interval keys |
| `POST` | `/api/ask` | AI assistant (streaming SSE) |
| `WS` | `/ws/prices` | Live price WebSocket |
| `GET` | `/docs` | Auto-generated Swagger UI |

---

## AI Assistant Setup

Requires [Ollama](https://ollama.com) running locally.

```bash
# 1. Install Ollama from https://ollama.com
# 2. Pull a model
ollama pull mistral

# 3. Start Ollama (keep this running in a separate terminal)
ollama serve
```

The AI tab in the app will work automatically. Configure the model in `.env`:

```
OLLAMA_MODEL=llama3
```

---

## Configuration

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `mistral` | Model name |

---

## Tech Stack

- **Backend** — FastAPI, uvicorn, aiosqlite, httpx, websockets
- **Frontend** — Vanilla JS, Chart.js 4, Luxon (time adapter)
- **Data** — CoinGecko API (free, no API key required)
- **AI** — Ollama (local LLM, any model)
- **Storage** — SQLite (automatic, zero config)

---

## License

MIT

---

**Author:** Soumil Jain · [github.com/soumilj2004](https://github.com/soumilj2004)
