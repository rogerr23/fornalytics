"""Side by side: the same question in the three lenses, in ONE structured model call."""

import uuid

from app.citations.markers import check_markers, find_markers
from app.core.config import Settings
from app.db.session import SessionFactory
from app.domain.enums import Lens
from app.domain.lenses import CompareDraft, CompareResult, LensAnswer
from app.lenses.answer import load_question_context
from app.lenses.context import question_message
from app.llm.base import ChatMessage, LLMProvider
from app.llm.errors import InvalidModelOutput
from app.prompts.builder import PromptBuilder, Task


class CompareService:
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

    async def compare(self, project_id: uuid.UUID, question: str) -> CompareResult:
        context = await load_question_context(self._sessions, project_id, question, self._settings)
        draft = await self._provider.generate_json(
            self._prompts.build_for_lenses(Task.COMPARE, list(Lens)),
            [
                ChatMessage(
                    role="user",
                    content=question_message(context.base.data, context.selected, question),
                )
            ],
            CompareDraft,
        )
        line_counts = context.line_counts
        answers = []
        for lens in Lens:
            text = getattr(draft, lens.value).strip()
            if not text:
                raise InvalidModelOutput()
            answers.append(
                LensAnswer(
                    lens=lens,
                    text=text,
                    citations=check_markers(find_markers(text), line_counts),
                )
            )
        return CompareResult(question=question, answers=answers)
