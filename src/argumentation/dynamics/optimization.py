"""OMT-backed optimization semantics for abstract argumentation.

This module turns Dung-style argumentation constraints into a Z3 Optimize
problem. The semantics constraints cite Dung 1995, p.326, where
conflict-free, acceptability, and admissibility are defined. The lexicographic
objective behaviour cites Bjorner and Phan 2014, p.7, and Sebastiani and
Trentin 2015, p.450, which describe lexicographic multi-objective OMT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from argumentation.core.dung import ArgumentationFramework


OptimizationDirection = Literal["maximize", "minimize"]
OptimizationSemantics = Literal["conflict_free", "admissible"]
OptimizationStatus = Literal["optimal", "unsat", "unknown", "unavailable"]


@dataclass(frozen=True)
class OptimizationFeature:
    """Integer-valued argument feature used by an optimization objective."""

    argument: str
    name: str
    value: int


@dataclass(frozen=True)
class OptimizationObjective:
    """One lexicographic objective over accepted argument features."""

    name: str
    direction: OptimizationDirection
    priority: int = 0
    weight: int = 1

    def __post_init__(self) -> None:
        if self.direction not in {"maximize", "minimize"}:
            raise ValueError(f"unknown objective direction: {self.direction}")
        if self.weight <= 0:
            raise ValueError("objective weight must be positive")


@dataclass(frozen=True)
class OptimizationPolicy:
    """Optimization policy for selecting one candidate argument.

    ``semantics`` currently supports the Dung constraints needed by the chess
    sidecar: conflict-free sets and admissible sets. See Dung 1995, p.326.
    """

    semantics: OptimizationSemantics = "conflict_free"
    objectives: tuple[OptimizationObjective, ...] = ()
    candidates: frozenset[str] = frozenset()
    required: frozenset[str] = frozenset()
    forbidden: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.semantics not in {"conflict_free", "admissible"}:
            raise ValueError(f"unknown optimization semantics: {self.semantics}")
        object.__setattr__(self, "objectives", tuple(self.objectives))
        object.__setattr__(self, "candidates", frozenset(self.candidates))
        object.__setattr__(self, "required", frozenset(self.required))
        object.__setattr__(self, "forbidden", frozenset(self.forbidden))


@dataclass(frozen=True)
class OptimizationResult:
    """Result of optimizing an argumentation framework."""

    status: OptimizationStatus
    selected_arguments: frozenset[str] = frozenset()
    selected_candidate: str | None = None
    objective_values: dict[str, int] = field(default_factory=dict)
    backend: str = "z3"
    trace: dict[str, Any] = field(default_factory=dict)


def optimize_framework(
    framework: ArgumentationFramework,
    policy: OptimizationPolicy,
    features: tuple[OptimizationFeature, ...] | list[OptimizationFeature],
) -> OptimizationResult:
    """Return an optimal accepted candidate under ``policy``.

    The selected set is constrained by Dung conflict-freeness or admissibility.
    Objectives are applied lexicographically over accepted-argument feature
    sums, following the OMT combination pattern in Bjorner-Phan 2014 and
    Sebastiani-Trentin 2015.
    """

    _validate_policy(framework, policy)
    z3 = _import_z3()
    if z3 is None:
        return OptimizationResult(
            status="unavailable",
            trace={"reason": "z3-solver is not importable"},
        )

    arguments = tuple(sorted(framework.arguments))
    candidates = tuple(sorted(policy.candidates))
    variables = {
        argument: z3.Bool(f"in_{_z3_safe_name(argument)}")
        for argument in arguments
    }
    optimizer = z3.Optimize()
    optimizer.set(priority="lex")

    _add_candidate_constraints(z3, optimizer, variables, candidates)
    _add_required_forbidden_constraints(optimizer, variables, policy)
    _add_conflict_free_constraints(z3, optimizer, variables, framework)
    if policy.semantics == "admissible":
        _add_admissibility_constraints(z3, optimizer, variables, framework)

    objective_terms = _objective_terms(z3, variables, policy.objectives, tuple(features))
    for objective in sorted(policy.objectives, key=lambda item: (item.priority, item.name)):
        term = objective_terms[objective.name]
        if objective.direction == "maximize":
            optimizer.maximize(term)
        else:
            optimizer.minimize(term)
    tie_break = z3.Sum(
        [
            z3.If(variables[candidate], rank, 0)
            for rank, candidate in enumerate(candidates)
        ]
    )
    optimizer.minimize(tie_break)

    check = optimizer.check()
    if check == z3.unsat:
        return OptimizationResult(status="unsat")
    if check != z3.sat:
        return OptimizationResult(status="unknown", trace={"z3_status": str(check)})

    model = optimizer.model()
    selected_arguments = frozenset(
        argument
        for argument in arguments
        if bool(model.eval(variables[argument], model_completion=True))
    )
    selected_candidate = next(
        (candidate for candidate in candidates if candidate in selected_arguments),
        None,
    )
    objective_values = {
        objective.name: _model_int(model.eval(objective_terms[objective.name], model_completion=True))
        for objective in policy.objectives
    }
    objective_values["tie_break"] = _model_int(model.eval(tie_break, model_completion=True))
    return OptimizationResult(
        status="optimal",
        selected_arguments=selected_arguments,
        selected_candidate=selected_candidate,
        objective_values=objective_values,
        trace={
            "semantics": policy.semantics,
            "objectives": [
                {
                    "name": objective.name,
                    "direction": objective.direction,
                    "priority": objective.priority,
                    "weight": objective.weight,
                }
                for objective in policy.objectives
            ],
        },
    )


def _validate_policy(framework: ArgumentationFramework, policy: OptimizationPolicy) -> None:
    unknown = (policy.candidates | policy.required | policy.forbidden) - framework.arguments
    if unknown:
        raise ValueError(f"policy references unknown arguments: {sorted(unknown)!r}")
    if not policy.candidates:
        raise ValueError("optimization policy requires at least one candidate")
    overlap = policy.required & policy.forbidden
    if overlap:
        raise ValueError(f"arguments cannot be both required and forbidden: {sorted(overlap)!r}")


def _add_candidate_constraints(
    z3: Any,
    optimizer: Any,
    variables: dict[str, Any],
    candidates: tuple[str, ...],
) -> None:
    optimizer.add(
        z3.Sum([z3.If(variables[candidate], 1, 0) for candidate in candidates]) == 1
    )


def _add_required_forbidden_constraints(
    optimizer: Any,
    variables: dict[str, Any],
    policy: OptimizationPolicy,
) -> None:
    for argument in sorted(policy.required):
        optimizer.add(variables[argument])
    for argument in sorted(policy.forbidden):
        optimizer.add(~variables[argument])


def _add_conflict_free_constraints(
    z3: Any,
    optimizer: Any,
    variables: dict[str, Any],
    framework: ArgumentationFramework,
) -> None:
    # Dung 1995, p.326, Definition 5: a conflict-free set contains no attacker
    # and target pair from the attack relation.
    for attacker, target in sorted(framework.defeats):
        optimizer.add(z3.Not(z3.And(variables[attacker], variables[target])))


def _add_admissibility_constraints(
    z3: Any,
    optimizer: Any,
    variables: dict[str, Any],
    framework: ArgumentationFramework,
) -> None:
    # Dung 1995, p.326, Definition 6: each selected argument must be acceptable
    # with respect to the selected set, i.e. every attacker is counter-attacked
    # by some selected argument.
    attackers: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    defenders: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in framework.defeats:
        attackers[target].add(attacker)
        defenders[target].add(attacker)

    for argument in sorted(framework.arguments):
        for attacker in sorted(attackers[argument]):
            selected_defenders = [
                variables[defender]
                for defender in sorted(defenders[attacker])
            ]
            defended = z3.Or(selected_defenders) if selected_defenders else z3.BoolVal(False)
            optimizer.add(z3.Implies(variables[argument], defended))


def _objective_terms(
    z3: Any,
    variables: dict[str, Any],
    objectives: tuple[OptimizationObjective, ...],
    features: tuple[OptimizationFeature, ...],
) -> dict[str, Any]:
    terms = {}
    feature_values: dict[tuple[str, str], int] = {}
    for feature in features:
        if feature.argument not in variables:
            raise ValueError(f"feature references unknown argument: {feature.argument!r}")
        feature_values[(feature.argument, feature.name)] = feature_values.get((feature.argument, feature.name), 0) + feature.value

    for objective in objectives:
        terms[objective.name] = z3.Sum(
            [
                z3.If(
                    variables[argument],
                    objective.weight * feature_values.get((argument, objective.name), 0),
                    0,
                )
                for argument in sorted(variables)
            ]
        )
    return terms


def _model_int(value: Any) -> int:
    if hasattr(value, "as_long"):
        return int(value.as_long())
    return int(str(value))


def _z3_safe_name(argument: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in argument)


def _import_z3() -> Any | None:
    try:
        import z3
    except ImportError:
        return None
    return z3
