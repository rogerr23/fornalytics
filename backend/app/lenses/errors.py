from app.core.errors import Conflict, NotFound


class BaseNotReady(Conflict):
    def __init__(self) -> None:
        super().__init__(
            "Este projeto ainda não tem base do produto. "
            "Processe o material antes de usar as lentes."
        )


class ConversationNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__("Conversa não encontrada neste projeto.")
