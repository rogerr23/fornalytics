"""The product base: one structured description of the product that every lens reads.

These models double as the structured-output schema sent to the model, so they only use
basic types, enums, lists and nested objects (CLAUDE.md, section 4.2).
"""

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FeatureStatus, SourceType


class Evidence(BaseModel):
    """A citation: a short quote that must appear inside lines [line_start, line_end] of path."""

    source_type: SourceType
    path: str
    line_start: int
    line_end: int
    quote: str


class Promise(BaseModel):
    """A feature the idea document promises (extraction step a)."""

    id: str
    name: str
    description: str
    evidence: list[Evidence]


class IdeaPromises(BaseModel):
    promises: list[Promise]


class Feature(BaseModel):
    name: str
    description: str
    status: FeatureStatus
    # Id of the promise this feature answers (P1, P2...), or "" when it was never promised.
    promise_ref: str
    evidence: list[Evidence]


class BusinessRule(BaseModel):
    rule: str
    evidence: list[Evidence]


class BaseFlow(BaseModel):
    name: str
    steps: list[str]
    evidence: list[Evidence]


class ProductBase(BaseModel):
    summary: str
    stack: list[str]
    entities: list[str]
    integrations: list[str]
    features: list[Feature]
    flows: list[BaseFlow]
    business_rules: list[BusinessRule]


class StoredProductBase(BaseModel):
    """A saved base plus where it came from."""

    data: ProductBase
    provider: str
    model: str
    created_at: datetime
