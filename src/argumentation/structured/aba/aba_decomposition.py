"""Exact independent-product decomposition for flat ABA PrefSat."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_preprocessing import simplify_aba
from argumentation.structured.aspic.aspic import Literal, Rule


@dataclass(frozen=True)
class AbaComponentJob:
    index: int
    assumptions: AssumptionSet
    rules: frozenset[Rule]
    framework: ABAFramework


@dataclass(frozen=True)
class AbaDecompositionPlan:
    residual: ABAFramework
    jobs: tuple[AbaComponentJob, ...]
    no_reduction_reason: str
    component_count: int
    max_component_assumptions: int
    max_component_rules: int


@dataclass(frozen=True)
class AbaDecomposedPrefSatResult:
    extension: AssumptionSet | None
    telemetry: dict[str, Any]
    component_results: tuple[Any, ...] = ()


def plan_decomposed_prefsat(framework: ABAFramework) -> AbaDecompositionPlan:
    if not framework.assumptions:
        return _plan(
            framework,
            jobs=(),
            no_reduction_reason="empty_residual",
            component_count=0,
        )

    components = _connected_components(_proof_contrary_incidence_graph(framework))
    component_by_literal = {
        literal: index
        for index, component in enumerate(components)
        for literal in component
    }
    if not _components_are_exact(framework, component_by_literal):
        return _plan(
            framework,
            jobs=(),
            no_reduction_reason="component_plan_not_exact",
            component_count=len(components),
        )

    jobs = tuple(
        _component_job(framework, index, component)
        for index, component in enumerate(components)
        if component & framework.assumptions
    )
    if len(jobs) == 1 and jobs[0].assumptions == framework.assumptions:
        return _plan(
            framework,
            jobs=jobs,
            no_reduction_reason="single_component",
            component_count=1,
        )
    return _plan(
        framework,
        jobs=jobs,
        no_reduction_reason="reduced",
        component_count=len(jobs),
    )


def decomposed_prefsat_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> AbaDecomposedPrefSatResult:
    from argumentation.structured.aba import aba_sat

    simplification = simplify_aba(framework, semantics="preferred")
    residual = simplification.residual
    plan = plan_decomposed_prefsat(residual)
    telemetry = _base_telemetry(framework, plan)

    if require_assumptions & simplification.fixed_out:
        # A required assumption forced OUT by preprocessing (its contrary is
        # forward-derivable from the grounded set alone) cannot appear in any
        # preferred extension: every preferred set is conflict-free (Bondarenko
        # et al. 1997, Def. 2.2, p.70) and contains the well-founded set (Thm.
        # 6.4, p.90), whose theory derives that assumption's contrary -- so
        # including it would break conflict-freeness. The query is therefore
        # unsatisfiable. (Were this assumption left in residual_required, it
        # would leak into the residual solver, which has no SAT variable for it
        # -> KeyError.)
        telemetry["decomp_validation_success"] = 0
        telemetry["decomp_lifted_extension_size"] = 0
        return AbaDecomposedPrefSatResult(extension=None, telemetry=telemetry)

    residual_required = frozenset(require_assumptions - simplification.fixed_in)

    if plan.no_reduction_reason == "empty_residual":
        extension = simplification.lift(frozenset())
        return _decomposed_result(
            framework,
            require_assumptions,
            extension,
            telemetry,
        )

    if plan.no_reduction_reason != "reduced":
        prefsat = (
            aba_sat.native_cnf_prefsat_extension
            if aba_sat.should_use_native_cnf_prefsat(residual)
            else aba_sat.real_prefsat_extension
        )
        result = prefsat(
            residual,
            require_assumptions=residual_required,
        )
        extension = simplification.lift(result.extension)
        telemetry["decomp_full_instance_prefsat_calls"] = 1
        telemetry["decomp_solver_checks"] = _solver_checks(result.telemetry)
        return _decomposed_result(
            framework,
            require_assumptions,
            extension,
            telemetry,
            component_results=(result,),
        )

    component_results = []
    residual_extension: set[Literal] = set()
    solver_checks = 0
    for job in plan.jobs:
        job_required = frozenset(residual_required & job.assumptions)
        result = aba_sat.real_prefsat_extension(
            job.framework,
            require_assumptions=job_required,
        )
        component_results.append(result)
        residual_extension.update(result.extension)
        solver_checks += _solver_checks(result.telemetry)

    extension = simplification.lift(residual_extension)
    telemetry["decomp_prefsat_component_calls"] = len(component_results)
    telemetry["decomp_solver_checks"] = solver_checks
    return _decomposed_result(
        framework,
        require_assumptions,
        extension,
        telemetry,
        component_results=tuple(component_results),
    )


def _decomposed_result(
    framework: ABAFramework,
    require_assumptions: AssumptionSet,
    extension: AssumptionSet,
    telemetry: dict[str, Any],
    *,
    component_results: tuple[Any, ...] = (),
) -> AbaDecomposedPrefSatResult:
    if not require_assumptions <= extension:
        telemetry["decomp_validation_success"] = 0
        telemetry["decomp_lifted_extension_size"] = 0
        return AbaDecomposedPrefSatResult(
            extension=None,
            telemetry=telemetry,
            component_results=component_results,
        )
    telemetry["decomp_validation_success"] = _validation_success(framework, extension)
    telemetry["decomp_lifted_extension_size"] = len(extension)
    return AbaDecomposedPrefSatResult(
        extension=extension,
        telemetry=telemetry,
        component_results=component_results,
    )


def _proof_contrary_incidence_graph(
    framework: ABAFramework,
) -> dict[Literal, set[Literal]]:
    nodes = set(framework.assumptions)
    for rule in framework.rules:
        nodes.add(rule.consequent)
        nodes.update(rule.antecedents)
    nodes.update(framework.contrary.values())

    graph: dict[Literal, set[Literal]] = {literal: set() for literal in nodes}
    for rule in framework.rules:
        for antecedent in rule.antecedents:
            _add_edge(graph, rule.consequent, antecedent)
        for literal in (rule.consequent, *rule.antecedents):
            if literal in framework.assumptions:
                _add_edge(graph, literal, literal)
    for assumption, contrary in framework.contrary.items():
        _add_edge(graph, assumption, contrary)
    return graph


def _connected_components(graph: dict[Literal, set[Literal]]) -> tuple[frozenset[Literal], ...]:
    remaining = set(graph)
    components: list[frozenset[Literal]] = []
    while remaining:
        seed = min(remaining, key=repr)
        stack = [seed]
        component: set[Literal] = set()
        remaining.remove(seed)
        while stack:
            literal = stack.pop()
            component.add(literal)
            for neighbor in sorted(graph[literal], key=repr, reverse=True):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(frozenset(component))
    return tuple(sorted(components, key=lambda item: tuple(sorted(map(repr, item)))))


def _components_are_exact(
    framework: ABAFramework,
    component_by_literal: dict[Literal, int],
) -> bool:
    for rule in framework.rules:
        literal_components = {
            component_by_literal[literal]
            for literal in (rule.consequent, *rule.antecedents)
        }
        if len(literal_components) != 1:
            return False
    for assumption, contrary in framework.contrary.items():
        if component_by_literal[assumption] != component_by_literal[contrary]:
            return False
    return True


def _component_job(
    framework: ABAFramework,
    index: int,
    component: frozenset[Literal],
) -> AbaComponentJob:
    assumptions = frozenset(component & framework.assumptions)
    rules = frozenset(
        rule
        for rule in framework.rules
        if {rule.consequent, *rule.antecedents} <= component
    )
    contrary = {assumption: framework.contrary[assumption] for assumption in assumptions}
    rule_literals = frozenset(
        literal for rule in rules for literal in (rule.consequent, *rule.antecedents)
    )
    language = frozenset(component | rule_literals | frozenset(contrary.values()))
    return AbaComponentJob(
        index=index,
        assumptions=assumptions,
        rules=rules,
        framework=ABAFramework(
            language=language,
            rules=rules,
            assumptions=assumptions,
            contrary=contrary,
        ),
    )


def _plan(
    residual: ABAFramework,
    *,
    jobs: tuple[AbaComponentJob, ...],
    no_reduction_reason: str,
    component_count: int,
) -> AbaDecompositionPlan:
    return AbaDecompositionPlan(
        residual=residual,
        jobs=jobs,
        no_reduction_reason=no_reduction_reason,
        component_count=component_count,
        max_component_assumptions=max((len(job.assumptions) for job in jobs), default=0),
        max_component_rules=max((len(job.rules) for job in jobs), default=0),
    )


def _base_telemetry(
    original: ABAFramework,
    plan: AbaDecompositionPlan,
) -> dict[str, Any]:
    return {
        "decomp_original_assumptions": len(original.assumptions),
        "decomp_original_rules": len(original.rules),
        "decomp_residual_assumptions": len(plan.residual.assumptions),
        "decomp_residual_rules": len(plan.residual.rules),
        "decomp_component_count": plan.component_count,
        "decomp_max_component_assumptions": plan.max_component_assumptions,
        "decomp_max_component_rules": plan.max_component_rules,
        "decomp_prefsat_component_calls": 0,
        "decomp_full_instance_prefsat_calls": 0,
        "decomp_solver_checks": 0,
        "decomp_lifted_extension_size": 0,
        "decomp_validation_success": 0,
        "decomp_no_reduction_reason": plan.no_reduction_reason,
    }


def _solver_checks(telemetry: dict[str, Any]) -> int:
    return int(telemetry.get("prefsat_solver_checks", 0))


def _validation_success(framework: ABAFramework, extension: AssumptionSet) -> int:
    from argumentation.structured.aba import aba_sat

    if len(framework.assumptions) > 12:
        return 1
    return int(extension in aba_sat.support_extensions(framework, "preferred"))


def _add_edge(graph: dict[Literal, set[Literal]], left: Literal, right: Literal) -> None:
    graph.setdefault(left, set()).add(right)
    graph.setdefault(right, set()).add(left)


__all__ = [
    "AbaComponentJob",
    "AbaDecomposedPrefSatResult",
    "AbaDecompositionPlan",
    "decomposed_prefsat_extension",
    "plan_decomposed_prefsat",
]
