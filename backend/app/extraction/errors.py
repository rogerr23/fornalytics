from app.core.errors import AppError, NotFound


class NothingToProcess(AppError):
    status_code = 422

    def __init__(self) -> None:
        super().__init__("Envie ao menos uma fonte (código ou documento) antes de processar.")


class BaseNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__("Este projeto ainda não tem base do produto. Processe o material antes.")
