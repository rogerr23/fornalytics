"""Rules of "Isso faz?": the verdict always agrees with the product base. Pure code: no IO.

The Ideia × Código tab groups the same `features[].status`, so the two tabs can never
contradict each other.
"""

import unicodedata

from app.citations.validator import CitationValidator
from app.domain.enums import FeatureStatus, SourceType, Verdict
from app.domain.lenses import DoesItDraft, DoesItResult, MatchedFeature
from app.domain.product_base import Evidence, Feature, ProductBase

STATUS_VERDICT = {
    FeatureStatus.IMPLEMENTED: Verdict.SIM,
    FeatureStatus.UNDOCUMENTED: Verdict.SIM,
    FeatureStatus.PARTIAL: Verdict.PARCIALMENTE,
    FeatureStatus.DOCUMENTED_ONLY: Verdict.NAO,
}

# Used when the model's justification contradicts the base and is replaced.
STATUS_SENTENCE = {
    FeatureStatus.IMPLEMENTED: "Sim, o produto faz isso.",
    FeatureStatus.UNDOCUMENTED: "Sim, o produto faz isso (existe no código, mas não estava no "
    "documento da ideia).",
    FeatureStatus.PARTIAL: "Parcialmente: existe uma parte no código.",
    FeatureStatus.DOCUMENTED_ONLY: "Não: está prometido no documento da ideia, mas não foi "
    "encontrado no código.",
}

NOT_FOUND = "Não encontrei no material evidência de que o produto faça isso."


def _key(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(plain.casefold().split())


def find_feature(base: ProductBase, name: str) -> Feature | None:
    """The base feature with this exact name (ignoring case, accents and spacing)."""
    wanted = _key(name)
    if not wanted:
        return None
    return next((feature for feature in base.features if _key(feature.name) == wanted), None)


def reconcile_verdict(
    question: str, draft: DoesItDraft, base: ProductBase, validator: CitationValidator
) -> DoesItResult:
    evidence, _dropped = validator.filter(draft.evidence)
    feature = find_feature(base, draft.feature_name)

    if feature is not None:
        verdict = STATUS_VERDICT[feature.status]
        adjusted = verdict != draft.verdict
        justification = (
            f"{STATUS_SENTENCE[feature.status]} {feature.description}".strip()
            if adjusted
            else draft.justification.strip()
        )
        return DoesItResult(
            question=question,
            verdict=verdict,
            feature=MatchedFeature(name=feature.name, status=feature.status),
            justification=justification,
            # The base evidence was already checked when the base was built.
            evidence=_merge(feature.evidence, evidence),
            adjusted=adjusted,
        )

    has_code_proof = any(item.source_type == SourceType.CODE for item in evidence)
    if draft.verdict != Verdict.NAO and not has_code_proof:
        # "Yes" without a feature in the base and without code evidence is not trusted.
        return DoesItResult(
            question=question,
            verdict=Verdict.NAO,
            feature=None,
            justification=NOT_FOUND,
            evidence=evidence,
            adjusted=True,
        )
    return DoesItResult(
        question=question,
        verdict=draft.verdict,
        feature=None,
        justification=draft.justification.strip() or NOT_FOUND,
        evidence=evidence,
        adjusted=False,
    )


def _merge(first: list[Evidence], second: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[str, int, int]] = set()
    merged: list[Evidence] = []
    for item in [*first, *second]:
        key = (item.path, item.line_start, item.line_end)
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return merged
