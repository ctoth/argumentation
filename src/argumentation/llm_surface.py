"""Thin formal-reasoning surface for argumentative LLM pipelines.

The LLM-facing boundary is intentionally narrow: callers supply propositions,
weights, and attack/support edges.  This module builds package-native weighted
bipolar graphs, computes gradual strengths, and returns typed explanation or
contestation witnesses without taking any LLM dependency.

Reference:
    Freedman, Dejl, Gorur, Yin, Rago, and Toni (2025). Argumentative large
    language models for explainable and contestable claim verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from argumentation.gradual import (
    ShapleyAttackImpactResult,
    WeightedBipolarGraph,
    quadratic_energy_strengths,
    shapley_attack_impacts,
)


EdgeKind = Literal["attack", "support"]


@dataclass(frozen=True)
class AcceptanceExplanation:
    target: str
    strength: float
    strengths: dict[str, float]
    attack_impacts: ShapleyAttackImpactResult


@dataclass(frozen=True)
class ContestationResult:
    claim: str
    before_strength: float
    after_strength: float
    accepted_before: bool
    accepted_after: bool
    added_arguments: frozenset[str]
    witness_graph: WeightedBipolarGraph


def build_qbaf_from_proposition_set(
    *,
    propositions: Mapping[str, float],
    edges: Mapping[tuple[str, str], EdgeKind],
) -> WeightedBipolarGraph:
    """Build a weighted bipolar graph from externally supplied propositions."""
    arguments = frozenset(str(argument) for argument in propositions)
    attacks = frozenset(
        (str(source), str(target))
        for (source, target), kind in edges.items()
        if kind == "attack"
    )
    supports = frozenset(
        (str(source), str(target))
        for (source, target), kind in edges.items()
        if kind == "support"
    )
    unknown_kinds = sorted({kind for kind in edges.values() if kind not in {"attack", "support"}})
    if unknown_kinds:
        raise ValueError(f"unsupported edge kinds: {unknown_kinds!r}")
    return WeightedBipolarGraph(
        arguments=arguments,
        initial_weights={str(argument): float(weight) for argument, weight in propositions.items()},
        attacks=attacks,
        supports=supports,
    )


def explain_acceptance(
    graph: WeightedBipolarGraph,
    target: str,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> AcceptanceExplanation:
    """Explain target acceptance with strengths and Shapley attack impacts."""
    strengths = quadratic_energy_strengths(
        graph,
        tolerance=tolerance,
        max_iterations=max_iterations,
    ).strengths
    return AcceptanceExplanation(
        target=target,
        strength=strengths[target],
        strengths=strengths,
        attack_impacts=shapley_attack_impacts(
            graph,
            target=target,
            tolerance=tolerance,
            max_iterations=max_iterations,
        ),
    )


def contest(
    graph: WeightedBipolarGraph,
    *,
    claim: str,
    evidence: Mapping[str, float],
    edges: Mapping[tuple[str, str], EdgeKind],
    acceptance_threshold: float = 0.5,
) -> ContestationResult:
    """Add contesting evidence and report the resulting claim-strength change."""
    if claim not in graph.arguments:
        raise ValueError(f"unknown claim: {claim}")
    added_arguments = frozenset(str(argument) for argument in evidence)
    overlap = added_arguments & graph.arguments
    if overlap:
        raise ValueError(f"evidence arguments already exist: {sorted(overlap)!r}")

    before = quadratic_energy_strengths(graph).strengths[claim]
    augmented_weights = dict(graph.initial_weights)
    augmented_weights.update({str(argument): float(weight) for argument, weight in evidence.items()})
    attacks = set(graph.attacks)
    supports = set(graph.supports)
    for (source, target), kind in edges.items():
        edge = (str(source), str(target))
        if kind == "attack":
            attacks.add(edge)
        elif kind == "support":
            supports.add(edge)
        else:
            raise ValueError(f"unsupported edge kind: {kind!r}")

    witness = WeightedBipolarGraph(
        arguments=graph.arguments | added_arguments,
        initial_weights=augmented_weights,
        attacks=frozenset(attacks),
        supports=frozenset(supports),
    )
    after = quadratic_energy_strengths(witness).strengths[claim]
    return ContestationResult(
        claim=claim,
        before_strength=before,
        after_strength=after,
        accepted_before=before >= acceptance_threshold,
        accepted_after=after >= acceptance_threshold,
        added_arguments=added_arguments,
        witness_graph=witness,
    )
