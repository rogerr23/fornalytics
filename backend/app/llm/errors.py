"""LLM errors. Messages are shown to the user (pt-BR) and never include secrets."""

import math

from app.core.errors import AppError


class LLMError(AppError):
    status_code = 502

    def __init__(self, message: str = "Erro inesperado ao falar com a IA.") -> None:
        super().__init__(message)


class QuotaExceeded(LLMError):
    status_code = 429

    def __init__(self, retry_after: float | None = None) -> None:
        self.retry_after = retry_after
        message = "O limite gratuito da IA foi atingido."
        if retry_after is None:
            message += " Tente de novo em alguns instantes."
        elif retry_after >= DAILY_LIMIT_SECONDS:
            message += (
                f" É o limite diário do plano gratuito: tente de novo em {wait_text(retry_after)}."
            )
        else:
            message += f" Tente de novo em {wait_text(retry_after)}."
        super().__init__(message)


# A wait this long means the daily quota is over, not the per-minute one.
DAILY_LIMIT_SECONDS = 3600


def wait_text(seconds: float) -> str:
    """'45 segundos', '3 minutos', 'cerca de 15 horas' (raw seconds are hard to read)."""
    whole = math.ceil(seconds)
    if whole < 120:
        return f"{whole} segundos"
    minutes = math.ceil(whole / 60)
    if minutes < 120:
        return f"{minutes} minutos"
    return f"cerca de {round(whole / 3600)} horas"


class ProviderUnavailable(LLMError):
    status_code = 503


class ProviderNotConfigured(LLMError):
    status_code = 503


class InvalidModelOutput(LLMError):
    def __init__(self) -> None:
        super().__init__("A IA devolveu uma resposta fora do formato esperado. Tente de novo.")


class RetryableError(Exception):
    """Temporary provider failure. Raised by providers, never shown to users directly.

    The retry layer (retry.py) tries again; when it gives up, it raises `give_up()`.
    """

    def __init__(self, retry_after: float | None = None) -> None:
        super().__init__(type(self).__name__)
        self.retry_after = retry_after

    def give_up(self) -> LLMError:
        raise NotImplementedError


class RateLimited(RetryableError):
    """HTTP 429: free-tier quota hit."""

    def give_up(self) -> LLMError:
        return QuotaExceeded(self.retry_after)


class Overloaded(RetryableError):
    """HTTP 5xx: provider under high demand or briefly unstable."""

    def give_up(self) -> LLMError:
        return ProviderUnavailable(
            "A IA está com alta demanda ou instável no momento. Tente de novo em instantes."
        )
