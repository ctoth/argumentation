from __future__ import annotations

from dataclasses import asdict
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aba.aba import ABAFramework
from tests.aba_hypothesis_generators import (
    flat_aba_frameworks,
    flat_aba_specs,
    renamed_framework,
)
from tools.aba_shape_benchmark import (
    ROUTE_REQUIRED_FIELDS,
    compute_aba_shape,
    route_candidates,
    route_candidates_from_shape_data,
)


SOLVER_CLASS = "aba/single-extension/preferred"
STABLE_SOLVER_CLASS = "aba/single-extension/stable"
AVAILABLE_BACKENDS = ("auto", "asp", "sat")


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_renaming_instance_path_does_not_change_route_decision(
    framework: ABAFramework,
) -> None:
    shape_data = asdict(compute_aba_shape(framework))

    left = dict(
        shape_data,
        path="C:/bench/iccma2025/a.apx",
        filename="a.apx",
        parent_directory="iccma2025",
        year=2025,
        generator_name="iccma",
        manifest_identity="left",
    )
    right = dict(
        shape_data,
        path="D:/unrelated/local-example/name-has-no-signal.apx",
        filename="name-has-no-signal.apx",
        parent_directory="local-example",
        year=2017,
        generator_name="local",
        manifest_identity="right",
    )

    assert _route_signature(left) == _route_signature(right)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_moving_same_file_to_different_directory_does_not_change_route_decision(
    framework: ABAFramework,
) -> None:
    shape_data = asdict(compute_aba_shape(framework))

    left = dict(shape_data, path="C:/first/root/case.apx", parent_directory="first")
    right = dict(shape_data, path="C:/second/root/case.apx", parent_directory="second")

    assert _route_signature(left) == _route_signature(right)


@given(st.lists(flat_aba_frameworks(), min_size=1, max_size=6))
@settings(max_examples=25)
def test_shuffling_manifest_row_order_does_not_change_route_decision(
    frameworks: list[ABAFramework],
) -> None:
    rows = [
        dict(asdict(compute_aba_shape(framework)), row_number=index)
        for index, framework in enumerate(frameworks)
    ]

    assert sorted(_route_signature(row) for row in rows) == sorted(
        _route_signature(row) for row in reversed(rows)
    )


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_atom_renaming_does_not_change_route_decision(framework: ABAFramework) -> None:
    renamed, _ = renamed_framework(framework)

    assert _candidate_signature(route_candidates(compute_aba_shape(framework), SOLVER_CLASS)) == (
        _candidate_signature(route_candidates(compute_aba_shape(renamed), SOLVER_CLASS))
    )


@given(flat_aba_specs())
@settings(max_examples=40)
def test_rule_order_permutation_does_not_change_route_decision(spec) -> None:
    forward = spec.to_framework()
    reversed_rules = ABAFramework(
        language=spec.language,
        assumptions=spec.assumptions,
        contrary=spec.contrary,
        rules=frozenset(reversed(spec.rules)),
    )

    assert _candidate_signature(route_candidates(compute_aba_shape(forward), SOLVER_CLASS)) == (
        _candidate_signature(route_candidates(compute_aba_shape(reversed_rules), SOLVER_CLASS))
    )


@given(flat_aba_frameworks())
@settings(max_examples=20)
def test_route_predicate_cannot_fire_with_missing_required_shape_fields(
    framework: ABAFramework,
) -> None:
    shape_data = asdict(compute_aba_shape(framework))

    for field in ROUTE_REQUIRED_FIELDS:
        incomplete = dict(shape_data)
        del incomplete[field]

        assert (
            route_candidates_from_shape_data(
                incomplete,
                SOLVER_CLASS,
                available_backends=AVAILABLE_BACKENDS,
            )
            == []
        )


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_route_predicates_emit_paper_backed_reason_fields(
    framework: ABAFramework,
) -> None:
    for candidate in route_candidates(
        compute_aba_shape(framework),
        SOLVER_CLASS,
        available_backends=AVAILABLE_BACKENDS,
        timeout_budget_class="30s",
    ):
        assert candidate.reason["paper"]
        assert set(candidate.reason["fields"]) <= ROUTE_REQUIRED_FIELDS
        assert candidate.reason["solver_class"] == SOLVER_CLASS
        assert candidate.reason["timeout_budget_class"] == "30s"


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_production_route_predicates_have_benchmark_evidence_id(
    framework: ABAFramework,
) -> None:
    for candidate in route_candidates(
        compute_aba_shape(framework),
        SOLVER_CLASS,
        available_backends=AVAILABLE_BACKENDS,
    ):
        if candidate.production:
            assert candidate.evidence_id


