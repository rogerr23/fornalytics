from app.domain.enums import Lens
from app.prompts.builder import PromptBuilder, Task


def test_prompt_is_base_then_lenses_then_task() -> None:
    builder = PromptBuilder()

    single = builder.build(Task.DOES_IT, Lens.CLIENTE)
    all_lenses = builder.build_for_lenses(Task.COMPARE, list(Lens))

    assert single.index("Você é o Fornalytics") < single.index("Lente: cliente")
    assert single.index("Lente: cliente") < single.index('Tarefa: "Isso o produto faz?"')
    positions = [
        all_lenses.index(f"Lente: {name}") for name in ("cliente", "não técnico", "técnico")
    ]
    assert positions == sorted(positions)
    assert all_lenses.index("Lente: técnico") < all_lenses.index("Tarefa: a mesma pergunta")
