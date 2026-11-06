from app.core.config import Settings
from app.llm.factory import create_provider, provider_status
from app.llm.retry import RetryingProvider


def test_creates_selected_provider_wrapped_with_retry() -> None:
    settings = Settings(llm_provider="ollama", ollama_model="llama-test")

    provider = create_provider(settings)

    assert isinstance(provider, RetryingProvider)
    assert (provider.name, provider.model) == ("ollama", "llama-test")


def test_status_reports_missing_configuration_without_calling_the_model() -> None:
    settings = Settings(llm_provider="gemini", gemini_api_key="", gemini_model="")

    status = provider_status(settings)

    assert (status.provider, status.configured) == ("gemini", False)
