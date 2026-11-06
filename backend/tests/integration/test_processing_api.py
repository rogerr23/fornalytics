import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_processing_runner, get_session_factory
from app.db.models import LensCache
from app.domain.enums import CacheKind, Lens
from app.extraction.extractor import ProductBaseExtractor
from app.extraction.runner import ProcessingRunner
from app.llm.errors import QuotaExceeded
from app.llm.fake import FakeProvider, FakeResponse
from app.prompts.builder import PromptBuilder
from tests.fixtures.builders import make_zip

ZIP = make_zip({"loja/src/routes/cart.py": "def add_item():\n    return 'ok'\n"})
IDEA = "Loja online.\nCarrinho de compras.\nCupom de desconto."

PROMISES = """{"promises": [
  {"id": "P1", "name": "Carrinho", "description": "Adicionar itens", "evidence": [
    {"source_type": "idea_doc", "path": "Escopo.txt", "line_start": 2, "line_end": 2,
     "quote": "Carrinho de compras."}]},
  {"id": "P2", "name": "Cupom", "description": "Desconto", "evidence": []}]}"""

BASE = """{"summary": "Uma loja.", "stack": ["Python"], "entities": [], "integrations": [],
 "features": [{"name": "Carrinho", "description": "Adiciona itens", "status": "implemented",
   "promise_ref": "P1", "evidence": [
     {"source_type": "code", "path": "src/routes/cart.py", "line_start": 1, "line_end": 1,
      "quote": "def add_item"},
     {"source_type": "code", "path": "src/routes/cart.py", "line_start": 1, "line_end": 1,
      "quote": "def remove_item"}]}],
 "flows": [], "business_rules": []}"""


class IdleRunner(ProcessingRunner):
    """Accepts work but never runs it (the project stays in `processing`)."""

    def submit(self, project_id: uuid.UUID) -> None:
        return None


@pytest.fixture
def use_runner(app: FastAPI, db_session: AsyncSession):  # noqa: ANN201
    """Install a runner with a FakeProvider that shares the rolled-back test session."""

    @asynccontextmanager
    async def shared_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session_factory] = lambda: shared_session

    def install(
        responses: list[FakeResponse], runner_cls: type = ProcessingRunner
    ) -> ProcessingRunner:
        provider = FakeProvider(responses)
        extractor = ProductBaseExtractor(provider, PromptBuilder(), 200_000)
        runner = runner_cls(shared_session, provider, extractor)
        app.dependency_overrides[get_processing_runner] = lambda: runner
        return runner

    return install


async def project_with_material(api: httpx.AsyncClient) -> str:
    project_id = (await api.post("/projects", json={"name": "Loja"})).json()["id"]
    await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "code"},
        files={"file": ("loja.zip", ZIP, "application/zip")},
    )
    await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "text", "title": "Escopo", "content": IDEA},
    )
    return project_id


async def test_process_builds_the_base_in_the_background(
    api: httpx.AsyncClient, db_session: AsyncSession, use_runner
) -> None:
    runner = use_runner([PROMISES, BASE])
    project_id = await project_with_material(api)
    db_session.add(
        LensCache(project_id=project_id, lens=Lens.CLIENTE, kind=CacheKind.OVERVIEW, content="x")
    )
    await db_session.flush()

    accepted = await api.post(f"/projects/{project_id}/process")
    await runner.wait_idle()

    assert accepted.status_code == 202
    assert accepted.json()["status"] == "processing"

    status = await api.get(f"/projects/{project_id}/status")
    assert status.headers["content-type"].startswith("text/event-stream")
    assert status.text.startswith("event: status\ndata: ")
    assert '"status":"ready"' in status.text
    assert "1 citação(ões) descartada(s)" in status.text

    base = (await api.get(f"/projects/{project_id}/base")).json()
    assert base["provider"] == "fake"
    assert base["base_outdated"] is False
    assert [(f["name"], f["status"]) for f in base["features"]] == [
        ("Carrinho", "implemented"),
        ("Cupom", "documented_only"),
    ]
    assert [e["path"] for e in base["features"][0]["evidence"]] == [
        "Escopo.txt",
        "src/routes/cart.py",
    ]
    assert (await db_session.scalars(select(LensCache))).all() == []


async def test_quota_error_marks_the_project_as_failed(api: httpx.AsyncClient, use_runner) -> None:
    runner = use_runner([QuotaExceeded(30)])
    project_id = await project_with_material(api)

    await api.post(f"/projects/{project_id}/process")
    await runner.wait_idle()

    project = (await api.get(f"/projects/{project_id}")).json()
    assert project["status"] == "failed"
    assert "limite gratuito" in project["status_detail"]
    assert (await api.get(f"/projects/{project_id}/base")).status_code == 404


async def test_processing_twice_is_a_conflict_and_sources_are_locked(
    api: httpx.AsyncClient, use_runner
) -> None:
    use_runner([], runner_cls=IdleRunner)
    project_id = await project_with_material(api)

    first = await api.post(f"/projects/{project_id}/process")
    second = await api.post(f"/projects/{project_id}/process")
    upload = await api.post(
        f"/projects/{project_id}/sources", data={"type": "text", "content": "mais"}
    )

    assert first.status_code == 202
    assert second.status_code == 409
    assert upload.status_code == 409


async def test_project_without_sources_cannot_be_processed(
    api: httpx.AsyncClient, use_runner
) -> None:
    use_runner([])
    project_id = (await api.post("/projects", json={"name": "Vazio"})).json()["id"]

    response = await api.post(f"/projects/{project_id}/process")

    assert response.status_code == 422
