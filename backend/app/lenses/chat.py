"""Chat in the chosen lens: base + relevant files + recent history, streamed answer."""

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.core.config import Settings
from app.db.repositories.conversations import ConversationRepository
from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.db.session import SessionFactory
from app.domain.enums import Lens, MessageRole
from app.domain.lenses import (
    AnswerDone,
    CitationsChecked,
    ConversationStarted,
    LensEvent,
    StoredMessage,
)
from app.lenses.answer import AnswerStream, check_citations, load_base
from app.lenses.context import question_message, recent_history, select_chat_files
from app.lenses.errors import ConversationNotFound
from app.llm.base import ChatMessage, LLMProvider
from app.prompts.builder import PromptBuilder, Task


@dataclass(frozen=True)
class PreparedChat:
    project_id: uuid.UUID
    conversation_id: uuid.UUID
    lens: Lens
    system: str
    messages: list[ChatMessage]
    files_sent: list[str]


class ChatService:
    def __init__(
        self,
        sessions: SessionFactory,
        provider: LLMProvider,
        prompts: PromptBuilder,
        settings: Settings,
    ) -> None:
        self._sessions = sessions
        self._provider = provider
        self._prompts = prompts
        self._settings = settings

    async def prepare(
        self,
        project_id: uuid.UUID,
        lens: Lens,
        question: str,
        conversation_id: uuid.UUID | None,
    ) -> PreparedChat:
        """Checks (404, 409), context selection and the saved question, before streaming."""
        turns = self._settings.chat_history_turns
        async with self._sessions() as session:
            base = await load_base(session, project_id)
            conversations = ConversationRepository(session)
            if conversation_id is None:
                conversation_id = await conversations.create(project_id)
                past: list[StoredMessage] = []
            elif not await conversations.belongs_to(project_id, conversation_id):
                raise ConversationNotFound()
            else:
                # +1: a question left without answer (failed stream) is skipped by the trim.
                past = await conversations.messages(conversation_id, last=2 * turns + 1)
            files = await SourceRepository(session).files(project_id)
            await conversations.add_message(conversation_id, lens, MessageRole.USER, question)
            await session.commit()

        selected = select_chat_files(
            question,
            base.data,
            files,
            max_files=self._settings.chat_max_files,
            max_tokens=self._settings.chat_context_tokens,
        )
        messages = [
            *recent_history(past, turns),
            ChatMessage(role="user", content=question_message(base.data, selected, question)),
        ]
        return PreparedChat(
            project_id=project_id,
            conversation_id=conversation_id,
            lens=lens,
            system=self._prompts.build(Task.CHAT, lens),
            messages=messages,
            files_sent=[file.path for file in selected],
        )

    async def answer(self, prepared: PreparedChat) -> AsyncIterator[LensEvent]:
        yield ConversationStarted(conversation_id=prepared.conversation_id)
        stream = AnswerStream()
        async for event in stream.run(self._provider, prepared.system, prepared.messages):
            yield event
        if stream.failed:
            return  # the question stays saved; the history skips it
        citations = await check_citations(self._sessions, prepared.project_id, stream.text)
        async with self._sessions() as session:
            message_id = await ConversationRepository(session).add_message(
                prepared.conversation_id,
                prepared.lens,
                MessageRole.ASSISTANT,
                stream.text,
                citations,
            )
            await session.commit()
        yield CitationsChecked(citations=citations)
        yield AnswerDone(message_id=message_id)

    async def messages(
        self, project_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> list[StoredMessage]:
        async with self._sessions() as session:
            await ProjectRepository(session).get(project_id)
            conversations = ConversationRepository(session)
            if not await conversations.belongs_to(project_id, conversation_id):
                raise ConversationNotFound()
            return await conversations.messages(conversation_id)
