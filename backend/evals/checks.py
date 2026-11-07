"""Objective checks of an answer. Pure functions: no model call, no IO.

What cannot be checked this way (the tone of each lens) is reviewed by hand (CLAUDE.md 4.5).
"""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.enums import Lens, Verdict
from evals.schema import CitationRule, Expect, IdeaVsCodeExpect

NOT_FOUND = "nao encontrei no material"

# Word limits from the prompts, with some slack (they are guidance for the model).
MAX_WORDS = {"chat": 320, "compare": 200}

DEFAULT_CITATIONS: dict[Lens, CitationRule] = {
    Lens.CLIENTE: "forbidden",
    Lens.NAO_TECNICO: "any",
    Lens.TECNICO: "required",
}


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str = ""


def plain(text: str) -> str:
    """Lowercase, no accents, single spaces: how every text comparison is made."""
    no_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(no_accents.casefold().split())


def contains_any(text: str, needles: Sequence[str]) -> list[str]:
    haystack = plain(text)
    return [needle for needle in needles if plain(needle) in haystack]


def words(text: str) -> int:
    return len(re.findall(r"\w+", text))


@dataclass(frozen=True)
class Citations:
    valid: int
    invalid: int

    @property
    def total(self) -> int:
        return self.valid + self.invalid


def citation_rule(expect: Expect, lens: Lens) -> CitationRule:
    if expect.citations is not None:
        return expect.citations
    return "any" if expect.not_found else DEFAULT_CITATIONS[lens]


def check_text(
    text: str, expect: Expect, lens: Lens, citations: Citations, max_words: int | None
) -> list[Check]:
    """Checks for a written answer (chat, one lens of side by side, a flow)."""
    checks: list[Check] = []
    says_not_found = NOT_FOUND in plain(text)
    if expect.not_found:
        checks.append(Check("não encontrei", says_not_found, "esperado: não encontrei no material"))
    elif says_not_found and expect.mentions_any:
        checks.append(Check("não encontrei", False, "disse não encontrei, mas o material tem"))
    if expect.mentions_any and not expect.not_found:
        found = contains_any(text, expect.mentions_any)
        checks.append(
            Check("menciona", bool(found), f"esperado um de: {', '.join(expect.mentions_any)}")
        )
    if expect.must_not_mention:
        found = contains_any(text, expect.must_not_mention)
        checks.append(
            Check("não menciona", not found, f"apareceu: {', '.join(found)}" if found else "")
        )

    rule = citation_rule(expect, lens)
    if rule == "required":
        ok = citations.valid > 0 and citations.invalid == 0
        detail = f"{citations.valid} válidas, {citations.invalid} inválidas"
        checks.append(Check("citações", ok, detail))
    elif rule == "forbidden":
        checks.append(
            Check("sem citações", citations.total == 0, f"{citations.total} marcador(es)")
        )
    else:
        checks.append(
            Check("citações válidas", citations.invalid == 0, f"{citations.invalid} inválida(s)")
        )

    if max_words is not None:
        count = words(text)
        checks.append(Check("tamanho", count <= max_words, f"{count} palavras (máx. {max_words})"))
    return checks


def check_verdict(verdict: Verdict, feature: str | None, expect: Expect) -> list[Check]:
    """Checks for "Isso faz?": verdict and the base feature it points to."""
    checks = [
        Check(
            "veredito",
            verdict == expect.verdict,
            f"esperado {expect.verdict}, veio {verdict}",
        )
    ]
    if expect.feature_any:
        found = bool(feature) and bool(contains_any(feature or "", expect.feature_any))
        checks.append(Check("funcionalidade", found, f"veio: {feature or 'nenhuma'}"))
    if expect.no_feature:
        checks.append(Check("sem funcionalidade", feature is None, f"veio: {feature}"))
    return checks


@dataclass(frozen=True)
class FeatureText:
    name: str
    description: str

    @property
    def text(self) -> str:
        return f"{self.name} {self.description}"


def check_column(
    name: str, features: Sequence[FeatureText], groups: Sequence[Sequence[str]], strict: bool
) -> list[Check]:
    """Every expected group is in the column; with `strict`, nothing else is."""
    checks = []
    matched: set[int] = set()
    for group in groups:
        hits = [i for i, f in enumerate(features) if contains_any(f.text, group)]
        matched.update(hits)
        checks.append(Check(f"{name}: {group[0]}", bool(hits), ""))
    extras = [f.name for i, f in enumerate(features) if i not in matched]
    if extras:
        checks.append(
            Check(
                f"{name}: só o esperado",
                not strict,
                ("inesperado: " if strict else "a mais (aviso): ") + "; ".join(extras),
            )
        )
    return checks


def check_idea_vs_code(
    delivered: Sequence[FeatureText],
    missing: Sequence[FeatureText],
    undocumented: Sequence[FeatureText],
    expect: IdeaVsCodeExpect,
) -> list[Check]:
    # The gaps must be exact: an extra "missing" feature would be a false alarm in the demo.
    return [
        *check_column("✅", delivered, expect.delivered, strict=False),
        *check_column("⚠️", missing, expect.missing, strict=True),
        *check_column("🔍", undocumented, expect.undocumented, strict=False),
    ]
