"""Gradual semantics for weighted bipolar argumentation graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class WeightedBipolarGraph:
    """A weighted bipolar argumentation graph.

    Potyka 2018, Definition 1: a BAG has finite arguments, an initial weight
    function into ``[0, 1]``, and disjoint binary attack/support relations.
    """

    arguments: frozenset[str]
    initial_weights: Mapping[str, float]
    attacks: frozenset[tuple[str, str]] = frozenset()
    supports: frozenset[tuple[str, str]] = frozenset()

    def __post_init__(self) -> None:
        arguments = frozenset(str(argument) for argument in self.arguments)
        weights = {
            str(argument): float(weight)
            for argument, weight in self.initial_weights.items()
        }
        if set(weights) != set(arguments):
            raise ValueError("initial_weights must cover exactly the arguments")
        out_of_range = sorted(
            argument for argument, weight in weights.items()
            if not 0.0 <= weight <= 1.0
        )
        if out_of_range:
            raise ValueError(f"initial weights must be in [0, 1]: {out_of_range!r}")

        attacks = _normalize_relation("attacks", self.attacks, arguments)
        supports = _normalize_relation("supports", self.supports, arguments)
        overlap = attacks & supports
        if overlap:
            raise ValueError(f"attacks and supports must not overlap: {sorted(overlap)!r}")

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "initial_weights", weights)
        object.__setattr__(self, "attacks", attacks)
        object.__setattr__(self, "supports", supports)


@dataclass(frozen=True)
class GradualStrengthResult:
    """Strengths plus fixed-point convergence metadata."""

    strengths: dict[str, float]
    converged: bool
    iterations: int
    max_delta: float
    tolerance: float


@dataclass(frozen=True)
class RevisedImpactResult:
    """Revised direct-impact attribution for one target argument."""

    influencers: frozenset[str]
    target: str
    removed_attacks: frozenset[tuple[str, str]]
    removed_arguments: frozenset[str]
    original_strength: float
    after_attack_removal_strength: float
    after_argument_removal_strength: float
    impact: float


def quadratic_energy_strengths(
    graph: WeightedBipolarGraph,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute fixed-point strengths for Potyka's quadratic energy model.

    Definition 2 gives energy as supporter strength minus attacker strength and
    uses ``h(x)=max(x,0)^2 / (1 + max(x,0)^2)``. At equilibrium, each argument
    has strength ``w + (1-w)h(E) - w h(-E)``.
    """
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    supporters = _predecessors(graph.supports, graph.arguments)
    attackers = _predecessors(graph.attacks, graph.arguments)
    strengths = {
        argument: graph.initial_weights[argument]
        for argument in graph.arguments
    }

    for iteration in range(1, max_iterations + 1):
        updated: dict[str, float] = {}
        for argument in graph.arguments:
            energy = sum(strengths[source] for source in supporters[argument])
            energy -= sum(strengths[source] for source in attackers[argument])
            updated[argument] = _equilibrium_strength(
                graph.initial_weights[argument],
                energy,
            )
        max_delta = max(
            (abs(updated[argument] - strengths[argument]) for argument in graph.arguments),
            default=0.0,
        )
        strengths = updated
        if max_delta <= tolerance:
            return GradualStrengthResult(
                strengths=dict(sorted(strengths.items())),
                converged=True,
                iterations=iteration,
                max_delta=max_delta,
                tolerance=tolerance,
            )

    return GradualStrengthResult(
        strengths=dict(sorted(strengths.items())),
        converged=False,
        iterations=max_iterations,
        max_delta=max_delta,
        tolerance=tolerance,
    )


def quadratic_impact(value: float) -> float:
    positive = max(value, 0.0)
    return (positive * positive) / (1.0 + positive * positive)


def revised_direct_impact(
    graph: WeightedBipolarGraph,
    *,
    influencers: frozenset[str],
    target: str,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> RevisedImpactResult:
    """Compute the revised removal-based impact of ``influencers`` on ``target``.

    Al Anaissy et al. 2024, Definition 12: remove direct attacks from the
    influencer set to the target, and compare against target-preserving argument
    deletion. The latter keeps ``target`` when it is also in ``influencers``,
    which makes self-attack attribution defined.
    """
    normalized_influencers = frozenset(str(argument) for argument in influencers)
    target = str(target)
    unknown = sorted((normalized_influencers | {target}) - graph.arguments)
    if unknown:
        raise ValueError(f"unknown arguments: {unknown!r}")

    original = quadratic_energy_strengths(
        graph,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )
    removed_attacks = frozenset(
        (source, attacked)
        for source, attacked in graph.attacks
        if source in normalized_influencers and attacked == target
    )
    attack_removed = _without_attacks(graph, removed_attacks)
    after_attack_removal = quadratic_energy_strengths(
        attack_removed,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    removed_arguments = normalized_influencers - {target}
    argument_removed = _without_arguments(graph, removed_arguments)
    after_argument_removal = quadratic_energy_strengths(
        argument_removed,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    attack_removed_strength = after_attack_removal.strengths[target]
    argument_removed_strength = after_argument_removal.strengths[target]
    return RevisedImpactResult(
        influencers=normalized_influencers,
        target=target,
        removed_attacks=removed_attacks,
        removed_arguments=removed_arguments,
        original_strength=original.strengths[target],
        after_attack_removal_strength=attack_removed_strength,
        after_argument_removal_strength=argument_removed_strength,
        impact=attack_removed_strength - argument_removed_strength,
    )


def _equilibrium_strength(initial_weight: float, energy: float) -> float:
    if energy >= 0.0:
        return initial_weight + (1.0 - initial_weight) * quadratic_impact(energy)
    return initial_weight - initial_weight * quadratic_impact(-energy)


def _normalize_relation(
    name: str,
    relation: frozenset[tuple[str, str]],
    arguments: frozenset[str],
) -> frozenset[tuple[str, str]]:
    normalized = frozenset((str(source), str(target)) for source, target in relation)
    unknown = sorted(
        (source, target)
        for source, target in normalized
        if source not in arguments or target not in arguments
    )
    if unknown:
        raise ValueError(f"{name} must only reference declared arguments: {unknown!r}")
    return normalized


def _predecessors(
    relation: frozenset[tuple[str, str]],
    arguments: frozenset[str],
) -> dict[str, frozenset[str]]:
    predecessors: dict[str, set[str]] = {argument: set() for argument in arguments}
    for source, target in relation:
        predecessors[target].add(source)
    return {
        argument: frozenset(values)
        for argument, values in predecessors.items()
    }


def _without_attacks(
    graph: WeightedBipolarGraph,
    removed_attacks: frozenset[tuple[str, str]],
) -> WeightedBipolarGraph:
    return WeightedBipolarGraph(
        arguments=graph.arguments,
        initial_weights=graph.initial_weights,
        attacks=graph.attacks - removed_attacks,
        supports=graph.supports,
    )


def _without_arguments(
    graph: WeightedBipolarGraph,
    removed_arguments: frozenset[str],
) -> WeightedBipolarGraph:
    remaining = graph.arguments - removed_arguments
    return WeightedBipolarGraph(
        arguments=remaining,
        initial_weights={
            argument: graph.initial_weights[argument]
            for argument in remaining
        },
        attacks=frozenset(
            (source, target)
            for source, target in graph.attacks
            if source in remaining and target in remaining
        ),
        supports=frozenset(
            (source, target)
            for source, target in graph.supports
            if source in remaining and target in remaining
        ),
    )