def test_large_dense_stable_route_candidate_is_production_sat() -> None:
    shape_data = _large_dense_stable_shape_data()

    candidates = route_candidates_from_shape_data(
        shape_data,
        STABLE_SOLVER_CLASS,
        available_backends=AVAILABLE_BACKENDS,
        timeout_budget_class="30s",
    )

    assert any(
        candidate.backend == "sat"
        and candidate.predicate == "large_dense_stable_sat_route"
        and candidate.production
        and candidate.evidence_id == "aba-c1-stable-route-2026-05-17"
        for candidate in candidates
    )


def test_large_dense_stable_route_ignores_locator_fields() -> None:
    shape_data = _large_dense_stable_shape_data()
    left = dict(
        shape_data,
        path="C:/bench/iccma2025/ABAs/aba_2000_0.1_5_5_3.aba",
        filename="aba_2000_0.1_5_5_3.aba",
        parent_directory="ABAs",
        year=2025,
        generator_name="iccma",
        row_number=84,
    )
    right = dict(
        shape_data,
        path="D:/local/renamed/unrelated.aba",
        filename="unrelated.aba",
        parent_directory="renamed",
        year=2019,
        generator_name="local",
        row_number=1,
    )

    assert _route_signature(left, solver_class_name=STABLE_SOLVER_CLASS) == _route_signature(
        right,
        solver_class_name=STABLE_SOLVER_CLASS,
    )


def test_large_dense_preferred_native_cnf_route_is_production_sat() -> None:
    candidates = route_candidates_from_shape_data(
        _large_dense_preferred_shape_data(),
        SOLVER_CLASS,
        available_backends=AVAILABLE_BACKENDS,
        timeout_budget_class="30s",
    )

    assert any(
        candidate.backend == "sat"
        and candidate.predicate == "native_cnf_dense_prefsat_route"
        and candidate.production
        and candidate.evidence_id == "aba-native-cnf-prefsat-2026-05-18"
        for candidate in candidates
    )


def test_large_dense_preferred_asp_candidate_is_not_production_route() -> None:
    candidates = route_candidates_from_shape_data(
        _large_dense_preferred_shape_data(),
        SOLVER_CLASS,
        available_backends=AVAILABLE_BACKENDS,
        timeout_budget_class="30s",
    )

    asp_candidates = [
        candidate
        for candidate in candidates
        if candidate.backend == "asp" and candidate.predicate == "flat_direct_asp_candidate"
    ]
    assert asp_candidates
    assert all(not candidate.production for candidate in asp_candidates)


def _large_dense_stable_shape_data() -> dict[str, Any]:
    return {
        "is_flat": True,
        "is_normal": False,
        "rule_density": 26.0,
        "p_acyclic": False,
        "tau_aba_primal_width_proxy": 26,
        "stable_obstruction_count": 0,
        "dependency_scc_max_size": 8,
        "contrary_target_in_degree_max": 1,
        "closure_growth_sample": 0.75,
        "decomp_component_count": 1,
        "decomp_max_component_assumptions": 151,
        "decomp_no_reduction_reason": "single_component",
        "assumptions": 151,
    }


def _large_dense_preferred_shape_data() -> dict[str, Any]:
    return {
        "is_flat": True,
        "is_normal": False,
        "rule_density": 26.0,
        "p_acyclic": False,
        "tau_aba_primal_width_proxy": 26,
        "stable_obstruction_count": 0,
        "dependency_scc_max_size": 8,
        "contrary_target_in_degree_max": 1,
        "closure_growth_sample": 0.75,
        "decomp_component_count": 1,
        "decomp_max_component_assumptions": 151,
        "decomp_no_reduction_reason": "single_component",
        "assumptions": 151,
    }


def _route_signature(
    shape_data: dict[str, Any],
    *,
    solver_class_name: str = SOLVER_CLASS,
) -> tuple[tuple[Any, ...], ...]:
    return _candidate_signature(
        route_candidates_from_shape_data(
            shape_data,
            solver_class_name,
            available_backends=AVAILABLE_BACKENDS,
            timeout_budget_class="30s",
        )
    )


def _candidate_signature(candidates) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        sorted(
            (
                candidate.backend,
                candidate.predicate,
                candidate.production,
                candidate.evidence_id,
                tuple(sorted(candidate.reason.items())),
            )
            for candidate in candidates
        )
    )
