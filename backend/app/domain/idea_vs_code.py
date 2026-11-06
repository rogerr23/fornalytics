"""Ideia × Código: the product base features grouped by status (no model call)."""

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import ComparisonState
from app.domain.product_base import Feature


class IdeaVsCodeColumns(BaseModel):
    # ✅ promised and implemented (partial ones included, flagged by their status)
    delivered: list[Feature]
    # ⚠️ promised and not found in the code
    missing: list[Feature]
    # 🔍 in the code but not in the idea document
    undocumented: list[Feature]


class IdeaVsCode(BaseModel):
    state: ComparisonState
    columns: IdeaVsCodeColumns
    promised: int
    implemented: int
    partial: int
    base_created_at: datetime
    base_outdated: bool
