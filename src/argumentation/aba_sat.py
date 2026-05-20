"""Task-directed SAT solving for flat ABA stable and support semantics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import importlib
from typing import Any

from argumentation.aba import ABAFramework, AssumptionSet, derives
from argumentation.aba_route_policy import (
    SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
    native_cnf_prefsat_dense_shape,
)
from argumentation.aspic import Literal, Rule


@dataclass(frozen=True)
class RealPrefSatResult:
    extension: AssumptionSet
    prefsat_in: dict[Literal, bool]
    prefsat_out: dict[Literal, bool]
    prefsat_undec: dict[Literal, bool]
    telemetry: dict[str, int]
    progress_events: tuple[dict[str, int], ...]
    route_metadata: dict[str, Any]


@dataclass(frozen=True)
class NativeSparseNarrowSatResult:
    extension: AssumptionSet | None
    telemetry: dict[str, int]
    route_metadata: dict[str, Any]


def _aba_simplification(framework: ABAFramework, semantics: str):
    """Lazily import to avoid a module import cycle (aba_preprocessing -> aba_sat)."""
    from argumentation.aba_preprocessing import simplify_aba

    return simplify_aba(framework, semantics=semantics)


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


def real_prefsat_attack_edge_count(framework: ABAFramework) -> int:
    """Count singleton-closure attack edges without enumerating supports."""
    count = 0
    for source in framework.assumptions:
        closure = _prefsat_closure(framework, frozenset({source}))
        count += sum(
            1
            for target in framework.assumptions
            if framework.contrary[target] in closure
        )
    return count


def real_prefsat_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> RealPrefSatResult:
    solver = _RealPrefSatSolver(framework)
    extension = solver.preferred_extension(require_assumptions=require_assumptions)
    return solver.result(extension)


def native_cnf_prefsat_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> RealPrefSatResult:
    solver = _NativeCnfPrefSatSolver(framework)
    extension = solver.preferred_extension(require_assumptions=require_assumptions)
    return solver.result(extension)


def native_sparse_narrow_sat_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> NativeSparseNarrowSatResult:
    if semantics == "preferred":
        result = native_cnf_prefsat_extension(
            framework,
            require_assumptions=require_assumptions,
        )
        telemetry = _native_sparse_narrow_telemetry(result.telemetry)
        return NativeSparseNarrowSatResult(
            extension=result.extension,
            telemetry=telemetry,
            route_metadata=_native_sparse_narrow_route_metadata("preferred", telemetry),
        )
    if semantics == "stable":
        solver = _NativeSparseNarrowStableSolver(framework)
        extension = solver.stable_extension(require_assumptions=require_assumptions)
        return NativeSparseNarrowSatResult(
            extension=extension,
            telemetry=dict(solver.telemetry),
            route_metadata=_native_sparse_narrow_route_metadata("stable", solver.telemetry),
        )
    raise ValueError(f"unsupported sparse/narrow native SAT semantics: {semantics}")


def should_use_native_cnf_prefsat(framework: ABAFramework) -> bool:
    assumption_count = len(framework.assumptions)
    return native_cnf_prefsat_dense_shape(
        is_flat=True,
        assumptions=assumption_count,
        rule_density=(len(framework.rules) / assumption_count) if assumption_count else 0.0,
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
        program = [*self._asp_facts(), *self._stable_program()]
        if require_derived is not None:
            program.append(f":- not derived({self.literal_ids[require_derived]}).")
        if require_not_derived is not None:
            program.append(f":- derived({self.literal_ids[require_not_derived]}).")

        return self._solve_selected(program)

    def admissible_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
        require_any_assumption: AssumptionSet = frozenset(),
        prefer_large: bool = False,
        maximize: bool = False,
    ) -> AssumptionSet | None:
        self._validate_assumptions(require_assumptions)
        self._validate_assumptions(require_any_assumption)
        return self._solve_selected(
            (
                *self._asp_facts(),
                *self._admissible_program(
                    require_assumptions=require_assumptions,
                    require_any_assumption=require_any_assumption,
                    prefer_large=prefer_large,
                    maximize=maximize,
                ),
            ),
            optimize=maximize,
        )

    def preferred_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        self._validate_assumptions(require_assumptions)
        if not require_assumptions:
            stable = self.stable_extension()
            if stable is not None:
                return stable
        return self.admissible_extension(
            require_assumptions=require_assumptions,
            maximize=True,
        )

    def attacks(self, extension: AssumptionSet, assumption: Literal) -> bool:
        if assumption not in self.framework.assumptions:
            raise ValueError(f"unknown assumption: {assumption!r}")
        return self.framework.contrary[assumption] in self.closure(extension)

    def closure(self, extension: AssumptionSet) -> frozenset[Literal]:
        derived = set(extension)
        queue = list(derived)
        waiting: defaultdict[Literal, list[int]] = defaultdict(list)
        remaining: list[int] = []
        consequents: list[Literal] = []

        for index, rule in enumerate(sorted(self.framework.rules, key=repr)):
            missing = 0
            for antecedent in frozenset(rule.antecedents):
                if antecedent not in derived:
                    missing += 1
                    waiting[antecedent].append(index)
            remaining.append(missing)
            consequents.append(rule.consequent)
            if missing == 0 and rule.consequent not in derived:
                derived.add(rule.consequent)
                queue.append(rule.consequent)

        while queue:
            literal = queue.pop()
            for rule_index in waiting.get(literal, ()):
                remaining[rule_index] -= 1
                if remaining[rule_index] == 0:
                    consequent = consequents[rule_index]
                    if consequent not in derived:
                        derived.add(consequent)
                        queue.append(consequent)
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
        for rule in sorted(self.framework.rules, key=repr):
            head = self.literal_ids[rule.consequent]
            body = ", ".join(
                f"derived({self.literal_ids[antecedent]})"
                for antecedent in sorted(rule.antecedents, key=repr)
            )
            if body:
                facts.append(f"derived({head}) :- {body}.")
            else:
                facts.append(f"derived({head}).")
        return tuple(facts)

    def _stable_program(self) -> tuple[str, ...]:
        constraints = [
            "{ selected(A) } :- assumption(A).",
            "derived(L) :- selected(A), assumption_literal(A,L).",
            ":- selected(A), contrary(A,C), derived(C).",
            ":- assumption(A), not selected(A), contrary(A,C), not derived(C).",
        ]
        return tuple((*constraints, "#show selected/1."))

    def _admissible_program(
        self,
        *,
        require_assumptions: AssumptionSet,
        require_any_assumption: AssumptionSet,
        prefer_large: bool,
        maximize: bool,
    ) -> tuple[str, ...]:
        constraints = [
            "{ selected(A) } :- assumption(A).",
            "derived(L) :- selected(A), assumption_literal(A,L).",
            "available(A) :- assumption(A), contrary(A,C), not derived(C).",
            "attacker_derived(L) :- available(A), assumption_literal(A,L).",
            ":- selected(A), contrary(A,C), derived(C).",
            ":- selected(A), contrary(A,C), attacker_derived(C).",
        ]
        constraints.extend(self._attacker_closure_rules())
        constraints.extend(
            f"selected({self.assumption_ids[assumption]})."
            for assumption in sorted(require_assumptions, key=repr)
        )
        if require_any_assumption:
            constraints.append(
                ":- "
                + ", ".join(
                    f"not selected({self.assumption_ids[assumption]})"
                    for assumption in sorted(require_any_assumption, key=repr)
                )
                + "."
            )
        if prefer_large:
            constraints.append("#heuristic selected(A) : assumption(A). [1@1,true]")
        if maximize:
            constraints.append("#maximize { 1,A : selected(A) }.")
        return tuple((*constraints, "#show selected/1."))

    def _attacker_closure_rules(self) -> tuple[str, ...]:
        rules: list[str] = []
        for rule in sorted(self.framework.rules, key=repr):
            head = self.literal_ids[rule.consequent]
            body = ", ".join(
                f"attacker_derived({self.literal_ids[antecedent]})"
                for antecedent in sorted(rule.antecedents, key=repr)
            )
            if body:
                rules.append(f"attacker_derived({head}) :- {body}.")
            else:
                rules.append(f"attacker_derived({head}).")
        return tuple(rules)

    def _solve_selected(
        self,
        program: tuple[str, ...] | list[str],
        *,
        optimize: bool = False,
    ) -> AssumptionSet | None:
        clingo = _load_clingo()

        selected: list[str] = []

        def collect_model(model) -> None:
            selected.clear()
            selected.extend(str(symbol.arguments[0]) for symbol in model.symbols(shown=True))

        control = clingo.Control(["--models=0"] if optimize else ["--models=1"])
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

    def _validate_assumptions(self, assumptions: AssumptionSet) -> None:
        unknown = assumptions - self.framework.assumptions
        if unknown:
            raise ValueError(f"unknown assumptions: {sorted(unknown, key=repr)!r}")


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
    simplify: bool = True,
) -> tuple[bool, AssumptionSet | None]:
    """Return an ABA acceptance decision using support-aware SAT witnesses."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
    if simplify:
        simplification = _aba_simplification(framework, semantics)
        if not simplification.is_trivial:
            return _simplified_support_acceptance(
                simplification, semantics=semantics, task=task, query=query
            )
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


