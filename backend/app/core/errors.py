"""Domain errors. Services raise these; a single handler in main.py turns them into HTTP."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for expected errors. `message` is shown to the user (pt-BR)."""

    status_code: int = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


async def app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
