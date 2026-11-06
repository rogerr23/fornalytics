"""Citation markers inside streamed answers: [[path:L10-L20]] or [[path:L10]].

The text is streamed as is; once it ends, every marker is checked here and the result goes
in the final `citations` event (CLAUDE.md, section 4.3). Pure code: no IO.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from app.citations.validator import CitationProblem, canonical_path
from app.domain.lenses import TextCitation

MARKER = re.compile(r"\[\[([^\[\]\n]+?):L(\d+)(?:\s*-\s*L?(\d+))?\]\]")


@dataclass(frozen=True)
class Marker:
    text: str
    path: str
    line_start: int
    line_end: int


def find_markers(text: str) -> list[Marker]:
    """Every distinct marker, in order of appearance."""
    found: dict[str, Marker] = {}
    for match in MARKER.finditer(text):
        start = int(match.group(2))
        end = int(match.group(3) or start)
        found.setdefault(
            match.group(0), Marker(match.group(0), canonical_path(match.group(1)), start, end)
        )
    return list(found.values())


def check_markers(markers: list[Marker], line_counts: Mapping[str, int]) -> list[TextCitation]:
    """Valid when the file exists in the project and the lines exist in it.

    Markers carry no quote, so this check is weaker than the one on the product base.
    """
    return [_check(marker, line_counts.get(marker.path)) for marker in markers]


def _check(marker: Marker, line_count: int | None) -> TextCitation:
    if line_count is None:
        problem: CitationProblem | None = CitationProblem.FILE_NOT_FOUND
    elif not 1 <= marker.line_start <= marker.line_end <= line_count:
        problem = CitationProblem.LINES_OUT_OF_RANGE
    else:
        problem = None
    return TextCitation(
        marker=marker.text,
        path=marker.path,
        line_start=marker.line_start,
        line_end=marker.line_end,
        valid=problem is None,
        problem=problem.value if problem else None,
    )
