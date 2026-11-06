from fastapi.testclient import TestClient

from app import __version__
from app.api.deps import get_optional_engine
from app.main import create_app


def test_health_reports_database_not_configured() -> None:
    app = create_app()
    app.dependency_overrides[get_optional_engine] = lambda: None
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": __version__,
        "database": "not_configured",
    }
