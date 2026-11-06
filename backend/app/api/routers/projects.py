import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_project_service
from app.api.schemas.projects import ProjectCreate, ProjectDetailOut, ProjectOut
from app.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])

Service = Annotated[ProjectService, Depends(get_project_service)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(body: ProjectCreate, service: Service) -> ProjectOut:
    project = await service.create(body.name)
    return ProjectOut.model_validate(project.model_dump())


@router.get("")
async def list_projects(service: Service) -> list[ProjectOut]:
    return [ProjectOut.model_validate(p.model_dump()) for p in await service.list()]


@router.get("/{project_id}")
async def get_project(project_id: uuid.UUID, service: Service) -> ProjectDetailOut:
    detail = await service.detail(project_id)
    return ProjectDetailOut.model_validate(
        {
            **detail.project.model_dump(),
            "sources": [s.model_dump() for s in detail.sources],
            "limits": detail.limits.model_dump(),
        }
    )
