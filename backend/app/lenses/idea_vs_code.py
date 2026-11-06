"""Ideia × Código: groups the base by feature status. No model call (ADR 0002).

"Isso faz?" reads the same status, so the two tabs can never contradict each other.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.domain.enums import ComparisonState, FeatureStatus, SourceType
from app.domain.idea_vs_code import IdeaVsCode, IdeaVsCodeColumns
from app.domain.product_base import ProductBase
from app.lenses.answer import load_base


def comparison_state(base: ProductBase, has_documents: bool) -> ComparisonState:
    """Read from the base itself: no extra column is stored.

    - A feature tied to a promise means the extraction had the idea AND the code.
    - Only documented_only features means there was no code.
    - Otherwise the sources tell whether the document is missing or promised nothing.
    """
    features = base.features
    if any(feature.promise_ref for feature in features):
        return ComparisonState.AVAILABLE
    if features and all(f.status == FeatureStatus.DOCUMENTED_ONLY for f in features):
        return ComparisonState.MISSING_CODE
    return ComparisonState.NO_PROMISES if has_documents else ComparisonState.MISSING_IDEA


def group_features(base: ProductBase, state: ComparisonState) -> IdeaVsCodeColumns:
    features = base.features
    if state in (ComparisonState.MISSING_IDEA, ComparisonState.NO_PROMISES):
        # No promises to compare with: everything in the code is, literally, undocumented.
        return IdeaVsCodeColumns(delivered=[], missing=[], undocumented=list(features))
    return IdeaVsCodeColumns(
        delivered=[
            f for f in features if f.status in (FeatureStatus.IMPLEMENTED, FeatureStatus.PARTIAL)
        ],
        missing=[f for f in features if f.status == FeatureStatus.DOCUMENTED_ONLY],
        undocumented=[f for f in features if f.status == FeatureStatus.UNDOCUMENTED],
    )


class IdeaVsCodeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, project_id: uuid.UUID) -> IdeaVsCode:
        stored = await load_base(self._session, project_id)
        project = await ProjectRepository(self._session).get(project_id)
        refs = await SourceRepository(self._session).file_refs(project_id)
        has_documents = any(ref.source_type != SourceType.CODE for ref in refs)

        state = comparison_state(stored.data, has_documents)
        columns = group_features(stored.data, state)
        promised = [*columns.delivered, *columns.missing]
        return IdeaVsCode(
            state=state,
            columns=columns,
            promised=len(promised),
            implemented=sum(f.status == FeatureStatus.IMPLEMENTED for f in promised),
            partial=sum(f.status == FeatureStatus.PARTIAL for f in promised),
            base_created_at=stored.created_at,
            base_outdated=project.base_outdated,
        )
