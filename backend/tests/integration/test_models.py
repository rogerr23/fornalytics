from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project, Source, SourceFile
from app.domain.enums import ProjectStatus, SourceType


async def test_deleting_project_cascades_to_sources_and_files(db_session: AsyncSession) -> None:
    project = Project(name="Loja demo")
    db_session.add(project)
    await db_session.flush()
    source = Source(project_id=project.id, type=SourceType.CODE, filename="loja.zip")
    db_session.add(source)
    await db_session.flush()
    db_session.add(
        SourceFile(source_id=source.id, path="README.md", content="# Loja", token_estimate=2)
    )
    await db_session.flush()

    assert project.status == ProjectStatus.DRAFT

    await db_session.execute(delete(Project).where(Project.id == project.id))

    remaining_sources = await db_session.scalar(select(func.count()).select_from(Source))
    remaining_files = await db_session.scalar(select(func.count()).select_from(SourceFile))
    assert remaining_sources == 0
    assert remaining_files == 0
