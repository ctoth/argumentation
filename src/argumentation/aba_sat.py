"""Task-directed SAT solving for flat ABA stable semantics."""

from __future__ import annotations

from dataclasses import dataclass

from argumentation.aba import ABAFramework, AssumptionSet, derives
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


@dataclass(frozen=True)
class AssumptionKernel:
    """Reusable assumption-level solver state for flat ABA single-extension tasks."""

    framework: ABAFramework
    assumptions: tuple[Literal, ...]
    literals: tuple[Literal, ...]
    assumption_ids: dict[Literal, str]
    literal_ids: dict[Literal, str]

    @classmethod
    def from_framework(cls, framework: ABAFramework) -> AssumptionKernel:
        assumptions = tuple(sorted(framework.assumptions, key=repr))
        literals = tuple(sorted(framework.language, key=repr))
        return cls(
            framework=framework,
            assumptions=assumptions,
            literals=literals,
            assumption_ids={
                assumption: f"a{index}"
                for index, assumption in enumerate(assumptions)
            },
            literal_ids={
                literal: f"l{index}"
                for index, literal in enumerate(literals)
            },
        )

    def stable_extension(
        self,
        *,
        require_derived: Literal | None = None,
        require_not_derived: Literal | None = None,
    ) -> AssumptionSet | None:
        if require_derived is not None and require_derived not in self.framework.language:
            raise ValueError(f"required literal is not in framework language: {require_derived!r}")
        if require_not_derived is not None and require_not_derived not in self.framework.language:
            raise ValueError(
                f"excluded literal is not in framework language: {require_not_derived!r}"
            )
        try:
            import clingo  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("ABA assumption kernel requires clingo") from exc

        selected: list[str] = []

        def collect_model(model) -> None:
            selected.clear()
            selected.extend(str(symbol.arguments[0]) for symbol in model.symbols(shown=True))

        program = [*self._asp_facts(), *self._stable_program()]
        if require_derived is not None:
            program.append(f":- not derived({self.literal_ids[require_derived]}).")
        if require_not_derived is not None:
            program.append(f":- derived({self.literal_ids[require_not_derived]}).")

        control = clingo.Control(["--models=1"])
        control.add("base", [], "\n".join(program))
        control.ground([("base", [])])
        result = control.solve(on_model=collect_model)
        if not result.satisfiable:
            return None
        selected_ids = frozenset(selected)
        return frozenset(
            assumption
            for assumption, assumption_id in self.assumption_ids.items()
            if assumption_id in selected_ids
        )

    def preferred_extension(self) -> AssumptionSet | None:
        stable = self.stable_extension()
        if stable is not None:
            return stable
        return _sat_preferred_cegar_extension(self.framework)

    def attacks(self, extension: AssumptionSet, assumption: Literal) -> bool:
        if assumption not in self.framework.assumptions:
            raise ValueError(f"unknown assumption: {assumption!r}")
        return self.framework.contrary[assumption] in self.closure(extension)

    def closure(self, extension: AssumptionSet) -> frozenset[Literal]:
        derived = set(extension)
        changed = True
        while changed:
            changed = False
            for rule in sorted(self.framework.rules, key=repr):
                if rule.consequent in derived:
                    continue
                if all(antecedent in derived for antecedent in rule.antecedents):
                    derived.add(rule.consequent)
                    changed = True
        return frozenset(derived)

    def _asp_facts(self) -> tuple[str, ...]:
        facts: list[str] = []
        for assumption in self.assumptions:
            assumption_id = self.assumption_ids[assumption]
            facts.append(f"assumption({assumption_id}).")
            facts.append(
                f"assumption_literal({assumption_id},{self.literal_ids[assumption]})."
            )
            facts.append(
                f"contrary({assumption_id},{self.literal_ids[self.framework.contrary[assumption]]})."
            )
        for index, rule in enumerate(sorted(self.framework.rules, key=repr)):
            rule_id = f"r{index}"
            facts.append(f"rule({rule_id}).")
            facts.append(f"head({rule_id},{self.literal_ids[rule.consequent]}).")
            facts.append(f"body_count({rule_id},{len(rule.antecedents)}).")
            for antecedent in rule.antecedents:
                facts.append(f"body({rule_id},{self.literal_ids[antecedent]}).")
        return tuple(facts)

    def _stable_program(self) -> tuple[str, ...]:
        constraints = [
            "{ selected(A) } :- assumption(A).",
            "derived(L) :- selected(A), assumption_literal(A,L).",
            "derived(H) :- rule(R), head(R,H), body_count(R,N), N = #count { B : body(R,B), derived(B) }.",
            ":- selected(A), contrary(A,C), derived(C).",
            ":- assumption(A), not selected(A), contrary(A,C), not derived(C).",
        ]
        return tuple((*constraints, "#show selected/1."))


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


