from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba import aba_sat
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from tools.aba_shape_benchmark import compute_aba_shape, route_candidates_from_shape_data


DECOMPOSED_PREFSAT_PAGE_IMAGES = (
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png",
    "papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png",
    "papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png",
    "papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-005.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-006.png",
    "papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-012.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-019.png",
    "papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png",
)

REQUIRED_DECOMPOSED_PREFSAT_TELEMETRY = (
    "decomp_original_assumptions",
    "decomp_original_rules",
    "decomp_residual_assumptions",
    "decomp_residual_rules",
    "decomp_component_count",
    "decomp_max_component_assumptions",
    "decomp_max_component_rules",
    "decomp_prefsat_component_calls",
    "decomp_full_instance_prefsat_calls",
    "decomp_solver_checks",
    "decomp_lifted_extension_size",
    "decomp_validation_success",
)

ALLOWED_NO_REDUCTION_REASONS = {
    "reduced",
    "empty_residual",
    "single_component",
    "component_plan_not_exact",
}


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


@st.composite
def layered_independent_aba_for_decomposition(draw) -> ABAFramework:
    component_count = draw(st.integers(min_value=2, max_value=5))
    two_assumption_components = draw(
        st.sets(
            st.integers(min_value=0, max_value=component_count - 1),
            min_size=0,
            max_size=min(4, 8 - component_count),
        )
    )
    assumptions: list[Literal] = []
    contrary: dict[Literal, Literal] = {}
    rules: list[Rule] = []
    language: set[Literal] = set()
    for component in range(component_count):
        local_count = 2 if component in two_assumption_components else 1
        local_assumptions = [
            lit(f"c{component}_a{index}") for index in range(local_count)
        ]
        local_contraries = [
            lit(f"c{component}_x{index}") for index in range(local_count)
        ]
        assumptions.extend(local_assumptions)
        language.update(local_assumptions)
        language.update(local_contraries)
        for index, assumption in enumerate(local_assumptions):
            contrary[assumption] = local_contraries[index]
        if local_count == 1:
            continue
        rules.append(Rule((local_assumptions[0],), local_contraries[1], "strict"))
        rules.append(Rule((local_assumptions[1],), local_contraries[0], "strict"))
    assert len(assumptions) <= 8
    assert len(rules) <= 18
    return ABAFramework(
        language=frozenset(language),
        assumptions=frozenset(assumptions),
        contrary=contrary,
        rules=frozenset(rules),
    )


@st.composite
def single_component_aba_for_no_reduction(draw) -> ABAFramework:
    size = draw(st.integers(min_value=2, max_value=6))
    assumptions = [lit(f"a{index}") for index in range(size)]
    contraries = [lit(f"x{index}") for index in range(size)]
    contrary = {assumption: contraries[index] for index, assumption in enumerate(assumptions)}
    rules = [
        Rule((assumptions[index],), contraries[(index + 1) % size], "strict")
        for index in range(size)
    ]
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        assumptions=frozenset(assumptions),
        contrary=contrary,
        rules=frozenset(rules),
    )


def test_decomposed_prefsat_page_image_contract() -> None:
    assert len(DECOMPOSED_PREFSAT_PAGE_IMAGES) == 13
    for path in DECOMPOSED_PREFSAT_PAGE_IMAGES:
        assert path.endswith(".png")
        assert Path(path).exists(), path


@given(layered_independent_aba_for_decomposition())
@settings(max_examples=25, deadline=None)
def test_decomposed_prefsat_matches_preferred_oracle_on_small_products(
    framework: ABAFramework,
) -> None:
    from argumentation.structured.aba import aba_decomposition

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    assert result.extension in aba_sat.support_extensions(framework, "preferred")


@given(layered_independent_aba_for_decomposition())
@settings(max_examples=25, deadline=None)
def test_decomposition_reports_required_telemetry(framework: ABAFramework) -> None:
    from argumentation.structured.aba import aba_decomposition

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    _assert_decomposition_telemetry(framework, result.telemetry)


def test_reduced_product_never_calls_full_instance_prefsat(monkeypatch: pytest.MonkeyPatch) -> None:
    from argumentation.structured.aba import aba_decomposition

    framework = _independent_product_framework(component_count=3)
    original_kernel = aba_sat.real_prefsat_extension
    calls: list[ABAFramework] = []

    def spy_real_prefsat(
        called_framework: ABAFramework,
        **kwargs: Any,
    ) -> Any:
        assert called_framework is not framework
        calls.append(called_framework)
        return original_kernel(called_framework, **kwargs)

    monkeypatch.setattr(aba_sat, "real_prefsat_extension", spy_real_prefsat)

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    assert result.telemetry["decomp_no_reduction_reason"] == "reduced"
    assert result.telemetry["decomp_full_instance_prefsat_calls"] == 0
    assert result.telemetry["decomp_prefsat_component_calls"] == len(calls) == 3
    assert all(len(call.assumptions) < len(framework.assumptions) for call in calls)


def test_no_reduction_calls_real_prefsat_once_and_reports_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from argumentation.structured.aba import aba_decomposition

    framework = _single_component_framework(size=4)
    original_kernel = aba_sat.real_prefsat_extension
    calls: list[ABAFramework] = []

    def spy_real_prefsat(
        called_framework: ABAFramework,
        **kwargs: Any,
    ) -> Any:
        calls.append(called_framework)
        return original_kernel(called_framework, **kwargs)

    monkeypatch.setattr(aba_sat, "real_prefsat_extension", spy_real_prefsat)

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    assert result.telemetry["decomp_no_reduction_reason"] == "single_component"
    assert result.telemetry["decomp_full_instance_prefsat_calls"] == 1
    assert result.telemetry["decomp_prefsat_component_calls"] == 0
    assert len(calls) == 1


