from app.citations.validator import CitationValidator, MaterialFile
from app.domain.enums import FeatureStatus, SourceType
from app.domain.product_base import Evidence, Feature, IdeaPromises, ProductBase, Promise
from app.extraction.reconcile import ExtractionMode, clean_promises, reconcile

CODE = "def checkout(cart):\n    return pay(cart)\n\ndef login(email, password):\n    ...\n"
DOC = "# Escopo\nCheckout com pagamento.\nCupom de desconto.\n"

VALIDATOR = CitationValidator(
    [
        MaterialFile("src/shop.py", SourceType.CODE, CODE),
        MaterialFile("escopo.md", SourceType.IDEA_DOC, DOC),
    ]
)


def ev(path: str, line: int, quote: str) -> Evidence:
    return Evidence(
        source_type=SourceType.CODE, path=path, line_start=line, line_end=line, quote=quote
    )


def feature(name: str, status: FeatureStatus, ref: str, *evidence: Evidence) -> Feature:
    return Feature(
        name=name, description=name, status=status, promise_ref=ref, evidence=list(evidence)
    )


def base(*features: Feature) -> ProductBase:
    return ProductBase(
        summary="Loja",
        stack=["Python"],
        entities=[],
        integrations=[],
        features=list(features),
        flows=[],
        business_rules=[],
    )


PROMISES = IdeaPromises(
    promises=[
        Promise(
            id="P1", name="Checkout", description="Pagar", evidence=[ev("escopo.md", 2, "Checkout")]
        ),
        Promise(
            id="P2", name="Cupom", description="Desconto", evidence=[ev("escopo.md", 3, "Cupom")]
        ),
    ]
)


def test_promises_are_renumbered_and_checked() -> None:
    raw = IdeaPromises(
        promises=[
            Promise(
                id="7", name="Checkout", description="", evidence=[ev("escopo.md", 2, "Checkout")]
            ),
            Promise(id="x", name="  ", description="", evidence=[]),
            Promise(id="9", name="Cupom", description="", evidence=[ev("escopo.md", 1, "Cupom")]),
        ]
    )

    promises, dropped = clean_promises(raw, VALIDATOR)

    assert [p.id for p in promises.promises] == ["P1", "P2"]
    assert dropped == 1  # "Cupom" is on line 3, not 1
    assert promises.promises[0].evidence[0].source_type == SourceType.IDEA_DOC


def test_every_promise_becomes_one_feature_and_extras_are_undocumented() -> None:
    draft = base(
        feature("Checkout", FeatureStatus.IMPLEMENTED, "p1", ev("src/shop.py", 2, "pay(cart)")),
        feature("Checkout de novo", FeatureStatus.IMPLEMENTED, "P1"),  # duplicate reference
        feature("Login", FeatureStatus.IMPLEMENTED, "P9", ev("src/shop.py", 4, "def login")),
        feature("Inventado", FeatureStatus.IMPLEMENTED, "", ev("src/shop.py", 1, "def refund")),
    )

    result, dropped = reconcile(draft, ExtractionMode.CODE_WITH_PROMISES, VALIDATOR, PROMISES)

    statuses = [(f.name, f.status, f.promise_ref) for f in result.features]
    assert statuses == [
        ("Checkout", FeatureStatus.IMPLEMENTED, "P1"),
        # Forgotten by the model: still listed, as promised and not implemented.
        ("Cupom", FeatureStatus.DOCUMENTED_ONLY, "P2"),
        ("Checkout de novo", FeatureStatus.UNDOCUMENTED, ""),
        ("Login", FeatureStatus.UNDOCUMENTED, ""),
        ("Inventado", FeatureStatus.UNDOCUMENTED, ""),
    ]
    assert dropped == 1
    # Document evidence from step (a) + code evidence from step (b).
    assert [e.path for e in result.features[0].evidence] == ["escopo.md", "src/shop.py"]
    assert result.features[4].evidence == []


def test_promised_feature_labeled_undocumented_counts_as_implemented() -> None:
    draft = base(feature("Checkout", FeatureStatus.UNDOCUMENTED, "P1"))

    result, _ = reconcile(draft, ExtractionMode.CODE_WITH_PROMISES, VALIDATOR, PROMISES)

    assert result.features[0].status == FeatureStatus.IMPLEMENTED


def test_code_only_has_no_idea_statuses() -> None:
    draft = base(
        feature("Checkout", FeatureStatus.DOCUMENTED_ONLY, "P1"),
        feature("Login", FeatureStatus.PARTIAL, ""),
    )

    result, _ = reconcile(draft, ExtractionMode.CODE_ONLY, VALIDATOR)

    assert [(f.status, f.promise_ref) for f in result.features] == [
        (FeatureStatus.IMPLEMENTED, ""),
        (FeatureStatus.PARTIAL, ""),
    ]


def test_idea_only_is_all_documented_only() -> None:
    draft = base(feature("Cupom", FeatureStatus.IMPLEMENTED, "", ev("escopo.md", 3, "Cupom")))

    result, dropped = reconcile(draft, ExtractionMode.IDEA_ONLY, VALIDATOR)

    assert result.features[0].status == FeatureStatus.DOCUMENTED_ONLY
    assert dropped == 0
