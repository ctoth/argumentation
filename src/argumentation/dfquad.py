"""DF-QuAD gradual semantics for weighted bipolar graphs."""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Mapping

from argumentation.gradual import GradualStrengthResult, WeightedBipolarGraph


def dfquad_aggregate(base_score: float, combined_influence: float) -> float:
    """Aggregate base score with net support minus attack influence.

    Rago, Toni, Aurisicchio, and Baroni 2016, KR, p. 65, Defs. 1-3,
    and p. 66, Lemma 3: when attack and support are equal, the result is
    exactly the base score, removing the older QuAD discontinuity.
    """

    _validate_unit_interval(base_score, "base_score")
    if not -1.0 <= combined_influence <= 1.0:
        raise ValueError("combined_influence must be in [-1, 1]")
    if combined_influence >= 0.0:
        return base_score + combined_influence * (1.0 - base_score)
    return base_score + combined_influence * base_score


def dfquad_combine(
    supporter_strengths: list[float],
    attacker_strengths: list[float],
) -> float:
    """Return probabilistic-or support minus probabilistic-or attack.

    Rago et al. 2016, KR, p. 65, Def. 1 and Lemma 1 define the sequence
    aggregation as ``1 - product(1-v_i)``.
    """

    for index, value in enumerate(supporter_strengths):
        _validate_unit_interval(value, f"supporter_strengths[{index}]")
    for index, value in enumerate(attacker_strengths):
        _validate_unit_interval(value, f"attacker_strengths[{index}]")

    support = 1.0 - math.prod(1.0 - value for value in supporter_strengths)
    attack = 1.0 - math.prod(1.0 - value for value in attacker_strengths)
    return support - attack


def dfquad_strengths(
    graph: WeightedBipolarGraph,
    *,
    base_scores: Mapping[str, float] | None = None,
    support_weights: Mapping[tuple[str, str], float] | None = None,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute DF-QuAD strengths on a weighted bipolar graph.

    Rago et al. 2016, KR, p. 66, Def. 3 gives the recursive score function.
    Cycles are handled as the fixed-point equation induced by that same
    score function; the acyclic case is evaluated in topological order.
    """

    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    scores = _normalized_base_scores(graph, base_scores)
    weights = _normalized_support_weights(graph, support_weights)
    attackers = _predecessors(graph.attacks, graph.arguments)
    supporters = _predecessors(graph.supports, graph.arguments)
    order = _topological_order(graph)

    strengths = dict(scores)
    if len(order) == len(graph.arguments):
        for argument in order:
            strengths[argument] = _dfquad_update(
                argument,
                scores,
                strengths,
                attackers,
                supporters,
                weights,
            )
        return GradualStrengthResult(
            strengths=dict(sorted(strengths.items())),
            converged=True,
            iterations=1,
            max_delta=0.0,
            tolerance=tolerance,
            integration_method="dfquad_topological",
        )

    max_delta = 0.0
    for iteration in range(1, max_iterations + 1):
        updated = {}
        for argument in sorted(graph.arguments):
            updated[argument] = _dfquad_update(
                argument,
                scores,
                strengths,
                attackers,
                supporters,
                weights,
            )
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
                integration_method="dfquad_fixed_point",
            )

    return GradualStrengthResult(
        strengths=dict(sorted(strengths.items())),
        converged=False,
        iterations=max_iterations,
        max_delta=max_delta,
        tolerance=tolerance,
        integration_method="dfquad_fixed_point",
    )


def dfquad_bipolar_strengths(
    graph: WeightedBipolarGraph,
    *,
    base_score: float | None = None,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GradualStrengthResult:
    """Compute the bipolar DF-QuAD adaptation.

    Rago, Cyras, and Toni 2016, SAFA, p. 35, Defs. 1-3 set the BAF
    mediating function around 0.5. Passing ``base_score`` applies the same
    neutral point to every argument; otherwise graph initial weights are used.
    """

    base_scores = None
    if base_score is not None:
        _validate_unit_interval(base_score, "base_score")
        base_scores = {argument: base_score for argument in graph.arguments}
    return dfquad_strengths(
        graph,
        base_scores=base_scores,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )


def _dfquad_update(
    argument: str,
    base_scores: Mapping[str, float],
    strengths: Mapping[str, float],
    attackers: Mapping[str, frozenset[str]],
    supporters: Mapping[str, frozenset[str]],
    support_weights: Mapping[tuple[str, str], float],
) -> float:
    attacker_strengths = [strengths[source] for source in attackers[argument]]
    supporter_strengths = [
        min(1.0, max(0.0, strengths[source] * support_weights[(source, argument)]))
        for source in supporters[argument]
    ]
    return dfquad_aggregate(
        base_scores[argument],
        dfquad_combine(supporter_strengths, attacker_strengths),
    )


def _normalized_base_scores(
    graph: WeightedBipolarGraph,
    base_scores: Mapping[str, float] | None,
) -> dict[str, float]:
    scores = dict(graph.initial_weights)
    if base_scores is not None:
        unknown = sorted(set(base_scores) - graph.arguments)
        if unknown:
            raise ValueError(f"base_scores contains unknown arguments: {unknown!r}")
        for argument, value in base_scores.items():
            scores[str(argument)] = float(value)
    for argument, value in scores.items():
        _validate_unit_interval(value, f"base_scores[{argument!r}]")
    return scores


def _normalized_support_weights(
    graph: WeightedBipolarGraph,
    support_weights: Mapping[tuple[str, str], float] | None,
) -> dict[tuple[str, str], float]:
    weights = {edge: 1.0 for edge in graph.supports}
    if support_weights is None:
        return weights
    unknown = sorted(set(support_weights) - graph.supports)
    if unknown:
        raise ValueError(f"support_weights contains unknown supports: {unknown!r}")
    for edge, value in support_weights.items():
        value = float(value)
        _validate_unit_interval(value, f"support_weights[{edge!r}]")
        weights[(str(edge[0]), str(edge[1]))] = value
    return weights


def _topological_order(graph: WeightedBipolarGraph) -> list[str]:
    predecessors: dict[str, set[str]] = {argument: set() for argument in graph.arguments}
    successors: dict[str, set[str]] = {argument: set() for argument in graph.arguments}
    for source, target in graph.attacks | graph.supports:
        predecessors[target].add(source)
        successors[source].add(target)

    queue = deque(sorted(argument for argument, values in predecessors.items() if not values))
    order: list[str] = []
    while queue:
        argument = queue.popleft()
        order.append(argument)
        for successor in sorted(successors[argument]):
            predecessors[successor].remove(argument)
            if not predecessors[successor]:
                queue.append(successor)
    return order


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


def _validate_unit_interval(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value!r}")
