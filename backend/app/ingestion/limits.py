"""How a project's material fits MAX_CONTEXT_TOKENS, per extraction step."""

from collections.abc import Sequence
from typing import Protocol

from app.domain.enums import SourceType
from app.domain.projects import ContextLimits, FileRef, GroupLimit
from app.ingestion.filters import path_priority
from app.ingestion.selection import Selection, select_within_budget


class StepFile(Protocol):
    @property
    def path(self) -> str: ...

    @property
    def token_estimate(self) -> int: ...

    @property
    def source_type(self) -> SourceType: ...


def select_documents[T: StepFile](files: Sequence[T], budget: int) -> Selection[T]:
    """Step (a): idea documents, transcripts and pasted text, in path order."""
    documents = [file for file in files if file.source_type != SourceType.CODE]
    return select_within_budget(documents, budget, sort_key=lambda file: file.path)


def select_code[T: StepFile](files: Sequence[T], budget: int) -> Selection[T]:
    """Step (b): code files, README and routes first (filters.path_priority)."""
    code = [file for file in files if file.source_type == SourceType.CODE]
    return select_within_budget(code, budget, sort_key=lambda file: path_priority(file.path))


def compute_limits(files: Sequence[FileRef], budget: int) -> ContextLimits:
    """Documents feed step (a) and code feeds step (b); each step has its own budget."""
    return ContextLimits(
        budget_per_step=budget,
        documents=_group(select_documents(files, budget)),
        code=_group(select_code(files, budget)),
    )


def _group(selection: Selection[FileRef]) -> GroupLimit:
    return GroupLimit(
        total_tokens=selection.included_tokens
        + sum(file.token_estimate for file in selection.excluded),
        included_tokens=selection.included_tokens,
        excluded=selection.excluded,
    )
