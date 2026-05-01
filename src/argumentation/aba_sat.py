"""Task-directed SAT solving for flat ABA stable semantics."""

from __future__ import annotations

from argumentation.aba import ABAFramework, AssumptionSet
from argumentation.aspic import Literal


def sat_stable_extension(
    framework: ABAFramework,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
) -> AssumptionSet | None:
    """Return one stable assumption set satisfying optional query constraints."""
    if require_derived is not None and require_derived not in framework.language:
        raise ValueError(f"required literal is not in framework language: {require_derived!r}")
    if require_not_derived is not None and require_not_derived not in framework.language:
        raise ValueError(
            f"excluded literal is not in framework language: {require_not_derived!r}"
        )

    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    supports = _minimal_supports(framework)

    for assumption in sorted(framework.assumptions, key=repr):
        attack_supports = supports.get(framework.contrary[assumption], frozenset())
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(_any_support_selected(z3, variables, attack_supports)),
            )
        )
        solver.add(
            z3.Or(
                variables[assumption],
                _any_support_selected(z3, variables, attack_supports),
            )
        )

    if require_derived is not None:
        solver.add(_any_support_selected(z3, variables, supports.get(require_derived, frozenset())))
    if require_not_derived is not None:
        solver.add(
            z3.Not(
                _any_support_selected(
                    z3,
                    variables,
                    supports.get(require_not_derived, frozenset()),
                )
            )
        )

    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return frozenset(
        assumption
        for assumption, variable in variables.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def _minimal_supports(framework: ABAFramework) -> dict[Literal, frozenset[AssumptionSet]]:
    supports: dict[Literal, set[AssumptionSet]] = {
        literal: set() for literal in framework.language
    }
    for assumption in framework.assumptions:
        supports[assumption].add(frozenset({assumption}))

    changed = True
    while changed:
        changed = False
        for rule in sorted(framework.rules, key=repr):
            consequent_supports = _combine_supports(
                tuple(supports[antecedent] for antecedent in rule.antecedents)
            )
            for support in consequent_supports:
                if _add_minimal_support(supports[rule.consequent], support):
                    changed = True

    return {
        literal: frozenset(values)
        for literal, values in supports.items()
    }


def _combine_supports(
    support_sets: tuple[set[AssumptionSet], ...],
) -> set[AssumptionSet]:
    if not support_sets:
        return {frozenset()}
    combined: set[AssumptionSet] = {frozenset()}
    for choices in support_sets:
        if not choices:
            return set()
        combined = {
            frozenset(left | right)
            for left in combined
            for right in choices
        }
    return _minimal_set(combined)


def _add_minimal_support(
    supports: set[AssumptionSet],
    candidate: AssumptionSet,
) -> bool:
    if any(existing <= candidate for existing in supports):
        return False
    supersets = {existing for existing in supports if candidate < existing}
    supports.difference_update(supersets)
    supports.add(candidate)
    return True


def _minimal_set(supports: set[AssumptionSet]) -> set[AssumptionSet]:
    minimal: set[AssumptionSet] = set()
    for support in sorted(supports, key=lambda item: (len(item), tuple(sorted(map(repr, item))))):
        _add_minimal_support(minimal, support)
    return minimal


def _any_support_selected(z3, variables, supports: frozenset[AssumptionSet]):
    if not supports:
        return z3.BoolVal(False)
    return z3.Or(
        *(
            _support_selected(z3, variables, support)
            for support in sorted(supports, key=lambda item: (len(item), tuple(sorted(map(repr, item)))))
        )
    )


def _support_selected(z3, variables, support: AssumptionSet):
    if not support:
        return z3.BoolVal(True)
    return z3.And(*(variables[assumption] for assumption in sorted(support, key=repr)))


def _literal_key(literal: Literal) -> str:
    text = repr(literal)
    return "".join(character if character.isalnum() else "_" for character in text)


def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("ABA stable SAT solving requires z3-solver") from exc
    return z3


__all__ = ["sat_stable_extension"]
