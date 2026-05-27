<img width="1199" height="240" alt="image" src="https://github.com/user-attachments/assets/5cbd6a85-a3d1-4fd5-8033-f6cb97c854c8" />


A production-grade, real-time cryptocurrency trading terminal built with FastAPI and vanilla JS with localized LLM assistance. 
---

## Quickstart (one command)

```bash
python start.py
```

The launcher automatically creates a virtual environment, installs all dependencies, and opens the app in your browser. No manual setup needed.

---

<img width="1910" height="867" alt="image" src="https://github.com/user-attachments/assets/d3b916e1-5c28-4cc1-b19f-4fb813255c96" />

<img width="1900" height="859" alt="image" src="https://github.com/user-attachments/assets/7836896a-463b-4b23-91be-ac7939564ec9" />

<img width="1915" height="837" alt="image" src="https://github.com/user-attachments/assets/210d92c4-6974-4d12-9eb3-9aa4aa801e81" />


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

## AI Assistance

<img width="405" height="826" alt="image" src="https://github.com/user-attachments/assets/8a904c2c-eb1b-47aa-8026-c338c7b41b7f" />


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
