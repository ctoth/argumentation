"""Gabbay equational argumentation-network semantics."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from argumentation.gradual import GradualStrengthResult, WeightedBipolarGraph


EquationScheme = Literal["inverse", "max", "min"]


def equational_fixpoint(
    graph: WeightedBipolarGraph,
    *,
    scheme: EquationScheme = "inverse",
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute a Gabbay-style equational fixed point.

    Gabbay 2012, Argument & Computation, pp. 104-108 defines equation
    families over attacker values; Eq-inverse multiplies ``1-attacker`` terms
    and Eq-max uses ``1-max(attacker)``. ``scheme="min"`` is accepted as the
    workstream spelling for Eq-inverse.
    """

    if scheme not in {"inverse", "max", "min"}:
        raise ValueError("scheme must be 'inverse', 'min', or 'max'")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    attackers = _predecessors(graph.attacks, graph.arguments)
    supporters = _predecessors(graph.supports, graph.arguments)
    strengths = {
        argument: graph.initial_weights[argument]
        for argument in graph.arguments
    }
    max_delta = 0.0
    for iteration in range(1, max_iterations + 1):
        updated: dict[str, float] = {}
        for argument in sorted(graph.arguments):
            attack_value = _attack_value(
                [strengths[source] for source in attackers[argument]],
                scheme=scheme,
            )
            support_value = 1.0
            if supporters[argument]:
                support_value = 1.0 - _product(
                    1.0 - strengths[source]
                    for source in supporters[argument]
                )
            base = graph.initial_weights[argument]
            updated[argument] = min(1.0, max(0.0, base * attack_value + (1.0 - base) * support_value))
        max_delta = max(
            abs(updated[argument] - strengths[argument])
            for argument in graph.arguments
        )
        strengths = updated
        if max_delta <= tolerance:
            return GradualStrengthResult(
                strengths=dict(sorted(strengths.items())),
                converged=True,
                iterations=iteration,
                max_delta=max_delta,
                tolerance=tolerance,
                integration_method=f"gabbay_eq_{scheme}",
            )

    return GradualStrengthResult(
        strengths=dict(sorted(strengths.items())),
        converged=False,
        iterations=max_iterations,
        max_delta=max_delta,
        tolerance=tolerance,
        integration_method=f"gabbay_eq_{scheme}",
    )


def _attack_value(values: list[float], *, scheme: EquationScheme) -> float:
    if not values:
        return 1.0
    if scheme == "max":
        return 1.0 - max(values)
    return _product(1.0 - value for value in values)


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


def _product(values: Iterable[float]) -> float:
    product = 1.0
    for value in values:
        product *= value
    return product
