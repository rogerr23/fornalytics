import uuid

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm_provider
from app.db.repositories.product_bases import ProductBaseRepository
from app.domain.enums import FeatureStatus
from app.domain.product_base import Feature, ProductBase


def feature(name: str, status: FeatureStatus, ref: str) -> Feature:
    return Feature(name=name, description=name, status=status, promise_ref=ref, evidence=[])


BASE = ProductBase(
    summary="Loja",
    stack=[],
    entities=[],
    integrations=[],
    features=[
        feature("Catálogo", FeatureStatus.IMPLEMENTED, "P1"),
        feature("Checkout", FeatureStatus.PARTIAL, "P2"),
        feature("Nota fiscal", FeatureStatus.DOCUMENTED_ONLY, "P3"),
        feature("Lista de desejos", FeatureStatus.UNDOCUMENTED, ""),
    ],
    flows=[],
    business_rules=[],
)


def no_model() -> None:
    raise AssertionError("Ideia × Código must not touch the AI provider")


async def test_groups_the_base_without_calling_the_model(
    app: FastAPI, api: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app.dependency_overrides[get_llm_provider] = no_model
    project_id = (await api.post("/projects", json={"name": "Loja"})).json()["id"]
    await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "text", "title": "Escopo", "content": "Catálogo, checkout e nota fiscal."},
    )
    await ProductBaseRepository(db_session).replace(uuid.UUID(project_id), BASE, "fake", "fake")
    await db_session.flush()

    response = await api.get(f"/projects/{project_id}/idea-vs-code")

    body = response.json()
    assert response.status_code == 200
    assert body["state"] == "available"
    assert [f["name"] for f in body["columns"]["delivered"]] == ["Catálogo", "Checkout"]
    assert [f["name"] for f in body["columns"]["missing"]] == ["Nota fiscal"]
    assert [f["name"] for f in body["columns"]["undocumented"]] == ["Lista de desejos"]
    assert (body["promised"], body["implemented"], body["partial"]) == (3, 1, 1)


async def test_needs_a_processed_project(api: httpx.AsyncClient) -> None:
    project_id = (await api.post("/projects", json={"name": "Sem base"})).json()["id"]

    response = await api.get(f"/projects/{project_id}/idea-vs-code")

    assert response.status_code == 409
