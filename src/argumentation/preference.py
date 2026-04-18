"""Generic preference helpers for formal argumentation."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import TypeVar

TOrder = TypeVar("TOrder", bound=Hashable)


def strict_partial_order_closure(
    pairs: Iterable[tuple[TOrder, TOrder]],
) -> frozenset[tuple[TOrder, TOrder]]:
    """Return the transitive closure of a strict partial order.

    Pairs are oriented ``(weaker, stronger)``. The result is the smallest
    transitive relation containing the authored pairs. Any reflexive edge or
    cycle is rejected because Modgil & Prakken Def 22 requires a strict
    partial order.
    """
    closure: set[tuple[TOrder, TOrder]] = set()
    for weaker, stronger in pairs:
        if weaker == stronger:
            raise ValueError("strict partial order cannot contain a reflexive pair")
        closure.add((weaker, stronger))

    changed = True
    while changed:
        changed = False
        new_pairs: set[tuple[TOrder, TOrder]] = set()
        for left, mid in closure:
            for source, right in closure:
                if mid == source and (left, right) not in closure:
                    if left == right:
                        raise ValueError("strict partial order contains a cycle")
                    new_pairs.add((left, right))
        if new_pairs:
            closure |= new_pairs
            changed = True

    for weaker, stronger in closure:
        if (stronger, weaker) in closure:
            raise ValueError("strict partial order contains a cycle")
    return frozenset(closure)


def strictly_weaker(
    set_a: list[float],
    set_b: list[float],
    comparison: str,
) -> bool:
    """Test whether ``set_a`` is strictly weaker than ``set_b``.

    Modgil & Prakken 2018, Def 19:
    - Elitist: A < B iff some x in A is weaker than every y in B.
    - Democratic: A < B iff every x in A is weaker than some y in B.
    """
    if not set_a or not set_b:
        return False
    if comparison == "elitist":
        return any(all(x < y for y in set_b) for x in set_a)
    if comparison == "democratic":
        return all(any(x < y for y in set_b) for x in set_a)
    raise ValueError(f"Unknown comparison: {comparison}")


def defeat_holds(
    attack_type: str,
    attacker_strengths: list[float],
    target_strengths: list[float],
    comparison: str,
) -> bool:
    """Determine whether a generic attack succeeds as a defeat.

    Undercutting-style attacks are preference-independent. Rebutting and
    undermining attacks succeed iff the attacker is not strictly weaker.
    """
    if attack_type in ("undercuts", "supersedes"):
        return True
    if attack_type in ("rebuts", "undermines"):
        return not strictly_weaker(attacker_strengths, target_strengths, comparison)
    raise ValueError(f"Unknown attack type: {attack_type}")
