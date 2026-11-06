from fastapi.testclient import TestClient

from app import __version__
from app.api.deps import get_optional_engine
from app.core.config import Settings, get_settings
from app.main import create_app


def test_health_reports_missing_database_and_llm_configuration() -> None:
    app = create_app()
    app.dependency_overrides[get_optional_engine] = lambda: None
    app.dependency_overrides[get_settings] = lambda: Settings(
        llm_provider="gemini", gemini_api_key="", gemini_model=""
    )
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": __version__,
        "database": "not_configured",
        "llm": {"provider": "gemini", "model": "", "configured": False},
    }
