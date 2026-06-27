"""Iterative fixed-point driver shared by ranking and gradual semantics.

Many score-based semantics (Besnard-Hunter Categoriser, damped counting,
Potyka's discrete quadratic energy, DF-QuAD, Gabbay equational) share one
update loop: start from initial scores, repeatedly replace every score by a
rule over the current scores, and stop once the largest single-argument change
drops to a tolerance. This module isolates that loop so each semantics only has
to supply its own update rule and wrap the outcome in its own result type.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import NamedTuple


class FixpointOutcome(NamedTuple):
    """Result of an :func:`iterate_fixpoint` run.

    ``converged=False`` is data, not an exception: it reports that the loop hit
    ``max_iterations`` before the change fell to ``tolerance``.
    """

    scores: dict[str, float]
    converged: bool
    iterations: int
    last_delta: float


def iterate_fixpoint(
    initial: Mapping[str, float],
    update: Callable[[dict[str, float]], dict[str, float]],
    *,
    tolerance: float,
    max_iterations: int,
) -> FixpointOutcome:
    """Iterate ``scores = update(scores)`` until convergence or exhaustion.

    Each iteration computes ``updated = update(scores)`` and the change
    ``delta = max(abs(updated[k] - scores[k]) for k in updated)`` (``0.0`` when
    ``updated`` is empty), then swaps ``scores = updated``. The loop is 1-based:
    iteration ``i`` runs over ``range(1, max_iterations + 1)``. As soon as
    ``delta <= tolerance`` it returns with ``converged=True`` and
    ``iterations=i``; if the loop exhausts ``max_iterations`` first it returns
    ``converged=False`` and ``iterations=max_iterations``. In both cases
    ``last_delta`` is the change from the final iteration that ran.

    ``update`` must return a fresh dict keyed exactly like ``initial`` (the
    delta is taken over the returned dict's keys). Callers are responsible for
    validating ``tolerance`` and ``max_iterations`` before calling.
    """

    scores = dict(initial)
    last_delta = 0.0
    for iteration in range(1, max_iterations + 1):
        updated = update(scores)
        last_delta = max(
            (abs(updated[key] - scores[key]) for key in updated),
            default=0.0,
        )
        scores = updated
        if last_delta <= tolerance:
            return FixpointOutcome(scores, True, iteration, last_delta)
    return FixpointOutcome(scores, False, max_iterations, last_delta)
