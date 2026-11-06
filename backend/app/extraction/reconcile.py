"""Make the model's base consistent and verifiable, without calling the model again.

- Every citation is checked; invalid ones are dropped (the base is what every lens trusts).
- Every promise ends up as exactly one feature; promises the model forgot become
  documented_only, and features without a known promise become undocumented.
- Without an idea document there is nothing to compare: no documented_only/undocumented.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from app.citations.validator import CitationValidator
from app.domain.enums import FeatureStatus
from app.domain.product_base import Evidence, Feature, IdeaPromises, ProductBase, Promise


class ExtractionMode(StrEnum):
    """Told to the model in the user message (prompts/extraction.md)."""

    CODE_WITH_PROMISES = "codigo_com_promessas"
    CODE_ONLY = "so_codigo"
    IDEA_ONLY = "so_ideia"


@dataclass
class _Checker:
    validator: CitationValidator
    dropped: int = field(default=0)

    def __call__(self, evidence: list[Evidence]) -> list[Evidence]:
        kept, dropped = self.validator.filter(evidence)
        self.dropped += dropped
        return kept


def clean_promises(
    promises: IdeaPromises, validator: CitationValidator
) -> tuple[IdeaPromises, int]:
    """Renumber promises P1..Pn (ids the model can rely on in step b) and check citations."""
    check = _Checker(validator)
    named = [promise for promise in promises.promises if promise.name.strip()]
    cleaned = [
        Promise(
            id=f"P{number}",
            name=promise.name.strip(),
            description=promise.description.strip(),
            evidence=check(promise.evidence),
        )
        for number, promise in enumerate(named, 1)
    ]
    return IdeaPromises(promises=cleaned), check.dropped


def reconcile(
    draft: ProductBase,
    mode: ExtractionMode,
    validator: CitationValidator,
    promises: IdeaPromises | None = None,
) -> tuple[ProductBase, int]:
    """Return the final base and how many citations were dropped."""
    check = _Checker(validator)
    by_id = {promise.id: promise for promise in (promises.promises if promises else [])}
    answered: dict[str, Feature] = {}
    undocumented: list[Feature] = []

    for feature in draft.features:
        evidence = check(feature.evidence)
        ref = feature.promise_ref.strip().upper()
        match mode:
            case ExtractionMode.CODE_WITH_PROMISES if ref in by_id and ref not in answered:
                promise = by_id[ref]
                status = feature.status
                if status == FeatureStatus.UNDOCUMENTED:
                    # It was promised and found in the code: the label was wrong, not the match.
                    status = FeatureStatus.IMPLEMENTED
                answered[ref] = feature.model_copy(
                    update={
                        "status": status,
                        "promise_ref": ref,
                        "evidence": _merge(promise.evidence, evidence),
                    }
                )
            case ExtractionMode.CODE_WITH_PROMISES:
                undocumented.append(_with(feature, FeatureStatus.UNDOCUMENTED, evidence))
            case ExtractionMode.CODE_ONLY:
                status = (
                    feature.status
                    if feature.status in (FeatureStatus.IMPLEMENTED, FeatureStatus.PARTIAL)
                    else FeatureStatus.IMPLEMENTED
                )
                undocumented.append(_with(feature, status, evidence))
            case ExtractionMode.IDEA_ONLY:
                undocumented.append(_with(feature, FeatureStatus.DOCUMENTED_ONLY, evidence))

    promised = [
        answered.get(promise.id)
        or Feature(
            name=promise.name,
            description=promise.description,
            status=FeatureStatus.DOCUMENTED_ONLY,
            promise_ref=promise.id,
            evidence=promise.evidence,
        )
        for promise in by_id.values()
    ]
    base = draft.model_copy(
        update={
            "features": [*promised, *undocumented],
            "flows": [f.model_copy(update={"evidence": check(f.evidence)}) for f in draft.flows],
            "business_rules": [
                r.model_copy(update={"evidence": check(r.evidence)}) for r in draft.business_rules
            ],
        }
    )
    return base, check.dropped


def _with(feature: Feature, status: FeatureStatus, evidence: list[Evidence]) -> Feature:
    return feature.model_copy(update={"status": status, "promise_ref": "", "evidence": evidence})


def _merge(first: list[Evidence], second: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[str, int, int]] = set()
    merged: list[Evidence] = []
    for item in [*first, *second]:
        key = (item.path, item.line_start, item.line_end)
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return merged
