from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation import aba_sat
from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from tests.aba_hypothesis_generators import renamed_framework
from tools.aba_shape_benchmark import compute_aba_shape, route_candidates_from_shape_data


REAL_PREFSAT_PAGE_IMAGES = (
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png",
    "papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000005.png",
    "papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000006.png",
    "papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000012.png",
)


REQUIRED_TELEMETRY_FIELDS = (
    "prefsat_labelling_variables",
    "prefsat_exactly_one_clauses",
    "prefsat_complete_clauses",
    "prefsat_support_materializations",
    "prefsat_solver_checks",
    "prefsat_candidate_models",
    "prefsat_candidate_blocks",
    "prefsat_rejected_supersets",
    "prefsat_max_in_count_seen",
    "prefsat_final_in_count",
    "prefsat_attacker_solver_builds",
    "prefsat_attacker_solver_checks",
    "prefsat_attacker_bitset_closure_checks",
    "prefsat_attacker_bitset_shrink_checks",
    "prefsat_attacker_bitset_rule_firings",
)


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


@st.composite
def small_flat_aba_for_real_prefsat(draw) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=1, max_value=8))
    assumptions = tuple(lit(f"a{index}") for index in range(assumption_count))
    atoms = tuple(lit(f"x{index}") for index in range(max(assumption_count + 2, 4)))
    contraries = {
        assumption: atoms[(index + 1) % len(atoms)]
        for index, assumption in enumerate(assumptions)
    }
    max_rules = min(16, max(4, assumption_count * 2))
    rule_count = draw(st.integers(min_value=0, max_value=max_rules))
    body_pool = (*assumptions, *atoms)
    rule_specs = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=len(atoms) - 1),
                st.lists(
                    st.integers(min_value=0, max_value=len(body_pool) - 1),
                    min_size=0,
                    max_size=min(3, len(body_pool)),
                    unique=True,
                ),
            ),
            min_size=rule_count,
            max_size=rule_count,
        )
    )
    generated_rules = [
        Rule(tuple(body_pool[index] for index in body), atoms[head], "strict")
        for head, body in rule_specs
    ]
    cycle_rules = [
        Rule((atoms[0],), atoms[1], "strict"),
        Rule((atoms[1],), atoms[0], "strict"),
    ]
    empty_body_rule = [Rule((), atoms[-1], "strict")]
    rules = frozenset((*generated_rules, *cycle_rules, *empty_body_rule))
    language = frozenset((*assumptions, *atoms, *(literal for rule in rules for literal in rule.antecedents)))
    return ABAFramework(
        language=language,
        assumptions=frozenset(assumptions),
        contrary=contraries,
        rules=rules,
    )


def test_real_prefsat_exposes_three_valued_labelling_surface() -> None:
    framework = _two_choice_framework()

    result = aba_sat.real_prefsat_extension(framework)

    assert result.route_metadata["algorithm"] == "complete-labelling-prefsat"
    assert set(result.prefsat_in) == framework.assumptions, REAL_PREFSAT_PAGE_IMAGES[0]
    assert set(result.prefsat_out) == framework.assumptions, REAL_PREFSAT_PAGE_IMAGES[0]
    assert set(result.prefsat_undec) == framework.assumptions, REAL_PREFSAT_PAGE_IMAGES[0]
    for assumption in framework.assumptions:
        labels = (
            result.prefsat_in[assumption],
            result.prefsat_out[assumption],
            result.prefsat_undec[assumption],
        )
        assert sum(bool(label) for label in labels) == 1, REAL_PREFSAT_PAGE_IMAGES[1]


def test_real_prefsat_labels_mutual_attack_witness_decisively() -> None:
    framework = _two_choice_framework()

    result = aba_sat.real_prefsat_extension(framework)
    selected = next(iter(result.extension))
    rejected = next(iter(framework.assumptions - result.extension))

    assert result.extension in aba_sat.support_extensions(framework, "preferred")
    assert result.prefsat_in[selected]
    assert result.prefsat_out[rejected]
    assert not result.prefsat_undec[selected]
    assert not result.prefsat_undec[rejected]
    assert result.route_metadata["algorithm"] == "complete-labelling-prefsat"


def test_real_prefsat_rejects_asp_and_greedy_substitutes() -> None:
    result = aba_sat.real_prefsat_extension(_two_choice_framework())

    assert result.route_metadata["backend"] == "sat", REAL_PREFSAT_PAGE_IMAGES[3]
    assert result.route_metadata["algorithm"] == "complete-labelling-prefsat"
    assert result.route_metadata["rejected_substitutes"] == (
        "old-support-aware-cegar",
        "asp-optimization",
        "greedy-growth",
    )


