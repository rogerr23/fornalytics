import pytest

from app.citations.validator import CitationValidator, MaterialFile
from app.domain.enums import FeatureStatus, SourceType, Verdict
from app.domain.lenses import CompareDraft, DoesItDraft
from app.domain.product_base import Evidence, Feature, ProductBase
from app.lenses.verdict import NOT_FOUND, find_feature, reconcile_verdict

CODE = "def apply_coupon(cart, code):\n    return cart.total * 0.9\n"
DOC = "# Escopo\nEmissão de nota fiscal.\n"
VALIDATOR = CitationValidator(
    [
        MaterialFile("src/coupon.py", SourceType.CODE, CODE),
        MaterialFile("escopo.md", SourceType.IDEA_DOC, DOC),
    ]
)
DOC_EVIDENCE = Evidence(
    source_type=SourceType.IDEA_DOC, path="escopo.md", line_start=2, line_end=2, quote="nota fiscal"
)
CODE_EVIDENCE = Evidence(
    source_type=SourceType.CODE,
    path="src/coupon.py",
    line_start=1,
    line_end=2,
    quote="apply_coupon",
)
FAKE_EVIDENCE = Evidence(
    source_type=SourceType.CODE, path="src/coupon.py", line_start=1, line_end=1, quote="def refund("
)


def feature(name: str, status: FeatureStatus, *evidence: Evidence) -> Feature:
    return Feature(
        name=name,
        description=f"{name} no checkout.",
        status=status,
        promise_ref="",
        evidence=list(evidence),
    )


BASE = ProductBase(
    summary="Loja",
    stack=[],
    entities=[],
    integrations=[],
    features=[
        feature("Emissão de nota fiscal", FeatureStatus.DOCUMENTED_ONLY, DOC_EVIDENCE),
        feature("Cupom de desconto", FeatureStatus.PARTIAL, CODE_EVIDENCE),
        feature("Carrinho", FeatureStatus.UNDOCUMENTED),
    ],
    flows=[],
    business_rules=[],
)


def draft(verdict: Verdict, name: str = "", *evidence: Evidence) -> DoesItDraft:
    return DoesItDraft(
        verdict=verdict,
        feature_name=name,
        justification="Resposta do modelo.",
        evidence=list(evidence),
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Emissão de nota fiscal", Verdict.NAO),
        ("cupom DE desconto", Verdict.PARCIALMENTE),  # case and spacing are ignored
        ("Emissao de nota fiscal", Verdict.NAO),  # accents too
        ("Carrinho", Verdict.SIM),
    ],
)
def test_verdict_comes_from_the_base_status(name: str, expected: Verdict) -> None:
    result = reconcile_verdict("Faz?", draft(expected, name), BASE, VALIDATOR)

    assert result.verdict == expected
    assert result.adjusted is False
    assert result.justification == "Resposta do modelo."


def test_a_verdict_that_contradicts_the_base_is_corrected() -> None:
    result = reconcile_verdict(
        "Gera nota fiscal?", draft(Verdict.SIM, "Emissão de nota fiscal"), BASE, VALIDATOR
    )

    assert result.verdict == Verdict.NAO
    assert result.adjusted is True
    assert result.justification.startswith("Não: está prometido no documento da ideia")
    assert result.feature is not None and result.feature.status == FeatureStatus.DOCUMENTED_ONLY
    # The base evidence comes along, so the answer is always backed.
    assert [e.path for e in result.evidence] == ["escopo.md"]


def test_yes_without_base_feature_needs_code_proof() -> None:
    unproven = reconcile_verdict(
        "Faz reembolso?", draft(Verdict.SIM, "", FAKE_EVIDENCE), BASE, VALIDATOR
    )
    proven = reconcile_verdict(
        "Calcula desconto?", draft(Verdict.SIM, "Inexistente", CODE_EVIDENCE), BASE, VALIDATOR
    )

    assert (unproven.verdict, unproven.adjusted, unproven.justification) == (
        Verdict.NAO,
        True,
        NOT_FOUND,
    )
    assert unproven.evidence == []
    assert (proven.verdict, proven.adjusted, proven.feature) == (Verdict.SIM, False, None)


def test_find_feature_needs_a_name() -> None:
    assert find_feature(BASE, "  ") is None
    assert find_feature(BASE, "Pagamento") is None


def test_structured_output_parses() -> None:
    compare = CompareDraft.model_validate_json(
        '{"cliente": "a", "nao_tecnico": "b", "tecnico": "c [[x.py:L1]]"}'
    )
    does_it = DoesItDraft.model_validate_json(
        '{"verdict": "parcialmente", "feature_name": "", "justification": "x", "evidence": []}'
    )

    assert compare.tecnico.endswith("]]")
    assert does_it.verdict == Verdict.PARCIALMENTE