def test_decomposition_never_calls_aba_to_dung(monkeypatch: pytest.MonkeyPatch) -> None:
    from argumentation.structured.aba import aba_decomposition

    def fail_aba_to_dung(_framework: ABAFramework) -> None:
        raise AssertionError("decomposed PrefSat must stay on direct ABA facts")

    monkeypatch.setattr(native_aba, "aba_to_dung", fail_aba_to_dung)

    result = aba_decomposition.decomposed_prefsat_extension(
        _independent_product_framework(component_count=2)
    )

    assert result.telemetry["decomp_validation_success"] == 1


@given(layered_independent_aba_for_decomposition())
@settings(max_examples=25, deadline=None)
def test_lifted_answer_validates_against_original_framework(framework: ABAFramework) -> None:
    from argumentation.structured.aba import aba_decomposition

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    assert result.telemetry["decomp_validation_success"] == 1
    assert result.extension <= framework.assumptions


def test_decomposed_route_ignores_filename_manifest_year_and_path() -> None:
    framework = _independent_product_framework(component_count=3)
    shape_data = asdict(compute_aba_shape(framework))
    left = dict(
        shape_data,
        path="C:/iccma/2025/ABAs/aba_2000_0.1_5_5_0.aba",
        filename="aba_2000_0.1_5_5_0.aba",
        parent_directory="ABAs",
        year=2025,
        generator_name="iccma",
        manifest_identity="T1",
    )
    right = dict(
        shape_data,
        path="D:/local/not-a-benchmark/renamed.aba",
        filename="renamed.aba",
        parent_directory="not-a-benchmark",
        year=2011,
        generator_name="synthetic",
        manifest_identity="local",
    )

    assert any(
        candidate[0] == "sat"
        and candidate[1] == "decomposed_prefsat_reduced_product"
        and candidate[2] is True
        and candidate[3] == "aba-decomposed-prefsat-composition-2026-05-18"
        for candidate in _decomposed_route_signature(left)
    )
    assert _decomposed_route_signature(left) == _decomposed_route_signature(right)


def _assert_decomposition_telemetry(
    framework: ABAFramework,
    telemetry: dict[str, Any],
) -> None:
    assert set(REQUIRED_DECOMPOSED_PREFSAT_TELEMETRY) <= set(telemetry)
    assert telemetry["decomp_no_reduction_reason"] in ALLOWED_NO_REDUCTION_REASONS
    assert telemetry["decomp_original_assumptions"] == len(framework.assumptions)
    assert telemetry["decomp_original_rules"] == len(framework.rules)
    assert telemetry["decomp_residual_assumptions"] <= telemetry["decomp_original_assumptions"]
    assert telemetry["decomp_residual_rules"] <= telemetry["decomp_original_rules"]
    if telemetry["decomp_no_reduction_reason"] == "reduced":
        assert telemetry["decomp_full_instance_prefsat_calls"] == 0
        assert telemetry["decomp_prefsat_component_calls"] == telemetry["decomp_component_count"]
        assert telemetry["decomp_max_component_assumptions"] < len(framework.assumptions)
    elif telemetry["decomp_no_reduction_reason"] == "empty_residual":
        assert telemetry["decomp_full_instance_prefsat_calls"] == 0
        assert telemetry["decomp_prefsat_component_calls"] == 0
        assert telemetry["decomp_component_count"] == 0
    else:
        assert telemetry["decomp_full_instance_prefsat_calls"] == 1
    assert telemetry["decomp_validation_success"] == 1


def _decomposed_route_signature(shape_data: dict[str, Any]) -> tuple[tuple[Any, ...], ...]:
    candidates = route_candidates_from_shape_data(
        shape_data,
        "aba/single-extension/preferred",
        available_backends=("auto", "asp", "sat"),
        timeout_budget_class="30s",
    )
    return tuple(
        sorted(
            (
                candidate.backend,
                candidate.predicate,
                candidate.production,
                candidate.evidence_id,
            )
            for candidate in candidates
        )
    )


def _independent_product_framework(component_count: int) -> ABAFramework:
    assumptions: list[Literal] = []
    contrary: dict[Literal, Literal] = {}
    rules: list[Rule] = []
    language: set[Literal] = set()
    for component in range(component_count):
        left = lit(f"p{component}_left")
        right = lit(f"p{component}_right")
        left_contrary = lit(f"p{component}_not_left")
        right_contrary = lit(f"p{component}_not_right")
        assumptions.extend((left, right))
        language.update((left, right, left_contrary, right_contrary))
        contrary[left] = left_contrary
        contrary[right] = right_contrary
        rules.append(Rule((left,), right_contrary, "strict"))
        rules.append(Rule((right,), left_contrary, "strict"))
    return ABAFramework(
        language=frozenset(language),
        assumptions=frozenset(assumptions),
        contrary=contrary,
        rules=frozenset(rules),
    )


def _single_component_framework(size: int) -> ABAFramework:
    assumptions = [lit(f"s{index}") for index in range(size)]
    contraries = [lit(f"sx{index}") for index in range(size)]
    contrary = {assumption: contraries[index] for index, assumption in enumerate(assumptions)}
    rules = [
        Rule((assumptions[index],), contraries[(index + 1) % size], "strict")
        for index in range(size)
    ]
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        assumptions=frozenset(assumptions),
        contrary=contrary,
        rules=frozenset(rules),
    )
