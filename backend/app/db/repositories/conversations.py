import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message
from app.domain.enums import Lens, MessageRole
from app.domain.lenses import StoredMessage, TextCitation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project_id: uuid.UUID) -> uuid.UUID:
        conversation = Conversation(project_id=project_id)
        self._session.add(conversation)
        await self._session.flush()
        return conversation.id

    async def belongs_to(self, project_id: uuid.UUID, conversation_id: uuid.UUID) -> bool:
        return bool(
            await self._session.scalar(
                select(
                    exists().where(
                        Conversation.id == conversation_id,
                        Conversation.project_id == project_id,
                    )
                )
            )
        )

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        lens: Lens,
        role: MessageRole,
        content: str,
        citations: Sequence[TextCitation] | None = None,
    ) -> uuid.UUID:
        message = Message(
            conversation_id=conversation_id,
            lens=lens,
            role=role,
            content=content,
            citations=[c.model_dump() for c in citations] if citations is not None else None,
            # Set here, not by the database: now() is fixed for a whole transaction, and the
            # history order must never depend on a tie.
            created_at=datetime.now(UTC),
        )
        self._session.add(message)
        await self._session.flush()
        return message.id

    async def messages(
        self, conversation_id: uuid.UUID, last: int | None = None
    ) -> list[StoredMessage]:
        """Messages in order; with `last`, only the most recent ones."""
        query = select(Message).where(Message.conversation_id == conversation_id)
        if last is None:
            rows = await self._session.scalars(query.order_by(Message.created_at, Message.id))
            return [_to_domain(row) for row in rows]
        rows = await self._session.scalars(
            query.order_by(Message.created_at.desc(), Message.id.desc()).limit(last)
        )
        return [_to_domain(row) for row in reversed(list(rows))]


def _to_domain(row: Message) -> StoredMessage:
    return StoredMessage(
        id=row.id,
        lens=row.lens,
        role=row.role,
        content=row.content,
        citations=[TextCitation.model_validate(c) for c in row.citations or []],
        created_at=row.created_at,
    )