def test_real_prefsat_route_ignores_filename_and_manifest_identity() -> None:
    shape_data = asdict(compute_aba_shape(_dense_flat_framework(6)))
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

    assert _real_prefsat_route_signature(left) == _real_prefsat_route_signature(right)


def test_dense_flat_real_prefsat_does_not_materialize_minimal_supports() -> None:
    result = aba_sat.real_prefsat_extension(_dense_flat_framework(8))

    assert result.telemetry["prefsat_support_materializations"] == 0, REAL_PREFSAT_PAGE_IMAGES[8]


@given(st.integers(min_value=3, max_value=9).filter(lambda size: size % 2 == 1))
@settings(max_examples=4, deadline=None)
def test_real_prefsat_preserves_undecided_odd_cycle_labelling(size: int) -> None:
    framework = _odd_cycle_framework(size)

    result = aba_sat.real_prefsat_extension(framework)

    assert result.extension == frozenset()
    assert not any(result.prefsat_in.values())
    assert not any(result.prefsat_out.values())
    assert all(result.prefsat_undec.values())
    assert result.telemetry["prefsat_final_in_count"] == 0


@given(st.integers(min_value=3, max_value=8))
@settings(max_examples=6, deadline=None)
def test_real_prefsat_support_pressure_stays_structural(size: int) -> None:
    framework = _support_pressure_framework(size)

    result = aba_sat.real_prefsat_extension(framework)
    telemetry = result.telemetry
    attack_edge_count = aba_sat.real_prefsat_attack_edge_count(framework)

    assert result.extension in aba_sat.support_extensions(framework, "preferred")
    assert telemetry["prefsat_support_materializations"] == 0
    assert telemetry["prefsat_labelling_variables"] == 3 * len(framework.assumptions)
    assert telemetry["prefsat_exactly_one_clauses"] == len(framework.assumptions)
    assert telemetry["prefsat_complete_clauses"] <= 24 * (
        len(framework.assumptions) + len(framework.rules) + attack_edge_count
    )
    assert telemetry["prefsat_attacker_solver_builds"] == 0, REAL_PREFSAT_PAGE_IMAGES[4]
    assert telemetry["prefsat_attacker_solver_checks"] == 0
    assert telemetry["prefsat_attacker_bitset_closure_checks"] >= (
        telemetry["prefsat_attacker_bitset_shrink_checks"]
    )
    assert telemetry["prefsat_attacker_bitset_rule_firings"] <= (
        telemetry["prefsat_attacker_bitset_closure_checks"]
        * max(1, _rule_antecedent_count(framework))
    )


def test_real_prefsat_page_image_contract_is_complete() -> None:
    assert len(REAL_PREFSAT_PAGE_IMAGES) == 11
    assert all(path.endswith(".png") for path in REAL_PREFSAT_PAGE_IMAGES)


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=40, deadline=None)
def test_real_prefsat_matches_preferred_oracle(framework: ABAFramework) -> None:
    result = aba_sat.real_prefsat_extension(framework)

    assert result.extension in aba_sat.support_extensions(framework, "preferred")


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=40, deadline=None)
def test_real_prefsat_operational_bounds(framework: ABAFramework) -> None:
    result = aba_sat.real_prefsat_extension(framework)
    telemetry = result.telemetry
    attack_edge_count = aba_sat.real_prefsat_attack_edge_count(framework)

    assert set(REQUIRED_TELEMETRY_FIELDS) <= set(telemetry)
    assert telemetry["prefsat_solver_checks"] <= 2 * telemetry["prefsat_candidate_blocks"] + 4
    assert telemetry["prefsat_candidate_models"] <= telemetry["prefsat_candidate_blocks"] + 2
    assert telemetry["prefsat_candidate_blocks"] <= len(framework.assumptions) + 2
    assert telemetry["prefsat_labelling_variables"] == 3 * len(framework.assumptions)
    assert telemetry["prefsat_exactly_one_clauses"] == len(framework.assumptions)
    assert telemetry["prefsat_complete_clauses"] <= 24 * (
        len(framework.assumptions) + len(framework.rules) + attack_edge_count
    )
    assert telemetry["prefsat_attacker_solver_builds"] == 0
    assert telemetry["prefsat_attacker_solver_checks"] == 0
    assert telemetry["prefsat_attacker_bitset_closure_checks"] >= (
        telemetry["prefsat_attacker_bitset_shrink_checks"]
    )
    assert telemetry["prefsat_attacker_bitset_rule_firings"] <= (
        telemetry["prefsat_attacker_bitset_closure_checks"]
        * max(1, _rule_antecedent_count(framework))
    )


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=40, deadline=None)
def test_real_prefsat_labelling_matches_closure_observations(framework: ABAFramework) -> None:
    result = aba_sat.real_prefsat_extension(framework)
    closure = _closure(framework, result.extension)

    for assumption in framework.assumptions:
        labels = (
            result.prefsat_in[assumption],
            result.prefsat_out[assumption],
            result.prefsat_undec[assumption],
        )
        assert sum(bool(label) for label in labels) == 1
        assert result.prefsat_in[assumption] is (assumption in result.extension)
        assert result.prefsat_out[assumption] is (framework.contrary[assumption] in closure)
        assert result.prefsat_undec[assumption] is (
            assumption not in result.extension
            and framework.contrary[assumption] not in closure
        )


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=40, deadline=None)
def test_real_prefsat_residual_reduction_progress(framework: ABAFramework) -> None:
    result = aba_sat.real_prefsat_extension(framework)
    events = result.progress_events

    stalled = 0
    previous_max = -1
    previous_blocks = -1
    for event in events:
        max_seen = event["prefsat_max_in_count_seen"]
        blocks = event["prefsat_candidate_blocks"]
        if max_seen > previous_max or blocks > previous_blocks:
            stalled = 0
        else:
            stalled += 1
        assert stalled < 2
        previous_max = max_seen
        previous_blocks = blocks


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=20, deadline=None)
def test_real_prefsat_renaming_preserves_extension_size(framework: ABAFramework) -> None:
    renamed, mapping = renamed_framework(framework)
    inverse = {renamed_literal: original for original, renamed_literal in mapping.items()}

    original = aba_sat.real_prefsat_extension(framework).extension
    renamed_extension = aba_sat.real_prefsat_extension(renamed).extension
    lifted = frozenset(inverse[assumption] for assumption in renamed_extension)

    assert len(original) == len(lifted)


