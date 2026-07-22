from __future__ import annotations

from collections.abc import Iterable

from hypothesis import given, settings

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from tests.aba_hypothesis_generators import (
    flat_aba_frameworks,
    normal_candidate_frameworks,
    p_acyclic_frameworks,
)
from tools.aba_shape_benchmark import compute_aba_shape


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_stable_sets_are_closed_conflict_free_and_attack_outsiders(
    framework: ABAFramework,
) -> None:
    for extension in native_aba.stable_extensions(framework):
        assert native_aba.closed(framework, extension)
        assert native_aba.conflict_free(framework, extension)
        assert all(
            native_aba.attacks(framework, extension, frozenset({assumption}))
            for assumption in framework.assumptions - extension
        )


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_admissible_sets_are_conflict_free_and_counterattack_attackers(
    framework: ABAFramework,
) -> None:
    for extension in _all_assumption_subsets(framework.assumptions):
        if not native_aba.admissible(framework, extension):
            continue
        assert native_aba.closed(framework, extension)
        assert native_aba.conflict_free(framework, extension)
        for attacker in _all_assumption_subsets(framework.assumptions):
            if native_aba.closed(framework, attacker) and native_aba.attacks(
                framework,
                attacker,
                extension,
            ):
                assert native_aba.attacks(framework, extension, attacker)


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_preferred_sets_are_maximal_admissible_sets(framework: ABAFramework) -> None:
    admissible_sets = {
        extension
        for extension in _all_assumption_subsets(framework.assumptions)
        if native_aba.admissible(framework, extension)
    }

    for preferred in native_aba.preferred_extensions(framework):
        assert preferred in admissible_sets
        assert not any(preferred < candidate for candidate in admissible_sets)


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_every_preferred_set_is_admissible(framework: ABAFramework) -> None:
    assert all(
        native_aba.admissible(framework, extension)
        for extension in native_aba.preferred_extensions(framework)
    )


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_empty_set_is_admissible_in_flat_frameworks(framework: ABAFramework) -> None:
    assert compute_aba_shape(framework).is_flat is True
    assert native_aba.admissible(framework, frozenset())


@given(normal_candidate_frameworks())
@settings(max_examples=10)
def test_normal_candidate_frameworks_have_preferred_stable_coincidence(
    framework: ABAFramework,
) -> None:
    assert compute_aba_shape(framework).is_normal is True
    assert native_aba.preferred_extensions(framework) == native_aba.stable_extensions(
        framework
    )


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_grounded_iteration_reaches_fixpoint_within_assumption_count(
    framework: ABAFramework,
) -> None:
    shape = compute_aba_shape(framework)

    assert shape.grounded_iteration_count <= shape.assumption_count


@given(p_acyclic_frameworks())
@settings(max_examples=35)
def test_p_acyclic_frameworks_have_no_cyclic_non_assumption_support(
    framework: ABAFramework,
) -> None:
    shape = compute_aba_shape(framework)

    assert shape.p_acyclic is True
    assert shape.dependency_cycle_count_or_flag == 0


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6))
@settings(max_examples=35, deadline=10000)
def test_stable_extensions_contain_no_self_obstructing_assumptions(
    framework: ABAFramework,
) -> None:
    self_obstructing = {
        assumption
        for assumption in framework.assumptions
        if framework.contrary[assumption]
        in _closure(framework, frozenset({assumption}))
    }
    for extension in native_aba.stable_extensions(framework):
        assert not (extension & self_obstructing)


def test_stable_obstruction_count_is_positive_for_impossible_self_attacker() -> None:
    a = Literal(GroundAtom("a"))
    ca = Literal(GroundAtom("ca"))
    framework = ABAFramework(
        language=frozenset({a, ca}),
        assumptions=frozenset({a}),
        contrary={a: ca},
        rules=frozenset({Rule((a,), ca, "strict")}),
    )

    assert native_aba.stable_extensions(framework) == ()
    assert compute_aba_shape(framework).stable_obstruction_count == 1


def _all_assumption_subsets(
    assumptions: frozenset[Literal],
) -> tuple[AssumptionSet, ...]:
    ordered = sorted(assumptions, key=repr)
    subsets: list[AssumptionSet] = [frozenset()]
    for assumption in ordered:
        subsets.extend(subset | frozenset({assumption}) for subset in tuple(subsets))
    return tuple(subsets)


def _closure(
    framework: ABAFramework, premises: Iterable[Literal]
) -> frozenset[Literal]:
    closure = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(antecedent in closure for antecedent in rule.antecedents):
                if rule.consequent not in closure:
                    closure.add(rule.consequent)
                    changed = True
    return frozenset(closure)
