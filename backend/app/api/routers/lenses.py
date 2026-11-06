import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_overview_service
from app.api.schemas.lenses import ChatIn, ConversationOut, MessageOut
from app.api.sse import lens_events, sse_response
from app.domain.enums import Lens
from app.lenses.chat import ChatService
from app.lenses.overview import OverviewService

router = APIRouter(prefix="/projects/{project_id}", tags=["lenses"])

Overview = Annotated[OverviewService, Depends(get_overview_service)]
Chat = Annotated[ChatService, Depends(get_chat_service)]


@router.get("/overview", response_class=StreamingResponse)
async def overview(project_id: uuid.UUID, lens: Lens, service: Overview) -> StreamingResponse:
    """SSE: overview in the lens. Generated on the first opening, then served from the cache."""
    prepared = await service.prepare(project_id, lens)
    return sse_response(lens_events(service.answer(prepared)))


@router.post("/chat", response_class=StreamingResponse)
async def chat(project_id: uuid.UUID, body: ChatIn, service: Chat) -> StreamingResponse:
    """SSE: answer in the chosen lens, then the checked citations (docs/api-events.md)."""
    prepared = await service.prepare(
        project_id, body.lens, body.question.strip(), body.conversation_id
    )
    return sse_response(lens_events(service.answer(prepared)))


@router.get("/conversations/{conversation_id}")
async def conversation(
    project_id: uuid.UUID, conversation_id: uuid.UUID, service: Chat
) -> ConversationOut:
    messages = await service.messages(project_id, conversation_id)
    return ConversationOut(
        id=conversation_id,
        messages=[MessageOut.model_validate(m.model_dump()) for m in messages],
    )
