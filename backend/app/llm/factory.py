"""Builds the configured provider (Factory). Selection is manual via LLM_PROVIDER."""

from pydantic import BaseModel

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.ollama import OllamaProvider
from app.llm.retry import RetryingProvider


class LLMStatus(BaseModel):
    provider: str
    model: str
    configured: bool


def create_provider(settings: Settings) -> LLMProvider:
    """Return the configured provider wrapped with the 429 retry policy."""
    match settings.llm_provider:
        case "gemini":
            inner: LLMProvider = GeminiProvider(settings.gemini_api_key, settings.gemini_model)
        case "ollama":
            inner = OllamaProvider(settings.ollama_base_url, settings.ollama_model)
    return RetryingProvider(inner)


def provider_status(settings: Settings) -> LLMStatus:
    """Whether the provider has what it needs in .env. Never calls the model (no quota used)."""
    match settings.llm_provider:
        case "gemini":
            model = settings.gemini_model
            configured = bool(settings.gemini_api_key and model)
        case "ollama":
            model = settings.ollama_model
            configured = bool(model)
    return LLMStatus(provider=settings.llm_provider, model=model, configured=configured)