def sat_support_acceptance(
    framework: ABAFramework,
    *,
    semantics: str,
    task: str,
    query: Literal,
) -> tuple[bool, AssumptionSet | None]:
    """Return an ABA acceptance decision using support-aware SAT witnesses."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
    if task == "credulous":
        witness = sat_support_extension(
            framework,
            semantics,
            require_derived=query,
        )
        return witness is not None, witness
    if task == "skeptical":
        if semantics == "preferred":
            counterexample = _sat_preferred_counterexample_not_deriving(framework, query)
            return counterexample is None, counterexample
        counterexample = sat_support_extension(
            framework,
            semantics,
            require_not_derived=query,
        )
        return counterexample is None, counterexample
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def sat_support_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
    require_assumptions: AssumptionSet = frozenset(),
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
    if (
        semantics == "preferred"
        and require_derived is None
        and require_not_derived is None
        and not require_assumptions
    ):
        stable = AssumptionKernel.from_framework(framework).stable_extension()
        if stable is not None:
            return stable
    if semantics == "preferred" and (
        require_derived is not None or require_not_derived is not None
    ):
        return _sat_preferred_extension_satisfying(
            framework,
            require_derived=require_derived,
            require_not_derived=require_not_derived,
            require_assumptions=require_assumptions,
        )
    if semantics == "preferred":
        return _sat_preferred_cegar_extension(
            framework,
            require_assumptions=require_assumptions,
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
    for assumption in sorted(require_assumptions, key=repr):
        solver.add(variables[assumption])

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


def _sat_preferred_extension_satisfying(
    framework: ABAFramework,
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
    require_assumptions: AssumptionSet,
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )
    for assumption in sorted(require_assumptions, key=repr):
        solver.add(variables[assumption])

    while solver.check() == z3.sat:
        seed = _model_extension(z3, solver, variables)
        preferred = sat_support_extension(
            framework,
            "preferred",
            require_assumptions=seed,
        )
        if preferred is None:
            return None
        if _extension_satisfies_constraints(
            preferred,
            supports,
            require_derived=require_derived,
            require_not_derived=require_not_derived,
        ):
            return preferred
        outside = framework.assumptions - preferred
        if outside:
            solver.add(z3.Or(*(variables[assumption] for assumption in sorted(outside, key=repr))))
        else:
            solver.add(z3.BoolVal(False))
    return None


def _sat_preferred_cegar_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> AssumptionSet | None:
    current = _sat_admissible_cegar_extension(
        framework,
        require_assumptions=require_assumptions,
    )
    if current is None:
        return None
    while True:
        outside = framework.assumptions - current
        if not outside:
            return current
        larger = _sat_admissible_cegar_extension(
            framework,
            require_assumptions=current,
            require_any_assumption=outside,
        )
        if larger is None:
            return current
        if not current < larger:
            raise RuntimeError("ABA preferred CEGAR growth did not produce a strict superset")
        current = larger


def _sat_admissible_cegar_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
    require_any_assumption: AssumptionSet = frozenset(),
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    derived = _add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(derived[framework.contrary[assumption]]),
            )
        )
    for assumption in sorted(require_assumptions, key=repr):
        solver.add(variables[assumption])
    if require_any_assumption:
        solver.add(z3.Or(*(variables[assumption] for assumption in sorted(require_any_assumption, key=repr))))

    while solver.check() == z3.sat:
        model = solver.model()
        candidate = frozenset(
            assumption
            for assumption, variable in variables.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )
        closure = frozenset(
            literal
            for literal, variable in derived.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )
        counterexample = _defense_counterexample(framework, candidate, closure)
        if counterexample is None:
            return candidate
        target, attack_support = counterexample
        if not attack_support:
            solver.add(z3.Not(variables[target]))
            continue
        solver.add(
            z3.Or(
                z3.Not(variables[target]),
                *(
                    derived[framework.contrary[assumption]]
                    for assumption in sorted(attack_support, key=repr)
                ),
            )
        )
    return None


def _defense_counterexample(
    framework: ABAFramework,
    candidate: AssumptionSet,
    closure: frozenset[Literal],
) -> tuple[Literal, AssumptionSet] | None:
    counterattacked = frozenset(
        assumption
        for assumption in framework.assumptions
        if framework.contrary[assumption] in closure
    )
    for target in sorted(candidate, key=repr):
        attack_support = _attacker_support_not_counterattacked(
            framework,
            target,
            counterattacked=counterattacked,
        )
        if attack_support is not None:
            return target, attack_support
    return None


def _attacker_support_not_counterattacked(
    framework: ABAFramework,
    target: Literal,
    *,
    counterattacked: AssumptionSet,
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"attacker_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    derived = _add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(counterattacked, key=repr):
        solver.add(z3.Not(variables[assumption]))
    solver.add(derived[framework.contrary[target]])
    if solver.check() != z3.sat:
        return None
    model = solver.model()
    support = frozenset(
        assumption
        for assumption, variable in variables.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )
    return _shrink_attack_support(framework, support, framework.contrary[target])


def _shrink_attack_support(
    framework: ABAFramework,
    support: AssumptionSet,
    conclusion: Literal,
) -> AssumptionSet:
    current = set(support)
    for assumption in sorted(support, key=repr):
        reduced = frozenset(current - {assumption})
        if derives(framework, reduced, conclusion):
            current.remove(assumption)
    return frozenset(current)


def sat_stable_extension(
    framework: ABAFramework,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
) -> AssumptionSet | None:
    """Return one stable assumption set satisfying optional query constraints."""
    return AssumptionKernel.from_framework(framework).stable_extension(
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )


def _add_ranked_closure_constraints(z3, solver, framework, variables):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    derived = {
        literal: z3.Bool(f"der_{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.Int(f"rank_{_literal_key(literal)}")
        for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)

    for literal in literals:
        solver.add(ranks[literal] >= 0, ranks[literal] <= rank_bound)

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == 0))

    for rule in sorted(framework.rules, key=repr):
        antecedents = tuple(rule.antecedents)
        if not antecedents:
            solver.add(derived[rule.consequent])
        else:
            solver.add(
                z3.Implies(
                    z3.And(*(derived[antecedent] for antecedent in antecedents)),
                    derived[rule.consequent],
                )
            )

    for literal in literals:
        if literal in framework.assumptions:
            continue
        support_terms = []
        for rule in rules_by_consequent[literal]:
            antecedents = tuple(rule.antecedents)
            if not antecedents:
                support_terms.append(z3.BoolVal(True))
                continue
            support_terms.append(
                z3.And(
                    *(
                        z3.And(
                            derived[antecedent],
                            ranks[antecedent] < ranks[literal],
                        )
                        for antecedent in antecedents
                    )
                )
            )
        solver.add(
            z3.Implies(
                derived[literal],
                z3.Or(*support_terms) if support_terms else z3.BoolVal(False),
            )
        )
    return derived


def _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    rank_bits = max(1, (rank_bound + 1).bit_length())
    rank_bound_value = z3.BitVecVal(rank_bound, rank_bits)
    derived = {
        literal: z3.Bool(f"der_{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.BitVec(f"rank_bv_{_literal_key(literal)}", rank_bits)
        for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)

    for literal in literals:
        solver.add(z3.ULE(ranks[literal], rank_bound_value))

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == z3.BitVecVal(0, rank_bits)))

    for rule in sorted(framework.rules, key=repr):
        antecedents = tuple(rule.antecedents)
        if not antecedents:
            solver.add(derived[rule.consequent])
        else:
            solver.add(
                z3.Implies(
                    z3.And(*(derived[antecedent] for antecedent in antecedents)),
                    derived[rule.consequent],
                )
            )

    for literal in literals:
        if literal in framework.assumptions:
            continue
        support_terms = []
        for rule in rules_by_consequent[literal]:
            antecedents = tuple(rule.antecedents)
            if not antecedents:
                support_terms.append(z3.BoolVal(True))
                continue
            support_terms.append(
                z3.And(
                    *(
                        z3.And(
                            derived[antecedent],
                            z3.ULT(ranks[antecedent], ranks[literal]),
                        )
                        for antecedent in antecedents
                    )
                )
            )
        solver.add(
            z3.Implies(
                derived[literal],
                z3.Or(*support_terms) if support_terms else z3.BoolVal(False),
            )
        )
    return derived


def _rules_by_consequent(framework: ABAFramework, literals: tuple[Literal, ...]):
    grouped: dict[Literal, list[Rule]] = {literal: [] for literal in literals}
    for rule in sorted(framework.rules, key=repr):
        grouped[rule.consequent].append(rule)
    return {
        literal: tuple(rules)
        for literal, rules in grouped.items()
    }


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


def _sat_preferred_counterexample_not_deriving(
    framework: ABAFramework,
    query: Literal,
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=None,
        require_not_derived=query,
    )

    while solver.check() == z3.sat:
        seed = _model_extension(z3, solver, variables)
        preferred = sat_support_extension(
            framework,
            "preferred",
            require_assumptions=seed,
        )
        if preferred is None:
            return None
        if not _extension_derives(preferred, query, supports):
            return preferred
        outside = framework.assumptions - preferred
        if outside:
            solver.add(z3.Or(*(variables[assumption] for assumption in sorted(outside, key=repr))))
        else:
            solver.add(z3.BoolVal(False))
    return None


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


def _extension_derives(
    extension: AssumptionSet,
    literal: Literal,
    supports: dict[Literal, frozenset[AssumptionSet]],
) -> bool:
    return any(support <= extension for support in supports.get(literal, frozenset()))


def _extension_satisfies_constraints(
    extension: AssumptionSet,
    supports: dict[Literal, frozenset[AssumptionSet]],
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
) -> bool:
    if require_derived is not None and not _extension_derives(extension, require_derived, supports):
        return False
    if require_not_derived is not None and _extension_derives(extension, require_not_derived, supports):
        return False
    return True


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
    "AssumptionKernel",
    "sat_stable_extension",
    "sat_support_acceptance",
    "sat_support_extension",
    "support_acceptance",
    "support_extensions",
]
