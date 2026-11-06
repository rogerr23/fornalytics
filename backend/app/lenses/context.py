"""What each lens use case sends to the model (CLAUDE.md, section 4.4). Pure code: no IO.

- Overview: the product base only.
- Chat: product base + the most relevant files, ranked without embeddings, plus the last
  CHAT_HISTORY_TURNS exchanges.
"""

import re
import unicodedata
from collections import defaultdict
from collections.abc import Sequence

from app.domain.enums import MessageRole
from app.domain.lenses import StoredMessage
from app.domain.product_base import Evidence, ProductBase
from app.domain.projects import StoredFile
from app.ingestion.filters import path_priority
from app.ingestion.rendering import render_files
from app.ingestion.selection import select_within_budget
from app.llm.base import ChatMessage

PATH_WEIGHT = 3
CONTENT_WEIGHT = 1
EVIDENCE_WEIGHT = 4
MIN_WORD_LENGTH = 3

# Common Portuguese/English words that say nothing about where the answer is (written
# without accents, as `words` compares them).
STOPWORDS = frozenset(
    """
    que como para com uma por dos das nos nas nao sim isso esse essa este esta qual quais
    quando onde porque ele ela eles elas seu sua seus suas tem ter faz fazer pode podem
    produto sistema existe existem funciona acontece sobre mais menos muito tudo todo toda
    the and for with what how does where when which this that from are can
    """.split()  # noqa: SIM905 (a word block is easier to read and edit)
)

_WORD = re.compile(r"[a-z0-9_]+")


def words(text: str) -> set[str]:
    """Lowercase words without accents, minus stopwords and very short words."""
    plain = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return {
        word
        for word in _WORD.findall(plain.replace("_", " ").replace("-", " "))
        if len(word) >= MIN_WORD_LENGTH and word not in STOPWORDS
    }


def evidence_scores(question_words: set[str], base: ProductBase) -> dict[str, int]:
    """Files cited by base items (features, flows, rules) whose text matches the question."""
    scores: dict[str, int] = defaultdict(int)
    items: list[tuple[str, list[Evidence]]] = [
        *((f"{f.name} {f.description}", f.evidence) for f in base.features),
        *((f"{f.name} {' '.join(f.steps)}", f.evidence) for f in base.flows),
        *((r.rule, r.evidence) for r in base.business_rules),
    ]
    for text, evidence in items:
        overlap = len(question_words & words(text))
        if overlap:
            for item in evidence:
                scores[item.path] += overlap
    return scores


def rank_files(
    question: str, base: ProductBase, files: Sequence[StoredFile]
) -> list[tuple[int, StoredFile]]:
    """Files with any match, most relevant first (ties: README/routes first, then path)."""
    question_words = words(question)
    if not question_words:
        return []
    from_evidence = evidence_scores(question_words, base)
    ranked: list[tuple[int, StoredFile]] = []
    for file in files:
        score = (
            PATH_WEIGHT * len(question_words & words(file.path))
            + CONTENT_WEIGHT * len(question_words & words(file.content))
            + EVIDENCE_WEIGHT * from_evidence.get(file.path, 0)
        )
        if score:
            ranked.append((score, file))
    ranked.sort(key=lambda item: (-item[0], path_priority(item[1].path)))
    return ranked


def select_chat_files(
    question: str,
    base: ProductBase,
    files: Sequence[StoredFile],
    *,
    max_files: int,
    max_tokens: int,
) -> list[StoredFile]:
    """Relevant files in ranking order until the first of the two limits is reached."""
    ranked = [file for _score, file in rank_files(question, base, files)]
    order = {file.path: index for index, file in enumerate(ranked)}
    selection = select_within_budget(ranked, max_tokens, sort_key=lambda f: order[f.path])
    return selection.included[:max_files]


def recent_history(messages: Sequence[StoredMessage], turns: int) -> list[ChatMessage]:
    """The last `turns` complete exchanges (a question left without answer is skipped)."""
    pairs: list[tuple[StoredMessage, StoredMessage]] = []
    pending: StoredMessage | None = None
    for message in messages:
        if message.role == MessageRole.USER:
            pending = message
        elif pending is not None:
            pairs.append((pending, message))
            pending = None
    history: list[ChatMessage] = []
    for question, answer in pairs[-turns:] if turns > 0 else []:
        history.append(ChatMessage(role="user", content=question.content))
        history.append(ChatMessage(role="assistant", content=answer.content))
    return history


def render_base(base: ProductBase) -> str:
    return base.model_dump_json()


def overview_message(base: ProductBase) -> str:
    return f"## Base do produto (JSON)\n{render_base(base)}\n\nEscreva a visão geral."


def chat_message(base: ProductBase, files: Sequence[StoredFile], question: str) -> str:
    material = render_files(files) if files else "(nenhum arquivo relevante encontrado)"
    return (
        f"## Base do produto (JSON)\n{render_base(base)}\n\n"
        f"## Arquivos relevantes\n{material}\n\n"
        f"## Pergunta\n{question}"
    )
