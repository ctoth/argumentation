"""z3 SAT-backed Dung extension computation.

Provides SAT-encoded alternatives to the brute-force extension
computation in dung.py. Results are identical but scale better
for large argumentation frameworks.

References:
    Dung, P.M. (1995). On the acceptability of arguments and its
    fundamental role in nonmonotonic reasoning, logic programming
    and n-person games. Artificial Intelligence, 77(2), 321-357.
"""

from __future__ import annotations

from typing import Any

from z3 import And, Bool, BoolVal, ModelRef, Not, Or, Solver, is_true

from argumentation.dung import ArgumentationFramework, _attackers_index
from argumentation.solver import (
    DEFAULT_Z3_TIMEOUT_MS,
    SolverSat,
    SolverUnknown,
    Z3UnknownError,
    solver_result_from_z3,
)


Z3BoolExpr = Any


def _new_solver() -> Solver:
    solver = Solver()
    solver.set(timeout=DEFAULT_Z3_TIMEOUT_MS)
    return solver


def _next_model(solver: Solver) -> ModelRef | None:
    result = solver_result_from_z3(solver)
    if isinstance(result, SolverSat):
        model = result.model
        if not isinstance(model, ModelRef):
            raise TypeError("Z3 SAT result did not include a model")
        return model
    if isinstance(result, SolverUnknown):
        raise Z3UnknownError(result)
    return None


def _make_vars(
    framework: ArgumentationFramework,
) -> dict[str, Z3BoolExpr]:
    """Create one z3 Bool variable per argument."""
    return {a: Bool(f"in_{a}") for a in sorted(framework.arguments)}


def _conflict_free_constraints(
    framework: ArgumentationFramework,
    v: dict[str, Z3BoolExpr],
) -> list[Z3BoolExpr]:
    """Conflict-free: no two args in the set attack each other.

    Per Modgil & Prakken 2018 Def 14, uses attacks (pre-preference)
    when available, falls back to defeats for pure Dung AFs.
    """
    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    return [Not(And(v[a], v[b])) for a, b in cf_relation]


def _extract_extension(
    v: dict[str, Z3BoolExpr],
    model: ModelRef,
) -> frozenset[str]:
    """Extract the extension (set of accepted args) from a z3 model."""
    return frozenset(
        a for a, var in v.items() if is_true(model.evaluate(var, model_completion=True))
    )


def _block_solution(
    v: dict[str, Z3BoolExpr],
    extension: frozenset[str],
) -> list[Z3BoolExpr]:
    """Add a blocking clause to exclude an already-found extension."""
    # The clause says: at least one variable must differ from this solution
    clause_parts = []
    for a, var in v.items():
        if a in extension:
            clause_parts.append(Not(var))
        else:
            clause_parts.append(var)
    return [Or(*clause_parts)] if clause_parts else []


def _or_vars(v: dict[str, Z3BoolExpr], arguments: tuple[str, ...]) -> Z3BoolExpr:
    """Build a disjunction over argument-membership variables."""
    if not arguments:
        return BoolVal(False)
    if len(arguments) == 1:
        return v[arguments[0]]
    return Or(*(v[arg] for arg in arguments))


def _defended_expressions(
    args: list[str],
    v: dict[str, Z3BoolExpr],
    attackers_index: dict[str, frozenset[str]],
) -> dict[str, Z3BoolExpr]:
    """Build one defended-expression per argument.

    defended(a) means: every attacker of ``a`` is itself attacked by some
    accepted argument. Unattacked arguments are always defended.
    """
    defender_exprs: dict[str, Z3BoolExpr] = {
        target: _or_vars(v, tuple(sorted(attackers)))
        for target, attackers in attackers_index.items()
    }
    defended: dict[str, Z3BoolExpr] = {}
    for arg in args:
        attackers = tuple(sorted(attackers_index.get(arg, frozenset())))
        if not attackers:
            defended[arg] = BoolVal(True)
            continue
        if any(attacker not in defender_exprs for attacker in attackers):
            defended[arg] = BoolVal(False)
            continue
        parts = tuple(defender_exprs[attacker] for attacker in attackers)
        if len(parts) == 1:
            defended[arg] = parts[0]
        else:
            defended[arg] = And(*parts)
    return defended


# ── Stable extensions ──────────────────────────────────────────────


