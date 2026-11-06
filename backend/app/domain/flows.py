"""Flows: step by step + a diagram. The model returns nodes and edges; the backend writes Mermaid.

The draft models double as the structured-output schema (basic types only, CLAUDE.md 4.2).
"""

from pydantic import BaseModel

from app.domain.product_base import Evidence


class FlowStep(BaseModel):
    text: str
    evidence: list[Evidence]


class FlowNode(BaseModel):
    id: str
    label: str


class FlowEdge(BaseModel):
    source: str
    target: str
    # Condition or action on the arrow ("aprovado", "não"); "" for none.
    label: str


class FlowDraft(BaseModel):
    name: str
    steps: list[FlowStep]
    nodes: list[FlowNode]
    edges: list[FlowEdge]


class FlowResult(BaseModel):
    name: str
    # The question asked, or "" for a flow that comes from the product base.
    question: str
    steps: list[FlowStep]
    # Evidence for the flow as a whole (base flows carry it at this level).
    evidence: list[Evidence]
    mermaid: str
    from_base: bool
