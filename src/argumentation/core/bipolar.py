"""Explicit bipolar argumentation semantics for Cayrol-style frameworks.

This module implements the Cayrol and Lagasquie-Schiex 2005 abstract
set-defeat account. Amgoud et al. 2008 distinguish richer support modes
(deductive, necessary, evidence-style); those are intentionally not collapsed
into this abstract support relation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from argumentation.core.dung import (
    ArgumentationFramework as DungArgumentationFramework,
    grounded_extension as dung_grounded_extension,
)


@dataclass(frozen=True)
class BipolarArgumentationFramework:
    """A finite bipolar argumentation framework.

    Arguments are atomic. Defeats and supports are independent binary
    relations, as in Cayrol & Lagasquie-Schiex (2005).
    """

    arguments: frozenset[str]
    defeats: frozenset[tuple[str, str]]
    supports: frozenset[tuple[str, str]] = frozenset()

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        defeats = _normalize_relation("defeats", self.defeats, arguments)
        supports = _normalize_relation("supports", self.supports, arguments)

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "defeats", defeats)
        object.__setattr__(self, "supports", supports)


def _normalize_relation(
    name: str,
    relation: frozenset[tuple[str, str]],
    arguments: frozenset[str],
) -> frozenset[tuple[str, str]]:
    normalized = frozenset((source, target) for source, target in relation)
    unknown = sorted(
        (source, target)
        for source, target in normalized
        if source not in arguments or target not in arguments
    )
    if unknown:
        raise ValueError(
            f"{name} must only contain pairs over arguments: {unknown!r}"
        )
    return normalized


def _support_successors(supports: frozenset[tuple[str, str]]) -> dict[str, frozenset[str]]:
    successors: dict[str, set[str]] = {}
    for source, target in supports:
        successors.setdefault(source, set()).add(target)
    return {source: frozenset(targets) for source, targets in successors.items()}


def _support_predecessors(supports: frozenset[tuple[str, str]]) -> dict[str, frozenset[str]]:
    predecessors: dict[str, set[str]] = {}
    for source, target in supports:
        predecessors.setdefault(target, set()).add(source)
    return {target: frozenset(sources) for target, sources in predecessors.items()}


def _attackers_index(
    defeats: frozenset[tuple[str, str]],
) -> dict[str, frozenset[str]]:
    attackers: dict[str, set[str]] = {}
    for source, target in defeats:
        attackers.setdefault(target, set()).add(source)
    return {target: frozenset(sources) for target, sources in attackers.items()}


def _closure_or_compute(
    framework: BipolarArgumentationFramework,
    defeat_closure: frozenset[tuple[str, str]] | None,
) -> frozenset[tuple[str, str]]:
    if defeat_closure is not None:
        return defeat_closure
    return _defeat_closure(framework.defeats, framework.supports)


def support_closure(
    args: frozenset[str],
    supports: frozenset[tuple[str, str]],
) -> frozenset[str]:
    """Return the closure of ``args`` under direct support successors."""
    closure = set(args)
    successors = _support_successors(supports)
    queue = list(args)
    while queue:
        current = queue.pop()
        for target in successors.get(current, frozenset()):
            if target not in closure:
                closure.add(target)
                queue.append(target)
    return frozenset(closure)


def _supported_targets(
    args: frozenset[str],
    supports: frozenset[tuple[str, str]],
) -> frozenset[str]:
    supported: set[str] = set()
    successors = _support_successors(supports)
    for source in args:
        seen: set[str] = set()
        queue = list(successors.get(source, frozenset()))
        seen.update(queue)
        while queue:
            current = queue.pop()
            supported.add(current)
            for target in successors.get(current, frozenset()):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
    return frozenset(supported)


def cayrol_derived_defeats(
    defeats: frozenset[tuple[str, str]],
    supports: frozenset[tuple[str, str]],
) -> frozenset[tuple[str, str]]:
    """Return the derived defeats induced by support/defeat interaction.

    This computes Cayrol & Lagasquie-Schiex (2005, Definition 3)
    supported and indirect defeats to a fixpoint.
    """
    support_reach: dict[str, frozenset[str]] = {}
    successors = _support_successors(supports)
    for source in successors:
        seen = {source}
        queue = [source]
        reach: set[str] = set()
        while queue:
            current = queue.pop()
            for target in successors.get(current, frozenset()):
                if target not in seen:
                    seen.add(target)
                    reach.add(target)
                    queue.append(target)
        support_reach[source] = frozenset(reach)

    working_defeats = set(defeats)
    all_derived: set[tuple[str, str]] = set()
    while True:
        new_derived: set[tuple[str, str]] = set()

        for defeated, target in working_defeats:
            for source, reachable in support_reach.items():
                if defeated in reachable and source != target and (source, target) not in working_defeats:
                    new_derived.add((source, target))

        for source, defeated in working_defeats:
            reachable = support_reach.get(defeated)
            if not reachable:
                continue
            for target in reachable:
                if source != target and (source, target) not in working_defeats:
                    new_derived.add((source, target))

        new_derived = {(source, target) for source, target in new_derived if source != target}
        if not new_derived:
            break

        working_defeats |= new_derived
        all_derived |= new_derived

    return frozenset(all_derived)


def derived_set_defeats(
    framework: BipolarArgumentationFramework,
) -> frozenset[tuple[str, str]]:
    """Return the defeat closure induced by support/defeat interaction."""
    return frozenset(
        set(framework.defeats)
        | set(cayrol_derived_defeats(framework.defeats, framework.supports))
    )


def _defeat_closure(
    defeats: frozenset[tuple[str, str]],
    supports: frozenset[tuple[str, str]],
) -> frozenset[tuple[str, str]]:
    return frozenset(set(defeats) | set(cayrol_derived_defeats(defeats, supports)))


def _set_defeats(
    args: frozenset[str],
    target: str,
    defeat_closure: frozenset[tuple[str, str]],
) -> bool:
    return target in {
        defeated
        for source, defeated in defeat_closure
        if source in args
    }


def _conflict_free(
    args: frozenset[str],
    defeat_closure: frozenset[tuple[str, str]],
) -> bool:
    return not any(
        _set_defeats(args, target, defeat_closure)
        for target in args
    )


def _safe(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
    defeat_closure: frozenset[tuple[str, str]],
) -> bool:
    for arg in framework.arguments:
        if _set_defeats(args, arg, defeat_closure) and (
            set_supports(args, arg, framework) or arg in args
        ):
            return False
    return True


def set_defeats(
    args: frozenset[str],
    target: str,
    framework: BipolarArgumentationFramework,
) -> bool:
    """Return whether ``args`` set-defeats ``target``."""
    return _set_defeats(
        args,
        target,
        _defeat_closure(framework.defeats, framework.supports),
    )


def set_supports(
    args: frozenset[str],
    target: str,
    framework: BipolarArgumentationFramework,
) -> bool:
    """Return whether ``args`` set-supports ``target``."""
    return target in _supported_targets(args, framework.supports)


def support_closed(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Return whether ``args`` is closed under direct support."""
    return support_closure(args, framework.supports) == args


