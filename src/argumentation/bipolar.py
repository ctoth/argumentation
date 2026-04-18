"""Explicit bipolar argumentation semantics for Cayrol-style frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class BipolarArgumentationFramework:
    """A finite bipolar argumentation framework.

    Arguments are atomic. Defeats and supports are independent binary
    relations, as in Cayrol & Lagasquie-Schiex (2005).
    """

    arguments: frozenset[str]
    defeats: frozenset[tuple[str, str]]
    supports: frozenset[tuple[str, str]] = frozenset()


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


def set_defeats(
    args: frozenset[str],
    target: str,
    framework: BipolarArgumentationFramework,
) -> bool:
    """Return whether ``args`` set-defeats ``target``."""
    return target in {
        defeated
        for source, defeated in _defeat_closure(framework.defeats, framework.supports)
        if source in args
    }


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
    return not any(set_defeats(args, target, framework) for target in args)


def safe(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 7: no set-defeated argument is set-supported."""
    for arg in framework.arguments:
        if set_defeats(args, arg, framework) and (
            set_supports(args, arg, framework) or arg in args
        ):
            return False
    return True


def defends(
    args: frozenset[str],
    arg: str,
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 5: collective defence via set-defeat."""
    closure = _defeat_closure(framework.defeats, framework.supports)
    attackers_index: dict[str, set[str]] = {}
    for source, target in closure:
        attackers_index.setdefault(target, set()).add(source)
    attackers = attackers_index.get(arg, set())
    for attacker in attackers:
        if not any((defender, attacker) in closure for defender in args):
            return False
    return True


def d_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 9."""
    return conflict_free(args, framework) and all(
        defends(args, arg, framework) for arg in args
    )


def s_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 10."""
    return safe(args, framework) and all(
        defends(args, arg, framework) for arg in args
    )


def c_admissible(
    args: frozenset[str],
    framework: BipolarArgumentationFramework,
) -> bool:
    """Cayrol 2005, Definition 11."""
    return (
        conflict_free(args, framework)
        and support_closed(args, framework)
        and all(defends(args, arg, framework) for arg in args)
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
    admissible_sets = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if predicate(candidate, framework)
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
    stable: list[frozenset[str]] = []
    for candidate in _all_subsets(framework.arguments):
        if not conflict_free(candidate, framework):
            continue
        outsiders = framework.arguments - candidate
        if all(set_defeats(candidate, target, framework) for target in outsiders):
            stable.append(candidate)
    return sorted(stable, key=lambda s: (len(s), tuple(sorted(s))))
