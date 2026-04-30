from __future__ import annotations

from argumentation.epistemic import (
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
        constraints=(BeliefConstraint("a", lower=0.6), BeliefConstraint("b", lower=0.5),),
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

    assert update_assignment(graph, {"a": 0.8}) == {"a": 0.8, "b": 0.8, "c": 0.2}


def test_negative_influence_projection_to_constellation_praf() -> None:
    graph = EpistemicGraph(
        arguments=frozenset({"a", "b"}),
        influences=frozenset({Influence("a", "b", InfluenceKind.NEGATIVE)}),
        constraints=(BeliefConstraint("a", lower=0.25), BeliefConstraint("b", upper=0.75),),
    )

    praf = project_to_constellation_praf(graph)

    assert praf.framework.defeats == frozenset({("a", "b")})
    assert praf.p_args == {"a": 0.25, "b": 0.75}
    assert praf.p_defeats == {("a", "b"): 1.0}