def conflict_free(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 6: no set-defeat within the set."""
    return _conflict_free(
        args,
        _defeat_closure(framework.defeats, framework.supports),
    )


def safe(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 7: no set-defeated argument is set-supported."""
    return _safe(
        args,
        framework,
        _defeat_closure(framework.defeats, framework.supports),
    )


def defends(
    args: frozenset[str],
    arg: str,
    framework: BipolarArgumentationFramework,
    *,
    defeat_closure: frozenset[tuple[str, str]] | None = None,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> bool:
    """Cayrol 2005, Definition 5: collective defence via set-defeat."""
    closure = _closure_or_compute(framework, defeat_closure)
    if attackers_index is None:
        attackers_index = _attackers_index(closure)
    attackers = attackers_index.get(arg, frozenset())
    for attacker in attackers:
        if not any((defender, attacker) in closure for defender in args):
            return False
    return True


def d_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 9."""
    defeat_closure = _defeat_closure(framework.defeats, framework.supports)
    return _d_admissible(
        args,
        framework,
        defeat_closure,
        _attackers_index(defeat_closure),
    )


def _d_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
    defeat_closure: frozenset[tuple[str, str]],
    attackers_index: dict[str, frozenset[str]],
) -> bool:
    return _conflict_free(args, defeat_closure) and all(
        defends(
            args,
            arg,
            framework,
            defeat_closure=defeat_closure,
            attackers_index=attackers_index,
        )
        for arg in args
    )


def s_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 10."""
    defeat_closure = _defeat_closure(framework.defeats, framework.supports)
    return _s_admissible(
        args,
        framework,
        defeat_closure,
        _attackers_index(defeat_closure),
    )


def _s_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
    defeat_closure: frozenset[tuple[str, str]],
    attackers_index: dict[str, frozenset[str]],
) -> bool:
    return _safe(args, framework, defeat_closure) and all(
        defends(
            args,
            arg,
            framework,
            defeat_closure=defeat_closure,
            attackers_index=attackers_index,
        )
        for arg in args
    )


def c_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 11."""
    defeat_closure = _defeat_closure(framework.defeats, framework.supports)
    return _c_admissible(
        args,
        framework,
        defeat_closure,
        _attackers_index(defeat_closure),
    )


def _c_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
    defeat_closure: frozenset[tuple[str, str]],
    attackers_index: dict[str, frozenset[str]],
) -> bool:
    return (
        _conflict_free(args, defeat_closure)
        and support_closed(args, framework)
        and all(
            defends(
                args,
                arg,
                framework,
                defeat_closure=defeat_closure,
                attackers_index=attackers_index,
            )
            for arg in args
        )
    )


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    subsets: list[frozenset[str]] = []
    for size in range(len(ordered) + 1):
        for subset in combinations(ordered, size):
            subsets.append(frozenset(subset))
    return subsets


def _maximal_sets(
    framework: BipolarArgumentationFramework,
    predicate,
) -> list[frozenset[str]]:
    defeat_closure = derived_set_defeats(framework)
    attackers_index = _attackers_index(defeat_closure)
    closure_predicates = {
        d_admissible: _d_admissible,
        s_admissible: _s_admissible,
        c_admissible: _c_admissible,
    }
    closure_predicate = closure_predicates.get(predicate)
    admissible_sets = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if (
            closure_predicate(
                candidate,
                framework,
                defeat_closure,
                attackers_index,
            )
            if closure_predicate is not None
            else predicate(candidate, framework)
        )
    ]
    maximal = [
        candidate
        for candidate in admissible_sets
        if not any(candidate < other for other in admissible_sets)
    ]
    return sorted(maximal, key=lambda s: (len(s), tuple(sorted(s))))


def d_preferred_extensions(
    framework: BipolarArgumentationFramework,
) -> list[frozenset[str]]:
    """Maximal d-admissible sets."""
    return _maximal_sets(framework, d_admissible)


def s_preferred_extensions(
    framework: BipolarArgumentationFramework,
) -> list[frozenset[str]]:
    """Maximal s-admissible sets."""
    return _maximal_sets(framework, s_admissible)


def c_preferred_extensions(
    framework: BipolarArgumentationFramework,
) -> list[frozenset[str]]:
    """Maximal c-admissible sets."""
    return _maximal_sets(framework, c_admissible)


def stable_extensions(
    framework: BipolarArgumentationFramework,
) -> list[frozenset[str]]:
    """Cayrol 2005, Definition 8: conflict-free and defeats every outsider."""
    defeat_closure = derived_set_defeats(framework)
    stable: list[frozenset[str]] = []
    for candidate in _all_subsets(framework.arguments):
        if not _conflict_free(candidate, defeat_closure):
            continue
        outsiders = framework.arguments - candidate
        if all(
            _set_defeats(
                candidate,
                target,
                defeat_closure,
            )
            for target in outsiders
        ):
            stable.append(candidate)
    return sorted(stable, key=lambda s: (len(s), tuple(sorted(s))))


def characteristic_fn(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
    *,
    defeat_closure: frozenset[tuple[str, str]] | None = None,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> frozenset[str]:
    """Return the Cayrol/Dung characteristic function over set-defeats."""
    closure = _closure_or_compute(framework, defeat_closure)
    if attackers_index is None:
        attackers_index = _attackers_index(closure)
    return frozenset(
        argument
        for argument in framework.arguments
        if defends(
            args,
            argument,
            framework,
            defeat_closure=closure,
            attackers_index=attackers_index,
        )
    )


def bipolar_grounded_extension(
    framework: BipolarArgumentationFramework,
) -> frozenset[str]:
    """Return the least fixed point over Cayrol set-defeat.

    Cayrol and Lagasquie-Schiex 2005, p. 385, instantiate Dung's framework
    with set-defeats; Dung grounded is the least fixed point of the resulting
    characteristic function.
    """
    defeat_closure = derived_set_defeats(framework)
    return dung_grounded_extension(
        DungArgumentationFramework(
            arguments=framework.arguments,
            defeats=defeat_closure,
        )
    )


def bipolar_complete_extensions(
    framework: BipolarArgumentationFramework,
) -> list[frozenset[str]]:
    """Return fixed points of the Cayrol characteristic function."""
    defeat_closure = derived_set_defeats(framework)
    attackers_index = _attackers_index(defeat_closure)
    completes = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if _d_admissible(
            candidate,
            framework,
            defeat_closure,
            attackers_index,
        )
        and characteristic_fn(
            candidate,
            framework,
            defeat_closure=defeat_closure,
            attackers_index=attackers_index,
        ) == candidate
    ]
    return sorted(completes, key=lambda s: (len(s), tuple(sorted(s))))
