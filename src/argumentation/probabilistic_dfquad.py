"""DF-QuAD gradual semantics for Quantitative Bipolar Argumentation Frameworks.

Implements the aggregation function from Freedman et al. (2025, p.3).
Computes continuous argument strengths in [0,1] by propagating base scores
through attack and support relations.

Per Freedman et al. (2025): QBAFs extend Dung AFs with graded base
strengths τ(a) ∈ [0,1] and explicit support relations R⁺, alongside
attack relations R⁻.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argumentation.probabilistic import ProbabilisticAF


def dfquad_aggregate(base_score: float, combined_influence: float) -> float:
    """DF-QuAD aggregation function.

    Per Freedman et al. (2025, p.3):
    - If combined_influence >= 0: base + influence * (1 - base)
    - If combined_influence < 0:  base + influence * base

    This ensures:
    - Positive influence pushes strength toward 1, proportional to headroom.
    - Negative influence pushes strength toward 0, proportional to current value.
    - Output is always in [0,1] when base in [0,1] and influence in [-1,1].
    """
    if combined_influence >= 0:
        return base_score + combined_influence * (1.0 - base_score)
    else:
        return base_score + combined_influence * base_score


def dfquad_combine(
    supporter_strengths: list[float],
    attacker_strengths: list[float],
) -> float:
    """Combine supporter and attacker influences.

    Per Freedman et al. (2025, p.3):
    support = 1 - product(1 - s for s in supporters)  [0 if empty]
    attack = 1 - product(1 - a for a in attackers)     [0 if empty]
    combined = support - attack

    The support/attack aggregation uses the probabilistic "noisy-OR":
    each additional supporter/attacker has diminishing marginal effect.
    """
    if supporter_strengths:
        product_sup = math.prod(1.0 - s for s in supporter_strengths)
        support = 1.0 - product_sup
    else:
        support = 0.0

    if attacker_strengths:
        product_att = math.prod(1.0 - a for a in attacker_strengths)
        attack = 1.0 - product_att
    else:
        attack = 0.0

    return support - attack


def _validated_base_scores(
    praf: ProbabilisticAF,
    *,
    base_scores: dict[str, float],
    score_name: str,
) -> dict[str, float]:
    normalized: dict[str, float] = {}
    missing = sorted(arg for arg in praf.framework.arguments if arg not in base_scores)
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"missing {score_name} for arguments: {missing_text}")
    for arg in praf.framework.arguments:
        value = float(base_scores[arg])
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{score_name}[{arg!r}] must be in [0,1], got {value}")
        normalized[arg] = value
    return normalized


def compute_dfquad_strengths(
    praf: ProbabilisticAF,
    supports: dict[tuple[str, str], float],
    *,
    base_scores: dict[str, float],
) -> dict[str, float]:
    """Compute DF-QuAD strengths for all arguments from explicit base scores.

    Attack structure comes from `praf.framework.defeats`.
    Support structure comes from the `supports` dict.
    Base scores are supplied explicitly so QuAD-mode τ is never conflated
    with PrAF argument-existence probabilities.

    Evaluation order: topological sort of the combined attack+support graph.
    If cycles exist, use iterative fixpoint (max 100 iterations,
    per Freedman 2025 assumption of acyclic QBAFs).

    Per Freedman et al. (2025, p.3): σ(a) = f_agg(τ(a), f_comb(v_a⁺, v_a⁻))
    """
    args = praf.framework.arguments
    defeats = praf.framework.defeats

    normalized_base_scores = _validated_base_scores(
        praf,
        base_scores=base_scores,
        score_name="base_scores",
    )

    # Build adjacency: who attacks/supports whom
    attackers_of: dict[str, list[str]] = {a: [] for a in args}
    for src, tgt in defeats:
        if src in args and tgt in args:
            attackers_of[tgt].append(src)

    supporters_of: dict[str, list[str]] = {a: [] for a in args}
    for (src, tgt), _weight in supports.items():
        if src in args and tgt in args:
            supporters_of[tgt].append(src)

    # Build predecessor graph for topological sort
    # An argument depends on its attackers and supporters
    predecessors: dict[str, set[str]] = {a: set() for a in args}
    for tgt, atk_list in attackers_of.items():
        for src in atk_list:
            predecessors[tgt].add(src)
    for tgt, sup_list in supporters_of.items():
        for src in sup_list:
            predecessors[tgt].add(src)

    # Topological sort (Kahn's algorithm)
    in_degree: dict[str, int] = {a: len(predecessors[a]) for a in args}
    queue: list[str] = [a for a in args if in_degree[a] == 0]
    topo_order: list[str] = []
    visited: set[str] = set()

    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        topo_order.append(node)
        # Decrease in-degree of successors
        for a in args:
            if node in predecessors[a]:
                in_degree[a] -= 1
                if in_degree[a] == 0 and a not in visited:
                    queue.append(a)

    # Handle cycles: any unvisited args get iterative fixpoint
    remaining = [a for a in args if a not in visited]

    # Initialize strengths with base scores
    strengths: dict[str, float] = dict(normalized_base_scores)

    # Evaluate in topological order (acyclic portion)
    for arg in topo_order:
        attacker_strs = [strengths[a] for a in attackers_of[arg]]
        supporter_strs = [
            min(1.0, max(0.0, strengths[a] * supports[(a, arg)]))
            for a in supporters_of[arg]
        ]
        combined = dfquad_combine(supporter_strs, attacker_strs)
        strengths[arg] = dfquad_aggregate(normalized_base_scores[arg], combined)

    # Iterative fixpoint for cyclic arguments (if any)
    # Per Freedman et al. (2025): acyclic QBAFs assumed, but we handle
    # cycles gracefully with iterative convergence.
    if remaining:
        for _iteration in range(100):
            max_delta = 0.0
            for arg in remaining:
                attacker_strs = [strengths[a] for a in attackers_of[arg]]
                supporter_strs = [
                    min(1.0, max(0.0, strengths[a] * supports[(a, arg)]))
                    for a in supporters_of[arg]
                ]
                combined = dfquad_combine(supporter_strs, attacker_strs)
                new_strength = dfquad_aggregate(normalized_base_scores[arg], combined)
                max_delta = max(max_delta, abs(new_strength - strengths[arg]))
                strengths[arg] = new_strength
            if max_delta < 1e-9:
                break

    return strengths


def compute_dfquad_quad_strengths(
    praf: ProbabilisticAF,
    supports: dict[tuple[str, str], float],
    *,
    tau: dict[str, float],
) -> dict[str, float]:
    """Compute QuAD/DF-QuAD strengths from explicit intrinsic scores τ."""
    normalized_tau = _validated_base_scores(
        praf,
        base_scores=tau,
        score_name="tau",
    )
    return compute_dfquad_strengths(
        praf,
        supports,
        base_scores=normalized_tau,
    )


def compute_dfquad_baf_strengths(
    praf: ProbabilisticAF,
    supports: dict[tuple[str, str], float],
) -> dict[str, float]:
    """Compute the BAF adaptation with neutral base score 0.5 everywhere."""
    neutral_scores = {arg: 0.5 for arg in praf.framework.arguments}
    return compute_dfquad_strengths(
        praf,
        supports,
        base_scores=neutral_scores,
    )
