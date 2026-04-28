"""Dung's abstract argumentation framework and extension semantics.

Implements grounded, preferred, stable, and complete extensions
over an abstract argumentation framework AF = (Args, Defeats).

References:
    Dung, P.M. (1995). On the acceptability of arguments and its
    fundamental role in nonmonotonic reasoning, logic programming
    and n-person games. Artificial Intelligence, 77(2), 321-357.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class ArgumentationFramework:
    """Argumentation framework with attack and defeat relations.

    Arguments are string identifiers. Defeats is a set of
    (attacker, target) pairs representing the defeat relation
    (attacks surviving preference filter). Attacks is the full
    set of attacks before preference filtering.

    Pure Dung semantics use ``defeats`` only. Consumers that need the
    full pre-preference attack layer can consult ``attacks`` explicitly.

    References:
        Dung 1995: AF = (Args, Defeats)
        Modgil & Prakken 2018 Def 14: conflict-free uses attacks, not defeats
    """

    arguments: frozenset[str]
    defeats: frozenset[tuple[str, str]]
    attacks: frozenset[tuple[str, str]] | None = None

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        defeats = _normalize_relation("defeats", self.defeats, arguments)
        attacks = (
            None
            if self.attacks is None
            else _normalize_relation("attacks", self.attacks, arguments)
        )

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "defeats", defeats)
        object.__setattr__(self, "attacks", attacks)


def _normalize_relation(
    name: str,
    relation: frozenset[tuple[str, str]],
    arguments: frozenset[str],
) -> frozenset[tuple[str, str]]:
    normalized = frozenset((attacker, target) for attacker, target in relation)
    unknown = sorted(
        (attacker, target)
        for attacker, target in normalized
        if attacker not in arguments or target not in arguments
    )
    if unknown:
        raise ValueError(
            f"{name} must only contain pairs over arguments: {unknown!r}"
        )
    return normalized


def _attackers_index(
    defeats: frozenset[tuple[str, str]],
) -> dict[str, frozenset[str]]:
    """Build target -> attackers adjacency for a defeat relation."""
    attackers: dict[str, set[str]] = {}
    for attacker, target in defeats:
        attackers.setdefault(target, set()).add(attacker)
    return {
        target: frozenset(sources)
        for target, sources in attackers.items()
    }


def attackers_of(
    arg: str,
    defeats: frozenset[tuple[str, str]],
    *,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> frozenset[str]:
    """Return the set of all arguments that defeat `arg`."""
    if attackers_index is None:
        attackers_index = _attackers_index(defeats)
    return attackers_index.get(arg, frozenset())


def conflict_free(s: frozenset[str], relation: frozenset[tuple[str, str]]) -> bool:
    """Check if s is conflict-free w.r.t. a binary relation.

    No argument in s is related to another in s under the given relation.
    Per Modgil & Prakken 2018 Def 14, this should be the attack relation
    (pre-preference), not the defeat relation. When only defeats are
    available (pure Dung AF), pass defeats.
    """
    for a, t in relation:
        if a in s and t in s:
            return False
    return True


def defends(
    s: frozenset[str],
    arg: str,
    all_args: frozenset[str],  # noqa: ARG001
    defeats: frozenset[tuple[str, str]],
    *,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> bool:
    """Check if s defends arg: for every attacker of arg, s counter-attacks it."""
    if attackers_index is None:
        attackers_index = _attackers_index(defeats)
    for attacker in attackers_of(arg, defeats, attackers_index=attackers_index):
        if not any((d, attacker) in defeats for d in s):
            return False
    return True


def characteristic_fn(
    s: frozenset[str],
    all_args: frozenset[str],
    defeats: frozenset[tuple[str, str]],
    *,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> frozenset[str]:
    """Characteristic function F(S) = {A in Args | A is defended by S}.

    Reference: Dung 1995, Definition 17.
    """
    if attackers_index is None:
        attackers_index = _attackers_index(defeats)
    return frozenset(
        a
        for a in all_args
        if defends(
            s,
            a,
            all_args,
            defeats,
            attackers_index=attackers_index,
        )
    )


def range_of(
    s: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    """Return ``s`` plus every argument defeated by an argument in ``s``."""
    defeated = frozenset(target for attacker, target in defeats if attacker in s)
    return s | defeated


def admissible(
    s: frozenset[str],
    all_args: frozenset[str],
    defeats: frozenset[tuple[str, str]],
    *,
    attacks: frozenset[tuple[str, str]] | None = None,
    attackers_index: dict[str, frozenset[str]] | None = None,
) -> bool:
    """Check if s is admissible: conflict-free and defends all its members.

    Conflict-free is checked against attacks (Modgil & Prakken 2018 Def 14).
    Defense is checked against defeats (Dung 1995 Def 6).
    When attacks is None, defeats is used for both.
    """
    cf_relation = attacks if attacks is not None else defeats
    if not conflict_free(s, cf_relation):
        return False
    if attackers_index is None:
        attackers_index = _attackers_index(defeats)
    for a in s:
        if not defends(
            s,
            a,
            all_args,
            defeats,
            attackers_index=attackers_index,
        ):
            return False
    return True


def grounded_extension(framework: ArgumentationFramework) -> frozenset[str]:
    """Compute the unique grounded extension.

    This is pure Dung grounded semantics: the least fixed point of the
    characteristic function over ``defeats`` only. Attack metadata is
    ignored here.

    References:
        Dung 1995, Definition 20 + Theorem 25 (least fixed point).
    """
    current: frozenset[str] = frozenset()
    attackers_index = _attackers_index(framework.defeats)
    while True:
        next_current = characteristic_fn(
            current,
            framework.arguments,
            framework.defeats,
            attackers_index=attackers_index,
        )
        if next_current == current:
            return current
        current = next_current


def complete_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all complete extensions.

    A complete extension is a fixed point of F that is admissible.

    Reference: Dung 1995, Definition 10.
    """
    from argumentation.labelling import complete_labellings

    attackers_index = _attackers_index(framework.defeats)
    return [
        labelling.extension
        for labelling in complete_labellings(framework)
        if admissible(
            labelling.extension,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        )
    ]


