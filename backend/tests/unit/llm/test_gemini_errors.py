from google.genai import errors

from app.llm.errors import Overloaded, ProviderNotConfigured, RateLimited
from app.llm.gemini import GeminiProvider

RATE_LIMIT_BODY = {
    "error": {
        "code": 429,
        "status": "RESOURCE_EXHAUSTED",
        "message": "Quota exceeded",
        "details": [
            {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "37s"},
        ],
    }
}


def provider() -> GeminiProvider:
    return GeminiProvider(api_key="test-key", model="gemini-test-flash")


def test_429_becomes_rate_limited_with_server_delay() -> None:
    translated = provider()._from_api_error(errors.ClientError(429, RATE_LIMIT_BODY))

    assert isinstance(translated, RateLimited)
    assert translated.retry_after == 37.0


def test_unknown_model_points_to_the_env_variable() -> None:
    body = {"error": {"code": 404, "status": "NOT_FOUND", "message": "model not found"}}

    translated = provider()._from_api_error(errors.ClientError(404, body))

    assert isinstance(translated, ProviderNotConfigured)
    assert "GEMINI_MODEL" in translated.message


def test_high_demand_503_is_retryable() -> None:
    body = {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}}

    translated = provider()._from_api_error(errors.ServerError(503, body))

    assert isinstance(translated, Overloaded)
