"""Task-directed SAT solving for flat ABA stable semantics."""

from __future__ import annotations

from argumentation.aba import ABAFramework, AssumptionSet
from argumentation.aspic import Literal


def support_extensions(
    framework: ABAFramework,
    semantics: str,
) -> tuple[AssumptionSet, ...]:
    """Enumerate ABA extensions using precomputed derivation support masks."""
    state = _SupportState.from_framework(framework)
    if semantics == "stable":
        masks = [
            mask
            for mask in range(1 << len(state.assumptions))
            if state.stable(mask)
        ]
    elif semantics == "complete":
        masks = [
            mask
            for mask in range(1 << len(state.assumptions))
            if state.complete(mask)
        ]
    elif semantics == "preferred":
        admissible = [
            mask
            for mask in range(1 << len(state.assumptions))
            if state.admissible(mask)
        ]
        masks = [
            mask
            for mask in admissible
            if not any(mask != other and (mask | other) == other for other in admissible)
        ]
    else:
        raise ValueError(f"unsupported ABA support semantics: {semantics}")
    return tuple(
        sorted(
            (state.extension(mask) for mask in masks),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )


def support_acceptance(
    framework: ABAFramework,
    *,
    semantics: str,
    task: str,
    query: Literal,
) -> tuple[bool, AssumptionSet | None]:
    """Return a decision and witness/counterexample for exact ABA support solving."""
    state = _SupportState.from_framework(framework)
    extensions = support_extensions(framework, semantics)
    if task == "credulous":
        witness = next(
            (extension for extension in extensions if state.derives_extension(extension, query)),
            None,
        )
        return witness is not None, witness
    if task == "skeptical":
        counterexample = next(
            (
                extension
                for extension in extensions
                if not state.derives_extension(extension, query)
            ),
            None,
        )
        return counterexample is None, counterexample
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def sat_support_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
) -> AssumptionSet | None:
    """Return one complete/preferred ABA extension using support-aware SAT."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
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
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    if semantics == "complete":
        _add_complete_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )

    if semantics == "complete":
        if solver.check() != z3.sat:
            return None
        return _model_extension(z3, solver, variables)

    if solver.check() != z3.sat:
        return None
    current = _model_extension(z3, solver, variables)
    while True:
        outside = framework.assumptions - current
        if not outside:
            return current
        solver.push()
        try:
            for assumption in sorted(current, key=repr):
                solver.add(variables[assumption])
            solver.add(z3.Or(*(variables[assumption] for assumption in sorted(outside, key=repr))))
            if solver.check() != z3.sat:
                return current
            larger = _model_extension(z3, solver, variables)
        finally:
            solver.pop()
        if not current < larger:
            raise RuntimeError("ABA preferred SAT growth did not produce a strict superset")
        current = larger


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


class _SupportState:
    def __init__(
        self,
        framework: ABAFramework,
        assumptions: tuple[Literal, ...],
        supports: dict[Literal, frozenset[int]],
    ) -> None:
        self.framework = framework
        self.assumptions = assumptions
        self.index = {assumption: index for index, assumption in enumerate(assumptions)}
        self.supports = supports
        self.attack_supports = {
            assumption: supports.get(framework.contrary[assumption], frozenset())
            for assumption in assumptions
        }

    @classmethod
    def from_framework(cls, framework: ABAFramework) -> _SupportState:
        assumptions = tuple(sorted(framework.assumptions, key=repr))
        index = {assumption: offset for offset, assumption in enumerate(assumptions)}
        supports = {
            literal: frozenset(
                _support_mask(support, index)
                for support in values
            )
            for literal, values in _minimal_supports(framework).items()
        }
        return cls(framework, assumptions, supports)

    def extension(self, mask: int) -> AssumptionSet:
        return frozenset(
            assumption
            for index, assumption in enumerate(self.assumptions)
            if mask & (1 << index)
        )

    def derives_extension(self, extension: AssumptionSet, literal: Literal) -> bool:
        return self.derives(_support_mask(extension, self.index), literal)

    def derives(self, mask: int, literal: Literal) -> bool:
        return any((support & mask) == support for support in self.supports.get(literal, ()))

    def attacks(self, mask: int, assumption: Literal) -> bool:
        return any(
            (support & mask) == support
            for support in self.attack_supports.get(assumption, ())
        )

    def conflict_free(self, mask: int) -> bool:
        return not any(
            mask & (1 << index) and self.attacks(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def defends(self, mask: int, assumption: Literal) -> bool:
        for attack_support in self.attack_supports.get(assumption, ()):
            if attack_support == 0:
                return False
            if not any(
                attack_support & (1 << index) and self.attacks(mask, target)
                for index, target in enumerate(self.assumptions)
            ):
                return False
        return True

    def admissible(self, mask: int) -> bool:
        return self.conflict_free(mask) and all(
            not (mask & (1 << index)) or self.defends(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def complete(self, mask: int) -> bool:
        return self.admissible(mask) and all(
            bool(mask & (1 << index)) == self.defends(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def stable(self, mask: int) -> bool:
        return self.conflict_free(mask) and all(
            bool(mask & (1 << index)) or self.attacks(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )


def _support_mask(
    support: AssumptionSet,
    index: dict[Literal, int],
) -> int:
    mask = 0
    for assumption in support:
        mask |= 1 << index[assumption]
    return mask


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


def _add_admissible_constraints(z3, solver, framework, variables, supports) -> None:
    for assumption in sorted(framework.assumptions, key=repr):
        attack_supports = supports.get(framework.contrary[assumption], frozenset())
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(_any_support_selected(z3, variables, attack_supports)),
            )
        )
        solver.add(
            z3.Implies(
                variables[assumption],
                _defended_expr(z3, framework, variables, supports, assumption),
            )
        )


def _add_complete_constraints(z3, solver, framework, variables, supports) -> None:
    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(
            z3.Implies(
                _defended_expr(z3, framework, variables, supports, assumption),
                variables[assumption],
            )
        )


def _defended_expr(z3, framework, variables, supports, assumption):
    attack_supports = supports.get(framework.contrary[assumption], frozenset())
    defenses = []
    for attack_support in sorted(
        attack_supports,
        key=lambda item: (len(item), tuple(sorted(map(repr, item)))),
    ):
        if not attack_support:
            return z3.BoolVal(False)
        defenses.append(
            z3.Or(
                *(
                    _any_support_selected(
                        z3,
                        variables,
                        supports.get(framework.contrary[target], frozenset()),
                    )
                    for target in sorted(attack_support, key=repr)
                )
            )
        )
    return z3.And(*defenses) if defenses else z3.BoolVal(True)


def _add_derived_constraints(
    z3,
    solver,
    variables,
    supports,
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
) -> None:
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


def _model_extension(z3, solver, variables) -> AssumptionSet:
    model = solver.model()
    return frozenset(
        assumption
        for assumption, variable in variables.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def _literal_key(literal: Literal) -> str:
    text = repr(literal)
    return "".join(character if character.isalnum() else "_" for character in text)


def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("ABA stable SAT solving requires z3-solver") from exc
    return z3


__all__ = [
    "sat_stable_extension",
    "sat_support_extension",
    "support_acceptance",
    "support_extensions",
]
