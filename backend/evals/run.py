"""Run the evaluation set against the real model (npm run eval).

Calls the backend services directly (no server needed), saves after every answer so a run
can resume after a quota error, and writes the report to docs/evals/.

    npm run eval                      # everything not answered yet in today's run
    npm run eval -- --core            # the quick subset (after changing a prompt)
    npm run eval -- --only nt-09,tec-02 --redo
    npm run eval -- --report          # only rewrite the report from the saved answers
"""

import argparse
import asyncio
import sys
import time
import uuid
from datetime import date, datetime
from pathlib import Path

from app.core.config import REPO_ROOT, get_settings
from app.core.errors import AppError
from app.db.repositories.projects import ProjectRepository
from app.db.session import get_engine, get_sessionmaker
from app.domain.enums import Lens
from app.domain.lenses import AnswerFailed, CitationsChecked, TextCitation, TextDelta
from app.lenses.chat import ChatService
from app.lenses.compare import CompareService
from app.lenses.does_it import DoesItService
from app.lenses.flow import FlowService
from app.lenses.idea_vs_code import IdeaVsCodeService
from app.llm.base import LLMProvider
from app.llm.errors import QuotaExceeded
from app.llm.factory import create_provider
from app.prompts.builder import PromptBuilder
from evals.checks import (
    MAX_WORDS,
    Check,
    Citations,
    FeatureText,
    check_idea_vs_code,
    check_text,
    check_verdict,
)
from evals.report import render_answers, render_report, render_reserve
from evals.results import CheckOut, CitationOut, LensText, Record, Run
from evals.schema import EvalSet, Question, load_eval_set

RUNS_DIR = Path(__file__).resolve().parent / "runs"
REPORTS_DIR = REPO_ROOT / "docs" / "evals"
RESERVE_DIR = REPO_ROOT / "demo" / "reserva"
DAILY_LIMIT_SECONDS = 3600


class StopRun(Exception):
    """The daily quota is over: save and stop; the next run resumes."""


def _checks(items: list[Check], prefix: str = "") -> list[CheckOut]:
    return [CheckOut(name=f"{prefix}{c.name}", passed=c.passed, detail=c.detail) for c in items]


def _citations(items: list[TextCitation]) -> tuple[list[CitationOut], Citations]:
    out = [CitationOut(marker=c.marker, valid=c.valid) for c in items]
    return out, Citations(
        valid=sum(c.valid for c in items), invalid=sum(not c.valid for c in items)
    )


class Evaluator:
    def __init__(self, provider: LLMProvider, project_id: uuid.UUID) -> None:
        settings = get_settings()
        sessions = get_sessionmaker()
        prompts = PromptBuilder()
        self._project_id = project_id
        self._chat = ChatService(sessions, provider, prompts, settings)
        self._compare = CompareService(sessions, provider, prompts, settings)
        self._does_it = DoesItService(sessions, provider, prompts, settings)
        self._flow = FlowService(sessions, provider, prompts, settings)

    async def answer(self, q: Question) -> Record:
        record = Record(id=q.id, kind=q.kind, lens=q.lens, question=q.question, status="ok")
        match q.kind:
            case "chat":
                await self._answer_chat(q, record)
            case "compare":
                result = await self._compare.compare(self._project_id, q.question)
                for answer in result.answers:
                    cites, counts = _citations(answer.citations)
                    record.answers.append(
                        LensText(lens=answer.lens, text=answer.text, citations=cites)
                    )
                    checks = check_text(
                        answer.text, q.expect, answer.lens, counts, MAX_WORDS["compare"]
                    )
                    record.checks += _checks(checks, prefix=f"{answer.lens}: ")
            case "does_it":
                assert q.lens is not None
                result = await self._does_it.ask(self._project_id, q.question, q.lens)
                record.answers.append(LensText(lens=q.lens, text=result.justification))
                record.verdict = result.verdict
                record.feature = result.feature.name if result.feature else None
                record.evidence = len(result.evidence)
                record.checks = _checks(check_verdict(result.verdict, record.feature, q.expect))
            case "flow":
                assert q.lens is not None
                flow = await self._flow.ask(self._project_id, q.question, q.lens)
                text = "\n".join(
                    [f"**{flow.name}**", *(f"{i}. {s.text}" for i, s in enumerate(flow.steps, 1))]
                )
                evidence = sum(len(step.evidence) for step in flow.steps)
                record.answers.append(LensText(lens=q.lens, text=text))
                record.evidence = evidence
                checks = check_text(
                    text, q.expect, q.lens, Citations(valid=evidence, invalid=0), None
                )
                record.checks = _checks(checks)
        return record

    async def _answer_chat(self, q: Question, record: Record) -> None:
        assert q.lens is not None
        prepared = await self._chat.prepare(self._project_id, q.lens, q.question, None)
        text, citations = "", []
        async for event in self._chat.answer(prepared):
            if isinstance(event, TextDelta):
                text += event.text
            elif isinstance(event, CitationsChecked):
                citations = event.citations
            elif isinstance(event, AnswerFailed):
                # The stream turns errors into a message; recover the quota case.
                if "limite diário" in event.message:
                    raise QuotaExceeded(DAILY_LIMIT_SECONDS * 24)
                raise AppError(event.message)
        cites, counts = _citations(citations)
        record.answers.append(LensText(lens=q.lens, text=text, citations=cites))
        record.checks = _checks(check_text(text, q.expect, q.lens, counts, MAX_WORDS["chat"]))


