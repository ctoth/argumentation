"""Deterministic in-package enumeration of SAT-supported Dung extensions.

This module exposes :func:`sat_extensions`, the ``sat`` backend's entry point.
It routes each semantics to the native Dung/SCC machinery (grounded, complete,
preferred, stable, semi-stable, stage, ideal) plus a finite brute-force
admissible enumerator, avoiding a hard dependency on an external SAT solver.
"""

from __future__ import annotations

from argumentation.core.dung import (
    ArgumentationFramework,
    admissible,
    grounded_extension,
    ideal_extension,
    semi_stable_extensions,
    stage_extensions,
)
from argumentation.core.finite import predecessors_index


def sat_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    """Enumerate SAT-supported Dung extensions.

    Niskanen and Järvisalo 2020 encode central Dung semantics with Boolean
    variables for extension membership, plus iterative SAT calls for maximality
    and enumeration. This in-package backend uses the same finite candidate
    surface and blocking-style deterministic enumeration, while avoiding a hard
    dependency on a specific external SAT solver.
    """
    if semantics == "admissible":
        return _sorted_extensions(_admissible_sets(framework))
    if semantics == "grounded":
        return (grounded_extension(framework),)
    # complete / preferred / stable -> SCC-recursive layer (Wave B2): grounded-reduct
    # preprocessing composed with Baroni-Giacomin-Guida SCC decomposition. Transparent.
    if semantics in ("complete", "preferred", "stable"):
        from argumentation.core.scc_recursive import scc_extensions

        return _sorted_extensions(scc_extensions(framework, semantics))
    if semantics == "semi-stable":
        return _sorted_extensions(semi_stable_extensions(framework))
    if semantics == "stage":
        return _sorted_extensions(stage_extensions(framework))
    if semantics == "ideal":
        return (ideal_extension(framework),)
    raise ValueError(f"unsupported SAT Dung semantics: {semantics}")


def _admissible_sets(framework: ArgumentationFramework) -> list[frozenset[str]]:
    attackers_index = predecessors_index(framework.defeats)
    arguments = sorted(framework.arguments)
    results: list[frozenset[str]] = []
    for mask in range(1 << len(arguments)):
        candidate = frozenset(
            argument for index, argument in enumerate(arguments) if mask & (1 << index)
        )
        if admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        ):
            results.append(candidate)
    return results


def _sorted_extensions(values: list[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )


__all__ = ["sat_extensions"]
