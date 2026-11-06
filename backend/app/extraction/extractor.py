"""Two-step extraction with the model: (a) promises from the idea, (b) the base from the code.

No database here: it receives the stored files and returns the final base, so it is tested
with the FakeProvider alone.
"""

from collections.abc import Awaitable, Callable, Sequence

from pydantic import BaseModel

from app.citations.validator import CitationValidator, MaterialFile
from app.domain.product_base import IdeaPromises, ProductBase
from app.domain.projects import StoredFile
from app.extraction.errors import NothingToProcess
from app.extraction.reconcile import ExtractionMode, clean_promises, reconcile
from app.ingestion.limits import select_code, select_documents
from app.ingestion.rendering import render_files
from app.llm.base import ChatMessage, LLMProvider
from app.prompts.builder import PromptBuilder, Task

Progress = Callable[[str], Awaitable[None]]


class ExtractionOutcome(BaseModel):
    base: ProductBase
    mode: ExtractionMode
    model_calls: int
    dropped_citations: int
    excluded_files: int


class ProductBaseExtractor:
    def __init__(self, provider: LLMProvider, prompts: PromptBuilder, budget: int) -> None:
        self._provider = provider
        self._prompts = prompts
        self._budget = budget

    async def extract(self, files: Sequence[StoredFile], progress: Progress) -> ExtractionOutcome:
        documents = select_documents(files, self._budget)
        code = select_code(files, self._budget)
        if not documents.included and not code.included:
            raise NothingToProcess()
        # Only what was sent to the model can be cited.
        validator = CitationValidator(
            MaterialFile(file.path, file.source_type, file.content)
            for file in [*documents.included, *code.included]
        )
        excluded = len(documents.excluded) + len(code.excluded)

        if documents.included and code.included:
            await progress("Lendo as promessas do documento da ideia (etapa 1 de 2)")
            raw = await self._ask(
                Task.EXTRACTION_IDEA, render_files(documents.included), IdeaPromises
            )
            promises, dropped_in_promises = clean_promises(raw, validator)
            await progress("Montando a base a partir do código (etapa 2 de 2)")
            mode = ExtractionMode.CODE_WITH_PROMISES
            draft = await self._ask(
                Task.EXTRACTION, _base_message(mode, code.included, promises), ProductBase
            )
            calls = 2
        else:
            promises, dropped_in_promises = None, 0
            if code.included:
                mode, material = ExtractionMode.CODE_ONLY, code.included
                await progress("Montando a base a partir do código (etapa 1 de 1)")
            else:
                mode, material = ExtractionMode.IDEA_ONLY, documents.included
                await progress("Montando a base a partir do documento da ideia (etapa 1 de 1)")
            draft = await self._ask(Task.EXTRACTION, _base_message(mode, material), ProductBase)
            calls = 1

        await progress("Conferindo as citações")
        base, dropped = reconcile(draft, mode, validator, promises)
        return ExtractionOutcome(
            base=base,
            mode=mode,
            model_calls=calls,
            dropped_citations=dropped + dropped_in_promises,
            excluded_files=excluded,
        )

    async def _ask[T: BaseModel](self, task: Task, user_message: str, schema: type[T]) -> T:
        return await self._provider.generate_json(
            self._prompts.build(task),
            [ChatMessage(role="user", content=user_message)],
            schema,
        )


def _base_message(
    mode: ExtractionMode, files: Sequence[StoredFile], promises: IdeaPromises | None = None
) -> str:
    parts = [f"MODO: {mode.value}"]
    if promises is not None:
        listed = "\n".join(f"- {p.id}: {p.name} — {p.description}" for p in promises.promises)
        parts.append(f"## Promessas do documento da ideia\n{listed or '(nenhuma promessa)'}")
    parts.append(f"## Material\n{render_files(files)}")
    return "\n\n".join(parts)
