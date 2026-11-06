"""Priority cut: which files fit in a token budget. Used by extraction (Phase 4) and chat."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class HasTokens(Protocol):
    @property
    def path(self) -> str: ...

    @property
    def token_estimate(self) -> int: ...


@dataclass(frozen=True)
class Selection[T: HasTokens]:
    included: list[T]
    excluded: list[T]

    @property
    def included_tokens(self) -> int:
        return sum(item.token_estimate for item in self.included)


def select_within_budget[T: HasTokens](
    files: Sequence[T], budget: int, sort_key: Callable[[T], Any]
) -> Selection[T]:
    """Walk files in priority order; a file enters if it still fits, otherwise it is listed out.

    Smaller lower-priority files may still enter after a large one is left out, so the budget
    is used fully. The result is deterministic for the same input.
    """
    included: list[T] = []
    excluded: list[T] = []
    used = 0
    for item in sorted(files, key=sort_key):
        if used + item.token_estimate <= budget:
            included.append(item)
            used += item.token_estimate
        else:
            excluded.append(item)
    return Selection(included=included, excluded=excluded)
