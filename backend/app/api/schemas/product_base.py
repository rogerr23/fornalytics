"""API contract for processing and the product base (DTOs, separate from the domain models)."""

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FeatureStatus, ProjectStatus, SourceType


class ProcessingStatusOut(BaseModel):
    status: ProjectStatus
    status_detail: str | None
    base_outdated: bool


class EvidenceOut(BaseModel):
    source_type: SourceType
    path: str
    line_start: int
    line_end: int
    quote: str


class FeatureOut(BaseModel):
    name: str
    description: str
    status: FeatureStatus
    promise_ref: str
    evidence: list[EvidenceOut]


class BusinessRuleOut(BaseModel):
    rule: str
    evidence: list[EvidenceOut]


class BaseFlowOut(BaseModel):
    name: str
    steps: list[str]
    evidence: list[EvidenceOut]


class ProductBaseOut(BaseModel):
    provider: str
    model: str
    created_at: datetime
    base_outdated: bool
    summary: str
    stack: list[str]
    entities: list[str]
    integrations: list[str]
    features: list[FeatureOut]
    flows: list[BaseFlowOut]
    business_rules: list[BusinessRuleOut]
