from datetime import datetime

from evals.report import render_answers, render_report, render_reserve
from evals.results import CheckOut, CitationOut, LensText, Record, Run
from evals.schema import load_eval_set


def test_report_lists_failures_errors_and_tone_review() -> None:
    eval_set = load_eval_set()
    run = Run(
        name="2026-11-07",
        started_at=datetime(2026, 11, 7, 9, 0),
        provider="gemini",
        model="gemini-3.5-flash",
        project=eval_set.project,
        records={
            "tec-02": Record(
                id="tec-02",
                kind="chat",
                lens="tecnico",
                question="Como funciona o login?",
                status="ok",
                answers=[
                    LensText(
                        lens="tecnico",
                        text="Usa scrypt [[a.ts:L1]].",
                        citations=[CitationOut(marker="[[a.ts:L1]]", valid=True)],
                    )
                ],
                checks=[CheckOut(name="menciona", passed=True)],
            ),
            "nt-09": Record(
                id="nt-09",
                kind="does_it",
                lens="nao_tecnico",
                question="O sistema gera nota fiscal?",
                status="ok",
                verdict="sim",
                checks=[CheckOut(name="veredito", passed=False, detail="esperado nao, veio sim")],
            ),
            "cmp-01": Record(
                id="cmp-01",
                kind="compare",
                lens=None,
                question="Como funciona o frete?",
                status="error",
                error="O limite gratuito da IA foi atingido.",
            ),
        },
    )

    report = render_report(run, eval_set)
    answers = render_answers(run, eval_set)
    reserve = render_reserve(run.records["tec-02"], run.model, "07/11/2026")

    assert "**Aprovadas:** 1 de 2 (50%)" in report
    assert "| nt-09 | Não técnico | Isso faz? |" in report
    assert "`cmp-01`: O limite gratuito" in report
    assert "- [ ] **Técnico**" in report and "tec-02" in report
    assert "## tec-02 · Técnico · Chat ✅" in answers
    assert "Citações conferidas: `[[a.ts:L1]]`" in reserve
