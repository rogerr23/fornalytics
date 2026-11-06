"""Check that a citation really exists in the material (anti-hallucination, CLAUDE.md 4.3).

A citation is valid when the file exists, the lines exist and the short quote appears inside
that line range, ignoring whitespace differences. Pure code: no IO.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from app.domain.enums import SourceType
from app.domain.product_base import Evidence

_WHITESPACE = re.compile(r"\s+")
# Models sometimes copy the "12| " prefix of the numbered rendering into the quote.
_LINE_PREFIX = re.compile(r"^\s*\d+\|\s?", re.MULTILINE)
_ELLIPSIS = ("...", "…")


class CitationProblem(StrEnum):
    FILE_NOT_FOUND = "file_not_found"
    LINES_OUT_OF_RANGE = "lines_out_of_range"
    EMPTY_QUOTE = "empty_quote"
    QUOTE_NOT_FOUND = "quote_not_found"


@dataclass(frozen=True)
class CitationCheck:
    problem: CitationProblem | None
    # Canonical path and real source type of the file, when it exists.
    path: str | None = None
    source_type: SourceType | None = None

    @property
    def valid(self) -> bool:
        return self.problem is None


@dataclass(frozen=True)
class MaterialFile:
    path: str
    source_type: SourceType
    content: str


def normalize(text: str) -> str:
    """Remove every whitespace character, so line breaks and indentation never matter."""
    return _WHITESPACE.sub("", text)


def clean_quote(quote: str) -> str:
    quote = _LINE_PREFIX.sub("", quote.strip())
    for mark in _ELLIPSIS:
        quote = quote.strip().removeprefix(mark).removesuffix(mark)
    return quote.strip().strip("\"'`“”")


def canonical_path(path: str) -> str:
    path = path.strip().strip("`").replace("\\", "/")
    while path.startswith(("./", "/")):
        path = path.removeprefix("./").removeprefix("/")
    return path


class CitationValidator:
    def __init__(self, files: Iterable[MaterialFile]) -> None:
        self._files: Mapping[str, tuple[SourceType, list[str]]] = {
            file.path: (file.source_type, file.content.split("\n")) for file in files
        }

    def check(self, path: str, line_start: int, line_end: int, quote: str) -> CitationCheck:
        path = canonical_path(path)
        found = self._files.get(path)
        if found is None:
            return CitationCheck(CitationProblem.FILE_NOT_FOUND)
        source_type, lines = found
        if not 1 <= line_start <= line_end <= len(lines):
            return CitationCheck(CitationProblem.LINES_OUT_OF_RANGE, path, source_type)
        needle = normalize(clean_quote(quote))
        if not needle:
            return CitationCheck(CitationProblem.EMPTY_QUOTE, path, source_type)
        haystack = normalize("\n".join(lines[line_start - 1 : line_end]))
        if needle not in haystack:
            return CitationCheck(CitationProblem.QUOTE_NOT_FOUND, path, source_type)
        return CitationCheck(None, path, source_type)

    def filter(self, evidence: Iterable[Evidence]) -> tuple[list[Evidence], int]:
        """Keep valid citations (with canonical path and real source type); count the dropped."""
        kept: list[Evidence] = []
        seen: set[tuple[str, int, int]] = set()
        dropped = 0
        for item in evidence:
            check = self.check(item.path, item.line_start, item.line_end, item.quote)
            if not check.valid or check.path is None or check.source_type is None:
                dropped += 1
                continue
            key = (check.path, item.line_start, item.line_end)
            if key in seen:
                continue
            seen.add(key)
            kept.append(
                item.model_copy(
                    update={
                        "path": check.path,
                        "source_type": check.source_type,
                        "quote": clean_quote(item.quote),
                    }
                )
            )
        return kept, dropped
