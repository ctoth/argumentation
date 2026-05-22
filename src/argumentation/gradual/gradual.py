"""Gradual semantics for weighted bipolar argumentation graphs."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import factorial
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
    integration_method: str


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


@dataclass(frozen=True)
class ShapleyAttackImpactResult:
    """Exact Shapley impact attribution for direct attacks into a target."""

    target: str
    attack_impacts: dict[tuple[str, str], float]
    exact: bool
    coalition_count: int


def quadratic_energy_strengths(
    graph: WeightedBipolarGraph,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute Potyka quadratic-energy strengths with the continuous model.

    Potyka 2018, KR, p. 150, Definition 2 gives the differential equation
    ``ds_j/dt = w(j) - s_j + (1-w(j))h(E_j) - w(j)h(-E_j)``. This public
    entry point uses that continuous system by default.
    """
    return quadratic_energy_strengths_continuous(
        graph,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )


def quadratic_energy_strengths_discrete(
    graph: WeightedBipolarGraph,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute fixed-point strengths for Potyka's quadratic energy model.

    This is the explicit Euler-style fixed-point iteration for Potyka 2018,
    KR, p. 150, Definition 2. Use it only when the discretisation itself is
    the subject; ``quadratic_energy_strengths`` is the continuous default.
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
                integration_method="fixed_point_discrete",
            )

    return GradualStrengthResult(
        strengths=dict(sorted(strengths.items())),
        converged=False,
        iterations=max_iterations,
        max_delta=max_delta,
        tolerance=tolerance,
        integration_method="fixed_point_discrete",
    )


def quadratic_energy_strengths_continuous(
    graph: WeightedBipolarGraph,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
    initial_step: float = 0.25,
) -> GradualStrengthResult:
    """Integrate Potyka's continuous quadratic-energy ODE.

    Potyka 2018, KR, p. 150, Definition 2 defines the quadratic energy
    model as a system of differential equations and notes RK4 as the basic
    numerical integration method. This implementation uses adaptive step
    halving/doubling around RK4 and reports the largest residual derivative.
    """
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if initial_step <= 0.0:
        raise ValueError("initial_step must be positive")

    arguments = tuple(sorted(graph.arguments))
    strengths = {
        argument: graph.initial_weights[argument]
        for argument in arguments
    }
    step = initial_step
    max_delta = 0.0
    for iteration in range(1, max_iterations + 1):
        derivative = _quadratic_derivative(graph, strengths)
        max_delta = max((abs(value) for value in derivative.values()), default=0.0)
        if max_delta <= tolerance:
            return GradualStrengthResult(
                strengths=dict(sorted(strengths.items())),
                converged=True,
                iterations=iteration - 1,
                max_delta=max_delta,
                tolerance=tolerance,
                integration_method="rk4_adaptive",
            )

        while True:
            full = _rk4_step(graph, strengths, step)
            half = _rk4_step(graph, _rk4_step(graph, strengths, step / 2.0), step / 2.0)
            error = max(
                abs(full[argument] - half[argument])
                for argument in arguments
            )
            scale = tolerance + tolerance * max(abs(half[argument]) for argument in arguments)
            if error <= scale or step <= 1e-6:
                strengths = {
                    argument: min(1.0, max(0.0, half[argument]))
                    for argument in arguments
                }
                if error < scale / 16.0:
                    step = min(step * 2.0, 1.0)
                break
            step /= 2.0

    return GradualStrengthResult(
        strengths=dict(sorted(strengths.items())),
        converged=False,
        iterations=max_iterations,
        max_delta=max_delta,
        tolerance=tolerance,
        integration_method="rk4_adaptive",
    )


def quadratic_impact(value: float) -> float:
    positive = max(value, 0.0)
    return (positive * positive) / (1.0 + positive * positive)


def _quadratic_derivative(
    graph: WeightedBipolarGraph,
    strengths: Mapping[str, float],
) -> dict[str, float]:
    supporters = _predecessors(graph.supports, graph.arguments)
    attackers = _predecessors(graph.attacks, graph.arguments)
    derivative: dict[str, float] = {}
    for argument in graph.arguments:
        energy = sum(strengths[source] for source in supporters[argument])
        energy -= sum(strengths[source] for source in attackers[argument])
        target = _equilibrium_strength(graph.initial_weights[argument], energy)
        derivative[argument] = target - strengths[argument]
    return derivative


def _rk4_step(
    graph: WeightedBipolarGraph,
    strengths: Mapping[str, float],
    step: float,
) -> dict[str, float]:
    arguments = tuple(sorted(graph.arguments))
    k1 = _quadratic_derivative(graph, strengths)
    k2_input = {
        argument: strengths[argument] + step * k1[argument] / 2.0
        for argument in arguments
    }
    k2 = _quadratic_derivative(graph, k2_input)
    k3_input = {
        argument: strengths[argument] + step * k2[argument] / 2.0
        for argument in arguments
    }
    k3 = _quadratic_derivative(graph, k3_input)
    k4_input = {
        argument: strengths[argument] + step * k3[argument]
        for argument in arguments
    }
    k4 = _quadratic_derivative(graph, k4_input)
    return {
        argument: strengths[argument]
        + step
        * (
            k1[argument]
            + 2.0 * k2[argument]
            + 2.0 * k3[argument]
            + k4[argument]
        )
        / 6.0
        for argument in arguments
    }


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
    impact = attack_removed_strength - argument_removed_strength
    if abs(impact) <= tolerance:
        impact = 0.0
    return RevisedImpactResult(
        influencers=normalized_influencers,
        target=target,
        removed_attacks=removed_attacks,
        removed_arguments=removed_arguments,
        original_strength=original.strengths[target],
        after_attack_removal_strength=attack_removed_strength,
        after_argument_removal_strength=argument_removed_strength,
        impact=impact,
    )


def shapley_attack_impacts(
    graph: WeightedBipolarGraph,
    *,
    target: str,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> ShapleyAttackImpactResult:
    """Compute exact Shapley impact for attacks directly targeting ``target``.

    Al Anaissy et al. 2024, Definition 13: for an attack `(b, a)`, enumerate
    all coalitions of the other direct attacks toward `a` and average the
    marginal target-strength gain from additionally removing `(b, a)`.
    """
    target = str(target)
    if target not in graph.arguments:
        raise ValueError(f"unknown target argument: {target!r}")

    target_attacks = tuple(sorted(
        attack for attack in graph.attacks if attack[1] == target
    ))
    n_attacks = len(target_attacks)
    impacts: dict[tuple[str, str], float] = {}
    for attack in target_attacks:
        others = tuple(other for other in target_attacks if other != attack)
        impact = 0.0
        for size in range(len(others) + 1):
            coefficient = (
                factorial(size)
                * factorial(n_attacks - size - 1)
                / factorial(n_attacks)
            )
            for coalition in combinations(others, size):
                removed = frozenset(coalition)
                before = quadratic_energy_strengths(
                    _without_attacks(graph, removed),
                    tolerance=tolerance,
                    max_iterations=max_iterations,
                ).strengths[target]
                after = quadratic_energy_strengths(
                    _without_attacks(graph, removed | frozenset({attack})),
                    tolerance=tolerance,
                    max_iterations=max_iterations,
                ).strengths[target]
                impact += coefficient * (after - before)
        impacts[attack] = impact

    return ShapleyAttackImpactResult(
        target=target,
        attack_impacts=dict(sorted(impacts.items())),
        exact=True,
        coalition_count=2 ** n_attacks,
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
