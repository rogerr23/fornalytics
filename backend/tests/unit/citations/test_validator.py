import pytest

from app.citations.validator import CitationProblem, CitationValidator, MaterialFile
from app.domain.enums import SourceType
from app.domain.product_base import Evidence

CART = """def add_item(cart, product):
    if product.stock <= 0:
        raise OutOfStock()
    cart.items.append(product)
    return cart
"""

VALIDATOR = CitationValidator(
    [
        MaterialFile("src/cart.py", SourceType.CODE, CART),
        MaterialFile("escopo.md", SourceType.IDEA_DOC, "# Escopo\nCupom de desconto no checkout."),
    ]
)


def evidence(path: str, start: int, end: int, quote: str) -> Evidence:
    return Evidence(
        source_type=SourceType.CODE, path=path, line_start=start, line_end=end, quote=quote
    )


@pytest.mark.parametrize(
    ("path", "start", "end", "quote"),
    [
        ("src/cart.py", 2, 3, "if product.stock <= 0:"),
        # Whitespace differences and quotes spanning lines are fine.
        ("src/cart.py", 2, 3, "if product.stock<=0:\n raise OutOfStock()"),
        # Copied line-number prefix, "./" and ellipsis are cleaned.
        ("./src/cart.py", 4, 4, "4| cart.items.append(product)..."),
    ],
)
def test_valid_citations(path: str, start: int, end: int, quote: str) -> None:
    assert VALIDATOR.check(path, start, end, quote).valid


@pytest.mark.parametrize(
    ("path", "start", "end", "quote", "problem"),
    [
        ("src/payment.py", 1, 2, "pay()", CitationProblem.FILE_NOT_FOUND),
        ("src/cart.py", 5, 40, "return cart", CitationProblem.LINES_OUT_OF_RANGE),
        ("src/cart.py", 0, 1, "def add_item", CitationProblem.LINES_OUT_OF_RANGE),
        ("src/cart.py", 3, 2, "raise", CitationProblem.LINES_OUT_OF_RANGE),
        ("src/cart.py", 1, 1, "  ...  ", CitationProblem.EMPTY_QUOTE),
        # The text exists in the file, but not inside the cited lines.
        ("src/cart.py", 1, 1, "raise OutOfStock()", CitationProblem.QUOTE_NOT_FOUND),
        ("src/cart.py", 1, 5, "apply_coupon(", CitationProblem.QUOTE_NOT_FOUND),
    ],
)
def test_invalid_citations(
    path: str, start: int, end: int, quote: str, problem: CitationProblem
) -> None:
    assert VALIDATOR.check(path, start, end, quote).problem == problem


def test_filter_keeps_valid_fixes_source_type_and_counts_dropped() -> None:
    kept, dropped = VALIDATOR.filter(
        [
            evidence("escopo.md", 2, 2, "Cupom de desconto"),  # model said "code"
            evidence("escopo.md", 2, 2, "Cupom"),  # same range: deduplicated
            evidence("src/cart.py", 1, 1, "invented()"),
        ]
    )

    assert dropped == 1
    assert [(e.path, e.source_type) for e in kept] == [("escopo.md", SourceType.IDEA_DOC)]
