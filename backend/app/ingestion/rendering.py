"""Render files with numbered lines, the format the model cites from (CLAUDE.md, section 4.1)."""

from collections.abc import Iterable
from typing import Protocol


class HasContent(Protocol):
    @property
    def path(self) -> str: ...

    @property
    def content(self) -> str: ...


def render_file(path: str, content: str) -> str:
    lines = content.split("\n")
    numbered = "\n".join(f"{number}| {line}" for number, line in enumerate(lines, 1))
    return f"=== {path} ===\n{numbered}"


def render_files(files: Iterable[HasContent]) -> str:
    return "\n\n".join(render_file(file.path, file.content) for file in files)