def _simplified_support_acceptance(
    simplification,
    *,
    semantics: str,
    task: str,
    query: Literal,
) -> tuple[bool, AssumptionSet | None]:
    if task not in {"credulous", "skeptical"}:
        raise ValueError(f"unsupported ABA acceptance task: {task}")
    residual = simplification.residual

    def _residual_witness() -> AssumptionSet | None:
        witness = sat_support_extension(residual, semantics, simplify=False)
        return None if witness is None else simplification.lift(witness)

    if query in simplification.fixed_in:
        if task == "credulous":
            return True, _residual_witness()
        return True, None
    if query in simplification.fixed_out or query not in residual.language:
        if task == "credulous":
            return False, None
        return False, _residual_witness()
    answer, witness = sat_support_acceptance(
        residual,
        semantics=semantics,
        task=task,
        query=query,
        simplify=False,
    )
    if witness is None:
        return answer, None
    return answer, simplification.lift(witness)


def sat_support_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
    require_assumptions: AssumptionSet = frozenset(),
    simplify: bool = True,
) -> AssumptionSet | None:
    """Return one complete/preferred ABA extension using support-aware SAT."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
    if semantics == "preferred" and require_derived is None and require_not_derived is None:
        if should_use_native_cnf_prefsat(framework):
            return native_cnf_prefsat_extension(
                framework,
                require_assumptions=require_assumptions,
            ).extension
    if (
        simplify
        and require_derived is None
        and require_not_derived is None
        and not require_assumptions
    ):
        simplification = _aba_simplification(framework, semantics)
        if not simplification.is_trivial:
            witness = sat_support_extension(
                simplification.residual,
                semantics,
                simplify=False,
            )
            return None if witness is None else simplification.lift(witness)
    if require_derived is not None and require_derived not in framework.language:
        raise ValueError(f"required literal is not in framework language: {require_derived!r}")
    if require_not_derived is not None and require_not_derived not in framework.language:
        raise ValueError(
            f"excluded literal is not in framework language: {require_not_derived!r}"
        )
    if semantics == "preferred" and require_derived is None and require_not_derived is None:
        from argumentation.aba_decomposition import decomposed_prefsat_extension

        return decomposed_prefsat_extension(
            framework,
            require_assumptions=require_assumptions,
        ).extension
    if semantics == "preferred" and (
        require_derived is not None or require_not_derived is not None
    ):
        return _sat_preferred_extension_satisfying(
            framework,
            require_derived=require_derived,
            require_not_derived=require_not_derived,
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


class _NativeCnfPrefSatSolver:
    def __init__(self, framework: ABAFramework) -> None:
        solver_class = _load_pysat_solver()
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self._next_var = 1
        self.in_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.out_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.undec_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.solver = solver_class(name="glucose4")
        self.telemetry = {
            "native_cnf_variables": self._next_var - 1,
            "native_cnf_clauses": 0,
            "native_cnf_solver_checks": 0,
            "native_cnf_candidate_models": 0,
            "native_cnf_candidate_blocks": 0,
            "native_cnf_z3_main_checks": 0,
            "native_cnf_closure_materializations": 0,
            "prefsat_labelling_variables": 3 * len(self.assumptions),
            "prefsat_exactly_one_clauses": 0,
            "prefsat_complete_clauses": 0,
            "prefsat_support_materializations": 0,
            "prefsat_solver_checks": 0,
            "prefsat_candidate_models": 0,
            "prefsat_candidate_blocks": 0,
            "prefsat_rejected_supersets": 0,
            "prefsat_max_in_count_seen": 0,
            "prefsat_final_in_count": 0,
            "prefsat_attacker_solver_builds": 0,
            "prefsat_attacker_solver_checks": 0,
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self.progress_events: list[dict[str, int]] = []
        self._attacker_closure = _BitsetHornClosure.from_framework(
            framework,
            self.telemetry,
        )
        self._contrary_bits = {
            assumption: self._attacker_closure.literal_bits[framework.contrary[assumption]]
            for assumption in self.assumptions
        }
        self._empty_closure_mask = self._attacker_closure.closure_mask(frozenset())
        self._add_labelling_skeleton()
        self._add_static_conflict_clauses()
        self.solver.set_phases([self.in_vars[assumption] for assumption in self.assumptions])

    def _new_var(self) -> int:
        variable = self._next_var
        self._next_var += 1
        return variable

    def _add_clause(self, clause: list[int]) -> None:
        self.solver.add_clause(clause)
        self.telemetry["native_cnf_clauses"] += 1
        self.telemetry["prefsat_complete_clauses"] += 1

    def _add_labelling_skeleton(self) -> None:
        for assumption in self.assumptions:
            in_var = self.in_vars[assumption]
            out_var = self.out_vars[assumption]
            undec_var = self.undec_vars[assumption]
            self._add_clause([in_var, out_var, undec_var])
            self._add_clause([-in_var, -out_var])
            self._add_clause([-in_var, -undec_var])
            self._add_clause([-out_var, -undec_var])
            self.telemetry["prefsat_exactly_one_clauses"] += 1

    def _add_static_conflict_clauses(self) -> None:
        for target in self.assumptions:
            if self._empty_closure_mask & self._contrary_bits[target]:
                self._add_clause([-self.in_vars[target]])
        for source in self.assumptions:
            closure = self._closure_mask(frozenset({source}))
            for target in self.assumptions:
                if closure & self._contrary_bits[target]:
                    if source == target:
                        self._add_clause([-self.in_vars[target]])
                    else:
                        self._add_clause([-self.in_vars[source], -self.in_vars[target]])

    def preferred_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet:
        current = self._solve_admissible(require_in=require_assumptions)
        if current is None:
            self.telemetry["prefsat_final_in_count"] = 0
            return frozenset()
        while True:
            outside = self.framework.assumptions - current
            if not outside:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            larger = self._solve_admissible(require_in=current, require_any_in=outside)
            if larger is None:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            if not current < larger:
                raise RuntimeError("native CNF PrefSat grow step did not produce a strict superset")
            self._record_progress()
            current = larger

    def _solve_admissible(
        self,
        *,
        require_in: AssumptionSet = frozenset(),
        require_any_in: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        assumptions = [self.in_vars[assumption] for assumption in sorted(require_in, key=repr)]
        if require_any_in:
            guard = self._new_var()
            self.telemetry["native_cnf_variables"] = self._next_var - 1
            self._add_clause(
                [
                    *(self.in_vars[assumption] for assumption in sorted(require_any_in, key=repr)),
                    -guard,
                ]
            )
            assumptions.append(guard)
        while True:
            self.telemetry["native_cnf_solver_checks"] += 1
            self.telemetry["prefsat_solver_checks"] += 1
            if not self.solver.solve(assumptions=assumptions):
                self._record_progress()
                return None
            self.telemetry["native_cnf_candidate_models"] += 1
            self.telemetry["prefsat_candidate_models"] += 1
            candidate = self._model_extension()
            closure = self._closure_mask(candidate)
            self.telemetry["prefsat_max_in_count_seen"] = max(
                self.telemetry["prefsat_max_in_count_seen"],
                len(candidate),
            )
            refinement = self._semantic_refinement(candidate, closure)
            if refinement is None:
                self._record_progress()
                return candidate
            self._add_clause(refinement)
            self.telemetry["native_cnf_candidate_blocks"] += 1
            self.telemetry["prefsat_candidate_blocks"] += 1
            self.telemetry["prefsat_rejected_supersets"] += 1
            self._record_progress()

    def _semantic_refinement(
        self,
        candidate: AssumptionSet,
        closure: int,
    ) -> list[int] | None:
        for target in sorted(candidate, key=repr):
            if closure & self._contrary_bits[target]:
                contrary = self.framework.contrary[target]
                attack_support = self._attacker_closure.shrink_support(candidate, contrary)
                return [
                    -self.in_vars[target],
                    *(
                        -self.in_vars[assumption]
                        for assumption in sorted(attack_support - {target}, key=repr)
                    ),
                ]
        counterexample = self._attacker_counterexample(candidate, closure)
        if counterexample is None:
            return None
        target, attack_support = counterexample
        if not attack_support:
            return [-self.in_vars[target]]
        outside_candidate = self.framework.assumptions - candidate
        if outside_candidate:
            return [
                -self.in_vars[target],
                *(self.in_vars[assumption] for assumption in sorted(outside_candidate, key=repr)),
            ]
        return [-self.in_vars[target]]

    def _attacker_counterexample(
        self,
        candidate: AssumptionSet,
        closure: int,
    ) -> tuple[Literal, AssumptionSet] | None:
        if not candidate:
            return None
        counterattacked = frozenset(
            assumption
            for assumption in self.assumptions
            if closure & self._contrary_bits[assumption]
        )
        available = self.framework.assumptions - counterattacked
        attacker_closure = self._attacker_closure.closure_mask(available)
        for target in sorted(candidate, key=repr):
            contrary_bit = self._contrary_bits[target]
            if attacker_closure & contrary_bit:
                if self._empty_closure_mask & contrary_bit:
                    return target, frozenset()
                return target, available
        return None

    def _model_extension(self) -> AssumptionSet:
        model = frozenset(literal for literal in self.solver.get_model() if literal > 0)
        return frozenset(
            assumption
            for assumption, variable in self.in_vars.items()
            if variable in model
        )

    def _closure_mask(self, extension: AssumptionSet) -> int:
        return self._attacker_closure.closure_mask(extension)

    def _closure(self, extension: AssumptionSet) -> frozenset[Literal]:
        self.telemetry["native_cnf_closure_materializations"] += 1
        closure = self._closure_mask(extension)
        return frozenset(
            literal
            for literal, bit in self._attacker_closure.literal_bits.items()
            if closure & bit
        )

    def _record_progress(self) -> None:
        event = {
            "prefsat_max_in_count_seen": self.telemetry["prefsat_max_in_count_seen"],
            "prefsat_candidate_blocks": self.telemetry["prefsat_candidate_blocks"],
        }
        if not self.progress_events or self.progress_events[-1] != event:
            self.progress_events.append(event)

    def result(self, extension: AssumptionSet) -> RealPrefSatResult:
        closure = _prefsat_closure(self.framework, extension)
        prefsat_in = {assumption: assumption in extension for assumption in self.assumptions}
        prefsat_out = {
            assumption: self.framework.contrary[assumption] in closure
            for assumption in self.assumptions
        }
        prefsat_undec = {
            assumption: not prefsat_in[assumption] and not prefsat_out[assumption]
            for assumption in self.assumptions
        }
        return RealPrefSatResult(
            extension=extension,
            prefsat_in=prefsat_in,
            prefsat_out=prefsat_out,
            prefsat_undec=prefsat_undec,
            telemetry=dict(self.telemetry),
            progress_events=tuple(self.progress_events),
            route_metadata={
                "backend": "sat",
                "algorithm": "native-cnf-prefsat",
                "rejected_substitutes": (
                    "z3-main-complete-labelling",
                    "asp-optimization",
                    "greedy-growth",
                ),
            },
        )


class _NativeSparseNarrowStableSolver:
    def __init__(self, framework: ABAFramework) -> None:
        solver_class = _load_pysat_solver()
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self._next_var = 1
        self.in_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.solver = solver_class(name="glucose4")
        self.telemetry = {
            "clingo_solver_calls": 0,
            "native_sparse_narrow_solver_checks": 0,
            "native_sparse_narrow_candidate_models": 0,
            "native_sparse_narrow_learned_clauses": 0,
            "native_sparse_narrow_z3_main_checks": 0,
            "native_sparse_narrow_closure_checks": 0,
            "native_sparse_narrow_rule_firings": 0,
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self._closure = _BitsetHornClosure.from_framework(framework, self.telemetry)
        self._contrary_bits = {
            assumption: self._closure.literal_bits[framework.contrary[assumption]]
            for assumption in self.assumptions
        }
        self._add_static_conflict_clauses()
        self.solver.set_phases([self.in_vars[assumption] for assumption in self.assumptions])

    def _new_var(self) -> int:
        variable = self._next_var
        self._next_var += 1
        return variable

    def _add_clause(self, clause: list[int]) -> None:
        self.solver.add_clause(clause)
        self.telemetry["native_sparse_narrow_learned_clauses"] += 1

    def _add_static_conflict_clauses(self) -> None:
        empty_closure = self._closure.closure_mask(frozenset())
        for target in self.assumptions:
            if empty_closure & self._contrary_bits[target]:
                self._add_clause([-self.in_vars[target]])
        for source in self.assumptions:
            closure = self._closure.closure_mask(frozenset({source}))
            for target in self.assumptions:
                if closure & self._contrary_bits[target]:
                    if source == target:
                        self._add_clause([-self.in_vars[target]])
                    else:
                        self._add_clause([-self.in_vars[source], -self.in_vars[target]])

    def stable_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        assumptions = [self.in_vars[assumption] for assumption in sorted(require_assumptions, key=repr)]
        while True:
            self.telemetry["native_sparse_narrow_solver_checks"] += 1
            if not self.solver.solve(assumptions=assumptions):
                return None
            self.telemetry["native_sparse_narrow_candidate_models"] += 1
            extension = self._model_extension()
            refinement = self._stable_refinement(extension)
            if refinement is None:
                self._sync_closure_telemetry()
                return extension
            self._add_clause(refinement)
            self._sync_closure_telemetry()

    def _stable_refinement(self, extension: AssumptionSet) -> list[int] | None:
        closure = self._closure.closure_mask(extension)
        for target in sorted(extension, key=repr):
            if closure & self._contrary_bits[target]:
                support = self._closure.shrink_support(
                    extension,
                    self.framework.contrary[target],
                )
                return [
                    -self.in_vars[target],
                    *(
                        -self.in_vars[assumption]
                        for assumption in sorted(support - {target}, key=repr)
                    ),
                ]
        for target in self.assumptions:
            if target not in extension and not (closure & self._contrary_bits[target]):
                outside = self.framework.assumptions - extension
                return [
                    *(self.in_vars[assumption] for assumption in sorted(outside, key=repr)),
                    *(-self.in_vars[assumption] for assumption in sorted(extension, key=repr)),
                ]
        return None

    def _model_extension(self) -> AssumptionSet:
        model = frozenset(literal for literal in self.solver.get_model() if literal > 0)
        return frozenset(
            assumption
            for assumption, variable in self.in_vars.items()
            if variable in model
        )

    def _sync_closure_telemetry(self) -> None:
        self.telemetry["native_sparse_narrow_closure_checks"] = self.telemetry[
            "prefsat_attacker_bitset_closure_checks"
        ]
        self.telemetry["native_sparse_narrow_rule_firings"] = self.telemetry[
            "prefsat_attacker_bitset_rule_firings"
        ]


def _native_sparse_narrow_telemetry(telemetry: dict[str, int]) -> dict[str, int]:
    return {
        **telemetry,
        "clingo_solver_calls": 0,
        "native_sparse_narrow_solver_checks": telemetry.get("native_cnf_solver_checks", 0),
        "native_sparse_narrow_candidate_models": telemetry.get("native_cnf_candidate_models", 0),
        "native_sparse_narrow_learned_clauses": telemetry.get("native_cnf_candidate_blocks", 0),
        "native_sparse_narrow_z3_main_checks": telemetry.get("native_cnf_z3_main_checks", 0),
        "native_sparse_narrow_closure_checks": telemetry.get(
            "prefsat_attacker_bitset_closure_checks",
            0,
        ),
        "native_sparse_narrow_rule_firings": telemetry.get(
            "prefsat_attacker_bitset_rule_firings",
            0,
        ),
    }


def _native_sparse_narrow_route_metadata(
    semantics: str,
    telemetry: dict[str, int],
) -> dict[str, Any]:
    return {
        "backend": "sat",
        "algorithm": "native_sparse_narrow_sat",
        "semantics": semantics,
        "clingo_solver_calls": telemetry.get("clingo_solver_calls", 0),
        "paper_page_images": SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
    }


class _RealPrefSatSolver:
    def __init__(self, framework: ABAFramework) -> None:
        self.z3 = _load_z3()
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self.literals = tuple(sorted(framework.language, key=repr))
        self.solver = self.z3.Solver()
        self.prefsat_in = {
            assumption: self.z3.Bool(f"prefsat_in_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.prefsat_out = {
            assumption: self.z3.Bool(f"prefsat_out_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.prefsat_undec = {
            assumption: self.z3.Bool(f"prefsat_undec_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.telemetry = {
            "prefsat_labelling_variables": 3 * len(self.assumptions),
            "prefsat_exactly_one_clauses": 0,
            "prefsat_complete_clauses": 0,
            "prefsat_support_materializations": 0,
            "prefsat_solver_checks": 0,
            "prefsat_candidate_models": 0,
            "prefsat_candidate_blocks": 0,
            "prefsat_rejected_supersets": 0,
            "prefsat_max_in_count_seen": 0,
            "prefsat_final_in_count": 0,
            "prefsat_attacker_solver_builds": 0,
            "prefsat_attacker_solver_checks": 0,
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self.progress_events: list[dict[str, int]] = []
        self._pending_refinements: list = []
        self._attacker_closure = _BitsetHornClosure.from_framework(
            framework,
            self.telemetry,
        )
        self.derived = self._add_closure_constraints("prefsat", self.solver, self.prefsat_in)
        self._add_labelling_constraints()

    def _add_closure_constraints(self, prefix: str, solver, variables):
        derived, clause_count = _prefsat_add_closure_constraints(
            self.z3,
            solver,
            self.framework,
            variables,
            prefix=prefix,
        )
        self.telemetry["prefsat_complete_clauses"] += clause_count
        return derived

    def _add_labelling_constraints(self) -> None:
        z3 = self.z3
        for assumption in self.assumptions:
            in_var = self.prefsat_in[assumption]
            out_var = self.prefsat_out[assumption]
            undec_var = self.prefsat_undec[assumption]
            attacked_by_in = self.derived[self.framework.contrary[assumption]]
            self.solver.add(z3.Or(in_var, out_var, undec_var))
            self.solver.add(z3.AtMost(in_var, out_var, undec_var, 1))
            self.solver.add(out_var == attacked_by_in)
            self.solver.add(undec_var == z3.And(z3.Not(in_var), z3.Not(out_var)))
            self.solver.add(z3.Implies(in_var, z3.Not(attacked_by_in)))
            self.telemetry["prefsat_exactly_one_clauses"] += 1
            self.telemetry["prefsat_complete_clauses"] += 4

    def preferred_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet:
        current = self._solve_admissible(require_in=require_assumptions)
        if current is None:
            self.telemetry["prefsat_final_in_count"] = 0
            return frozenset()
        while True:
            outside = self.framework.assumptions - current
            if not outside:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            larger = self._solve_admissible(require_in=current, require_any_in=outside)
            if larger is None:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            if not current < larger:
                raise RuntimeError("real ABA PrefSat grow step did not produce a strict superset")
            self.telemetry["prefsat_candidate_blocks"] += 1
            self._record_progress()
            current = larger

    def _solve_admissible(
        self,
        *,
        require_in: AssumptionSet = frozenset(),
        require_any_in: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        z3 = self.z3
        self.solver.push()
        try:
            for clause in self._pending_refinements:
                self.solver.add(clause)
            for assumption in sorted(require_in, key=repr):
                self.solver.add(self.prefsat_in[assumption])
            if require_any_in:
                self.solver.add(
                    z3.Or(
                        *(
                            self.prefsat_in[assumption]
                            for assumption in sorted(require_any_in, key=repr)
                        )
                    )
                )
            while True:
                self.telemetry["prefsat_solver_checks"] += 1
                if self.solver.check() != z3.sat:
                    self._record_progress()
                    return None
                self.telemetry["prefsat_candidate_models"] += 1
                candidate = self._model_extension()
                closure = self._model_closure()
                self.telemetry["prefsat_max_in_count_seen"] = max(
                    self.telemetry["prefsat_max_in_count_seen"],
                    len(candidate),
                )
                counterexample = self._attacker_counterexample(candidate, closure)
                if counterexample is None:
                    self._record_progress()
                    return candidate
                clause = self._defense_refinement_clause(counterexample)
                self._pending_refinements.append(clause)
                self.solver.add(clause)
                self.telemetry["prefsat_candidate_blocks"] += 1
                self.telemetry["prefsat_rejected_supersets"] += 1
                self._record_progress()
        finally:
            self.solver.pop()

    def _attacker_counterexample(
        self,
        candidate: AssumptionSet,
        closure: frozenset[Literal],
    ) -> tuple[Literal, AssumptionSet] | None:
        if not candidate:
            return None
        counterattacked = frozenset(
            assumption
            for assumption in self.assumptions
            if self.framework.contrary[assumption] in closure
        )
        available = self.framework.assumptions - counterattacked
        attacker_closure = self._attacker_closure.closure_mask(available)
        for target in sorted(candidate, key=repr):
            conclusion = self.framework.contrary[target]
            if self._attacker_closure.contains(attacker_closure, conclusion):
                return target, self._attacker_closure.shrink_support(available, conclusion)
        return None

    def _defense_refinement_clause(self, counterexample):
        target, attack_support = counterexample
        if not attack_support:
            return self.z3.Not(self.prefsat_in[target])
        return self.z3.Or(
            self.z3.Not(self.prefsat_in[target]),
            *(
                self.derived[self.framework.contrary[attacker]]
                for attacker in sorted(attack_support, key=repr)
            ),
        )

    def _model_extension(self) -> AssumptionSet:
        model = self.solver.model()
        z3 = self.z3
        return frozenset(
            assumption
            for assumption, variable in self.prefsat_in.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def _model_closure(self) -> frozenset[Literal]:
        model = self.solver.model()
        z3 = self.z3
        return frozenset(
            literal
            for literal, variable in self.derived.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def _record_progress(self) -> None:
        event = {
            "prefsat_max_in_count_seen": self.telemetry["prefsat_max_in_count_seen"],
            "prefsat_candidate_blocks": self.telemetry["prefsat_candidate_blocks"],
        }
        if not self.progress_events or self.progress_events[-1] != event:
            self.progress_events.append(event)

    def result(self, extension: AssumptionSet) -> RealPrefSatResult:
        closure = _prefsat_closure(self.framework, extension)
        prefsat_in = {assumption: assumption in extension for assumption in self.assumptions}
        prefsat_out = {
            assumption: self.framework.contrary[assumption] in closure
            for assumption in self.assumptions
        }
        prefsat_undec = {
            assumption: not prefsat_in[assumption] and not prefsat_out[assumption]
            for assumption in self.assumptions
        }
        return RealPrefSatResult(
            extension=extension,
            prefsat_in=prefsat_in,
            prefsat_out=prefsat_out,
            prefsat_undec=prefsat_undec,
            telemetry=dict(self.telemetry),
            progress_events=tuple(self.progress_events),
            route_metadata={
                "backend": "sat",
                "algorithm": "complete-labelling-prefsat",
                "rejected_substitutes": (
                    "old-support-aware-cegar",
                    "asp-optimization",
                    "greedy-growth",
                ),
            },
        )


class _BitsetHornClosure:
    def __init__(
        self,
        literal_bits: dict[Literal, int],
        assumption_bits: dict[Literal, int],
        waiting: dict[int, tuple[int, ...]],
        remaining_counts: tuple[int, ...],
        consequents: tuple[int, ...],
        zero_consequents: tuple[int, ...],
        telemetry: dict[str, int],
    ) -> None:
        self.literal_bits = literal_bits
        self.assumption_bits = assumption_bits
        self.waiting = waiting
        self.remaining_counts = remaining_counts
        self.consequents = consequents
        self.zero_consequents = zero_consequents
        self.telemetry = telemetry
        self._closure_cache: dict[int, int] = {}

    @classmethod
    def from_framework(
        cls,
        framework: ABAFramework,
        telemetry: dict[str, int],
    ) -> _BitsetHornClosure:
        literals = sorted(
            set(framework.language)
            | set(framework.assumptions)
            | set(framework.contrary.values())
            | {rule.consequent for rule in framework.rules}
            | {antecedent for rule in framework.rules for antecedent in rule.antecedents},
            key=repr,
        )
        literal_bits = {literal: 1 << index for index, literal in enumerate(literals)}
        assumption_bits = {
            assumption: literal_bits[assumption]
            for assumption in sorted(framework.assumptions, key=repr)
        }
        waiting_lists: dict[int, list[int]] = defaultdict(list)
        remaining_counts: list[int] = []
        consequents: list[int] = []
        zero_consequents: list[int] = []
        for rule in sorted(framework.rules, key=repr):
            antecedent_bits = tuple(
                literal_bits[antecedent]
                for antecedent in frozenset(rule.antecedents)
            )
            consequent = literal_bits[rule.consequent]
            if antecedent_bits:
                rule_index = len(remaining_counts)
                remaining_counts.append(len(antecedent_bits))
                consequents.append(consequent)
                for bit in antecedent_bits:
                    waiting_lists[bit].append(rule_index)
            else:
                zero_consequents.append(consequent)
        waiting = {
            bit: tuple(indices)
            for bit, indices in waiting_lists.items()
        }
        return cls(
            literal_bits,
            assumption_bits,
            waiting,
            tuple(remaining_counts),
            tuple(consequents),
            tuple(zero_consequents),
            telemetry,
        )

    def closure_mask(self, assumptions: AssumptionSet) -> int:
        return self._closure_from_seed(self._assumption_mask(assumptions))

    def contains(self, closure: int, literal: Literal) -> bool:
        return bool(closure & self.literal_bits[literal])

    def shrink_support(
        self,
        support: AssumptionSet,
        conclusion: Literal,
    ) -> AssumptionSet:
        self.telemetry["prefsat_attacker_bitset_shrink_checks"] += 1
        current = self._assumption_mask(support)
        conclusion_bit = self.literal_bits[conclusion]
        for assumption in sorted(support, key=repr):
            reduced = current & ~self.assumption_bits[assumption]
            if self._closure_from_seed(reduced) & conclusion_bit:
                current = reduced
        return frozenset(
            assumption
            for assumption, bit in self.assumption_bits.items()
            if current & bit
        )

    def _assumption_mask(self, assumptions: AssumptionSet) -> int:
        mask = 0
        for assumption in assumptions:
            mask |= self.assumption_bits[assumption]
        return mask

    def _closure_from_seed(self, seed: int) -> int:
        cached = self._closure_cache.get(seed)
        if cached is not None:
            return cached
        self.telemetry["prefsat_attacker_bitset_closure_checks"] += 1
        closure = seed
        remaining = list(self.remaining_counts)
        queue = self._bits(seed)
        for consequent in self.zero_consequents:
            if not closure & consequent:
                closure |= consequent
                queue.append(consequent)
        while queue:
            bit = queue.pop()
            for rule_index in self.waiting.get(bit, ()):
                remaining[rule_index] -= 1
                self.telemetry["prefsat_attacker_bitset_rule_firings"] += 1
                if remaining[rule_index] == 0:
                    consequent = self.consequents[rule_index]
                    if not closure & consequent:
                        closure |= consequent
                        queue.append(consequent)
        self._closure_cache[seed] = closure
        return closure

    def _bits(self, mask: int) -> list[int]:
        bits: list[int] = []
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            bits.append(bit)
            remaining ^= bit
        return bits


class _AdmissibleCegarSolver:
    """Reusable Z3 CEGAR solver for flat ABA admissible sets.

    The query-independent encoding -- the ranked-closure constraints plus the
    per-assumption conflict-freeness implications -- is built once. Each
    :meth:`solve` call pushes the transient ``require_assumptions`` /
    ``require_any_assumption`` hypotheses, runs the abstraction-refinement loop,
    and pops. The defense-counterexample refinement clauses found during a call
    are globally valid (true of every admissible set, regardless of the transient
    hypotheses) and so are re-asserted at base level on the next call -- they
    accumulate forever, which is exactly the incremental CEGAR contract.

    This brings the preferred growth loop (``_sat_preferred_cegar_extension``) up
    to the standard of the admissible path: it no longer rebuilds the
    ``O(|literals| + |rules|)`` ranked-closure encoding once per grow-step.
    """

    def __init__(self, framework: ABAFramework) -> None:
        self.z3 = _load_z3()
        self.framework = framework
        self.variables = {
            assumption: self.z3.Bool(f"in_{_literal_key(assumption)}")
            for assumption in sorted(framework.assumptions, key=repr)
        }
        self.solver = self.z3.Solver()
        self.derived = _add_ranked_closure_constraints(
            self.z3, self.solver, framework, self.variables
        )
        for assumption in sorted(framework.assumptions, key=repr):
            self.solver.add(
                self.z3.Implies(
                    self.variables[assumption],
                    self.z3.Not(self.derived[framework.contrary[assumption]]),
                )
            )
        self._pending_permanent: list = []

    def _flush_permanent(self) -> None:
        for clause in self._pending_permanent:
            self.solver.add(clause)
        self._pending_permanent.clear()

    def solve(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
        require_any_assumption: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        z3 = self.z3
        self._flush_permanent()
        self.solver.push()
        try:
            for assumption in sorted(require_assumptions, key=repr):
                self.solver.add(self.variables[assumption])
            if require_any_assumption:
                self.solver.add(
                    z3.Or(
                        *(
                            self.variables[assumption]
                            for assumption in sorted(require_any_assumption, key=repr)
                        )
                    )
                )
            while self.solver.check() == z3.sat:
                model = self.solver.model()
                candidate = frozenset(
                    assumption
                    for assumption, variable in self.variables.items()
                    if z3.is_true(model.evaluate(variable, model_completion=True))
                )
                closure = frozenset(
                    literal
                    for literal, variable in self.derived.items()
                    if z3.is_true(model.evaluate(variable, model_completion=True))
                )
                counterexample = _defense_counterexample(self.framework, candidate, closure)
                if counterexample is None:
                    return candidate
                target, attack_support = counterexample
                if not attack_support:
                    clause = z3.Not(self.variables[target])
                else:
                    clause = z3.Or(
                        z3.Not(self.variables[target]),
                        *(
                            self.derived[self.framework.contrary[assumption]]
                            for assumption in sorted(attack_support, key=repr)
                        ),
                    )
                self._pending_permanent.append(clause)
                self.solver.add(clause)
            return None
        finally:
            self.solver.pop()


def _sat_preferred_cegar_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> AssumptionSet | None:
    solver = _AdmissibleCegarSolver(framework)
    current = solver.solve(require_assumptions=require_assumptions)
    if current is None:
        return None
    while True:
        outside = framework.assumptions - current
        if not outside:
            return current
        larger = solver.solve(
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
    return _AdmissibleCegarSolver(framework).solve(
        require_assumptions=require_assumptions,
        require_any_assumption=require_any_assumption,
    )


def _defense_counterexample(
    framework: ABAFramework,
    candidate: AssumptionSet,
    closure: frozenset[Literal],
) -> tuple[Literal, AssumptionSet] | None:
    counterexamples = _defense_counterexamples(framework, candidate, closure)
    return counterexamples[0] if counterexamples else None


def _defense_counterexamples(
    framework: ABAFramework,
    candidate: AssumptionSet,
    closure: frozenset[Literal],
) -> tuple[tuple[Literal, AssumptionSet], ...]:
    counterattacked = frozenset(
        assumption
        for assumption in framework.assumptions
        if framework.contrary[assumption] in closure
    )
    counterexamples: list[tuple[Literal, AssumptionSet]] = []
    for target in sorted(candidate, key=repr):
        attack_support = _attacker_support_not_counterattacked(
            framework,
            target,
            counterattacked=counterattacked,
        )
        if attack_support is not None:
            counterexamples.append((target, attack_support))
    return tuple(counterexamples)


def _attacker_support_not_counterattacked(
    framework: ABAFramework,
    target: Literal,
    *,
    counterattacked: AssumptionSet,
) -> AssumptionSet | None:
    available = framework.assumptions - counterattacked
    conclusion = framework.contrary[target]
    if not derives(framework, available, conclusion):
        return None
    return _shrink_attack_support(framework, available, conclusion)


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
    simplify: bool = True,
) -> AssumptionSet | None:
    """Return one stable assumption set satisfying optional query constraints."""
    del simplify
    return _sat_ranked_stable_extension(
        framework,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )


def _sat_ranked_stable_extension(
    framework: ABAFramework,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
) -> AssumptionSet | None:
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
    derived = _add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(framework.assumptions, key=repr):
        contrary = derived[framework.contrary[assumption]]
        solver.add(z3.Implies(variables[assumption], z3.Not(contrary)))
        solver.add(z3.Or(variables[assumption], contrary))
    if require_derived is not None:
        solver.add(derived[require_derived])
    if require_not_derived is not None:
        solver.add(z3.Not(derived[require_not_derived]))
    if solver.check() != z3.sat:
        return None
    return _model_extension(z3, solver, variables)


def sat_stable_acceptance(
    framework: ABAFramework,
    *,
    task: str,
    query: Literal,
    simplify: bool = True,
) -> tuple[bool, AssumptionSet | None]:
    """Return an ABA stable acceptance decision (with optional preprocessing)."""
    if task not in {"credulous", "skeptical"}:
        raise ValueError(f"unsupported ABA acceptance task: {task}")
    del simplify
    if task == "credulous":
        witness = sat_stable_extension(framework, require_derived=query, simplify=False)
        return witness is not None, witness
    counterexample = sat_stable_extension(framework, require_not_derived=query, simplify=False)
    return counterexample is None, counterexample


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


def _prefsat_add_closure_constraints(z3, solver, framework, variables, *, prefix: str):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    derived = {
        literal: z3.Bool(f"{prefix}_derived_{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.Int(f"{prefix}_rank_{_literal_key(literal)}")
        for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)
    clause_count = 0

    for literal in literals:
        solver.add(ranks[literal] >= 0, ranks[literal] <= rank_bound)
        clause_count += 1

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == 0))
        clause_count += 2

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
        clause_count += 1

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
        clause_count += 1
    return derived, clause_count


def _prefsat_closure(framework: ABAFramework, extension: AssumptionSet) -> frozenset[Literal]:
    derived = set(extension)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(antecedent in derived for antecedent in rule.antecedents):
                if rule.consequent not in derived:
                    derived.add(rule.consequent)
                    changed = True
    return frozenset(derived)


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


def _load_pysat_solver():
    try:
        from pysat.solvers import Solver  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("native ABA PrefSat solving requires python-sat") from exc
    return Solver


def _load_clingo():
    try:
        return importlib.import_module("clingo")
    except ImportError as exc:
        raise RuntimeError("ABA assumption kernel requires clingo") from exc


__all__ = [
    "AssumptionKernel",
    "NativeSparseNarrowSatResult",
    "RealPrefSatResult",
    "native_cnf_prefsat_extension",
    "native_sparse_narrow_sat_extension",
    "real_prefsat_attack_edge_count",
    "real_prefsat_extension",
    "sat_stable_extension",
    "sat_support_acceptance",
    "sat_support_extension",
    "support_acceptance",
    "support_extensions",
]
