"""Server-Sent Events helpers (StreamingResponse, no extra library)."""

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.domain.lenses import (
    AnswerDone,
    AnswerFailed,
    CitationsChecked,
    ConversationStarted,
    LensEvent,
    TextDelta,
)


def sse_event(event: str, data: BaseModel | dict[str, Any]) -> str:
    payload = data.model_dump_json() if isinstance(data, BaseModel) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


def sse_heartbeat() -> str:
    """A comment line: keeps proxies from closing an idle stream; clients ignore it."""
    return ": ping\n\n"


def sse_response(events: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        events,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


_LENS_EVENT_NAMES: dict[type[BaseModel], str] = {
    ConversationStarted: "conversation",
    TextDelta: "delta",
    CitationsChecked: "citations",
    AnswerDone: "done",
    AnswerFailed: "error",
}


async def lens_events(events: AsyncIterator[LensEvent]) -> AsyncIterator[str]:
    """Lens answer events as SSE (contract in docs/api-events.md)."""
    async for event in events:
        yield sse_event(_LENS_EVENT_NAMES[type(event)], event)
