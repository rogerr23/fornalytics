import pytest

from app.domain.enums import Lens, Verdict
from evals.checks import (
    Citations,
    FeatureText,
    check_column,
    check_text,
    check_verdict,
    citation_rule,
)
from evals.schema import Expect

NONE = Citations(valid=0, invalid=0)


def failed(checks: list) -> list[str]:
    return [c.name for c in checks if not c.passed]


def test_mentions_ignore_case_and_accents() -> None:
    expect = Expect(mentions_any=["memória", "Map"])

    checks = check_text("Os dados ficam em MEMORIA.", expect, Lens.NAO_TECNICO, NONE, None)

    assert failed(checks) == []


def test_not_found_is_required_only_when_expected() -> None:
    wanted = Expect(not_found=True)
    has_answer = Expect(mentions_any=["199"])

    assert failed(check_text("Não encontrei no material.", wanted, Lens.CLIENTE, NONE, None)) == []
    assert "não encontrei" in failed(check_text("Em 3 dias.", wanted, Lens.CLIENTE, NONE, None))
    assert "não encontrei" in failed(
        check_text("Não encontrei no material.", has_answer, Lens.CLIENTE, NONE, None)
    )


@pytest.mark.parametrize(
    ("lens", "citations", "ok"),
    [
        (Lens.TECNICO, Citations(valid=2, invalid=0), True),
        (Lens.TECNICO, Citations(valid=0, invalid=0), False),  # technical must cite
        (Lens.TECNICO, Citations(valid=2, invalid=1), False),  # and never invent
        (Lens.CLIENTE, Citations(valid=1, invalid=0), False),  # client has no markers
        (Lens.NAO_TECNICO, Citations(valid=0, invalid=0), True),
        (Lens.NAO_TECNICO, Citations(valid=1, invalid=1), False),
    ],
)
def test_citation_rule_follows_the_lens(lens: Lens, citations: Citations, ok: bool) -> None:
    checks = check_text("Resposta.", Expect(), lens, citations, None)

    assert (failed(checks) == []) is ok


def test_not_found_answers_need_no_citation() -> None:
    assert citation_rule(Expect(not_found=True), Lens.TECNICO) == "any"


def test_must_not_mention_and_word_limit() -> None:
    expect = Expect(must_not_mention=["boleto"])

    checks = check_text("Pague com boleto. " * 30, expect, Lens.NAO_TECNICO, NONE, 50)

    assert failed(checks) == ["não menciona", "tamanho"]


def test_verdict_and_feature() -> None:
    expect = Expect(verdict=Verdict.NAO, feature_any=["nota fiscal"])

    assert failed(check_verdict(Verdict.NAO, "Emissão de Nota Fiscal", expect)) == []
    assert failed(check_verdict(Verdict.SIM, None, expect)) == ["veredito", "funcionalidade"]
    assert failed(
        check_verdict(Verdict.NAO, "Pix", Expect(verdict=Verdict.NAO, no_feature=True))
    ) == ["sem funcionalidade"]


def test_strict_column_flags_unexpected_features() -> None:
    features = [
        FeatureText("Cupom de desconto", ""),
        FeatureText("Nota fiscal eletrônica", ""),
        FeatureText("Programa de pontos", ""),
    ]
    groups = [["cupom"], ["nota fiscal"]]

    strict = check_column("⚠️", features, groups, strict=True)
    loose = check_column("🔍", features, groups, strict=False)

    assert failed(strict) == ["⚠️: só o esperado"]
    assert failed(loose) == []
    assert "Programa de pontos" in loose[-1].detail