def z3_stable_extensions(
    framework: ArgumentationFramework,
) -> list[frozenset[str]]:
    """Compute all stable extensions using z3 SAT encoding.

    A stable extension S is conflict-free and every argument outside S
    is defeated by some member of S.
    """
    if not framework.arguments:
        return [frozenset()]

    v = _make_vars(framework)
    args = sorted(framework.arguments)
    defeats = framework.defeats
    attackers_index = _attackers_index(defeats)

    base_constraints = []

    # Conflict-free
    base_constraints.extend(_conflict_free_constraints(framework, v))

    # Every outsider must be attacked by some member of S
    for a in args:
        atks = tuple(sorted(attackers_index.get(a, frozenset())))
        if atks:
            # If a is out, some attacker must be in
            base_constraints.append(
                Or(v[a], *(v[b] for b in atks))
            )
        else:
            # No attackers: a must be in (undefeated)
            base_constraints.append(v[a])

    # Enumerate all solutions
    results: list[frozenset[str]] = []
    solver = _new_solver()
    solver.add(*base_constraints)

    while (model := _next_model(solver)) is not None:
        ext = _extract_extension(v, model)
        results.append(ext)
        solver.add(*_block_solution(v, ext))

    return results


# ── Complete extensions ────────────────────────────────────────────


def z3_complete_extensions(
    framework: ArgumentationFramework,
) -> list[frozenset[str]]:
    """Compute all complete extensions using z3 SAT encoding.

    A complete extension S is admissible and a fixed point of F:
    S = {a | S defends a}.
    """
    if not framework.arguments:
        return [frozenset()]

    v = _make_vars(framework)
    args = sorted(framework.arguments)
    defeats = framework.defeats
    attackers_index = _attackers_index(defeats)
    defended_exprs = _defended_expressions(args, v, attackers_index)

    base_constraints = []

    # Conflict-free
    base_constraints.extend(_conflict_free_constraints(framework, v))

    # Completeness can be expressed directly as:
    #   v[a] <-> defended(a)
    # This subsumes both admissibility-for-members and "every defended
    # argument must be in" while keeping the encoding compact.
    for a in args:
        base_constraints.append(v[a] == defended_exprs[a])

    # Enumerate
    results: list[frozenset[str]] = []
    solver = _new_solver()
    solver.add(*base_constraints)

    while (model := _next_model(solver)) is not None:
        ext = _extract_extension(v, model)
        results.append(ext)
        solver.add(*_block_solution(v, ext))

    return results


# ── Preferred extensions (enumerate and filter) ───────────────────────────────────


def z3_preferred_extensions(
    framework: ArgumentationFramework,
) -> list[frozenset[str]]:
    """Compute all preferred extensions by filtering maximal complete extensions.

    Preferred extensions are maximal complete extensions.
    1. Find complete extensions
    2. Filter to those that are maximal (no strictly larger complete ext)
    """
    completes = z3_complete_extensions(framework)
    maximal: list[frozenset[str]] = []
    for ext in completes:
        if not any(ext < other for other in completes):
            maximal.append(ext)
    return maximal


# ── Acceptance queries ─────────────────────────────────────────────


def credulously_accepted(
    framework: ArgumentationFramework,
    arg: str,
    *,
    semantics: str = "preferred",
) -> bool:
    """Check if arg is credulously accepted (in at least one extension)."""
    extensions = _extensions_for_semantics(framework, semantics)
    return any(arg in ext for ext in extensions)


def skeptically_accepted(
    framework: ArgumentationFramework,
    arg: str,
    *,
    semantics: str = "preferred",
) -> bool:
    """Check if arg is skeptically accepted (in all extensions).

    If there are no extensions (e.g. no stable extension exists),
    returns False.
    """
    extensions = _extensions_for_semantics(framework, semantics)
    if not extensions:
        return False
    return all(arg in ext for ext in extensions)


def _extensions_for_semantics(
    framework: ArgumentationFramework,
    semantics: str,
) -> list[frozenset[str]]:
    """Dispatch to the appropriate z3 extension function."""
    if semantics == "stable":
        return z3_stable_extensions(framework)
    elif semantics == "complete":
        return z3_complete_extensions(framework)
    elif semantics == "preferred":
        return z3_preferred_extensions(framework)
    else:
        msg = f"Unknown semantics: {semantics}"
        raise ValueError(msg)
