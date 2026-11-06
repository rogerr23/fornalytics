"""Builds system prompts as base + lens + task, always in that order (Builder)."""

from collections.abc import Iterable
from enum import StrEnum
from functools import cache
from pathlib import Path

from app.domain.enums import Lens

PROMPTS_DIR = Path(__file__).resolve().parent


class Task(StrEnum):
    """One file per task in this folder (task.value + '.md')."""

    EXTRACTION_IDEA = "extraction_idea"
    EXTRACTION = "extraction"
    OVERVIEW = "overview"
    CHAT = "chat"
    COMPARE = "compare_lenses"
    DOES_IT = "does_it"


@cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


class PromptBuilder:
    def build(self, task: Task, lens: Lens | None = None) -> str:
        return self.build_for_lenses(task, [] if lens is None else [lens])

    def build_for_lenses(self, task: Task, lenses: Iterable[Lens]) -> str:
        """Base + every given lens + task (side by side describes the three lenses at once)."""
        parts = [load_prompt("base")]
        parts.extend(load_prompt(f"lens_{lens.value}") for lens in lenses)
        parts.append(load_prompt(task.value))
        return "\n\n---\n\n".join(parts)
