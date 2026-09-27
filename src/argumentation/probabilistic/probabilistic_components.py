"""Connectivity helpers for probabilistic argumentation frameworks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argumentation.probabilistic.probabilistic import ProbabilisticAF


def connected_components(praf: "ProbabilisticAF") -> list[set[str]]:
    """Decompose a PrAF into primitive semantic dependency components.

    Per Hunter & Thimm (2017, Prop 18): acceptance probability separates
    over connected components. Each component can be solved independently.
    """
    adj: dict[str, set[str]] = {a: set() for a in praf.framework.arguments}
    primitive_attacks = (
        praf.framework.attacks
        if praf.framework.attacks is not None
        else praf.framework.defeats
    )
    relations = set(primitive_attacks) | set(praf.supports)
    for src, tgt in relations:
        adj[src].add(tgt)
        adj[tgt].add(src)

    visited: set[str] = set()
    components: list[set[str]] = []

    # Sorted start nodes give a hash-seed-independent component order, which
    # seeded Monte Carlo relies on for a reproducible sampling stream.
    for start in sorted(praf.framework.arguments):
        if start in visited:
            continue
        component: set[str] = set()
        queue = [start]
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(component)

    return components
