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


_AUTO_BACKEND_MAX_ARGS = 12


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
    s: frozenset[str] = frozenset()
    attackers_index = _attackers_index(framework.defeats)
    while True:
        next_s = characteristic_fn(
            s,
            framework.arguments,
            framework.defeats,
            attackers_index=attackers_index,
        )
        if next_s == s:
            break
        s = next_s

    return s

def _resolve_backend(
    framework: ArgumentationFramework,
    backend: str,
) -> str:
    """Resolve an extension-computation backend.

    `auto` prefers brute force for very small frameworks where Python-level
    Z3 expression construction can cost more than simple subset enumeration.
    """
    if backend == "auto":
        if len(framework.arguments) <= _AUTO_BACKEND_MAX_ARGS:
            return "brute"
        return "z3"
    if backend in {"brute", "z3"}:
        return backend
    raise ValueError(f"Unknown backend: {backend}")


def complete_extensions(
    framework: ArgumentationFramework, *, backend: str = "auto"
) -> list[frozenset[str]]:
    """Compute all complete extensions.

    A complete extension is a fixed point of F that is admissible.

    Reference: Dung 1995, Definition 10.
    """
    backend = _resolve_backend(framework, backend)
    if backend == "z3":
        from argumentation.dung_z3 import z3_complete_extensions

        return z3_complete_extensions(framework)
    args = framework.arguments
    defeats = framework.defeats
    attacks = framework.attacks
    attackers_index = _attackers_index(defeats)
    results: list[frozenset[str]] = []

    for size in range(len(args) + 1):
        for subset in combinations(sorted(args), size):
            s = frozenset(subset)
            if characteristic_fn(
                s,
                args,
                defeats,
                attackers_index=attackers_index,
            ) == s and admissible(
                s,
                args,
                defeats,
                attacks=attacks,
                attackers_index=attackers_index,
            ):
                results.append(s)

    return results


def preferred_extensions(
    framework: ArgumentationFramework, *, backend: str = "auto"
) -> list[frozenset[str]]:
    """Compute all preferred extensions.

    A preferred extension is a maximal (w.r.t. set inclusion) admissible set,
    equivalently a maximal complete extension.

    Reference: Dung 1995, Definition 8.
    """
    backend = _resolve_backend(framework, backend)
    if backend == "z3":
        from argumentation.dung_z3 import z3_preferred_extensions

        return z3_preferred_extensions(framework)
    completes = complete_extensions(framework, backend=backend)
    maximal: list[frozenset[str]] = []
    for ext in completes:
        if not any(ext < other for other in completes):
            maximal.append(ext)
    return maximal


def stable_extensions(
    framework: ArgumentationFramework, *, backend: str = "auto"
) -> list[frozenset[str]]:
    """Compute all stable extensions.

    A stable extension is conflict-free and defeats every argument not in it.

    Reference: Dung 1995, Definition 12.
    WARNING: Stable extensions may not exist.
    """
    backend = _resolve_backend(framework, backend)
    if backend == "z3":
        from argumentation.dung_z3 import z3_stable_extensions

        return z3_stable_extensions(framework)
    args = framework.arguments
    defeats = framework.defeats
    cf_relation = framework.attacks if framework.attacks is not None else defeats
    results: list[frozenset[str]] = []

    for size in range(len(args) + 1):
        for subset in combinations(sorted(args), size):
            s = frozenset(subset)
            if not conflict_free(s, cf_relation):
                continue
            outsiders = args - s
            if all(any((d, out) in defeats for d in s) for out in outsiders):
                results.append(s)

    return results
