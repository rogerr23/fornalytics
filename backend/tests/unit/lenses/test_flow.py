from app.citations.validator import CitationValidator, MaterialFile
from app.domain.enums import SourceType
from app.domain.flows import FlowDraft
from app.domain.product_base import BaseFlow, Evidence, ProductBase
from app.lenses.flow import MAX_STEPS, base_flows, flow_result

CODE = "def checkout(cart):\n    pay(cart)\n    send_email()\n"
VALIDATOR = CitationValidator([MaterialFile("src/checkout.py", SourceType.CODE, CODE)])

DRAFT = """{"name": "Finalizar compra",
 "steps": [
   {"text": "O cliente fecha o pedido.", "evidence": [
     {"source_type": "code", "path": "src/checkout.py", "line_start": 1, "line_end": 2,
      "quote": "def checkout(cart):"}]},
   {"text": "O sistema envia o e-mail.", "evidence": [
     {"source_type": "code", "path": "src/checkout.py", "line_start": 1, "line_end": 1,
      "quote": "send_email()"}]},
   {"text": "   ", "evidence": []}],
 "nodes": [{"id": "fecha", "label": "Fecha o pedido"}, {"id": "email", "label": "Envia e-mail"}],
 "edges": [{"source": "fecha", "target": "email", "label": ""}]}"""


def test_flow_result_checks_citations_and_builds_the_diagram() -> None:
    result = flow_result(
        "O que acontece ao comprar?", FlowDraft.model_validate_json(DRAFT), VALIDATOR
    )

    assert result.name == "Finalizar compra"
    assert [step.text for step in result.steps] == [
        "O cliente fecha o pedido.",
        "O sistema envia o e-mail.",
    ]
    assert len(result.steps[0].evidence) == 1
    assert result.steps[1].evidence == []  # the quote is not inside line 1
    assert result.mermaid.endswith("    n1 --> n2")
    assert result.from_base is False


def test_flow_result_keeps_the_step_limit() -> None:
    draft = FlowDraft(
        name="",
        steps=[{"text": f"Passo {n}", "evidence": []} for n in range(15)],  # type: ignore[misc]
        nodes=[],
        edges=[],
    )

    result = flow_result("Pergunta?", draft, VALIDATOR)

    assert len(result.steps) == MAX_STEPS
    assert result.name == "Pergunta?"
    assert result.mermaid.count('["') == MAX_STEPS


def test_base_flows_become_straight_diagrams() -> None:
    evidence = Evidence(
        source_type=SourceType.CODE, path="src/checkout.py", line_start=1, line_end=1, quote="x"
    )
    base = ProductBase(
        summary="",
        stack=[],
        entities=[],
        integrations=[],
        features=[],
        flows=[BaseFlow(name="Comprar", steps=["Escolhe", "Paga"], evidence=[evidence])],
        business_rules=[],
    )

    [flow] = base_flows(base)

    assert flow.from_base is True
    assert flow.evidence == [evidence]
    assert flow.mermaid == 'flowchart TD\n    n1["Escolhe"]\n    n2["Paga"]\n    n1 --> n2'
