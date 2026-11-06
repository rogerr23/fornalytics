"""Isso o produto faz?: one structured model call, then the verdict is checked against the base."""

import uuid

from app.citations.validator import CitationValidator, MaterialFile
from app.core.config import Settings
from app.db.session import SessionFactory
from app.domain.enums import Lens
from app.domain.lenses import DoesItDraft, DoesItResult
from app.lenses.answer import load_question_context
from app.lenses.context import question_message
from app.lenses.verdict import reconcile_verdict
from app.llm.base import ChatMessage, LLMProvider
from app.prompts.builder import PromptBuilder, Task


class DoesItService:
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

    async def ask(self, project_id: uuid.UUID, question: str, lens: Lens) -> DoesItResult:
        context = await load_question_context(self._sessions, project_id, question, self._settings)
        draft = await self._provider.generate_json(
            self._prompts.build(Task.DOES_IT, lens),
            [
                ChatMessage(
                    role="user",
                    content=question_message(context.base.data, context.selected, question),
                )
            ],
            DoesItDraft,
        )
        # Evidence is checked with the strong rule (file, lines and quote), like the base.
        validator = CitationValidator(
            MaterialFile(file.path, file.source_type, file.content) for file in context.files
        )
        return reconcile_verdict(question, draft, context.base.data, validator)
