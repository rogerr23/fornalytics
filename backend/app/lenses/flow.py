"""Flows: the base flows as straight diagrams (no AI) and a flow on demand (one call)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.validator import CitationValidator, MaterialFile
from app.core.config import Settings
from app.db.session import SessionFactory
from app.domain.enums import Lens
from app.domain.flows import FlowDraft, FlowResult, FlowStep
from app.domain.product_base import ProductBase
from app.lenses.answer import load_base, load_question_context
from app.lenses.context import question_message
from app.lenses.mermaid import build_mermaid, linear_mermaid
from app.llm.base import ChatMessage, LLMProvider
from app.prompts.builder import PromptBuilder, Task

MAX_STEPS = 10
MAX_NODES = 12


def base_flows(base: ProductBase) -> list[FlowResult]:
    """Flows already in the product base, drawn as a straight line. No model call."""
    return [
        FlowResult(
            name=flow.name,
            question="",
            steps=[FlowStep(text=step, evidence=[]) for step in flow.steps],
            evidence=flow.evidence,
            mermaid=linear_mermaid(flow.steps),
            from_base=True,
        )
        for flow in base.flows
    ]


def flow_result(question: str, draft: FlowDraft, validator: CitationValidator) -> FlowResult:
    """Trim to the limits, check every step citation and build the Mermaid text."""
    steps = [
        FlowStep(text=step.text.strip(), evidence=validator.filter(step.evidence)[0])
        for step in draft.steps[:MAX_STEPS]
        if step.text.strip()
    ]
    nodes = draft.nodes[:MAX_NODES]
    return FlowResult(
        name=draft.name.strip() or question,
        question=question,
        steps=steps,
        evidence=[],
        mermaid=build_mermaid(nodes, draft.edges, [step.text for step in steps]),
        from_base=False,
    )


class BaseFlowsService:
    """No AI provider here: the base flows show up even without a model configured."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, project_id: uuid.UUID) -> list[FlowResult]:
        stored = await load_base(self._session, project_id)
        return base_flows(stored.data)


class FlowService:
    def __init__(
        self,
        sessions: SessionFactory,
        provider: LLMProvider,
        prompts: PromptBuilder,
        settings: Settings,
    ) -> None:
        self._sessions = sessions
        self._provider = provider
        self._prompts = prompts
        self._settings = settings

    async def ask(self, project_id: uuid.UUID, question: str, lens: Lens) -> FlowResult:
        context = await load_question_context(self._sessions, project_id, question, self._settings)
        message = question_message(context.base.data, context.selected, question)
        draft = await self._provider.generate_json(
            self._prompts.build(Task.FLOW, lens),
            [ChatMessage(role="user", content=message)],
            FlowDraft,
        )
        validator = CitationValidator(
            MaterialFile(file.path, file.source_type, file.content) for file in context.files
        )
        return flow_result(question, draft, validator)
