"""Clingo/ASP assumption-level kernel for flat ABA single-extension tasks."""

from __future__ import annotations

from dataclasses import dataclass
import importlib

from argumentation.structured.aba._closure import horn_closure
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import Literal


def _load_clingo():
    try:
        return importlib.import_module("clingo")
    except ImportError as exc:
        raise RuntimeError("ABA assumption kernel requires clingo") from exc


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
                assumption: f"a{index}" for index, assumption in enumerate(assumptions)
            },
            literal_ids={
                literal: f"l{index}" for index, literal in enumerate(literals)
            },
        )

    def stable_extension(
        self,
        *,
        require_derived: Literal | None = None,
        require_not_derived: Literal | None = None,
    ) -> AssumptionSet | None:
        if (
            require_derived is not None
            and require_derived not in self.framework.language
        ):
            raise ValueError(
                f"required literal is not in framework language: {require_derived!r}"
            )
        if (
            require_not_derived is not None
            and require_not_derived not in self.framework.language
        ):
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
        return horn_closure(extension, self.framework.rules)

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
            selected.extend(
                str(symbol.arguments[0]) for symbol in model.symbols(shown=True)
            )

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
