from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active = [c for c in self.active if c is not ws]

    async def broadcast(self, msg: str):
        dead = []
        for c in self.active:
            try:
                await c.send_text(msg)
            except Exception:
                dead.append(c)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()