def preferred_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all preferred extensions.

    A preferred extension is a maximal (w.r.t. set inclusion) admissible set,
    equivalently a maximal complete extension.

    Reference: Dung 1995, Definition 8.
    """
    completes = complete_extensions(framework)
    return [
        extension
        for extension in completes
        if not any(extension < other for other in completes)
    ]


def stable_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all stable extensions.

    A stable extension is conflict-free and defeats every argument not in it.
    When ``framework.attacks`` is present, conflict-freeness is checked against
    attacks while outsider coverage is checked against defeats.

    References:
        Dung 1995, Definition 12.
        Modgil & Prakken 2018, Definition 14.

    WARNING: Stable extensions may not exist.
    """
    from argumentation.labelling import stable_labellings

    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    return [
        labelling.extension
        for labelling in stable_labellings(framework)
        if conflict_free(labelling.extension, cf_relation)
    ]


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    return [
        frozenset(ordered[index] for index in range(len(ordered)) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    ]


def _range_maximal_extensions(
    candidates: list[frozenset[str]],
    defeats: frozenset[tuple[str, str]],
) -> list[frozenset[str]]:
    maximal: list[frozenset[str]] = []
    ranges = {
        candidate: range_of(candidate, defeats)
        for candidate in candidates
    }
    for candidate in candidates:
        candidate_range = ranges[candidate]
        if not any(candidate_range < other_range for other_range in ranges.values()):
            maximal.append(candidate)
    return maximal


def semi_stable_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all semi-stable extensions.

    A semi-stable extension is a complete extension whose range is maximal
    under set inclusion.

    Reference:
        Caminada 2011, Definition 2.3.
    """
    return _range_maximal_extensions(complete_extensions(framework), framework.defeats)


def stage_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all stage extensions by range-maximal conflict-free sets.

    Gaggl and Woltran 2013, p. 927: stage extensions are conflict-free sets
    with maximal range.
    """
    args = framework.arguments
    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    candidates: list[frozenset[str]] = []
    for size in range(len(args) + 1):
        for subset in combinations(sorted(args), size):
            s = frozenset(subset)
            if conflict_free(s, cf_relation):
                candidates.append(s)

    return _range_maximal_extensions(candidates, framework.defeats)


def eager_extension(framework: ArgumentationFramework) -> frozenset[str]:
    """Compute the unique eager extension.

    Caminada 2007's eager extension is the least committed semi-stable choice:
    if semi-stable is unique, return it; otherwise return the largest
    admissible subset of the intersection of all semi-stable extensions.
    """
    semi_stables = semi_stable_extensions(framework)
    if not semi_stables:
        return frozenset()
    intersection = frozenset.intersection(*semi_stables)
    attackers_index = _attackers_index(framework.defeats)
    candidates = [
        candidate
        for candidate in _all_subsets(intersection)
        if admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        )
    ]
    return max(candidates, key=lambda candidate: (len(candidate), tuple(sorted(candidate))))


