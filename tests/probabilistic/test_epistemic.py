from __future__ import annotations

import pytest

from argumentation.probabilistic.epistemic import (
    BeliefConstraint,
    EpistemicGraph,
    Influence,
    InfluenceKind,
    belief_assignment_satisfies,
    enumerate_satisfying_assignments,
    project_to_constellation_praf,
    update_assignment,
)


def test_assignment_satisfies_interval_constraints_and_influences() -> None:
    graph = EpistemicGraph(
        arguments=frozenset({"a", "b"}),
        influences=frozenset({Influence("a", "b", InfluenceKind.POSITIVE)}),
        constraints=(
            BeliefConstraint("a", lower=0.6),
            BeliefConstraint("b", lower=0.5),
        ),
    )

    assert belief_assignment_satisfies(graph, {"a": 0.8, "b": 0.8}) is True
    assert belief_assignment_satisfies(graph, {"a": 0.8, "b": 0.4}) is False


def test_enumerates_discrete_satisfying_assignments() -> None:
    graph = EpistemicGraph(
        arguments=frozenset({"a"}),
        constraints=(BeliefConstraint("a", lower=0.5),),
    )

    assert enumerate_satisfying_assignments(graph, levels=(0.0, 0.5, 1.0)) == (
        {"a": 0.5},
        {"a": 1.0},
    )


def test_contradictory_belief_constraints_have_no_satisfying_assignment() -> None:
    """Issue #15: an inconsistent constraint set is satisfied by nothing.

    Hunter and Thimm (2017) define the constrained set P^beta(AF) as those
    functions meeting every constraint (p.20) and treat an empty set as
    inconsistency to be measured (p.23), not as an invalid query.
    """
    contradictory = EpistemicGraph(
        arguments=frozenset({"a"}),
        constraints=(BeliefConstraint("a", 0.0, 0.2), BeliefConstraint("a", 0.8, 1.0)),
    )
    overlapping = EpistemicGraph(
        arguments=frozenset({"a"}),
        constraints=(BeliefConstraint("a", 0.0, 0.6), BeliefConstraint("a", 0.4, 1.0)),
    )

    assert enumerate_satisfying_assignments(contradictory) == ()
    assert belief_assignment_satisfies(contradictory, {"a": 0.1}) is False
    assert belief_assignment_satisfies(contradictory, {"a": 0.9}) is False
    # Control: overlapping intervals are satisfied by their intersection.
    assert enumerate_satisfying_assignments(overlapping) == ({"a": 0.5},)


def test_update_assignment_clamps_evidence_and_propagates_fragment() -> None:
    graph = EpistemicGraph(
        arguments=frozenset({"a", "b", "c"}),
        influences=frozenset(
            {
                Influence("a", "b", InfluenceKind.POSITIVE),
                Influence("a", "c", InfluenceKind.NEGATIVE),
            }
        ),
    )

    # Values are returned exactly as validated (issue #16), so c is the float
    # 1 - 0.8 rather than a rounded 0.2.
    assert update_assignment(graph, {"a": 0.8}) == pytest.approx(
        {"a": 0.8, "b": 0.8, "c": 0.2}
    )


def test_update_assignment_respects_explicit_belief_constraints() -> None:
    """Issue #16: updated beliefs must lie in P^beta(AF) or be refused.

    Hunter and Thimm (2017), p.20: the admissible probability functions are
    those consistent with every stated constraint; an update that leaves that
    set is not a valid result.
    """
    pinned = EpistemicGraph(
        arguments=frozenset({"a"}),
        constraints=(BeliefConstraint("a", 1.0, 1.0),),
    )
    propagated = EpistemicGraph(
        arguments=frozenset({"a", "b"}),
        influences=frozenset({Influence("a", "b", InfluenceKind.NEGATIVE)}),
        constraints=(BeliefConstraint("b", lower=0.5),),
    )

    updated = update_assignment(pinned, {})
    assert updated == {"a": 1.0}
    assert belief_assignment_satisfies(pinned, updated)
    with pytest.raises(ValueError, match="constraints"):
        update_assignment(pinned, {"a": 0.2})
    # Propagation that would push b below its lower bound is reported.
    with pytest.raises(ValueError, match="constraints"):
        update_assignment(propagated, {"a": 0.9})
    # Control: evidence compatible with the constraints propagates as before.
    assert update_assignment(propagated, {"a": 0.3}) == {"a": 0.3, "b": 0.5}


def test_negative_influence_projection_to_constellation_praf() -> None:
    graph = EpistemicGraph(
        arguments=frozenset({"a", "b"}),
        influences=frozenset({Influence("a", "b", InfluenceKind.NEGATIVE)}),
        constraints=(
            BeliefConstraint("a", lower=0.25),
            BeliefConstraint("b", upper=0.75),
        ),
    )

    praf = project_to_constellation_praf(graph)

    assert praf.framework.defeats == frozenset({("a", "b")})
    assert praf.p_args == {"a": 0.25, "b": 0.75}
    assert praf.p_defeats == {("a", "b"): 1.0}