def _real_prefsat_route_signature(shape_data: dict[str, Any]) -> tuple[tuple[Any, ...], ...]:
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


def _two_choice_framework() -> ABAFramework:
    a0 = lit("a0")
    a1 = lit("a1")
    c0 = lit("c0")
    c1 = lit("c1")
    return ABAFramework(
        language=frozenset({a0, a1, c0, c1}),
        assumptions=frozenset({a0, a1}),
        contrary={a0: c0, a1: c1},
        rules=frozenset({
            Rule((a0,), c1, "strict"),
            Rule((a1,), c0, "strict"),
        }),
    )


def _dense_flat_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    atoms = tuple(lit(f"x{index}") for index in range(size))
    rules = frozenset(
        Rule(
            tuple(assumptions[(index + offset) % size] for offset in range(min(3, size))),
            atoms[index],
            "strict",
        )
        for index in range(size)
    )
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary={assumption: atoms[index] for index, assumption in enumerate(assumptions)},
        rules=rules,
    )


def _odd_cycle_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    contraries = tuple(lit(f"c{index}") for index in range(size))
    rules = frozenset(
        Rule((assumptions[index],), contraries[(index + 1) % size], "strict")
        for index in range(size)
    )
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        assumptions=frozenset(assumptions),
        contrary={assumption: contraries[index] for index, assumption in enumerate(assumptions)},
        rules=rules,
    )


def _support_pressure_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    contraries = tuple(lit(f"c{index}") for index in range(size))
    helper = tuple(lit(f"h{index}") for index in range(size))
    rules = []
    for index, assumption in enumerate(assumptions):
        next_assumption = assumptions[(index + 1) % size]
        previous_assumption = assumptions[(index - 1) % size]
        rules.append(Rule((assumption,), helper[index], "strict"))
        rules.append(Rule((helper[index], next_assumption), contraries[index], "strict"))
        rules.append(Rule((previous_assumption, next_assumption), contraries[index], "strict"))
    return ABAFramework(
        language=frozenset((*assumptions, *contraries, *helper)),
        assumptions=frozenset(assumptions),
        contrary={assumption: contraries[index] for index, assumption in enumerate(assumptions)},
        rules=frozenset(rules),
    )


def _closure(framework: ABAFramework, extension: frozenset[Literal]) -> frozenset[Literal]:
    derived = set(extension)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(antecedent in derived for antecedent in rule.antecedents):
                if rule.consequent not in derived:
                    derived.add(rule.consequent)
                    changed = True
    return frozenset(derived)


def _rule_antecedent_count(framework: ABAFramework) -> int:
    return sum(len(frozenset(rule.antecedents)) for rule in framework.rules)
