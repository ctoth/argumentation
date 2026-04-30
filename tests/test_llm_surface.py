from __future__ import annotations

from argumentation.llm_surface import (
    build_qbaf_from_proposition_set,
    contest,
    explain_acceptance,
)


def test_build_qbaf_from_externally_supplied_propositions() -> None:
    graph = build_qbaf_from_proposition_set(
        propositions={"claim": 0.6, "evidence": 0.8},
        edges={("evidence", "claim"): "support"},
    )

    assert graph.arguments == frozenset({"claim", "evidence"})
    assert graph.supports == frozenset({("evidence", "claim")})
    assert graph.initial_weights["claim"] == 0.6


def test_explain_acceptance_returns_shapley_attack_witnesses() -> None:
    graph = build_qbaf_from_proposition_set(
        propositions={"claim": 0.8, "rebuttal": 0.7},
        edges={("rebuttal", "claim"): "attack"},
    )

    result = explain_acceptance(graph, "claim")

    assert result.target == "claim"
    assert result.strength <= 0.8
    assert result.attack_impacts


def test_contest_adds_evidence_and_reports_acceptance_delta() -> None:
    graph = build_qbaf_from_proposition_set(
        propositions={"claim": 0.8},
        edges={},
    )

    result = contest(
        graph,
        claim="claim",
        evidence={"counter": 0.9},
        edges={("counter", "claim"): "attack"},
        acceptance_threshold=0.5,
    )

    assert result.claim == "claim"
    assert result.accepted_before is True
    assert result.accepted_after is False
    assert result.added_arguments == frozenset({"counter"})
