from collections import Counter

from evals.schema import load_eval_set


def test_question_file_is_valid_and_balanced() -> None:
    eval_set = load_eval_set()

    per_lens = Counter(q.lens for q in eval_set.questions if q.lens is not None)
    assert set(per_lens.values()) == {15}  # about 15 per lens (CLAUDE.md 4.5)
    assert any(q.kind == "compare" for q in eval_set.questions)
    # The demo script questions are covered (they become the backup answers).
    demo = {q.id for q in eval_set.questions if q.demo}
    assert {"nt-09", "tec-02", "cmp-01", "tec-15"} <= demo
    # Every "Isso faz?" has an expected verdict; the two promised gaps are there.
    gaps = [q for q in eval_set.questions if q.kind == "does_it" and q.expect.feature_any]
    assert {"cupom", "nota fiscal"} <= {name for q in gaps for name in q.expect.feature_any}
