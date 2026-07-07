from __future__ import annotations

from typing import Any


NATIVE_CNF_PREFSAT_MIN_ASSUMPTIONS = 150
NATIVE_CNF_PREFSAT_MIN_RULE_DENSITY = 25.0

SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES = (
    "papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-002.png",
    "papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-003.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-023.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-024.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-027.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-012.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png",
    "papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png",
    "papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-007.png",
    "papers/deKleer_1986_AssumptionBasedTMS/pngs/page-001.png",
    "papers/deKleer_1986_AssumptionBasedTMS/pngs/page-002.png",
)


def native_cnf_prefsat_dense_shape(
    *,
    is_flat: bool,
    assumptions: int,
    rule_density: float,
) -> bool:
    return (
        is_flat
        and assumptions > NATIVE_CNF_PREFSAT_MIN_ASSUMPTIONS
        and rule_density > NATIVE_CNF_PREFSAT_MIN_RULE_DENSITY
    )


def large_dense_flat_aba_shape(framework: Any) -> bool:
    """Framework-level view of the dense shape gate used by auto routing."""
    assumptions = len(framework.assumptions)
    return native_cnf_prefsat_dense_shape(
        is_flat=_is_flat_aba(framework),
        assumptions=assumptions,
        rule_density=(len(framework.rules) / assumptions) if assumptions else 0.0,
    )


def sparse_narrow_native_sat_shape(
    framework: Any,
    *,
    locator_metadata: dict[str, object] | None = None,
) -> bool:
    assumptions = len(framework.assumptions)
    if assumptions < 700:
        return False
    if not _is_flat_aba(framework):
        return False
    language_size = len(framework.language)
    if language_size == 0 or assumptions / language_size > 0.45:
        return False
    rules = len(framework.rules)
    if assumptions == 0 or rules / assumptions < 4.0:
        return False
    if any(len(rule.antecedents) > 2 for rule in framework.rules):
        return False
    if _max_counter(framework.contrary.values()) > 1:
        return False
    if _max_counter(framework.contrary.keys()) > 1:
        return False
    return True


def _is_flat_aba(framework: Any) -> bool:
    return not any(rule.consequent in framework.assumptions for rule in framework.rules)


def _max_counter(values) -> int:
    counts: dict[object, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return max(counts.values(), default=0)
