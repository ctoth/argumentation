"""Sensitivity and importance analysis of argumentation-framework outputs.

These functions measure how much a framework's accepted set or gradual
strengths *change* when one element is removed. They quantify the local
importance of an argument or an attack to the framework's verdict.
"""

from __future__ import annotations

from argumentation.core.dung import ArgumentationFramework, grounded_extension
from argumentation.gradual.dfquad import dfquad_strengths
from argumentation.gradual.gradual import GradualConvergenceError, WeightedBipolarGraph


def score_conflict(
    framework: ArgumentationFramework,
    claim_a_id: str,
    claim_b_id: str,
    *,
    semantics: str = "grounded",
) -> float:
    """Score how much two arguments swing the accepted extension.

    For each of ``claim_a_id`` and ``claim_b_id``, the argument (and every
    defeat touching it) is removed and the grounded extension is recomputed.
    The symmetric difference between the original and the reduced extension
    measures how many acceptance verdicts that removal flips. The returned
    value is the larger of the two normalized swing counts, clamped to
    ``[0, 1]``.

    A value of ``0.0`` means removing either argument leaves every other
    argument's acceptance unchanged; a value near ``1.0`` means one of them
    is pivotal for almost the whole framework.

    Only ``semantics="grounded"`` is supported; any other value raises
    ``ValueError``.
    """
    if semantics != "grounded":
        raise ValueError(f"Unsupported semantics: {semantics!r}")
    if not framework.arguments:
        return 0.0

    total = len(framework.arguments)
    current = grounded_extension(framework)

    def _remove(arg_id: str) -> frozenset[str]:
        reduced = ArgumentationFramework(
            arguments=frozenset(
                argument for argument in framework.arguments if argument != arg_id
            ),
            defeats=frozenset(
                (attacker, target)
                for attacker, target in framework.defeats
                if attacker != arg_id and target != arg_id
            ),
        )
        return grounded_extension(reduced)

    ext_remove_a = _remove(claim_a_id)
    ext_remove_b = _remove(claim_b_id)
    dist_a = len(current.symmetric_difference(ext_remove_a))
    dist_b = len(current.symmetric_difference(ext_remove_b))
    return min(1.0, max(dist_a, dist_b) / total)


def attack_removal_sensitivity(
    framework: ArgumentationFramework,
    supports: dict[tuple[str, str], float],
    base_scores: dict[str, float],
    attack: tuple[str, str],
) -> float:
    """Measure the DF-QuAD strength swing of an attack's target when removed.

    The DF-QuAD strengths of every argument are computed once with ``attack``
    present and once with ``attack`` removed. The returned number is the
    strength delta of the *attacked* argument (``attack[1]``):

        strength(target) without the attack  -  strength(target) with it.

    Because the attack suppresses its target, removing it normally *raises*
    the target's strength, so the result is typically non-negative; it is the
    amount of strength the target loses purely because this attack exists.
    If ``attack`` is not a defeat of ``framework``, the result is ``0.0``.

    ``supports`` maps support edges to their weights and ``base_scores`` gives
    each argument's base score; both are passed straight through to
    :func:`argumentation.gradual.dfquad.dfquad_strengths`.
    """
    if attack not in framework.defeats:
        return 0.0

    graph = WeightedBipolarGraph(
        arguments=framework.arguments,
        initial_weights=base_scores,
        attacks=framework.defeats,
        supports=frozenset(supports),
    )
    full_result = dfquad_strengths(
        graph,
        base_scores=base_scores,
        support_weights=supports,
    )
    if not full_result.converged:
        raise GradualConvergenceError(
            "attack removal sensitivity baseline",
            full_result,
        )
    strengths_full = full_result.strengths

    reduced_framework = ArgumentationFramework(
        arguments=framework.arguments,
        defeats=frozenset(defeat for defeat in framework.defeats if defeat != attack),
    )
    reduced_graph = WeightedBipolarGraph(
        arguments=reduced_framework.arguments,
        initial_weights=base_scores,
        attacks=reduced_framework.defeats,
        supports=frozenset(supports),
    )
    reduced_result = dfquad_strengths(
        reduced_graph,
        base_scores=base_scores,
        support_weights=supports,
    )
    if not reduced_result.converged:
        raise GradualConvergenceError(
            "attack removal sensitivity after removal",
            reduced_result,
        )
    strengths_reduced = reduced_result.strengths
    return strengths_reduced[attack[1]] - strengths_full[attack[1]]
