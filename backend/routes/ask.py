import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.ollama_service import stream_ollama, query_ollama

router = APIRouter(tags=["ai"])


class AskBody(BaseModel):
    question: str
    stream: bool = True


@router.post("/ask")
async def ask(body: AskBody):
    if body.stream:
        async def gen():
            async for token in stream_ollama(body.question):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache",
                                          "X-Accel-Buffering": "no"})
    answer = await query_ollama(body.question)
    return {"answer": answer}