def _strongly_connected_components(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> list[frozenset[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[frozenset[str]] = []
    outgoing: dict[str, list[str]] = {argument: [] for argument in arguments}
    for attacker, target in defeats:
        outgoing.setdefault(attacker, []).append(target)

    def connect(argument: str) -> None:
        nonlocal index
        indices[argument] = index
        lowlinks[argument] = index
        index += 1
        stack.append(argument)
        on_stack.add(argument)

        for target in sorted(outgoing.get(argument, [])):
            if target not in indices:
                connect(target)
                lowlinks[argument] = min(lowlinks[argument], lowlinks[target])
            elif target in on_stack:
                lowlinks[argument] = min(lowlinks[argument], indices[target])

        if lowlinks[argument] == indices[argument]:
            component: set[str] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == argument:
                    break
            components.append(frozenset(component))

    for argument in sorted(arguments):
        if argument not in indices:
            connect(argument)

    return sorted(components, key=lambda component: tuple(sorted(component)))


def _subframework(
    framework: ArgumentationFramework,
    arguments: frozenset[str],
) -> ArgumentationFramework:
    defeats = frozenset(
        (attacker, target)
        for attacker, target in framework.defeats
        if attacker in arguments and target in arguments
    )
    attacks = (
        None
        if framework.attacks is None
        else frozenset(
            (attacker, target)
            for attacker, target in framework.attacks
            if attacker in arguments and target in arguments
        )
    )
    return ArgumentationFramework(arguments=arguments, defeats=defeats, attacks=attacks)


def naive_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all maximal conflict-free sets."""
    candidates = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if conflict_free(candidate, framework.defeats)
    ]
    return [
        candidate
        for candidate in candidates
        if not any(candidate < other for other in candidates)
    ]


def _component_defeated(
    framework: ArgumentationFramework,
    candidate: frozenset[str],
    components: list[frozenset[str]],
) -> frozenset[str]:
    component_by_argument = {
        argument: component
        for component in components
        for argument in component
    }
    return frozenset(
        target
        for attacker, target in framework.defeats
        if attacker in candidate
        and component_by_argument[attacker] != component_by_argument[target]
    )


def _is_cf2_extension(
    framework: ArgumentationFramework,
    candidate: frozenset[str],
) -> bool:
    if not candidate <= framework.arguments:
        return False

    components = _strongly_connected_components(
        framework.arguments,
        framework.defeats,
    )
    if len(components) <= 1:
        return candidate in naive_extensions(framework)

    defeated = _component_defeated(framework, candidate, components)
    for component in components:
        sub_arguments = component - defeated
        subframework = _subframework(framework, sub_arguments)
        if not _is_cf2_extension(subframework, candidate & component):
            return False
    return True


def cf2_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute all CF2 extensions by recursive SCC decomposition.

    The base case for a single strongly connected component is the naive
    semantics. Solver-backed CF2 reasoning is a later workstream item.

    Reference:
        Gaggl and Woltran 2013, Definition 2.7.
    """
    return [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if _is_cf2_extension(framework, candidate)
    ]


def stage2_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Compute SCC-recursive stage2 extensions.

    Gaggl and Woltran 2013 give the SCC-recursive shape for CF2; stage2 uses
    the same component recursion with stage semantics as the single-SCC base.
    """
    return [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if _is_stage2_extension(framework, candidate)
    ]


def _is_stage2_extension(
    framework: ArgumentationFramework,
    candidate: frozenset[str],
) -> bool:
    if not candidate <= framework.arguments:
        return False

    components = _strongly_connected_components(
        framework.arguments,
        framework.defeats,
    )
    if len(components) <= 1:
        return candidate in stage_extensions(framework)

    defeated = _component_defeated(framework, candidate, components)
    for component in components:
        sub_arguments = component - defeated
        subframework = _subframework(framework, sub_arguments)
        if not _is_stage2_extension(subframework, candidate & component):
            return False
    return True


def indirect_attacks(framework: ArgumentationFramework) -> frozenset[tuple[str, str]]:
    """Return odd-length attack paths for prudent semantics.

    Coste-Marquis, Devred, and Marquis 2005, pp. 1-2 define the prudent
    indirect-conflict check over odd-length attack paths.
    """
    indirect: set[tuple[str, str]] = set()
    successors: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in framework.defeats:
        successors.setdefault(attacker, set()).add(target)

    for source in framework.arguments:
        stack = [(source, target, 1) for target in successors.get(source, set())]
        seen: set[tuple[str, int]] = set()
        while stack:
            origin, current, length = stack.pop()
            parity = length % 2
            if (current, parity) in seen:
                continue
            seen.add((current, parity))
            if length > 1 and parity == 1:
                indirect.add((origin, current))
            for target in successors.get(current, set()):
                stack.append((origin, target, length + 1))
    return frozenset(indirect)


def prudent_conflict_free(
    framework: ArgumentationFramework,
    candidate: frozenset[str],
) -> bool:
    """Return whether ``candidate`` has no prudent indirect conflict."""
    indirect = indirect_attacks(framework)
    return not any(
        attacker in candidate and target in candidate
        for attacker, target in indirect
    )


def prudent_admissible(
    framework: ArgumentationFramework,
    candidate: frozenset[str],
) -> bool:
    """Return prudent admissibility: admissible and no indirect conflicts."""
    return prudent_conflict_free(framework, candidate) and admissible(
        candidate,
        framework.arguments,
        framework.defeats,
        attacks=framework.attacks,
    )


def prudent_preferred_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    """Return inclusion-maximal prudent-admissible sets."""
    candidates = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if prudent_admissible(framework, candidate)
    ]
    return [
        candidate
        for candidate in candidates
        if not any(candidate < other for other in candidates)
    ]


def prudent_grounded_extension(framework: ArgumentationFramework) -> frozenset[str]:
    """Return the stationary prudent grounded extension.

    Coste-Marquis, Devred, and Marquis 2005, p. 3 define grounded prudent
    semantics by iterating the prudent characteristic function from empty.
    """
    current: frozenset[str] = frozenset()
    attackers_index = _attackers_index(framework.defeats)
    indirect = indirect_attacks(framework)
    while True:
        next_current = frozenset(
            argument
            for argument in framework.arguments
            if defends(
                current,
                argument,
                framework.arguments,
                framework.defeats,
                attackers_index=attackers_index,
            )
            and not any(
                attacker in current | frozenset({argument})
                and target in current | frozenset({argument})
                for attacker, target in indirect
            )
        )
        if next_current == current:
            return current
        current = next_current


def ideal_extension(framework: ArgumentationFramework) -> frozenset[str]:
    """Compute the unique maximal ideal extension.

    An ideal set is admissible and contained in every preferred extension. The
    ideal extension is the unique maximal ideal set.

    Reference:
        Dung, Mancarella, and Toni 2007, Definition 2.2 and Theorem 2.1.
    """
    preferred = preferred_extensions(framework)
    if not preferred:
        return frozenset()

    common = set(preferred[0])
    for extension in preferred[1:]:
        common.intersection_update(extension)

    attackers_index = _attackers_index(framework.defeats)
    candidates = [
        candidate
        for candidate in _all_subsets(frozenset(common))
        if admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        )
    ]
    maximal = [
        candidate
        for candidate in candidates
        if not any(candidate < other for other in candidates)
    ]
    if len(maximal) != 1:
        raise AssertionError(
            "ideal extension construction must have exactly one maximal "
            "admissible subset of the preferred-extension intersection"
        )
    return maximal[0]
