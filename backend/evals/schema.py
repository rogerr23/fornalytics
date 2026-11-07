"""Format of questions.yaml (validated with Pydantic, so a typo fails fast)."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from app.domain.enums import Lens, Verdict

QUESTIONS_FILE = Path(__file__).resolve().parent / "questions.yaml"

Kind = Literal["chat", "does_it", "compare", "flow"]
CitationRule = Literal["required", "forbidden", "any"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Expect(_Strict):
    mentions_any: list[str] = []
    must_not_mention: list[str] = []
    not_found: bool = False
    citations: CitationRule | None = None
    verdict: Verdict | None = None
    feature_any: list[str] = []
    no_feature: bool = False


class Question(_Strict):
    id: str
    kind: Kind
    lens: Lens | None = None
    question: str
    expect: Expect = Expect()
    demo: bool = False
    core: bool = False

    @model_validator(mode="after")
    def _lens_matches_kind(self) -> "Question":
        if self.kind == "compare" and self.lens is not None:
            raise ValueError(f"{self.id}: compare answers in the three lenses; remove 'lens'")
        if self.kind != "compare" and self.lens is None:
            raise ValueError(f"{self.id}: '{self.kind}' needs a lens")
        if self.kind == "does_it" and self.expect.verdict is None:
            raise ValueError(f"{self.id}: does_it needs expect.verdict")
        return self


class IdeaVsCodeExpect(_Strict):
    delivered: list[list[str]]
    missing: list[list[str]]
    undocumented: list[list[str]]


class EvalSet(_Strict):
    project: str
    idea_vs_code: IdeaVsCodeExpect
    questions: list[Question]

    @model_validator(mode="after")
    def _unique_ids(self) -> "EvalSet":
        ids = [q.id for q in self.questions]
        repeated = {i for i in ids if ids.count(i) > 1}
        if repeated:
            raise ValueError(f"repeated ids: {sorted(repeated)}")
        return self


def load_eval_set(path: Path = QUESTIONS_FILE) -> EvalSet:
    return EvalSet.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
