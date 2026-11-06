"""Upload errors shown to the user (pt-BR)."""

from app.core.errors import AppError


class InvalidUpload(AppError):
    status_code = 422


class UploadTooLarge(AppError):
    status_code = 413
