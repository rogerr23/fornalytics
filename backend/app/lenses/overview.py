"""Overview per lens: generated on the first opening, then served from lens_cache."""

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.db.repositories.lens_cache import LensCacheRepository
from app.db.repositories.product_bases import ProductBaseRepository
from app.db.session import SessionFactory
from app.domain.enums import CacheKind, Lens
from app.domain.lenses import AnswerDone, CitationsChecked, LensEvent, TextDelta
from app.domain.product_base import StoredProductBase
from app.lenses.answer import AnswerStream, check_citations, load_base
from app.lenses.context import overview_message
from app.llm.base import ChatMessage, LLMProvider
from app.prompts.builder import PromptBuilder, Task


@dataclass(frozen=True)
class PreparedOverview:
    project_id: uuid.UUID
    lens: Lens
    base: StoredProductBase
    cached: str | None


class OverviewService:
    def __init__(
        self, sessions: SessionFactory, provider: LLMProvider, prompts: PromptBuilder
    ) -> None:
        self._sessions = sessions
        self._provider = provider
        self._prompts = prompts

    async def prepare(self, project_id: uuid.UUID, lens: Lens) -> PreparedOverview:
        """Checks that raise plain HTTP errors (404, 409), before the stream opens."""
        async with self._sessions() as session:
            base = await load_base(session, project_id)
            cached = await LensCacheRepository(session).get(project_id, lens, CacheKind.OVERVIEW)
        return PreparedOverview(project_id, lens, base, cached)

    async def answer(self, prepared: PreparedOverview) -> AsyncIterator[LensEvent]:
        if prepared.cached is not None:
            text = prepared.cached
            yield TextDelta(text=text)
        else:
            stream = AnswerStream()
            messages = [ChatMessage(role="user", content=overview_message(prepared.base.data))]
            system = self._prompts.build(Task.OVERVIEW, prepared.lens)
            async for event in stream.run(self._provider, system, messages):
                yield event
            if stream.failed:
                return  # a broken answer is never cached
            text = stream.text
            await self._store(prepared, text)
        citations = await check_citations(self._sessions, prepared.project_id, text)
        yield CitationsChecked(citations=citations)
        yield AnswerDone(cached=prepared.cached is not None)

    async def _store(self, prepared: PreparedOverview, text: str) -> None:
        async with self._sessions() as session:
            current = await ProductBaseRepository(session).get(prepared.project_id)
            # Reprocessed while we answered: this text describes the old base, do not cache it.
            if current is None or current.created_at != prepared.base.created_at:
                return
            await LensCacheRepository(session).put(
                prepared.project_id, prepared.lens, CacheKind.OVERVIEW, text
            )
            await session.commit()
