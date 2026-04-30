"""Epistemic graphs over argument belief levels.

The surface is deliberately finite: belief assignments are mappings from
argument IDs to floats in ``[0, 1]``; constraints are interval bounds; and
positive/negative influences are checked directly over those assignments.

References:
    Hunter, Polberg, and Thimm (2018-2020). Epistemic graphs for representing
    and reasoning with positive and negative influences of arguments.
    Potyka, Polberg, and Hunter (2019). Polynomial-time updates of epistemic
    states in a fragment of probabilistic epistemic argumentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from typing import Mapping

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF


class InfluenceKind(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class Influence:
    source: str
    target: str
    kind: InfluenceKind


@dataclass(frozen=True)
class BeliefConstraint:
    argument: str
    lower: float = 0.0
    upper: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.lower <= self.upper <= 1.0:
            raise ValueError("belief constraint bounds must satisfy 0 <= lower <= upper <= 1")


@dataclass(frozen=True)
class EpistemicGraph:
    arguments: frozenset[str]
    influences: frozenset[Influence] = frozenset()
    constraints: tuple[BeliefConstraint, ...] = ()

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        unknown_influences = sorted(
            (influence.source, influence.target)
            for influence in self.influences
            if influence.source not in arguments or influence.target not in arguments
        )
        if unknown_influences:
            raise ValueError(f"influences must reference declared arguments: {unknown_influences!r}")
        unknown_constraints = sorted(
            constraint.argument
            for constraint in self.constraints
            if constraint.argument not in arguments
        )
        if unknown_constraints:
            raise ValueError(f"constraints must reference declared arguments: {unknown_constraints!r}")
        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "influences", frozenset(self.influences))
        object.__setattr__(self, "constraints", tuple(self.constraints))


def _constraint_by_argument(graph: EpistemicGraph) -> dict[str, BeliefConstraint]:
    constraints: dict[str, BeliefConstraint] = {}
    for constraint in graph.constraints:
        existing = constraints.get(constraint.argument)
        if existing is None:
            constraints[constraint.argument] = constraint
        else:
            constraints[constraint.argument] = BeliefConstraint(
                constraint.argument,
                lower=max(existing.lower, constraint.lower),
                upper=min(existing.upper, constraint.upper),
            )
    return constraints


def _validate_assignment(
    graph: EpistemicGraph,
    assignment: Mapping[str, float],
) -> dict[str, float]:
    missing = sorted(graph.arguments - set(assignment))
    extra = sorted(set(assignment) - graph.arguments)
    if missing or extra:
        raise ValueError(f"assignment keys must match graph arguments: missing={missing!r}, extra={extra!r}")
    normalized = {argument: float(value) for argument, value in assignment.items()}
    out_of_range = sorted(
        argument
        for argument, value in normalized.items()
        if not 0.0 <= value <= 1.0
    )
    if out_of_range:
        raise ValueError(f"assignment values must be in [0, 1]: {out_of_range!r}")
    return normalized


def belief_assignment_satisfies(
    graph: EpistemicGraph,
    assignment: Mapping[str, float],
) -> bool:
    """Return whether ``assignment`` satisfies graph constraints."""
    values = _validate_assignment(graph, assignment)
    constraints = _constraint_by_argument(graph)
    for argument, constraint in constraints.items():
        value = values[argument]
        if value < constraint.lower or value > constraint.upper:
            return False

    for influence in graph.influences:
        source = values[influence.source]
        target = values[influence.target]
        if influence.kind == InfluenceKind.POSITIVE and target < source:
            return False
        if influence.kind == InfluenceKind.NEGATIVE and target > 1.0 - source:
            return False
    return True


def enumerate_satisfying_assignments(
    graph: EpistemicGraph,
    *,
    levels: tuple[float, ...] = (0.0, 0.5, 1.0),
) -> tuple[dict[str, float], ...]:
    """Enumerate satisfying assignments over a finite belief grid."""
    if not levels:
        raise ValueError("levels must not be empty")
    if any(level < 0.0 or level > 1.0 for level in levels):
        raise ValueError("levels must lie in [0, 1]")
    ordered = sorted(graph.arguments)
    satisfying: list[dict[str, float]] = []
    for values in product(levels, repeat=len(ordered)):
        assignment = dict(zip(ordered, values, strict=True))
        if belief_assignment_satisfies(graph, assignment):
            satisfying.append(assignment)
    return tuple(satisfying)


def update_assignment(
    graph: EpistemicGraph,
    evidence: Mapping[str, float],
) -> dict[str, float]:
    """Update a belief assignment in the monotone influence fragment."""
    unknown = sorted(set(evidence) - graph.arguments)
    if unknown:
        raise ValueError(f"evidence references unknown arguments: {unknown!r}")
    assignment = {argument: 0.5 for argument in graph.arguments}
    for argument, value in evidence.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError("evidence values must lie in [0, 1]")
        assignment[argument] = float(value)

    changed = True
    while changed:
        changed = False
        for influence in sorted(
            graph.influences,
            key=lambda item: (item.source, item.target, item.kind.value),
        ):
            source = assignment[influence.source]
            target = assignment[influence.target]
            if influence.kind == InfluenceKind.POSITIVE and target < source:
                assignment[influence.target] = source
                changed = True
            elif influence.kind == InfluenceKind.NEGATIVE and target > 1.0 - source:
                assignment[influence.target] = 1.0 - source
                changed = True
    return {
        argument: round(assignment[argument], 12)
        for argument in sorted(graph.arguments)
    }


def project_to_constellation_praf(graph: EpistemicGraph) -> ProbabilisticAF:
    """Project influences to a constellation PrAF where the mapping is defined."""
    constraints = _constraint_by_argument(graph)
    p_args = {
        argument: constraints[argument].lower
        if argument in constraints and constraints[argument].lower > 0.0
        else constraints[argument].upper
        if argument in constraints
        else 1.0
        for argument in graph.arguments
    }
    defeats = frozenset(
        (influence.source, influence.target)
        for influence in graph.influences
        if influence.kind == InfluenceKind.NEGATIVE
    )
    supports = frozenset(
        (influence.source, influence.target)
        for influence in graph.influences
        if influence.kind == InfluenceKind.POSITIVE
    )
    return ProbabilisticAF(
        framework=ArgumentationFramework(arguments=graph.arguments, defeats=defeats),
        p_args=p_args,
        p_defeats={defeat: 1.0 for defeat in defeats},
        supports=supports,
        p_supports={support: 1.0 for support in supports},
    )
