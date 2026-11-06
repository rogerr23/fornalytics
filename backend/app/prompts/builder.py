"""Builds system prompts as base + lens + task, always in that order (Builder)."""

from enum import StrEnum
from functools import cache
from pathlib import Path

from app.domain.enums import Lens

PROMPTS_DIR = Path(__file__).resolve().parent


class Task(StrEnum):
    """One file per task in this folder (task.value + '.md')."""

    EXTRACTION_IDEA = "extraction_idea"
    EXTRACTION = "extraction"


@cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


class PromptBuilder:
    def build(self, task: Task, lens: Lens | None = None) -> str:
        parts = [load_prompt("base")]
        if lens is not None:
            parts.append(load_prompt(f"lens_{lens.value}"))
        parts.append(load_prompt(task.value))
        return "\n\n---\n\n".join(parts)
