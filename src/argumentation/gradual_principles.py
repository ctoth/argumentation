"""Baroni-Rago-Toni gradual argumentation principle predicates."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from argumentation.gradual import WeightedBipolarGraph


StrengthFunction = Callable[[WeightedBipolarGraph], dict[str, float]]


class ComplianceLabel(Enum):
    HOLDS = "holds"
    VIOLATES = "violates"
    CONDITIONAL = "conditional"


PRINCIPLE_COMPLIANCE: dict[str, dict[str, ComplianceLabel]] = {
    "dfquad": {
        "balance": ComplianceLabel.HOLDS,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.HOLDS,
    },
    "dfquad_bipolar": {
        "balance": ComplianceLabel.HOLDS,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.HOLDS,
    },
    "potyka_quadratic": {
        "balance": ComplianceLabel.HOLDS,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.CONDITIONAL,
    },
    "matt_toni": {
        "balance": ComplianceLabel.CONDITIONAL,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.CONDITIONAL,
    },
    "gabbay_inverse": {
        "balance": ComplianceLabel.HOLDS,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.CONDITIONAL,
    },
    "gabbay_max": {
        "balance": ComplianceLabel.HOLDS,
        "directionality": ComplianceLabel.HOLDS,
        "monotonicity": ComplianceLabel.CONDITIONAL,
    },
}


def principle_balance(strength_fn: StrengthFunction, graph: WeightedBipolarGraph) -> bool:
    """Check Baroni-Rago-Toni balance on the supplied graph.

    Baroni, Rago, and Toni 2019, IJAR 105, pp. 252-286, Section 4.1
    presents balance as the broad principle subsuming vacuity, weakening,
    strengthening, and their completeness variants.
    """

    strengths = strength_fn(graph)
    for argument in graph.arguments:
        has_attackers = any(target == argument for _source, target in graph.attacks)
        has_supporters = any(target == argument for _source, target in graph.supports)
        base = graph.initial_weights[argument]
        value = strengths[argument]
        if not has_attackers and not has_supporters and abs(value - base) > 1e-8:
            return False
        if has_attackers and not has_supporters and value > base + 1e-8:
            return False
        if has_supporters and not has_attackers and value < base - 1e-8:
            return False
    return True


def principle_directionality(
    strength_fn: StrengthFunction,
    graph: WeightedBipolarGraph,
) -> bool:
    """Check that disconnected isolated arguments keep their base strengths.

    Baroni et al. 2019, IJAR 105, p. 258 records directionality-style
    principles: unrelated structure must not affect an argument's strength.
    """

    strengths = strength_fn(graph)
    incident = {
        argument
        for edge in graph.attacks | graph.supports
        for argument in edge
    }
    return all(
        abs(strengths[argument] - graph.initial_weights[argument]) <= 1e-8
        for argument in graph.arguments - incident
    )


def principle_monotonicity(
    strength_fn: StrengthFunction,
    graph: WeightedBipolarGraph,
) -> bool:
    """Check one-step direct support/attack monotonicity.

    Baroni et al. 2019, IJAR 105, pp. 258-259, GPs 7-11 group the fine
    monotonicity principles; this executable predicate checks their direct
    attack/support instance on the supplied graph.
    """

    strengths = strength_fn(graph)
    attacked_targets = {target for _source, target in graph.attacks}
    supported_targets = {target for _source, target in graph.supports}
    for _source, target in graph.supports:
        if target in attacked_targets:
            continue
        if strengths[target] + 1e-8 < graph.initial_weights[target]:
            return False
    for _source, target in graph.attacks:
        if target in supported_targets:
            continue
        if strengths[target] - 1e-8 > graph.initial_weights[target]:
            return False
    return True