async def find_project(name: str) -> uuid.UUID:
    async with get_sessionmaker()() as session:
        projects = await ProjectRepository(session).list()
    for project in projects:
        if project.name == name:
            return project.id
    sys.exit(
        f"Projeto '{name}' não encontrado. Crie e processe a Loja Aurora (docs/demo-script.md)."
    )


async def idea_vs_code_checks(project_id: uuid.UUID, eval_set: EvalSet) -> list[CheckOut]:
    async with get_sessionmaker()() as session:
        result = await IdeaVsCodeService(session).get(project_id)

    def texts(features: list) -> list[FeatureText]:  # noqa: ANN001 (domain Feature list)
        return [FeatureText(f.name, f.description) for f in features]

    columns = result.columns
    return _checks(
        check_idea_vs_code(
            texts(columns.delivered),
            texts(columns.missing),
            texts(columns.undocumented),
            eval_set.idea_vs_code,
        )
    )


def select(eval_set: EvalSet, args: argparse.Namespace, run: Run) -> list[Question]:
    only = {item.strip() for item in args.only.split(",")} if args.only else None
    chosen = []
    for q in eval_set.questions:
        if only is not None and q.id not in only:
            continue
        if args.core and not q.core:
            continue
        if args.lens and q.lens != Lens(args.lens):
            continue
        done = run.records.get(q.id)
        if done and done.status == "ok" and not args.redo:
            continue
        chosen.append(q)
    return chosen


def save(run: Run, eval_set: EvalSet) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / f"{run.name}.json").write_text(run.model_dump_json(indent=2), encoding="utf-8")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / f"{run.name}.md").write_text(render_report(run, eval_set), encoding="utf-8")
    (REPORTS_DIR / f"{run.name}-respostas.md").write_text(
        render_answers(run, eval_set), encoding="utf-8"
    )
    RESERVE_DIR.mkdir(parents=True, exist_ok=True)
    for q in eval_set.questions:
        record = run.records.get(q.id)
        if q.demo and record and record.status == "ok":
            (RESERVE_DIR / f"{q.id}.md").write_text(
                render_reserve(record, run.model, f"{run.started_at:%d/%m/%Y}"), encoding="utf-8"
            )


async def main(args: argparse.Namespace) -> None:
    eval_set = load_eval_set()
    run_file = RUNS_DIR / f"{args.run}.json"
    settings = get_settings()

    if run_file.exists():
        run = Run.model_validate_json(run_file.read_text(encoding="utf-8"))
    else:
        run = Run(
            name=args.run,
            started_at=datetime.now(),
            provider=settings.llm_provider,
            model=settings.gemini_model
            if settings.llm_provider == "gemini"
            else settings.ollama_model,
            project=eval_set.project,
        )
    if args.report:
        save(run, eval_set)
        print(f"Relatório reescrito: docs/evals/{run.name}.md")
        return

    project_id = await find_project(eval_set.project)
    run.idea_vs_code = await idea_vs_code_checks(project_id, eval_set)
    questions = select(eval_set, args, run)
    print(f"{len(questions)} pergunta(s) para responder (rodada {run.name}).")

    provider = create_provider(settings)
    evaluator = Evaluator(provider, project_id)
    try:
        for index, q in enumerate(questions, 1):
            start = time.monotonic()
            try:
                record = await evaluator.answer(q)
            except QuotaExceeded as exc:
                record = Record(
                    id=q.id,
                    kind=q.kind,
                    lens=q.lens,
                    question=q.question,
                    status="error",
                    error=exc.message,
                )
                run.records[q.id] = record
                if exc.retry_after is None or exc.retry_after >= DAILY_LIMIT_SECONDS:
                    raise StopRun(exc.message) from exc
            except AppError as exc:
                record = Record(
                    id=q.id,
                    kind=q.kind,
                    lens=q.lens,
                    question=q.question,
                    status="error",
                    error=exc.message,
                )
            record.seconds = round(time.monotonic() - start, 1)
            run.records[q.id] = record
            save(run, eval_set)
            mark = "ok" if record.passed else ("ERRO" if record.status == "error" else "reprovada")
            print(f"[{index}/{len(questions)}] {q.id}: {mark} ({record.seconds}s)")
            if index < len(questions):
                await asyncio.sleep(args.delay)
    except StopRun as exc:
        print(f"Parado: {exc}. Rode de novo depois; as respostas salvas não são repetidas.")
    finally:
        save(run, eval_set)
        await provider.aclose()
        await get_engine().dispose()

    answered = [r for r in run.records.values() if r.status == "ok"]
    passed = sum(r.passed for r in answered)
    print(f"Aprovadas: {passed}/{len(answered)}. Relatório: docs/evals/{run.name}.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avaliação do Fornalytics com a Loja Aurora.")
    parser.add_argument(
        "--run", default=date.today().isoformat(), help="nome da rodada (padrão: hoje)"
    )
    parser.add_argument("--only", help="ids separados por vírgula")
    parser.add_argument("--core", action="store_true", help="só o subconjunto rápido")
    parser.add_argument("--lens", choices=[lens.value for lens in Lens])
    parser.add_argument("--redo", action="store_true", help="refaz perguntas já respondidas")
    parser.add_argument("--delay", type=float, default=4.0, help="segundos entre chamadas")
    parser.add_argument("--report", action="store_true", help="só reescreve o relatório")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
