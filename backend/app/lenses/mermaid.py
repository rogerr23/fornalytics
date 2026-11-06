"""Builds Mermaid text from nodes and edges. Pure code: the output is always valid syntax.

The model never writes Mermaid (it breaks often); it only returns nodes and edges.
"""

from collections.abc import Sequence

from app.domain.flows import FlowEdge, FlowNode

MAX_LABEL = 60
NOT_FOUND_LABEL = "Fluxo não encontrado no material"


def clean_label(text: str) -> str:
    """One line, short, and safe inside a quoted Mermaid label."""
    label = " ".join(text.split())
    if len(label) > MAX_LABEL:
        label = label[: MAX_LABEL - 1].rstrip() + "…"
    # Order matters: '#' first, since the escapes themselves use it.
    for char, entity in (("#", "#35;"), ('"', "#quot;"), ("<", "#lt;"), (">", "#gt;")):
        label = label.replace(char, entity)
    return label.replace("`", "'")


def build_mermaid(
    nodes: Sequence[FlowNode], edges: Sequence[FlowEdge], steps: Sequence[str] = ()
) -> str:
    """`flowchart TD` with ids n1, n2... (the model's ids may have spaces or accents).

    Repeated nodes and edges to unknown nodes are dropped. Without nodes, the steps become
    a straight line.
    """
    ids: dict[str, str] = {}
    lines = ["flowchart TD"]
    for node in nodes:
        key = node.id.strip()
        if not key or key in ids:
            continue
        ids[key] = f"n{len(ids) + 1}"
        lines.append(f'    {ids[key]}["{clean_label(node.label or key)}"]')
    if not ids:
        return linear_mermaid(steps)
    for edge in edges:
        source, target = ids.get(edge.source.strip()), ids.get(edge.target.strip())
        if source is None or target is None:
            continue
        label = clean_label(edge.label)
        lines.append(
            f'    {source} -->|"{label}"| {target}' if label else f"    {source} --> {target}"
        )
    return "\n".join(lines)


def linear_mermaid(steps: Sequence[str]) -> str:
    texts = [step for step in steps if step.strip()] or [NOT_FOUND_LABEL]
    lines = ["flowchart TD"]
    lines += [f'    n{i}["{clean_label(text)}"]' for i, text in enumerate(texts, 1)]
    lines += [f"    n{i} --> n{i + 1}" for i in range(1, len(texts))]
    return "\n".join(lines)
