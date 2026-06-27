"""Shared Horn forward-closure for flat ABA.

Least-fixpoint forward chaining used by the frozenset-based closures in
``aba``, ``aba_sat`` (``AssumptionKernel``), and ``aba_telemetry``. This is a
LEAF module: it imports no sibling ``aba`` modules (only ``aspic`` types, and
those only for typing), so any of them can route through it without an import
cycle.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from argumentation.structured.aspic.aspic import Literal, Rule


def horn_closure(
    seed: Iterable["Literal"], rules: Iterable["Rule"]
) -> frozenset["Literal"]:
    """Least-fixpoint forward chaining: derive every literal reachable from ``seed``.

    Starting from ``seed``, repeatedly fire any rule whose antecedents are all
    derived, adding its consequent, until no rule fires. The result includes the
    seed literals and every literal derivable from them under ``rules``.

    Implemented with a remaining-antecedent counter and per-literal waiting
    lists (the canonical ``aba._closure`` worklist). Because a Horn closure is a
    least fixpoint, the order in which ``rules`` are iterated and the order in
    which the worklist is drained do not affect the returned set.
    """
    closure = set(seed)
    queue = list(closure)
    waiting: defaultdict[Literal, list[int]] = defaultdict(list)
    remaining: list[int] = []
    consequents: list[Literal] = []

    for index, rule in enumerate(rules):
        missing = 0
        for antecedent in frozenset(rule.antecedents):
            if antecedent not in closure:
                missing += 1
                waiting[antecedent].append(index)
        remaining.append(missing)
        consequents.append(rule.consequent)
        if missing == 0 and rule.consequent not in closure:
            closure.add(rule.consequent)
            queue.append(rule.consequent)

    while queue:
        literal = queue.pop()
        for rule_index in waiting.get(literal, ()):
            remaining[rule_index] -= 1
            if remaining[rule_index] == 0:
                consequent = consequents[rule_index]
                if consequent not in closure:
                    closure.add(consequent)
                    queue.append(consequent)
    return frozenset(closure)
