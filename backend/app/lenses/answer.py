"""Pieces shared by the lens use cases: base lookup, streaming and citation checks."""

import logging
import uuid
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.markers import check_markers, find_markers
from app.core.config import Settings
from app.core.errors import AppError
from app.db.repositories.product_bases import ProductBaseRepository
from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.db.session import SessionFactory
from app.domain.lenses import AnswerFailed, LensEvent, TextCitation, TextDelta
from app.domain.product_base import StoredProductBase
from app.domain.projects import StoredFile
from app.lenses.context import select_chat_files
from app.lenses.errors import BaseNotReady
from app.llm.base import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

UNEXPECTED_ERROR = "Erro inesperado ao gerar a resposta. Tente de novo."
EMPTY_ANSWER = "A IA devolveu uma resposta vazia. Tente de novo."


async def load_base(session: AsyncSession, project_id: uuid.UUID) -> StoredProductBase:
    """The project's base; lenses answer from it even when it is outdated."""
    await ProjectRepository(session).get(project_id)  # 404 for an unknown project
    base = await ProductBaseRepository(session).get(project_id)
    if base is None:
        raise BaseNotReady()
    return base


class AnswerStream:
    """Streams the model answer as TextDelta events and keeps the full text.

    The stream is already open when the model fails, so errors become an AnswerFailed event
    (with the friendly message) instead of an HTTP error.
    """

    def __init__(self) -> None:
        self.text = ""
        self.failed = False

    async def run(
        self, provider: LLMProvider, system: str, messages: Sequence[ChatMessage]
    ) -> AsyncIterator[LensEvent]:
        try:
            async for chunk in provider.stream(system, messages):
                self.text += chunk
                yield TextDelta(text=chunk)
        except AppError as exc:
            logger.warning("Answer failed: %s", type(exc).__name__)
            self.failed = True
            yield AnswerFailed(message=exc.message)
            return
        except Exception:
            logger.exception("Answer failed unexpectedly")
            self.failed = True
            yield AnswerFailed(message=UNEXPECTED_ERROR)
            return
        if not self.text.strip():
            self.failed = True
            yield AnswerFailed(message=EMPTY_ANSWER)


async def check_citations(
    sessions: SessionFactory, project_id: uuid.UUID, text: str
) -> list[TextCitation]:
    """Check every [[path:Lx-Ly]] marker against the project's files."""
    markers = find_markers(text)
    if not markers:
        return []
    async with sessions() as session:
        files = await SourceRepository(session).files(project_id, {m.path for m in markers})
    line_counts = {file.path: file.content.count("\n") + 1 for file in files}
    return check_markers(markers, line_counts)


@dataclass(frozen=True)
class QuestionContext:
    """What a one-shot question (side by side, "Isso faz?") needs: base, files, selection."""

    base: StoredProductBase
    files: list[StoredFile]
    selected: list[StoredFile]

    @property
    def line_counts(self) -> dict[str, int]:
        return {file.path: file.content.count("\n") + 1 for file in self.files}


async def load_question_context(
    sessions: SessionFactory, project_id: uuid.UUID, question: str, settings: Settings
) -> QuestionContext:
    """Base + the relevant files for the question, with the chat limits (CLAUDE.md, 4.4)."""
    async with sessions() as session:
        base = await load_base(session, project_id)
        files = await SourceRepository(session).files(project_id)
    selected = select_chat_files(
        question,
        base.data,
        files,
        max_files=settings.chat_max_files,
        max_tokens=settings.chat_context_tokens,
    )
    return QuestionContext(base=base, files=files, selected=selected)
