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
        if retry_after is not None:
            message += f" Tente de novo em {math.ceil(retry_after)} segundos."
        else:
            message += " Tente de novo em alguns instantes."
        super().__init__(message)


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
