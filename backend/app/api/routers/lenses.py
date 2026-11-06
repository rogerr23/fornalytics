import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import (
    get_base_flows_service,
    get_chat_service,
    get_compare_service,
    get_does_it_service,
    get_flow_service,
    get_idea_vs_code_service,
    get_overview_service,
)
from app.api.schemas.lenses import (
    ChatIn,
    CompareOut,
    ConversationOut,
    DoesItIn,
    DoesItOut,
    FlowIn,
    FlowOut,
    IdeaVsCodeOut,
    MessageOut,
    QuestionIn,
)
from app.api.sse import lens_events, sse_response
from app.domain.enums import Lens
from app.lenses.chat import ChatService
from app.lenses.compare import CompareService
from app.lenses.does_it import DoesItService
from app.lenses.flow import BaseFlowsService, FlowService
from app.lenses.idea_vs_code import IdeaVsCodeService
from app.lenses.overview import OverviewService

router = APIRouter(prefix="/projects/{project_id}", tags=["lenses"])

Overview = Annotated[OverviewService, Depends(get_overview_service)]
Chat = Annotated[ChatService, Depends(get_chat_service)]
Compare = Annotated[CompareService, Depends(get_compare_service)]
DoesIt = Annotated[DoesItService, Depends(get_does_it_service)]
BaseFlows = Annotated[BaseFlowsService, Depends(get_base_flows_service)]
FlowDep = Annotated[FlowService, Depends(get_flow_service)]
IdeaVsCodeDep = Annotated[IdeaVsCodeService, Depends(get_idea_vs_code_service)]


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


@router.post("/compare-lenses")
async def compare_lenses(project_id: uuid.UUID, body: QuestionIn, service: Compare) -> CompareOut:
    """The same question in the three lenses, in one model call (no streaming)."""
    result = await service.compare(project_id, body.question.strip())
    return CompareOut.model_validate(result.model_dump())


@router.post("/does-it")
async def does_it(project_id: uuid.UUID, body: DoesItIn, service: DoesIt) -> DoesItOut:
    """sim | nao | parcialmente, always in agreement with the product base."""
    result = await service.ask(project_id, body.question.strip(), body.lens)
    return DoesItOut.model_validate(result.model_dump())


@router.get("/idea-vs-code")
async def idea_vs_code(project_id: uuid.UUID, service: IdeaVsCodeDep) -> IdeaVsCodeOut:
    """Base features grouped by status: promised and done, promised only, undocumented."""
    result = await service.get(project_id)
    return IdeaVsCodeOut.model_validate(result.model_dump())


@router.get("/flows")
async def base_flows(project_id: uuid.UUID, service: BaseFlows) -> list[FlowOut]:
    """Flows already in the product base, with a straight Mermaid diagram (no AI call)."""
    return [FlowOut.model_validate(flow.model_dump()) for flow in await service.list(project_id)]


@router.post("/flow")
async def flow(project_id: uuid.UUID, body: FlowIn, service: FlowDep) -> FlowOut:
    """'O que acontece quando…?': steps + nodes and edges from the model; Mermaid built here."""
    result = await service.ask(project_id, body.question.strip(), body.lens)
    return FlowOut.model_validate(result.model_dump())
