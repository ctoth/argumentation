from __future__ import annotations

from itertools import permutations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from argumentation.core.dung import ArgumentationFramework, admissible, conflict_free
from argumentation.optimization import (
    OptimizationFeature,
    OptimizationObjective,
    OptimizationPolicy,
    optimize_framework,
)


@st.composite
def small_af_with_candidates(draw: st.DrawFn) -> tuple[ArgumentationFramework, frozenset[str]]:
    arguments = frozenset(
        draw(
            st.sets(
                st.sampled_from(tuple(f"a{index}" for index in range(8))),
                min_size=1,
                max_size=8,
            )
        )
    )
    possible_defeats = tuple((left, right) for left in arguments for right in arguments)
    defeats = frozenset(draw(st.sets(st.sampled_from(possible_defeats), max_size=len(possible_defeats))))
    candidates = frozenset(
        draw(st.sets(st.sampled_from(tuple(sorted(arguments))), min_size=1, max_size=len(arguments)))
    )
    return ArgumentationFramework(arguments=arguments, defeats=defeats), candidates


@given(problem=small_af_with_candidates())
def test_conflict_free_policy_selects_conflict_free_arguments(
    problem: tuple[ArgumentationFramework, frozenset[str]],
) -> None:
    """Dung 1995 p.326 Def. 5: no selected A,B may satisfy attacks(A,B)."""
    framework, candidates = problem
    result = optimize_framework(
        framework,
        OptimizationPolicy(semantics="conflict_free", candidates=candidates),
        (),
    )

    assert result.status in {"optimal", "unsat"}
    if result.status == "optimal":
        assert result.selected_candidate in candidates
        assert conflict_free(result.selected_arguments, framework.defeats)


@given(problem=small_af_with_candidates())
def test_admissible_policy_selects_admissible_arguments(
    problem: tuple[ArgumentationFramework, frozenset[str]],
) -> None:
    """Dung 1995 p.326 Def. 6: admissible means conflict-free and defended."""
    framework, candidates = problem
    result = optimize_framework(
        framework,
        OptimizationPolicy(semantics="admissible", candidates=candidates),
        (),
    )

    assert result.status in {"optimal", "unsat"}
    if result.status == "optimal":
        assert result.selected_candidate in candidates
        assert admissible(result.selected_arguments, framework.arguments, framework.defeats)


def test_admissible_policy_rejects_undefended_candidate() -> None:
    """Dung 1995 p.326 Def. 6: a selected argument must be acceptable w.r.t. S."""
    framework = ArgumentationFramework(
        arguments=frozenset({"candidate", "attacker"}),
        defeats=frozenset({("attacker", "candidate")}),
    )

    result = optimize_framework(
        framework,
        OptimizationPolicy(semantics="admissible", candidates=frozenset({"candidate"})),
        (),
    )

    assert result.status == "unsat"
    assert result.selected_candidate is None


@given(
    primary_left=st.integers(min_value=-20, max_value=20),
    primary_right=st.integers(min_value=-20, max_value=20),
    secondary_left=st.integers(min_value=-20, max_value=20),
    secondary_right=st.integers(min_value=-20, max_value=20),
)
def test_lexicographic_objective_priority_dominates_lower_tier_score(
    primary_left: int,
    primary_right: int,
    secondary_left: int,
    secondary_right: int,
) -> None:
    """Bjorner-Phan 2014 p.7 and Sebastiani-Trentin 2015 p.450: lex optimizes higher-priority objectives first."""
    framework = ArgumentationFramework(
        arguments=frozenset({"left", "right"}),
        defeats=frozenset(),
    )
    result = optimize_framework(
        framework,
        OptimizationPolicy(
            semantics="conflict_free",
            candidates=frozenset({"left", "right"}),
            objectives=(
                OptimizationObjective("primary", direction="maximize", priority=0),
                OptimizationObjective("secondary", direction="maximize", priority=1),
            ),
        ),
        (
            OptimizationFeature("left", "primary", primary_left),
            OptimizationFeature("right", "primary", primary_right),
            OptimizationFeature("left", "secondary", secondary_left),
            OptimizationFeature("right", "secondary", secondary_right),
        ),
    )

    expected = max(
        ("left", "right"),
        key=lambda argument: (
            primary_left if argument == "left" else primary_right,
            secondary_left if argument == "left" else secondary_right,
            -("left", "right").index(argument),
        ),
    )
    assert result.selected_candidate == expected


@given(problem=small_af_with_candidates())
def test_candidate_selection_is_exactly_one_declared_candidate(
    problem: tuple[ArgumentationFramework, frozenset[str]],
) -> None:
    """The workstream's OMT semantics requires exactly one declared decision candidate."""
    framework, candidates = problem
    result = optimize_framework(
        framework,
        OptimizationPolicy(semantics="conflict_free", candidates=candidates),
        (),
    )

    assert result.status in {"optimal", "unsat"}
    if result.status == "optimal":
        assert result.selected_candidate in candidates
        assert sum(candidate == result.selected_candidate for candidate in candidates) == 1


def test_tie_break_is_stable_under_input_order_permutations() -> None:
    """Bjorner-Phan 2014 p.7: after equal objective values, our policy adds deterministic candidate ordering."""
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset(),
    )
    selected = set()
    for ordered_candidates in permutations(("c", "b", "a")):
        result = optimize_framework(
            framework,
            OptimizationPolicy(
                semantics="conflict_free",
                candidates=frozenset(ordered_candidates),
                objectives=(OptimizationObjective("score", direction="maximize", priority=0),),
            ),
            tuple(OptimizationFeature(candidate, "score", 10) for candidate in ordered_candidates),
        )
        selected.add(result.selected_candidate)

    assert selected == {"a"}


def test_unavailable_z3_is_explicit_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bjorner-Phan 2014 p.7 motivates a Z3-backed path; unavailable backends must not silently choose."""
    import argumentation.optimization as optimization

    monkeypatch.setattr(optimization, "_import_z3", lambda: None)
    framework = ArgumentationFramework(
        arguments=frozenset({"a"}),
        defeats=frozenset(),
    )

    result = optimize_framework(
        framework,
        OptimizationPolicy(semantics="conflict_free", candidates=frozenset({"a"})),
        (),
    )

    assert result.status == "unavailable"
    assert result.selected_candidate is None
