"""Shared framework-view helpers for ranking semantics.

``attack_relation`` encodes the Dung-AF "use attacks, fall back to defeats"
choice (genuine domain logic, not a generic graph primitive); ``attackers``
indexes predecessors over that chosen relation. ``ranking.py`` and
``ranking_axioms.py`` share this single definition instead of each holding a
byte-identical copy.
"""

from __future__ import annotations

from argumentation.core.dung import ArgumentationFramework
from argumentation.core.finite import predecessors_index


def attack_relation(
    framework: ArgumentationFramework,
) -> frozenset[tuple[str, str]]:
    return framework.attacks if framework.attacks is not None else framework.defeats


def attackers(framework: ArgumentationFramework) -> dict[str, frozenset[str]]:
    return predecessors_index(attack_relation(framework), nodes=framework.arguments)
