"""What one eval run stores (backend/evals/runs/<run>.json), so a run can resume."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CheckOut(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class CitationOut(BaseModel):
    marker: str
    valid: bool


class LensText(BaseModel):
    lens: str
    text: str
    citations: list[CitationOut] = []


class Record(BaseModel):
    id: str
    kind: str
    lens: str | None
    question: str
    status: Literal["ok", "error"]
    error: str | None = None
    seconds: float = 0
    answers: list[LensText] = []
    verdict: str | None = None
    feature: str | None = None
    evidence: int = 0
    checks: list[CheckOut] = []

    @property
    def passed(self) -> bool:
        return self.status == "ok" and all(check.passed for check in self.checks)


class Run(BaseModel):
    name: str
    started_at: datetime
    provider: str
    model: str
    project: str
    idea_vs_code: list[CheckOut] = []
    records: dict[str, Record] = {}
