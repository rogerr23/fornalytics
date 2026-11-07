"""Markdown report of a run (docs/evals/<run>.md) and the answers file. Pure functions."""

from collections import defaultdict

from evals.results import Record, Run
from evals.schema import EvalSet

LENS_LABEL = {"cliente": "Cliente", "nao_tecnico": "Não técnico", "tecnico": "Técnico"}
KIND_LABEL = {"chat": "Chat", "does_it": "Isso faz?", "compare": "Lado a lado", "flow": "Fluxo"}

TONE_CRITERIA = {
    "cliente": "valor e benefício, sem jargão (nada de arquivo, função, banco), frases curtas",
    "nao_tecnico": "como funciona na prática, analogias, passos e regras em linguagem simples",
    "tecnico": "arquivos, funções e integrações com nomes exatos, sempre com citação",
}


def _pct(part: int, total: int) -> str:
    return f"{round(100 * part / total)}%" if total else "—"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_report(run: Run, eval_set: EvalSet) -> str:
    records = [run.records[q.id] for q in eval_set.questions if q.id in run.records]
    answered = [r for r in records if r.status == "ok"]
    passed = [r for r in answered if r.passed]
    errors = [r for r in records if r.status == "error"]
    citations = [c for r in answered for a in r.answers for c in a.citations]
    invalid = sum(not c.valid for c in citations)

    lines = [
        f"# Avaliação — {run.name}",
        "",
        f"- **Data:** {run.started_at:%d/%m/%Y %H:%M}",
        f"- **Modelo:** {run.provider} · `{run.model}`",
        f"- **Projeto:** {run.project}",
        f"- **Respondidas:** {len(answered)} de {len(eval_set.questions)}"
        + (f" ({len(errors)} com erro da IA, não avaliadas)" if errors else ""),
        f"- **Aprovadas:** {len(passed)} de {len(answered)} ({_pct(len(passed), len(answered))})",
        f"- **Citações nas respostas:** {len(citations)}, inválidas: {invalid}"
        f" ({_pct(invalid, len(citations))})",
        "",
        "Checagens automáticas em `backend/evals/checks.py`. O tom de cada lente é revisado à mão"
        " (seção **Revisão de tom**).",
        "",
        "## Por lente e tipo",
        "",
        "| Lente | Tipo | Aprovadas |",
        "|---|---|---|",
    ]
    groups: dict[tuple[str, str], list[Record]] = defaultdict(list)
    for record in answered:
        groups[(record.lens or "todas", record.kind)].append(record)
    for (lens, kind), items in sorted(groups.items()):
        ok = sum(r.passed for r in items)
        lines.append(
            f"| {LENS_LABEL.get(lens, 'Três lentes')} | {KIND_LABEL[kind]} | {ok}/{len(items)} |"
        )

    lines += ["", "## Ideia × Código (sem IA)", ""]
    if run.idea_vs_code:
        lines += ["| Checagem | Ok | Detalhe |", "|---|---|---|"]
        lines += [
            f"| {_cell(c.name)} | {'✅' if c.passed else '❌'} | {_cell(c.detail)} |"
            for c in run.idea_vs_code
        ]
    else:
        lines.append("Não conferido nesta rodada.")

    failed = [r for r in answered if not r.passed]
    lines += ["", "## Reprovadas", ""]
    if failed:
        lines += [
            "| Id | Lente | Tipo | Pergunta | Checagem | Detalhe |",
            "|---|---|---|---|---|---|",
        ]
        for record in failed:
            for check in (c for c in record.checks if not c.passed):
                lines.append(
                    f"| {record.id} | {LENS_LABEL.get(record.lens or '', 'Três lentes')} |"
                    f" {KIND_LABEL[record.kind]} | {_cell(record.question)} | {_cell(check.name)} |"
                    f" {_cell(check.detail)} |"
                )
    else:
        lines.append("Nenhuma.")

    if errors:
        lines += ["", "## Erros da IA (não avaliadas)", ""]
        lines += [f"- `{r.id}`: {r.error}" for r in errors]

    lines += [
        "",
        "## Revisão de tom (Roger)",
        "",
        f"Leia as respostas em `{run.name}-respostas.md` e marque o que estiver no tom certo.",
        "",
    ]
    for lens, criteria in TONE_CRITERIA.items():
        ids = [r.id for r in answered if r.lens == lens and r.kind in ("chat", "flow")]
        lines.append(f"- [ ] **{LENS_LABEL[lens]}** ({criteria}): {', '.join(ids) or '—'}")
    lines.append(
        "- [ ] **Lado a lado:** as três respostas dizem a mesma coisa, cada uma no seu tom: "
        + ", ".join(r.id for r in answered if r.kind == "compare")
    )
    lines += ["", "Observações:", "", ""]
    return "\n".join(lines)


def render_answers(run: Run, eval_set: EvalSet) -> str:
    """Every answer in full, for the manual tone review."""
    lines = [f"# Respostas — {run.name}", "", f"Modelo: `{run.model}`.", ""]
    for question in eval_set.questions:
        record = run.records.get(question.id)
        if record is None:
            continue
        status = "✅" if record.passed else ("⚠️ erro" if record.status == "error" else "❌")
        lens = LENS_LABEL.get(record.lens or "", "Três lentes")
        lines += [
            f"## {record.id} · {lens} · {KIND_LABEL[record.kind]} {status}",
            "",
            f"> {record.question}",
            "",
        ]
        if record.status == "error":
            lines += [f"Erro: {record.error}", ""]
            continue
        if record.verdict:
            lines += [
                f"**Veredito:** {record.verdict} · funcionalidade: {record.feature or 'nenhuma'}",
                "",
            ]
        for answer in record.answers:
            if len(record.answers) > 1:
                lines += [f"**{LENS_LABEL.get(answer.lens, answer.lens)}**", ""]
            lines += [answer.text, ""]
    return "\n".join(lines)


def render_reserve(record: Record, model: str, date: str) -> str:
    """A saved demo answer (plan B of the presentation)."""
    lens = LENS_LABEL.get(record.lens or "", "Três lentes")
    lines = [
        f"# {record.question}",
        "",
        f"{KIND_LABEL[record.kind]} · lente {lens} · `{model}` · {date}",
        "",
    ]
    if record.verdict:
        lines += [
            f"**Veredito:** {record.verdict} · funcionalidade: {record.feature or 'nenhuma'}",
            "",
        ]
    for answer in record.answers:
        if len(record.answers) > 1:
            lines += [f"## {LENS_LABEL.get(answer.lens, answer.lens)}", ""]
        lines += [answer.text, ""]
        valid = [c.marker for c in answer.citations if c.valid]
        if valid:
            lines += ["Citações conferidas: " + ", ".join(f"`{m}`" for m in valid), ""]
    return "\n".join(lines)
