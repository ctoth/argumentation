"""Approximate and k-stable semantics for Dung AFs.

These routines are pure-Python reference surfaces for the heuristics-oriented
workstream.  They keep exact Dung semantics as the calibration point: k-stable
with ``k=0`` is stable semantics, bounded grounded iteration reports whether it
has reached the fixed point, and semi-stable approximation reports whether the
candidate budget was exhaustive.

References:
    Skiba and Thimm (2024). Optimisation and approximation in abstract
    argumentation: the case of k-stable semantics.
    Dung (1995). On the acceptability of arguments and its fundamental role.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from argumentation.dung import (
    ArgumentationFramework,
    admissible,
    characteristic_fn,
    conflict_free,
    range_of,
    semi_stable_extensions,
    stable_extensions,
)


@dataclass(frozen=True)
class GroundedApproximation:
    extension: frozenset[str]
    iterations: int
    exact: bool


@dataclass(frozen=True)
class SemiStableApproximation:
    extensions: tuple[frozenset[str], ...]
    examined_candidates: int
    exact: bool


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    return [
        frozenset(ordered[index] for index in range(len(ordered)) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    ]


def _range_maximal(
    candidates: list[frozenset[str]],
    defeats: frozenset[tuple[str, str]],
) -> tuple[frozenset[str], ...]:
    ranges = {candidate: range_of(candidate, defeats) for candidate in candidates}
    return tuple(
        candidate
        for candidate in candidates
        if not any(ranges[candidate] < other_range for other_range in ranges.values())
    )


def k_stable_extensions(
    framework: ArgumentationFramework,
    *,
    k: int,
) -> tuple[frozenset[str], ...]:
    """Return k-stable extensions.

    ``k`` bounds the tolerated deviation from stability: candidates remain
    conflict-free, but may leave at most ``k`` outsiders undefeated.  At
    ``k=0`` this is exactly Dung stable semantics.
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return tuple(stable_extensions(framework))

    candidates: list[frozenset[str]] = []
    for candidate in _all_subsets(framework.arguments):
        if not conflict_free(candidate, framework.defeats):
            continue
        covered = range_of(candidate, framework.defeats)
        uncovered_outsiders = len(framework.arguments - covered)
        if uncovered_outsiders <= k:
            candidates.append(candidate)
    return _range_maximal(candidates, framework.defeats)


def approximate_grounded(
    framework: ArgumentationFramework,
    *,
    k_iterations: int,
) -> GroundedApproximation:
    """Run at most ``k_iterations`` of the grounded characteristic function."""
    if k_iterations < 0:
        raise ValueError("k_iterations must be non-negative")

    current: frozenset[str] = frozenset()
    iterations = 0
    for _ in range(k_iterations):
        next_current = characteristic_fn(
            current,
            framework.arguments,
            framework.defeats,
        )
        iterations += 1
        current = next_current
        if characteristic_fn(current, framework.arguments, framework.defeats) == current:
            return GroundedApproximation(
                extension=current,
                iterations=iterations,
                exact=True,
            )

    exact = characteristic_fn(current, framework.arguments, framework.defeats) == current
    return GroundedApproximation(extension=current, iterations=iterations, exact=exact)


def approximate_semi_stable(
    framework: ArgumentationFramework,
    *,
    max_candidates: int | None,
) -> SemiStableApproximation:
    """Approximate semi-stable extensions under an optional candidate budget."""
    if max_candidates is None:
        exact = tuple(semi_stable_extensions(framework))
        return SemiStableApproximation(
            extensions=exact,
            examined_candidates=2 ** len(framework.arguments),
            exact=True,
        )
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive or None")

    complete_candidates: list[frozenset[str]] = []
    examined = 0
    for size in range(len(framework.arguments) + 1):
        for subset in combinations(sorted(framework.arguments), size):
            if examined >= max_candidates:
                return SemiStableApproximation(
                    extensions=_range_maximal(complete_candidates, framework.defeats),
                    examined_candidates=examined,
                    exact=False,
                )
            examined += 1
            candidate = frozenset(subset)
            if not conflict_free(candidate, framework.defeats):
                continue
            if not admissible(candidate, framework.arguments, framework.defeats):
                continue
            if characteristic_fn(candidate, framework.arguments, framework.defeats) == candidate:
                complete_candidates.append(candidate)

    return SemiStableApproximation(
        extensions=_range_maximal(complete_candidates, framework.defeats),
        examined_candidates=examined,
        exact=True,
    )
