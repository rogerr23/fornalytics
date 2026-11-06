import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ProductBase
from tests.fixtures.builders import make_zip

ZIP = make_zip(
    {
        "loja-main/README.md": "# Loja\nCatálogo e carrinho.",
        "loja-main/src/routes/cart.py": "def add_item():\n    return 'ok'\n",
        "loja-main/node_modules/lib/index.js": "x",
    }
)


async def create_project(api: httpx.AsyncClient) -> str:
    response = await api.post("/projects", json={"name": "Loja demo"})
    assert response.status_code == 201
    return response.json()["id"]


async def test_upload_zip_returns_summary_and_files_can_be_read(api: httpx.AsyncClient) -> None:
    project_id = await create_project(api)

    response = await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "code"},
        files={"file": ("loja.zip", ZIP, "application/zip")},
    )

    assert response.status_code == 201
    summary = response.json()
    assert sorted(f["path"] for f in summary["files"]) == ["README.md", "src/routes/cart.py"]
    assert summary["skipped"] == [
        {"reason": "ignored_dir", "count": 1, "examples": ["node_modules/lib/index.js"]}
    ]
    assert summary["limits"]["code"]["excluded"] == []

    file = await api.get(f"/projects/{project_id}/files", params={"path": "src/routes/cart.py"})
    assert file.json()["line_count"] == 3
    assert file.json()["content"].startswith("def add_item")


async def test_changing_sources_after_a_base_marks_it_outdated(
    api: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    project_id = await create_project(api)
    first = await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "text", "title": "Ideia", "content": "Uma loja com cupom de desconto."},
    )
    db_session.add(ProductBase(project_id=project_id, data={}, provider="fake", model="fake"))
    await db_session.flush()

    second = await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "text", "title": "Ideia", "content": "Também emite nota fiscal."},
    )

    assert first.json()["base_outdated"] is False
    assert second.json()["base_outdated"] is True
    assert second.json()["renamed"] == [{"original": "Ideia.txt", "stored_as": "Ideia (2).txt"}]

    delete = await api.delete(f"/projects/{project_id}/sources/{first.json()['source_id']}")
    assert delete.status_code == 204
    detail = (await api.get(f"/projects/{project_id}")).json()
    assert [s["file_count"] for s in detail["sources"]] == [1]


async def test_zip_sent_as_document_is_rejected(api: httpx.AsyncClient) -> None:
    project_id = await create_project(api)

    response = await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "idea_doc"},
        files={"file": ("loja.zip", ZIP, "application/zip")},
    )

    assert response.status_code == 422
    assert "code" in response.json()["detail"]
