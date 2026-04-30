from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.epistemic import (
    EpistemicLabel,
    LabelledArc,
    LabelledEpistemicGraph,
    LinearAtomicConstraint,
    LinearRelation,
    coherence_attack_constraint,
    constraints_entail,
    constraints_satisfiable,
    least_squares_update_labelling,
    support_monotonic_constraint,
)


def test_hunter_definition_2_1_labelled_graph_allows_multiple_arc_labels() -> None:
    graph = LabelledEpistemicGraph(
        arguments=frozenset({"a", "b"}),
        arcs=frozenset({
            LabelledArc("a", "b", frozenset({EpistemicLabel.POSITIVE, EpistemicLabel.DEPENDENT})),
        }),
    )

    assert graph.parents("b") == frozenset({"a"})
    assert graph.parents_by_label("b", EpistemicLabel.POSITIVE) == frozenset({"a"})
    assert graph.parents_by_label("b", EpistemicLabel.DEPENDENT) == frozenset({"a"})


def test_hunter_definition_2_1_labelled_graph_rejects_empty_or_unknown_labels() -> None:
    with pytest.raises(ValueError, match="at least one label"):
        LabelledEpistemicGraph(
            arguments=frozenset({"a", "b"}),
            arcs=frozenset({LabelledArc("a", "b", frozenset())}),
        )
    with pytest.raises(ValueError, match="declared arguments"):
        LabelledEpistemicGraph(
            arguments=frozenset({"a"}),
            arcs=frozenset({LabelledArc("a", "b", frozenset({EpistemicLabel.NEGATIVE}))}),
        )


def test_potyka_linear_atomic_constraint_evaluates_probability_labellings() -> None:
    constraint = LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0)

    assert constraint.satisfied_by({"a": 0.4, "b": 0.6})
    assert not constraint.satisfied_by({"a": 0.7, "b": 0.6})


def test_potyka_coherence_attack_constraint_is_upper_bound_by_attacker_belief() -> None:
    constraint = coherence_attack_constraint("a", "b")

    assert constraint.satisfied_by({"a": 0.7, "b": 0.3})
    assert not constraint.satisfied_by({"a": 0.7, "b": 0.4})


def test_support_dual_monotonic_constraint_requires_target_at_least_supporter() -> None:
    constraint = support_monotonic_constraint("a", "b")

    assert constraint.satisfied_by({"a": 0.7, "b": 0.7})
    assert constraint.satisfied_by({"a": 0.3, "b": 0.8})
    assert not constraint.satisfied_by({"a": 0.7, "b": 0.6})


def test_z3_backed_satisfiability_and_entailment_for_linear_fragment() -> None:
    constraints = (
        LinearAtomicConstraint({"a": 1.0}, LinearRelation.GE, 0.6),
        coherence_attack_constraint("a", "b"),
    )

    assert constraints_satisfiable(frozenset({"a", "b"}), constraints)
    assert constraints_entail(
        frozenset({"a", "b"}),
        constraints,
        LinearAtomicConstraint({"b": 1.0}, LinearRelation.LE, 0.4),
    )
    assert not constraints_entail(
        frozenset({"a", "b"}),
        constraints,
        LinearAtomicConstraint({"b": 1.0}, LinearRelation.LE, 0.3),
    )


def test_potyka_update_operator_success_and_failure_for_labellings() -> None:
    updated = least_squares_update_labelling(
        frozenset({"a", "b"}),
        {"a": 0.6, "b": 0.7},
        (LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0),),
    )
    impossible = least_squares_update_labelling(
        frozenset({"a"}),
        {"a": 0.5},
        (
            LinearAtomicConstraint({"a": 1.0}, LinearRelation.GE, 0.8),
            LinearAtomicConstraint({"a": 1.0}, LinearRelation.LE, 0.2),
        ),
    )

    assert updated is not None
    assert updated["a"] == pytest.approx(0.45)
    assert updated["b"] == pytest.approx(0.55)
    assert impossible is None


def test_potyka_update_operator_is_idempotent_when_evidence_already_satisfied() -> None:
    constraints = (LinearAtomicConstraint({"a": 1.0}, LinearRelation.GE, 0.4),)
    current = {"a": 0.5}

    assert least_squares_update_labelling(frozenset({"a"}), current, constraints) == pytest.approx(
        current
    )


@given(
    attacker=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    target=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_potyka_coherence_attack_constraint_matches_paper_inequality(
    attacker: float,
    target: float,
) -> None:
    constraint = coherence_attack_constraint("a", "b")

    assert constraint.satisfied_by({"a": attacker, "b": target}) is (
        target <= 1.0 - attacker + 1e-12
    )
