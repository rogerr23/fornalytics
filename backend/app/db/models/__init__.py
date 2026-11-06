"""Importing this package registers every table on Base.metadata (needed by Alembic)."""

from app.db.models.cache import LensCache
from app.db.models.conversation import Conversation, Message
from app.db.models.product_base import ProductBase
from app.db.models.project import Project
from app.db.models.source import Source, SourceFile

__all__ = [
    "Conversation",
    "LensCache",
    "Message",
    "ProductBase",
    "Project",
    "Source",
    "SourceFile",
]
