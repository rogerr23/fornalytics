import re

from app.domain.flows import FlowEdge, FlowNode
from app.lenses.mermaid import (
    MAX_LABEL,
    NOT_FOUND_LABEL,
    build_mermaid,
    clean_label,
    linear_mermaid,
)

NODE_LINE = re.compile(r'^    n\d+\["[^"\n]*"\]$')
EDGE_LINE = re.compile(r'^    n\d+ --> n\d+$|^    n\d+ -->\|"[^"\n]*"\| n\d+$')


def assert_valid(text: str) -> None:
    """Every line is the header, a node or an edge, in the only shapes we emit."""
    first, *rest = text.split("\n")
    assert first == "flowchart TD"
    for line in rest:
        assert NODE_LINE.match(line) or EDGE_LINE.match(line), line


def node(id_: str, label: str) -> FlowNode:
    return FlowNode(id=id_, label=label)


def edge(source: str, target: str, label: str = "") -> FlowEdge:
    return FlowEdge(source=source, target=target, label=label)


def test_builds_nodes_and_edges_with_safe_ids() -> None:
    text = build_mermaid(
        [
            node("início do fluxo", "Cliente abre o carrinho"),
            node("valida cupom", "Valida o cupom"),
        ],
        [edge("início do fluxo", "valida cupom", "aplica cupom")],
    )

    assert text == (
        "flowchart TD\n"
        '    n1["Cliente abre o carrinho"]\n'
        '    n2["Valida o cupom"]\n'
        '    n1 -->|"aplica cupom"| n2'
    )


def test_escapes_quotes_brackets_and_markup() -> None:
    text = build_mermaid(
        [node("a", 'Mostra "Pedido #1" <b>ok</b> [x]'), node("b", "Fim\ncom quebra")],
        [edge("a", "b", 'diz "sim"')],
    )

    assert_valid(text)
    assert "#quot;Pedido #35;1#quot; #lt;b#gt;ok#lt;/b#gt; [x]" in text
    assert '"Fim com quebra"' in text


def test_drops_repeated_nodes_and_edges_to_unknown_nodes() -> None:
    text = build_mermaid(
        [node("a", "A"), node("a", "A de novo"), node(" ", "sem id"), node("b", "B")],
        [edge("a", "b"), edge("a", "fantasma"), edge("x", "b")],
    )

    assert_valid(text)
    assert text.count('["') == 2
    assert text.endswith("    n1 --> n2")


def test_long_labels_are_cut() -> None:
    label = clean_label("palavra " * 30)

    assert len(label) == MAX_LABEL
    assert label.endswith("…")


def test_without_nodes_the_steps_become_a_line() -> None:
    text = build_mermaid([], [], ["Abre o app", "Faz login", "Vê o catálogo"])

    assert_valid(text)
    assert text.endswith("    n1 --> n2\n    n2 --> n3")


def test_nothing_at_all_still_renders() -> None:
    text = linear_mermaid([])

    assert_valid(text)
    assert NOT_FOUND_LABEL in text
