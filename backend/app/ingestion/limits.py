"""How a project's material fits MAX_CONTEXT_TOKENS, per extraction step."""

from collections.abc import Callable, Sequence
from typing import Any

from app.domain.enums import SourceType
from app.domain.projects import ContextLimits, FileRef, GroupLimit
from app.ingestion.filters import path_priority
from app.ingestion.selection import select_within_budget


def compute_limits(files: Sequence[FileRef], budget: int) -> ContextLimits:
    """Documents feed step (a) and code feeds step (b); each step has its own budget."""
    code = [file for file in files if file.source_type == SourceType.CODE]
    documents = [file for file in files if file.source_type != SourceType.CODE]
    return ContextLimits(
        budget_per_step=budget,
        documents=_group(documents, budget, sort_key=lambda file: file.path),
        code=_group(code, budget, sort_key=lambda file: path_priority(file.path)),
    )


def _group(files: list[FileRef], budget: int, sort_key: Callable[[FileRef], Any]) -> GroupLimit:
    selection = select_within_budget(files, budget, sort_key)
    return GroupLimit(
        total_tokens=sum(file.token_estimate for file in files),
        included_tokens=selection.included_tokens,
        excluded=selection.excluded,
    )
