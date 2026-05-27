import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL   = os.getenv("OLLAMA_HOST",  "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

SYSTEM = """You are Nexus, a senior quantitative analyst and crypto market strategist at a top-tier hedge fund.
Your expertise spans technical analysis, on-chain metrics, macro economics, DeFi protocols, market microstructure, and trading psychology.

Guidelines:
- Be concise, data-driven and direct. No fluff.
- Use bullet points for multi-point answers.
- Cite specific indicators (RSI, MACD, volume profiles, funding rates) when relevant.
- Maximum 200 words unless user explicitly asks for detail.
- Never give financial advice. Provide analysis only.
- Start immediately with the insight — no greetings or preamble.
"""


async def stream_ollama(prompt: str):
    payload = {
        "model":    OLLAMA_MODEL,
        "messages": [
            {"role": "system",  "content": SYSTEM},
            {"role": "user",    "content": prompt},
        ],
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except Exception:
                        continue
    except Exception as e:
        yield f"\n\n⚠️ Nexus AI offline — {e}\nRun `ollama serve` in a terminal."


async def query_ollama(prompt: str) -> str:
    return "".join([t async for t in stream_ollama(prompt)])
