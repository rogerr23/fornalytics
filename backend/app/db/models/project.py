from sqlalchemy import String, Text, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPrimaryKey, text_enum
from app.domain.enums import ProjectStatus


class Project(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[ProjectStatus] = mapped_column(
        text_enum(ProjectStatus, "project_status"), default=ProjectStatus.DRAFT
    )
    status_detail: Mapped[str | None] = mapped_column(Text)
    # Sources changed after the last product base was built (see docs/data-model.md).
    base_outdated: Mapped[bool] = mapped_column(default=False, server_default=false())
