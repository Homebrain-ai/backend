"""
app/api/chat.py
- Add heartbeat to chat_stream() ?
"""

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.dependencies.container import GraphDep
from app.schemas.api import ChatRequest
from app.schemas.events import ErrorEvent, StreamEvent
from app.services.chat import chat_turn_stream

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "homebrain-backend",
    }


def sse(event: StreamEvent) -> str:
    payload = event.model_dump()
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


type Graph = Any


@router.post("/chat/stream")
async def chat_stream(chat_request: ChatRequest, request: Request, graph: GraphDep) -> StreamingResponse:
    thread_id, event_gen = chat_turn_stream(graph, chat_request.thread_id, chat_request.message)
    log.info("chat stream start", extra={"thread_id": thread_id, "msg_len": len(chat_request.message)})

    async def event_stream() -> AsyncIterator[str]:
        try:
            for event in event_gen:
                if await request.is_disconnected():
                    log.info("SSE client disconnected", extra={"thread_id": thread_id})
                    break
                yield sse(event)
        except Exception:
            log.exception("SSE stream failed", extra={"thread_id": thread_id})
            yield sse(ErrorEvent(message="stream failed", thread_id=thread_id))

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)
