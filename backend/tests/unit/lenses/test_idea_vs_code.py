import pytest

from app.domain.enums import ComparisonState, FeatureStatus
from app.domain.product_base import Feature, ProductBase
from app.lenses.idea_vs_code import comparison_state, group_features

S = FeatureStatus


def feature(name: str, status: FeatureStatus, ref: str = "") -> Feature:
    return Feature(name=name, description="", status=status, promise_ref=ref, evidence=[])


def base(*features: Feature) -> ProductBase:
    return ProductBase(
        summary="",
        stack=[],
        entities=[],
        integrations=[],
        features=list(features),
        flows=[],
        business_rules=[],
    )


FULL = base(
    feature("Catálogo", S.IMPLEMENTED, "P1"),
    feature("Cupom", S.DOCUMENTED_ONLY, "P2"),
    feature("Checkout", S.PARTIAL, "P3"),
    feature("Nota fiscal", S.DOCUMENTED_ONLY, "P4"),
    feature("Lista de desejos", S.UNDOCUMENTED),
)


def names(features: list[Feature]) -> list[str]:
    return [f.name for f in features]


def test_columns_follow_the_status_and_keep_the_base_order() -> None:
    columns = group_features(FULL, ComparisonState.AVAILABLE)

    assert names(columns.delivered) == ["Catálogo", "Checkout"]
    assert names(columns.missing) == ["Cupom", "Nota fiscal"]
    assert names(columns.undocumented) == ["Lista de desejos"]


@pytest.mark.parametrize(
    ("the_base", "has_documents", "expected"),
    [
        (FULL, True, ComparisonState.AVAILABLE),
        (base(feature("Cupom", S.DOCUMENTED_ONLY)), True, ComparisonState.MISSING_CODE),
        (base(feature("Catálogo", S.IMPLEMENTED)), False, ComparisonState.MISSING_IDEA),
        # A document was sent, but no promise came out of it.
        (base(feature("Catálogo", S.IMPLEMENTED)), True, ComparisonState.NO_PROMISES),
        (base(), False, ComparisonState.MISSING_IDEA),
    ],
)
def test_comparison_state(
    the_base: ProductBase, has_documents: bool, expected: ComparisonState
) -> None:
    assert comparison_state(the_base, has_documents) == expected


def test_without_promises_everything_in_the_code_is_undocumented() -> None:
    code_only = base(feature("Catálogo", S.IMPLEMENTED), feature("Busca", S.PARTIAL))

    columns = group_features(code_only, ComparisonState.MISSING_IDEA)

    assert (columns.delivered, columns.missing) == ([], [])
    assert names(columns.undocumented) == ["Catálogo", "Busca"]
