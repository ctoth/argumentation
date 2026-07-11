"""Bounded reference semantics for collective-attack SCC composition in flat ABA.

This is a diagnostic contract artifact, not a production solver or routing helper.
It deliberately materializes minimal supports and branch states under explicit caps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import TypeAlias

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_support_model import _minimal_supports
from argumentation.structured.aspic.aspic import Literal


ExtensionFamily: TypeAlias = tuple[AssumptionSet, ...]


@dataclass(frozen=True)
class ReferenceCaps:
    """Deterministic limits that keep this exponential reference bounded."""

    collective_attacks: int = 4_096
    branch_states: int = 65_536
    boundary_items: int = 4_096


@dataclass(frozen=True, order=True)
class CollectiveAttack:
    tail: AssumptionSet
    target: Literal


@dataclass(frozen=True)
class ConditionedAttack:
    original: CollectiveAttack
    residual_tail: AssumptionSet
    mitigated: bool


@dataclass(frozen=True)
class ComponentBoundary:
    component: AssumptionSet
    selected: AssumptionSet
    attacked: AssumptionSet
    defeated: AssumptionSet
    provisionally_defeated: AssumptionSet
    undefeated: AssumptionSet
    undefeated_or_provisional: AssumptionSet
    candidates: AssumptionSet
    attacks: tuple[ConditionedAttack, ...]
    mitigated: tuple[ConditionedAttack, ...]


@dataclass(frozen=True)
class CollectiveFramework:
    assumptions: AssumptionSet
    attacks: frozenset[CollectiveAttack]
    fact_attacked: AssumptionSet
    components: tuple[AssumptionSet, ...]
    caps: ReferenceCaps


@dataclass(frozen=True)
class CompositionTrace:
    normalized_fact_attacked: int
    collective_attack_count: int
    scc_count: int
    cross_scc_collective_tails: int
    branch_states: int
    partially_activated_tails: int
    defeated_collective_tails: int
    mitigated_attacks: int
    nonempty_candidate_states: int
    annihilated_stable_branches: int
    maximum_boundary_items: int
    boundary_item_cap: int


@dataclass(frozen=True)
class CompositionResult:
    extensions: ExtensionFamily
    collective_framework: CollectiveFramework
    boundaries: tuple[ComponentBoundary, ...]
    trace: CompositionTrace


class ReferenceCapExceeded(RuntimeError):
    """Raised rather than silently weakening an exact bounded contract."""


@dataclass
class _TraceBuilder:
    branch_states: int = 0
    partially_activated_tails: int = 0
    defeated_collective_tails: int = 0
    mitigated_attacks: int = 0
    nonempty_candidate_states: int = 0
    annihilated_stable_branches: int = 0
    maximum_boundary_items: int = 0
    boundaries: list[ComponentBoundary] = field(default_factory=list)


def build_collective_framework(
    framework: ABAFramework,
    *,
    caps: ReferenceCaps = ReferenceCaps(),
) -> CollectiveFramework:
    """Materialize minimal-support attacks, normalize facts, and order primal SCCs."""
    supports = _minimal_supports(framework)
    raw_attacks = frozenset(
        CollectiveAttack(tail, target)
        for target in framework.assumptions
        for tail in supports.get(framework.contrary[target], frozenset())
    )
    if len(raw_attacks) > caps.collective_attacks:
        raise ReferenceCapExceeded(
            f"collective attack cap exceeded: {len(raw_attacks)} > {caps.collective_attacks}"
        )

    fact_attacked = frozenset(
        attack.target for attack in raw_attacks if not attack.tail
    )
    assumptions = framework.assumptions - fact_attacked
    attacks = frozenset(
        attack
        for attack in raw_attacks
        if attack.target in assumptions and not (attack.tail & fact_attacked)
    )
    components = _topological_sccs(assumptions, attacks)
    return CollectiveFramework(assumptions, attacks, fact_attacked, components, caps)


def stable_extensions(
    framework: ABAFramework,
    *,
    caps: ReferenceCaps = ReferenceCaps(),
) -> CompositionResult:
    collective = build_collective_framework(framework, caps=caps)
    return _compose(collective, preferred=False)


def preferred_extensions(
    framework: ABAFramework,
    *,
    caps: ReferenceCaps = ReferenceCaps(),
) -> CompositionResult:
    collective = build_collective_framework(framework, caps=caps)
    return _compose(collective, preferred=True)


def _compose(collective: CollectiveFramework, *, preferred: bool) -> CompositionResult:
    trace = _TraceBuilder()
    complete: list[AssumptionSet] = []

    def visit(component_index: int, selected: AssumptionSet) -> None:
        trace.branch_states += 1
        if trace.branch_states > collective.caps.branch_states:
            raise ReferenceCapExceeded(
                f"branch state cap exceeded: {trace.branch_states} > {collective.caps.branch_states}"
            )
        if component_index == len(collective.components):
            complete.append(selected)
            return

        component = collective.components[component_index]
        attacked_before = _attacked_by(collective.attacks, selected)
        boundary = _condition_boundary(
            collective, component, selected, attacked_before, trace
        )
        choices = (
            boundary.candidates if preferred else boundary.undefeated_or_provisional
        )
        surviving = 0
        for local in _subsets(choices):
            extended = selected | local
            attacked_now = attacked_before | _active_local_targets(boundary, local)
            if preferred:
                if not _locally_admissible(
                    collective.attacks,
                    component,
                    local,
                    attacked_now,
                ):
                    continue
            elif not _locally_stable(component, local, attacked_now):
                continue
            surviving += 1
            visit(component_index + 1, extended)
        if not preferred and surviving == 0:
            trace.annihilated_stable_branches += 1

    visit(0, frozenset())
    if preferred:
        complete = [
            candidate
            for candidate in complete
            if not any(candidate < other for other in complete)
        ]
    extensions = _sorted_extensions(complete)
    return CompositionResult(
        extensions=extensions,
        collective_framework=collective,
        boundaries=tuple(trace.boundaries),
        trace=_freeze_trace(collective, trace),
    )


def _condition_boundary(
    collective: CollectiveFramework,
    component: AssumptionSet,
    selected: AssumptionSet,
    attacked: AssumptionSet,
    trace: _TraceBuilder,
) -> ComponentBoundary:
    conditioned: list[ConditionedAttack] = []
    for attack in _sorted_attacks(collective.attacks):
        if attack.target not in component:
            continue
        if attack.tail & attacked:
            trace.defeated_collective_tails += 1
            continue
        external = attack.tail - component
        residual = attack.tail & component
        mitigated = not external <= selected
        item = ConditionedAttack(attack, residual, mitigated)
        conditioned.append(item)
        if external and not mitigated:
            trace.partially_activated_tails += 1
        if mitigated:
            trace.mitigated_attacks += 1

    defeated = frozenset(
        item.original.target
        for item in conditioned
        if not item.mitigated and not item.residual_tail
    )
    provisional = (
        frozenset(
            item.original.target
            for item in conditioned
            if item.mitigated and not item.residual_tail
        )
        - defeated
    )
    undefeated = component - defeated - provisional
    up = undefeated | provisional
    candidates = undefeated
    mitigated_attacks = tuple(item for item in conditioned if item.mitigated)
    boundary = ComponentBoundary(
        component=component,
        selected=selected,
        attacked=attacked,
        defeated=defeated,
        provisionally_defeated=provisional,
        undefeated=undefeated,
        undefeated_or_provisional=up,
        candidates=candidates,
        attacks=tuple(conditioned),
        mitigated=mitigated_attacks,
    )
    item_count = (
        len(component)
        + len(selected)
        + len(attacked)
        + len(defeated)
        + len(provisional)
        + len(undefeated)
        + len(up)
        + len(candidates)
        + sum(
            len(item.residual_tail) + len(item.original.tail) + 1
            for item in conditioned
        )
    )
    trace.maximum_boundary_items = max(trace.maximum_boundary_items, item_count)
    if item_count > collective.caps.boundary_items:
        raise ReferenceCapExceeded(
            f"boundary item cap exceeded: {item_count} > {collective.caps.boundary_items}"
        )
    if candidates:
        trace.nonempty_candidate_states += 1
    trace.boundaries.append(boundary)
    return boundary


def _active_local_targets(
    boundary: ComponentBoundary,
    local: AssumptionSet,
) -> AssumptionSet:
    """Only non-mitigated projections may counterattack or defeat a tail."""
    return frozenset(
        item.original.target
        for item in boundary.attacks
        if not item.mitigated and item.residual_tail <= local
    )


def _locally_stable(
    component: AssumptionSet,
    local: AssumptionSet,
    attacked: AssumptionSet,
) -> bool:
    return all(
        (assumption in local) != (assumption in attacked) for assumption in component
    )


def _locally_admissible(
    attacks: frozenset[CollectiveAttack],
    component: AssumptionSet,
    local: AssumptionSet,
    attacked: AssumptionSet,
) -> bool:
    if local & attacked:
        return False
    return all(
        attack.target not in local or bool(attack.tail & attacked)
        for attack in attacks
        if attack.target in component
    )


def _attacked_by(
    attacks: frozenset[CollectiveAttack],
    selected: AssumptionSet,
) -> AssumptionSet:
    return frozenset(attack.target for attack in attacks if attack.tail <= selected)


def _topological_sccs(
    assumptions: AssumptionSet,
    attacks: frozenset[CollectiveAttack],
) -> tuple[AssumptionSet, ...]:
    adjacency = {assumption: set() for assumption in assumptions}
    for attack in attacks:
        for source in attack.tail:
            adjacency[source].add(attack.target)
    components = _tarjan(adjacency)
    component_of = {
        assumption: index
        for index, component in enumerate(components)
        for assumption in component
    }
    successors = {index: set() for index in range(len(components))}
    indegree = {index: 0 for index in range(len(components))}
    for source, targets in adjacency.items():
        for target in targets:
            left = component_of[source]
            right = component_of[target]
            if left != right and right not in successors[left]:
                successors[left].add(right)
                indegree[right] += 1
    ready = sorted(
        (index for index, degree in indegree.items() if degree == 0),
        key=lambda index: _component_key(components[index]),
    )
    ordered: list[AssumptionSet] = []
    while ready:
        current = ready.pop(0)
        ordered.append(components[current])
        for successor in sorted(
            successors[current], key=lambda index: _component_key(components[index])
        ):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
                ready.sort(key=lambda index: _component_key(components[index]))
    return tuple(ordered)


def _tarjan(adjacency: dict[Literal, set[Literal]]) -> tuple[AssumptionSet, ...]:
    index = 0
    indices: dict[Literal, int] = {}
    lowlinks: dict[Literal, int] = {}
    stack: list[Literal] = []
    on_stack: set[Literal] = set()
    components: list[AssumptionSet] = []

    def strong_connect(vertex: Literal) -> None:
        nonlocal index
        indices[vertex] = index
        lowlinks[vertex] = index
        index += 1
        stack.append(vertex)
        on_stack.add(vertex)
        for successor in sorted(adjacency[vertex], key=repr):
            if successor not in indices:
                strong_connect(successor)
                lowlinks[vertex] = min(lowlinks[vertex], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[vertex] = min(lowlinks[vertex], indices[successor])
        if lowlinks[vertex] == indices[vertex]:
            component: set[Literal] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == vertex:
                    break
            components.append(frozenset(component))

    for vertex in sorted(adjacency, key=repr):
        if vertex not in indices:
            strong_connect(vertex)
    return tuple(components)


def _subsets(items: AssumptionSet) -> tuple[AssumptionSet, ...]:
    ordered = tuple(sorted(items, key=repr))
    return tuple(
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    )


def _sorted_attacks(
    attacks: frozenset[CollectiveAttack],
) -> tuple[CollectiveAttack, ...]:
    return tuple(
        sorted(
            attacks,
            key=lambda attack: (
                repr(attack.target),
                len(attack.tail),
                tuple(sorted(map(repr, attack.tail))),
            ),
        )
    )


def _component_key(component: AssumptionSet) -> tuple[str, ...]:
    return tuple(sorted(map(repr, component)))


def _sorted_extensions(extensions: list[AssumptionSet]) -> ExtensionFamily:
    return tuple(
        sorted(
            set(extensions),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )


def _freeze_trace(
    collective: CollectiveFramework,
    trace: _TraceBuilder,
) -> CompositionTrace:
    component_of = {
        assumption: index
        for index, component in enumerate(collective.components)
        for assumption in component
    }
    cross_tails = sum(
        1
        for attack in collective.attacks
        if len(attack.tail) > 1
        and any(
            component_of[source] != component_of[attack.target]
            for source in attack.tail
        )
    )
    return CompositionTrace(
        normalized_fact_attacked=len(collective.fact_attacked),
        collective_attack_count=len(collective.attacks),
        scc_count=len(collective.components),
        cross_scc_collective_tails=cross_tails,
        branch_states=trace.branch_states,
        partially_activated_tails=trace.partially_activated_tails,
        defeated_collective_tails=trace.defeated_collective_tails,
        mitigated_attacks=trace.mitigated_attacks,
        nonempty_candidate_states=trace.nonempty_candidate_states,
        annihilated_stable_branches=trace.annihilated_stable_branches,
        maximum_boundary_items=trace.maximum_boundary_items,
        boundary_item_cap=collective.caps.boundary_items,
    )


__all__ = [
    "CollectiveAttack",
    "CollectiveFramework",
    "ComponentBoundary",
    "CompositionResult",
    "CompositionTrace",
    "ConditionedAttack",
    "ReferenceCapExceeded",
    "ReferenceCaps",
    "build_collective_framework",
    "preferred_extensions",
    "stable_extensions",
]
