"""Upload errors shown to the user (pt-BR)."""

from app.core.errors import AppError


class InvalidUpload(AppError):
    status_code = 422


class UploadTooLarge(AppError):
    status_code = 413


class SourceUnavailable(AppError):
    """An external source (GitHub) could not be reached or refused the download."""

    status_code = 502
