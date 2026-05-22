from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_decomposition import plan_decomposed_prefsat
from argumentation.structured.aba.aba_preprocessing import simplify_aba
from argumentation.structured.aba.aba_route_policy import native_cnf_prefsat_dense_shape
from argumentation.structured.aspic.aspic import GroundAtom, Literal
from argumentation.iccma import parse_aba
from tools.iccma2025_run_native import TASK_TO_SEMANTICS, run_child as run_native_child


DEFAULT_ROOT = Path("data") / "iccma" / "2025"
DEFAULT_DATA_ROOT = Path("data") / "iccma"
DEFAULT_SUBTRACKS = ("SE-PR", "SE-ST")
DEFAULT_BACKENDS = ("auto", "asp", "sat")

TASK_PREFIXES = {
    "DC": "credulous-acceptance",
    "DS": "skeptical-acceptance",
    "SE": "single-extension",
}

ASSUMPTION_SIZE_THRESHOLDS = {"small_max": 50, "medium_max": 150}
RULE_DENSITY_THRESHOLDS = {"sparse_max": 5.0, "medium_max": 25.0}
MAX_ARITY_THRESHOLDS = {"low_max": 2, "medium_max": 5}
GROUNDED_SHAPE_COST_LIMIT = 1000
VALIDATION_COST_LIMIT = 1000
RULE_BODY_OVERLAP_EXACT_PAIR_LIMIT = 100_000
ROUTE_REQUIRED_FIELDS = frozenset(
    {
        "is_flat",
        "is_normal",
        "assumptions",
        "rule_density",
        "p_acyclic",
        "tau_aba_primal_width_proxy",
        "stable_obstruction_count",
        "dependency_scc_max_size",
        "contrary_target_in_degree_max",
        "closure_growth_sample",
        "decomp_component_count",
        "decomp_max_component_assumptions",
        "decomp_no_reduction_reason",
    }
)


@dataclass(frozen=True)
class AbaShape:
    is_flat: bool
    is_normal: bool
    assumption_count: int
    atom_count: int
    rule_count: int
    contrary_count: int
    assumptions: int
    language_literals: int
    rules: int
    contraries: int
    distinct_contrary_literals: int
    avg_rule_arity: float
    max_rule_arity: int
    zero_body_rules: int
    rules_per_head_max: int
    rules_per_head_avg: float
    rules_per_contrary_max: int
    rules_per_contrary_avg: float
    assumption_to_language_ratio: float
    rule_to_assumption_ratio: float
    grounded_fixed_in: int
    grounded_fixed_out: int
    residual_assumptions: int
    residual_rules: int
    decomp_component_count: int
    decomp_max_component_assumptions: int
    decomp_no_reduction_reason: str
    preprocessing_collapsed: bool
    grounded_shape_status: str
    rule_density: float
    dependency_scc_count: int
    dependency_scc_max_size: int
    dependency_cycle_count_or_flag: int
    p_acyclic: bool
    contrary_target_in_degree_max: int
    contrary_target_in_degree_avg: float
    contrary_target_entropy: float
    assumption_incidence_width_proxy: int
    rule_body_overlap_max: int
    rule_body_overlap_avg: float
    closure_growth_sample: float
    grounded_iteration_count: int
    grounded_in_count: int
    grounded_out_count: int
    stable_obstruction_count: int
    tau_aba_primal_width_proxy: int


@dataclass(frozen=True)
class BenchmarkJob:
    year: int | None
    track: str
    subtrack: str
    instance_kind: str
    instance: str
    root: Path
    path: Path
    arguments_or_atoms: int | None = None


@dataclass(frozen=True)
class RouteCandidate:
    backend: str
    predicate: str
    production: bool
    evidence_id: str | None
    reason: dict[str, Any]


def compute_aba_shape(framework: ABAFramework) -> AbaShape:
    arities = [len(rule.antecedents) for rule in framework.rules]
    rules_by_head = Counter(rule.consequent for rule in framework.rules)
    contrary_literals = tuple(framework.contrary.values())
    contrary_target_counts = Counter(contrary_literals)
    rules_by_contrary = Counter(
        rule.consequent for rule in framework.rules if rule.consequent in set(contrary_literals)
    )
    assumptions = len(framework.assumptions)
    language_literals = len(framework.language)
    rules = len(framework.rules)
    grounded = _grounded_shape_fields(framework, assumptions=assumptions, rules=rules)
    decomposition = _decomposition_shape_fields(
        framework,
        assumptions=assumptions,
        rules=rules,
    )
    dependency = _dependency_shape(framework)
    rule_density = _ratio(rules, assumptions)
    rule_body_overlap = _rule_body_overlap(framework)
    grounded_iterations = (
        _grounded_iteration_count(framework)
        if assumptions * rules <= GROUNDED_SHAPE_COST_LIMIT
        else 0
    )
    return AbaShape(
        is_flat=_is_flat(framework),
        is_normal=_is_normal_candidate(framework),
        assumption_count=assumptions,
        atom_count=language_literals,
        rule_count=rules,
        contrary_count=len(framework.contrary),
        assumptions=assumptions,
        language_literals=language_literals,
        rules=rules,
        contraries=len(framework.contrary),
        distinct_contrary_literals=len(set(contrary_literals)),
        avg_rule_arity=_average(arities),
        max_rule_arity=max(arities, default=0),
        zero_body_rules=sum(1 for arity in arities if arity == 0),
        rules_per_head_max=max(rules_by_head.values(), default=0),
        rules_per_head_avg=_average(rules_by_head.values()),
        rules_per_contrary_max=max(rules_by_contrary.values(), default=0),
        rules_per_contrary_avg=_average(rules_by_contrary.values()),
        assumption_to_language_ratio=_ratio(assumptions, language_literals),
        rule_to_assumption_ratio=_ratio(rules, assumptions),
        grounded_fixed_in=grounded["grounded_fixed_in"],
        grounded_fixed_out=grounded["grounded_fixed_out"],
        residual_assumptions=grounded["residual_assumptions"],
        residual_rules=grounded["residual_rules"],
        decomp_component_count=decomposition["decomp_component_count"],
        decomp_max_component_assumptions=decomposition["decomp_max_component_assumptions"],
        decomp_no_reduction_reason=decomposition["decomp_no_reduction_reason"],
        preprocessing_collapsed=grounded["preprocessing_collapsed"],
        grounded_shape_status=grounded["grounded_shape_status"],
        rule_density=rule_density,
        dependency_scc_count=dependency["scc_count"],
        dependency_scc_max_size=dependency["scc_max_size"],
        dependency_cycle_count_or_flag=dependency["cycle_count_or_flag"],
        p_acyclic=dependency["p_acyclic"],
        contrary_target_in_degree_max=max(contrary_target_counts.values(), default=0),
        contrary_target_in_degree_avg=_average(contrary_target_counts.values()),
        contrary_target_entropy=_entropy(contrary_target_counts.values()),
        assumption_incidence_width_proxy=_assumption_incidence_width_proxy(framework),
        rule_body_overlap_max=rule_body_overlap["max"],
        rule_body_overlap_avg=rule_body_overlap["avg"],
        closure_growth_sample=_closure_growth_sample(framework),
        grounded_iteration_count=grounded_iterations,
        grounded_in_count=len(native_aba.grounded_extension(framework))
        if assumptions * rules <= GROUNDED_SHAPE_COST_LIMIT
        else 0,
        grounded_out_count=grounded["grounded_fixed_out"],
        stable_obstruction_count=_stable_obstruction_count(framework),
        tau_aba_primal_width_proxy=_tau_aba_primal_width_proxy(framework),
    )


def _grounded_shape_fields(
    framework: ABAFramework,
    *,
    assumptions: int,
    rules: int,
) -> dict[str, Any]:
    if assumptions * rules > GROUNDED_SHAPE_COST_LIMIT:
        return {
            "grounded_fixed_in": 0,
            "grounded_fixed_out": 0,
            "residual_assumptions": assumptions,
            "residual_rules": rules,
            "preprocessing_collapsed": False,
            "grounded_shape_status": "skipped_cost",
        }
    simplification = simplify_aba(framework, semantics="preferred")
    return {
        "grounded_fixed_in": len(simplification.fixed_in),
        "grounded_fixed_out": len(simplification.fixed_out),
        "residual_assumptions": len(simplification.residual.assumptions),
        "residual_rules": len(simplification.residual.rules),
        "preprocessing_collapsed": not simplification.is_trivial,
        "grounded_shape_status": "exact",
    }


def _decomposition_shape_fields(
    framework: ABAFramework,
    *,
    assumptions: int,
    rules: int,
) -> dict[str, Any]:
    if assumptions * rules > GROUNDED_SHAPE_COST_LIMIT:
        return {
            "decomp_component_count": 0,
            "decomp_max_component_assumptions": assumptions,
            "decomp_no_reduction_reason": "component_plan_not_exact",
        }
    plan = plan_decomposed_prefsat(
        simplify_aba(framework, semantics="preferred").residual
    )
    return {
        "decomp_component_count": plan.component_count,
        "decomp_max_component_assumptions": plan.max_component_assumptions,
        "decomp_no_reduction_reason": plan.no_reduction_reason,
    }


def _average(values: Iterable[int]) -> float:
    materialized = list(values)
    if not materialized:
        return 0.0
    return sum(materialized) / len(materialized)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _entropy(counts: Iterable[int]) -> float:
    materialized = [count for count in counts if count > 0]
    total = sum(materialized)
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in materialized)


def _is_flat(framework: ABAFramework) -> bool:
    return not any(rule.consequent in framework.assumptions for rule in framework.rules)


def _is_normal_candidate(framework: ABAFramework) -> bool:
    """Cheap structural candidate for Dimopoulos-style stable/preferred collapse.

    The package currently accepts flat ABA only.  For routing we only need a
    conservative flag: every assumption's contrary must be derivable from that
    assumption alone or not derivable at all.  Small exhaustive semantic tests
    are responsible for guarding any stronger production use of this field.
    """

    for assumption in framework.assumptions:
        contrary = framework.contrary[assumption]
        if contrary in _closure(framework, frozenset({assumption})):
            continue
        if contrary in _closure(framework, framework.assumptions):
            return False
    return True


def _dependency_shape(framework: ABAFramework) -> dict[str, Any]:
    nodes = set(framework.language) - set(framework.assumptions)
    edges: dict[Literal, set[Literal]] = {node: set() for node in nodes}
    self_loop = False
    for rule in framework.rules:
        if rule.consequent in framework.assumptions:
            continue
        nodes.add(rule.consequent)
        edges.setdefault(rule.consequent, set())
        for antecedent in rule.antecedents:
            if antecedent in framework.assumptions:
                continue
            nodes.add(antecedent)
            edges.setdefault(antecedent, set())
            edges[antecedent].add(rule.consequent)
            if antecedent == rule.consequent:
                self_loop = True
    components = _strongly_connected_components(nodes, edges)
    cyclic_components = [
        component for component in components if len(component) > 1 or any(node in edges.get(node, ()) for node in component)
    ]
    if self_loop and not cyclic_components:
        cyclic_components = [frozenset()]
    return {
        "scc_count": len(components),
        "scc_max_size": max((len(component) for component in components), default=0),
        "cycle_count_or_flag": 1 if cyclic_components else 0,
        "p_acyclic": not cyclic_components,
    }


def _strongly_connected_components(
    nodes: set[Literal],
    edges: dict[Literal, set[Literal]],
) -> list[frozenset[Literal]]:
    all_nodes = set(nodes)
    reverse_edges: dict[Literal, set[Literal]] = {node: set() for node in all_nodes}
    for source, successors in edges.items():
        all_nodes.add(source)
        reverse_edges.setdefault(source, set())
        for successor in successors:
            all_nodes.add(successor)
            reverse_edges.setdefault(successor, set()).add(source)

    seen: set[Literal] = set()
    finish_order: list[Literal] = []
    for seed in sorted(all_nodes, key=repr):
        if seed in seen:
            continue
        stack: list[tuple[Literal, bool]] = [(seed, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                finish_order.append(node)
                continue
            if node in seen:
                continue
            seen.add(node)
            stack.append((node, True))
            for successor in sorted(edges.get(node, ()), key=repr, reverse=True):
                if successor not in seen:
                    stack.append((successor, False))

    components: list[frozenset[Literal]] = []
    assigned: set[Literal] = set()
    for seed in reversed(finish_order):
        if seed in assigned:
            continue
        component: set[Literal] = set()
        stack = [seed]
        assigned.add(seed)
        while stack:
            node = stack.pop()
            component.add(node)
            for predecessor in sorted(reverse_edges.get(node, ()), key=repr, reverse=True):
                if predecessor not in assigned:
                    assigned.add(predecessor)
                    stack.append(predecessor)
        components.append(frozenset(component))
    return components


def _closure(framework: ABAFramework, premises: AssumptionSet) -> frozenset[Literal]:
    closure = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(antecedent in closure for antecedent in rule.antecedents) and rule.consequent not in closure:
                closure.add(rule.consequent)
                changed = True
    return frozenset(closure)


def _grounded_iteration_count(framework: ABAFramework) -> int:
    current = frozenset()
    iterations = 0
    while True:
        next_extension = native_aba.def_operator(framework, current)
        if next_extension == current:
            return iterations
        iterations += 1
        if iterations > len(framework.assumptions):
            return iterations
        current = next_extension


def _assumption_incidence_width_proxy(framework: ABAFramework) -> int:
    incidence = Counter()
    for rule in framework.rules:
        for antecedent in rule.antecedents:
            if antecedent in framework.assumptions:
                incidence[antecedent] += 1
    for assumption, contrary in framework.contrary.items():
        incidence[assumption] += 1
        if contrary in framework.assumptions:
            incidence[contrary] += 1
    return max(incidence.values(), default=0)


def _rule_body_overlap(framework: ABAFramework) -> dict[str, float | int]:
    bodies = [frozenset(rule.antecedents) for rule in framework.rules]
    pair_count = len(bodies) * (len(bodies) - 1) // 2
    if pair_count == 0:
        return {"max": 0, "avg": 0.0}

    literal_counts = Counter(literal for body in bodies for literal in body)
    total_overlap = sum(count * (count - 1) // 2 for count in literal_counts.values())
    avg_overlap = total_overlap / pair_count
    if pair_count <= RULE_BODY_OVERLAP_EXACT_PAIR_LIMIT:
        max_overlap = 0
        for left_index, left in enumerate(bodies):
            for right in bodies[left_index + 1 :]:
                max_overlap = max(max_overlap, len(left & right))
        return {"max": max_overlap, "avg": avg_overlap}

    duplicate_body_counts = Counter(bodies)
    duplicate_body_max = max(
        (len(body) for body, count in duplicate_body_counts.items() if count > 1),
        default=0,
    )
    shared_literal_max = 1 if any(count > 1 for count in literal_counts.values()) else 0
    return {"max": max(duplicate_body_max, shared_literal_max), "avg": avg_overlap}


def _closure_growth_sample(framework: ABAFramework) -> float:
    if not framework.language:
        return 0.0
    samples: list[AssumptionSet] = [frozenset(), framework.assumptions]
    samples.extend(frozenset({assumption}) for assumption in sorted(framework.assumptions, key=repr)[:5])
    growth = [
        _ratio(len(_closure(framework, sample)) - len(sample), len(framework.language))
        for sample in samples
    ]
    return _average(int(value * 1_000_000) for value in growth) / 1_000_000


def _stable_obstruction_count(framework: ABAFramework) -> int:
    return sum(
        1
        for assumption in framework.assumptions
        if framework.contrary[assumption] in _closure(framework, frozenset({assumption}))
    )


def _tau_aba_primal_width_proxy(framework: ABAFramework) -> int:
    neighbors: dict[object, set[object]] = defaultdict(set)

    def connect(left: object, right: object) -> None:
        neighbors[left].add(right)
        neighbors[right].add(left)

    for literal in framework.language:
        neighbors.setdefault(("atom", literal), set())
    for assumption in framework.assumptions:
        connect(("atom", assumption), ("asm", assumption))
    for index, rule in enumerate(sorted(framework.rules, key=repr)):
        rule_node = ("rule", index)
        neighbors.setdefault(rule_node, set())
        connect(rule_node, ("atom", rule.consequent))
        for antecedent in rule.antecedents:
            connect(rule_node, ("atom", antecedent))
    for assumption, contrary in framework.contrary.items():
        connect(("atom", assumption), ("atom", contrary))
    return max((len(values) for values in neighbors.values()), default=0)


def solver_class(instance_kind: object, subtrack: object) -> str:
    parts = str(subtrack).split("-", maxsplit=1)
    if len(parts) != 2:
        return f"{instance_kind}/unknown/{subtrack}"
    task_prefix, semantic_tag = parts
    task = TASK_PREFIXES.get(task_prefix, task_prefix.lower())
    semantics = TASK_TO_SEMANTICS.get(semantic_tag, semantic_tag.lower())
    return f"{instance_kind}/{task}/{semantics}"


def shape_buckets(shape: AbaShape, solver_class_name: str) -> dict[str, str]:
    return {
        "assumption_size": _bucket_int(
            shape.assumptions,
            small_max=ASSUMPTION_SIZE_THRESHOLDS["small_max"],
            medium_max=ASSUMPTION_SIZE_THRESHOLDS["medium_max"],
        ),
        "rule_density": _bucket_float(
            shape.rule_to_assumption_ratio,
            sparse_max=RULE_DENSITY_THRESHOLDS["sparse_max"],
            medium_max=RULE_DENSITY_THRESHOLDS["medium_max"],
        ),
        "max_arity": _bucket_int(
            shape.max_rule_arity,
            small_max=MAX_ARITY_THRESHOLDS["low_max"],
            medium_max=MAX_ARITY_THRESHOLDS["medium_max"],
            labels=("low", "medium", "high"),
        ),
        "preprocessing": "collapsed" if shape.preprocessing_collapsed else "not_collapsed",
        "solver_class": solver_class_name,
    }


def route_candidates(
    shape: AbaShape,
    solver_class_name: str,
    *,
    available_backends: Iterable[str] = DEFAULT_BACKENDS,
    timeout_budget_class: str | None = None,
) -> list[RouteCandidate]:
    return route_candidates_from_shape_data(
        asdict(shape),
        solver_class_name,
        available_backends=available_backends,
        timeout_budget_class=timeout_budget_class,
    )


def route_candidates_from_shape_data(
    shape_data: Mapping[str, Any],
    solver_class_name: str,
    *,
    available_backends: Iterable[str] = DEFAULT_BACKENDS,
    timeout_budget_class: str | None = None,
) -> list[RouteCandidate]:
    if not ROUTE_REQUIRED_FIELDS <= set(shape_data):
        return []

    available = frozenset(available_backends)
    candidates: list[RouteCandidate] = []
    if (
        "sat" in available
        and solver_class_name == "aba/single-extension/stable"
        and bool(shape_data["is_flat"])
        and int(shape_data["assumptions"]) > ASSUMPTION_SIZE_THRESHOLDS["medium_max"]
        and float(shape_data["rule_density"]) > RULE_DENSITY_THRESHOLDS["medium_max"]
    ):
        candidates.append(
            RouteCandidate(
                backend="sat",
                predicate="large_dense_stable_sat_route",
                production=True,
                evidence_id="aba-c1-stable-route-2026-05-17",
                reason={
                    "paper": "Dimopoulos_2002_ComputationalComplexityAssumption-basedArgumentation",
                    "fields": [
                        "is_flat",
                        "assumptions",
                        "rule_density",
                        "stable_obstruction_count",
                    ],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if (
        "sat" in available
        and solver_class_name == "aba/single-extension/preferred"
        and native_cnf_prefsat_dense_shape(
            is_flat=bool(shape_data["is_flat"]),
            assumptions=int(shape_data["assumptions"]),
            rule_density=float(shape_data["rule_density"]),
        )
    ):
        candidates.append(
            RouteCandidate(
                backend="sat",
                predicate="native_cnf_dense_prefsat_route",
                production=True,
                evidence_id="aba-native-cnf-prefsat-2026-05-18",
                reason={
                    "paper": "Cerutti_2013_ComputingPreferredExtensionsAbstract; Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers; Thimm_2021_FudgeLight-weightSolverAbstract; Dvorak_2014_ComplexitySensitiveDecisionProcedures",
                    "fields": [
                        "is_flat",
                        "assumptions",
                        "rule_density",
                        "decomp_no_reduction_reason",
                    ],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if (
        "sat" in available
        and solver_class_name == "aba/single-extension/preferred"
        and bool(shape_data["is_flat"])
        and str(shape_data["decomp_no_reduction_reason"]) == "reduced"
    ):
        candidates.append(
            RouteCandidate(
                backend="sat",
                predicate="decomposed_prefsat_reduced_product",
                production=True,
                evidence_id="aba-decomposed-prefsat-composition-2026-05-18",
                reason={
                    "paper": "Cerutti_2013_ComputingPreferredExtensionsAbstract; Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers; Niskanen_2020_ToksiaEfficientAbstractArgumentation",
                    "fields": [
                        "is_flat",
                        "decomp_component_count",
                        "decomp_max_component_assumptions",
                        "decomp_no_reduction_reason",
                    ],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if "asp" in available and bool(shape_data["is_flat"]):
        candidates.append(
            RouteCandidate(
                backend="asp",
                predicate="flat_direct_asp_candidate",
                production=False,
                evidence_id=None,
                reason={
                    "paper": "Lehtonen_2021_DeclarativeAlgorithmsComplexityResults",
                    "fields": ["is_flat", "rule_density", "stable_obstruction_count"],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if bool(shape_data["p_acyclic"]):
        candidates.append(
            RouteCandidate(
                backend="future_dispute_search",
                predicate="p_acyclic_dispute_candidate",
                production=False,
                evidence_id=None,
                reason={
                    "paper": "Toni_2013_GeneralisedFrameworkDisputeDerivations",
                    "fields": ["p_acyclic", "dependency_scc_max_size"],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if int(shape_data["tau_aba_primal_width_proxy"]) <= 4:
        candidates.append(
            RouteCandidate(
                backend="future_tree_decomposition",
                predicate="low_tau_aba_width_candidate",
                production=False,
                evidence_id=None,
                reason={
                    "paper": "Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions",
                    "fields": [
                        "tau_aba_primal_width_proxy",
                        "dependency_scc_max_size",
                        "contrary_target_in_degree_max",
                    ],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    if bool(shape_data["is_normal"]):
        candidates.append(
            RouteCandidate(
                backend="semantic_equivalence",
                predicate="normal_preferred_stable_coincidence_candidate",
                production=False,
                evidence_id=None,
                reason={
                    "paper": "Dimopoulos_2002_ComputationalComplexityAssumption-basedArgumentation",
                    "fields": ["is_normal", "stable_obstruction_count"],
                    "solver_class": solver_class_name,
                    "timeout_budget_class": timeout_budget_class,
                },
            )
        )
    return candidates


def shape_bucket_id(buckets: Mapping[str, str]) -> str:
    return "|".join(f"{key}={value}" for key, value in sorted(buckets.items()))


def backend_outcomes(backend_results: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    return {
        backend: str(result.get("status", "unknown"))
        for backend, result in sorted(backend_results.items())
    }


def witness_validation_results(
    backend_results: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    return {
        backend: str(result.get("validation", {}).get("status", "not_checked"))
        for backend, result in sorted(backend_results.items())
    }


def route_counterexamples(
    candidates: Iterable[RouteCandidate],
    backend_results: Mapping[str, Mapping[str, Any]],
    *,
    best_solved: str | None,
) -> dict[str, list[dict[str, Any]]]:
    observed: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        examples: list[dict[str, Any]] = []
        result = backend_results.get(candidate.backend)
        if result is not None:
            validation_status = str(result.get("validation", {}).get("status", "not_checked"))
            status = str(result.get("status", "unknown"))
            if status != "solved" or validation_status == "invalid":
                examples.append(
                    {
                        "backend": candidate.backend,
                        "status": status,
                        "validation_status": validation_status,
                        "best_solved_backend": best_solved,
                    }
                )
            elif best_solved is not None and best_solved != candidate.backend:
                examples.append(
                    {
                        "backend": candidate.backend,
                        "status": status,
                        "validation_status": validation_status,
                        "best_solved_backend": best_solved,
                    }
                )
        observed[candidate.predicate] = examples
    return observed


def _bucket_int(
    value: int,
    *,
    small_max: int,
    medium_max: int,
    labels: tuple[str, str, str] = ("small", "medium", "large"),
) -> str:
    if value <= small_max:
        return labels[0]
    if value <= medium_max:
        return labels[1]
    return labels[2]


def _bucket_float(value: float, *, sparse_max: float, medium_max: float) -> str:
    if value <= sparse_max:
        return "sparse"
    if value <= medium_max:
        return "medium"
    return "dense"


def build_jobs_from_manifest(
    rows: list[dict[str, Any]],
    *,
    data_root: Path,
    years: set[int] | None,
    subtracks: set[str] | None,
    instance_kind: str,
) -> list[BenchmarkJob]:
    jobs: list[BenchmarkJob] = []
    seen: set[tuple[int | None, str, str, str, str]] = set()
    for row in rows:
        year = row.get("year")
        if years is not None and year not in years:
            continue
        if row.get("instance_kind") != instance_kind:
            continue
        if subtracks is not None and row.get("subtrack") not in subtracks:
            continue
        key = (
            year,
            str(row.get("track", "")),
            str(row.get("subtrack", "")),
            str(row.get("instance_kind", "")),
            str(row.get("instance", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        root = data_root / str(year)
        path = root / "extracted" / "instances" / Path(*str(row["instance"]).split("/"))
        jobs.append(
            BenchmarkJob(
                year=year,
                track=str(row.get("track", "aba")),
                subtrack=str(row["subtrack"]),
                instance_kind=str(row["instance_kind"]),
                instance=str(row["instance"]),
                root=root,
                path=path,
                arguments_or_atoms=row.get("arguments_or_atoms"),
            )
        )
    return jobs


def build_jobs_from_instances(
    paths: list[Path],
    *,
    root: Path,
    subtracks: tuple[str, ...],
) -> list[BenchmarkJob]:
    jobs: list[BenchmarkJob] = []
    instances_root = root / "extracted" / "instances"
    for path in paths:
        resolved = path.resolve()
        relative = _relative_instance_path(resolved, instances_root.resolve())
        framework = parse_aba(resolved.read_text(encoding="utf-8"))
        for subtrack in subtracks:
            jobs.append(
                BenchmarkJob(
                    year=_year_from_root(root),
                    track="aba",
                    subtrack=subtrack,
                    instance_kind="aba",
                    instance=relative.as_posix(),
                    root=root,
                    path=resolved,
                    arguments_or_atoms=len(framework.language),
                )
            )
    return jobs


def _relative_instance_path(path: Path, instances_root: Path) -> Path:
    try:
        return path.relative_to(instances_root)
    except ValueError as exc:
        raise ValueError(f"explicit instances must live under {instances_root}: {path}") from exc


def _year_from_root(root: Path) -> int | None:
    return int(root.name) if root.name.isdigit() else None


def run_backend_matrix(
    job: BenchmarkJob,
    *,
    framework: ABAFramework,
    backends: tuple[str, ...],
    timeout_seconds: float,
    profile_dir: Path | None = None,
    profile_format: str = "speedscope",
    profile_duration_seconds: float | None = None,
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for backend in backends:
        command = build_backend_command(job, backend=backend, timeout_seconds=timeout_seconds)
        emit_event(
            "aba_shape_backend_start",
            instance=job.instance,
            subtrack=job.subtrack,
            backend=backend,
            command=command,
        )
        started = time.perf_counter()
        result = run_backend_command(
            command,
            job_payload=backend_job(
                job,
                backend=backend,
                timeout_seconds=timeout_seconds,
                profile_path=benchmark_profile_path(
                    profile_dir,
                    job,
                    backend=backend,
                    profile_format=profile_format,
                ),
                profile_format=profile_format,
                profile_duration_seconds=profile_duration_seconds,
                clingo_control_args=clingo_control_args,
                collect_clingo_statistics=collect_clingo_statistics,
            ),
            timeout_seconds=timeout_seconds + 5.0,
        )
        elapsed = time.perf_counter() - started
        materialized = dict(result)
        materialized["elapsed_seconds"] = elapsed
        materialized["validation"] = validate_result(framework, job.subtrack, materialized)
        results[backend] = materialized
        emit_event(
            "aba_shape_backend_done",
            instance=job.instance,
            subtrack=job.subtrack,
            backend=backend,
            status=materialized.get("status"),
            reason=materialized.get("reason"),
        )
    return results


def build_backend_command(
    job: BenchmarkJob,
    *,
    backend: str,
    timeout_seconds: float,
) -> list[str]:
    worker_script = Path(__file__).resolve().with_name("iccma2025_run_native.py")
    command = [
        sys.executable,
        str(worker_script),
        "_worker",
        "{job_path}",
    ]
    return command


def backend_job(
    job: BenchmarkJob,
    *,
    backend: str,
    timeout_seconds: float,
    profile_path: Path | None = None,
    profile_format: str = "speedscope",
    profile_duration_seconds: float | None = None,
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
) -> dict[str, Any]:
    return {
        "root": str(job.root),
        "backend": backend,
        "iccma_binary": None,
        "solver_timeout_seconds": timeout_seconds,
        "clingo_control_args": list(clingo_control_args),
        "collect_clingo_statistics": collect_clingo_statistics,
        "profile_path": str(profile_path) if profile_path is not None else None,
        "profile_format": profile_format,
        "profile_duration_seconds": profile_duration_seconds,
        "instance": {
            "kind": "aba",
            "relative_path": job.instance,
            "arguments_or_atoms": job.arguments_or_atoms,
        },
        "task": {
            "track": job.track,
            "subtrack": job.subtrack,
            "instance_kind": job.instance_kind,
        },
    }


def benchmark_profile_path(
    profile_dir: Path | None,
    job: BenchmarkJob,
    *,
    backend: str,
    profile_format: str,
) -> Path | None:
    if profile_dir is None:
        return None
    identity = "\n".join(
        [
            str(job.year),
            job.track,
            job.subtrack,
            job.instance_kind,
            backend,
            job.instance,
        ]
    )
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
    leaf = Path(job.instance).name
    safe_leaf = re.sub(r"[^A-Za-z0-9_.-]+", "_", leaf)[:80] or "instance"
    extension = "json" if profile_format in {"speedscope", "chrometrace"} else "txt"
    return (
        profile_dir
        / f"{job.track}-{job.subtrack}-{backend}-{safe_leaf}-{digest}.{profile_format}.{extension}"
    )


def run_backend_command(
    command_template: list[str],
    *,
    job_payload: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    _ = command_template
    result = dict(run_native_child(job_payload, timeout_seconds=timeout_seconds))
    result.setdefault("stdout", "")
    result.setdefault("stderr", "")
    result.setdefault("returncode", None)
    return result


def _parse_json_line(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def validate_result(framework: ABAFramework, subtrack: str, result: dict[str, Any]) -> dict[str, Any]:
    if result.get("status") != "solved":
        return {"status": "not_checked", "reason": "solver did not return solved"}
    witness_text = result.get("witness")
    if witness_text is None:
        return {"status": "not_checked", "reason": "no witness"}
    witness = _parse_witness(framework, str(witness_text))
    validation_cost = len(framework.assumptions) * max(1, len(framework.rules))
    if validation_cost > VALIDATION_COST_LIMIT:
        return _large_witness_validation(framework, subtrack, witness)
    semantics = solver_class("aba", subtrack).split("/")[-1]
    if semantics == "stable":
        valid = native_aba.closed(framework, witness) and native_aba.conflict_free(framework, witness) and all(
            native_aba.attacks(framework, witness, frozenset({assumption}))
            for assumption in framework.assumptions - witness
        )
        return {"status": "valid" if valid else "invalid", "check": "stable"}
    if semantics == "preferred":
        valid = native_aba.admissible(framework, witness)
        return {
            "status": "valid" if valid else "invalid",
            "check": "preferred_admissible_necessary",
        }
    return {"status": "not_checked", "reason": f"unsupported semantics: {semantics}"}


def _large_witness_validation(
    framework: ABAFramework,
    subtrack: str,
    witness: AssumptionSet,
) -> dict[str, Any]:
    from argumentation.structured.aba import aba_sat

    semantics = solver_class("aba", subtrack).split("/")[-1]
    if not witness <= framework.assumptions:
        return {"status": "invalid", "check": f"{semantics}_large_witness_subset"}
    closure = aba_sat._prefsat_closure(framework, witness)
    conflict_free = not any(
        framework.contrary[assumption] in closure
        for assumption in witness
    )
    if semantics == "preferred":
        return {
            "status": "valid" if conflict_free else "invalid",
            "check": "preferred_large_conflict_free_necessary",
        }
    if semantics == "stable":
        attacks_all_outside = all(
            framework.contrary[assumption] in closure
            for assumption in framework.assumptions - witness
        )
        return {
            "status": "valid" if conflict_free and attacks_all_outside else "invalid",
            "check": "stable_large_closure",
        }
    return {"status": "not_checked", "reason": f"unsupported semantics: {semantics}"}


def _parse_witness(framework: ABAFramework, witness_text: str) -> AssumptionSet:
    assumptions_by_repr = {repr(assumption): assumption for assumption in framework.assumptions}
    result: set[Literal] = set()
    for token in witness_text.split():
        assumption = assumptions_by_repr.get(token)
        if assumption is None:
            assumption = Literal(GroundAtom(token))
        result.add(assumption)
    return frozenset(result)


def best_solved_backend(backend_results: dict[str, dict[str, Any]]) -> str | None:
    solved = [
        (backend, result)
        for backend, result in backend_results.items()
        if result.get("status") == "solved" and result.get("validation", {}).get("status") != "invalid"
    ]
    if not solved:
        return None
    return min(solved, key=lambda item: float(item[1].get("elapsed_seconds", float("inf"))))[0]


def benchmark_rows(
    jobs: list[BenchmarkJob],
    *,
    backends: tuple[str, ...],
    timeout_seconds: float,
    profile_dir: Path | None = None,
    profile_format: str = "speedscope",
    profile_duration_seconds: float | None = None,
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, job in enumerate(jobs, start=1):
        emit_event("aba_shape_parse_start", index=index, total=len(jobs), instance=job.instance, subtrack=job.subtrack)
        framework = parse_aba(job.path.read_text(encoding="utf-8"))
        emit_event("aba_shape_compute_start", index=index, total=len(jobs), instance=job.instance, subtrack=job.subtrack)
        shape = compute_aba_shape(framework)
        emit_event(
            "aba_shape_compute_done",
            index=index,
            total=len(jobs),
            instance=job.instance,
            subtrack=job.subtrack,
            grounded_shape_status=shape.grounded_shape_status,
        )
        class_name = solver_class(job.instance_kind, job.subtrack)
        backend_results = run_backend_matrix(
            job,
            framework=framework,
            backends=backends,
            timeout_seconds=timeout_seconds,
            profile_dir=profile_dir,
            profile_format=profile_format,
            profile_duration_seconds=profile_duration_seconds,
            clingo_control_args=clingo_control_args,
            collect_clingo_statistics=collect_clingo_statistics,
        )
        best = best_solved_backend(backend_results)
        buckets = shape_buckets(shape, class_name)
        candidates = route_candidates(
            shape,
            class_name,
            available_backends=backends,
            timeout_budget_class=f"{timeout_seconds:g}s",
        )
        row = {
            "index": index,
            "year": job.year,
            "track": job.track,
            "subtrack": job.subtrack,
            "instance_kind": job.instance_kind,
            "instance": job.instance,
            "solver_class": class_name,
            "shape": asdict(shape),
            "buckets": buckets,
            "shape_bucket_id": shape_bucket_id(buckets),
            "backend_results": backend_results,
            "backend_outcomes": backend_outcomes(backend_results),
            "witness_validation_results": witness_validation_results(backend_results),
            "best_solved_backend": best,
            "all_timed_out": all(result.get("status") == "timeout" for result in backend_results.values()),
            "route_candidates": [asdict(candidate) for candidate in candidates],
            "route_evidence_ids": [
                candidate.evidence_id
                for candidate in candidates
                if candidate.production and candidate.evidence_id
            ],
            "route_counterexamples": route_counterexamples(
                candidates,
                backend_results,
                best_solved=best,
            ),
        }
        rows.append(row)
        emit_event(
            "aba_shape_row",
            index=index,
            total=len(jobs),
            instance=job.instance,
            subtrack=job.subtrack,
            best_solved_backend=best,
            all_timed_out=row["all_timed_out"],
        )
    return rows


def emit_event(event: str, **fields: Any) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True), file=sys.stderr, flush=True)


def summarize(rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> dict[str, Any]:
    return {
        "by_solver_class": _count_by(rows, "solver_class"),
        "by_backend": _backend_summary(rows, backends),
        "shape_buckets": _shape_bucket_summary(rows),
        "portfolio_proposals": propose_portfolio_rules(rows, backends=backends),
        "total_rows": len(rows),
    }


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(row[key]) for row in rows)
    return dict(sorted(counts.items()))


def _backend_summary(rows: list[dict[str, Any]], backends: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for backend in backends:
        statuses = Counter(str(row["backend_results"][backend].get("status")) for row in rows)
        summary[backend] = dict(sorted(statuses.items()))
    return summary


def _shape_bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[tuple[str, str], ...], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = tuple(sorted(row["buckets"].items()))
        status = "all_timeout" if row["all_timed_out"] else f"best:{row['best_solved_backend']}"
        counts[key][status] += 1
    return [
        {"bucket": dict(key), "outcomes": dict(sorted(counter.items())), "total": sum(counter.values())}
        for key, counter in sorted(counts.items())
    ]


def propose_portfolio_rules(rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, str], ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(sorted(row["buckets"].items()))].append(row)
    proposals: list[dict[str, Any]] = []
    for key, bucket_rows in sorted(grouped.items()):
        if len(bucket_rows) < 2:
            continue
        counts = Counter(row["best_solved_backend"] for row in bucket_rows if row["best_solved_backend"])
        if not counts:
            continue
        backend, count = counts.most_common(1)[0]
        if count < 2:
            continue
        counterexamples = [
            {
                "instance": row["instance"],
                "outcome": "all_timeout" if row["all_timed_out"] else f"best:{row['best_solved_backend']}",
                "solver_class": row["solver_class"],
            }
            for row in bucket_rows
            if row["best_solved_backend"] != backend
        ]
        if counterexamples:
            continue
        evidence_rows = [
            {
                "instance": row["instance"],
                "solver_class": row["solver_class"],
                "subtrack": row["subtrack"],
            }
            for row in bucket_rows
        ]
        proposals.append(
            {
                "backend": backend,
                "candidate_rule": f"prefer {backend} when shape_predicate matches",
                "confidence": "medium" if count >= 2 else "low",
                "counterexamples": counterexamples,
                "evidence_rows": evidence_rows,
                "failures": [],
                "shape_predicate": dict(key),
                "solver_classes": sorted({row["solver_class"] for row in bucket_rows}),
            }
        )
    return proposals


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "instance",
        "subtrack",
        "solver_class",
        "shape_bucket_id",
        "backend",
        "backend_outcome",
        "status",
        "elapsed_seconds",
        "reason",
        "witness_size",
        "validation_status",
        "witness_validation_result",
        "best_solved_backend",
        "all_timed_out",
        "route_candidate_predicates",
        "route_evidence_ids",
        "route_counterexample_count",
    ]
    shape_fields = list(AbaShape.__dataclass_fields__)
    bucket_fields = ["assumption_size", "rule_density", "max_arity", "preprocessing"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*fields, *shape_fields, *bucket_fields])
        writer.writeheader()
        for row in rows:
            for backend in backends:
                result = row["backend_results"][backend]
                writer.writerow(
                    {
                        **{field: row["shape"][field] for field in shape_fields},
                        **{field: row["buckets"][field] for field in bucket_fields},
                        "all_timed_out": row["all_timed_out"],
                        "backend": backend,
                        "backend_outcome": row["backend_outcomes"].get(backend),
                        "best_solved_backend": row["best_solved_backend"],
                        "elapsed_seconds": result.get("elapsed_seconds"),
                        "instance": row["instance"],
                        "reason": result.get("reason"),
                        "route_candidate_predicates": " ".join(
                            candidate["predicate"] for candidate in row["route_candidates"]
                        ),
                        "route_counterexample_count": sum(
                            len(examples) for examples in row["route_counterexamples"].values()
                        ),
                        "route_evidence_ids": " ".join(row["route_evidence_ids"]),
                        "shape_bucket_id": row["shape_bucket_id"],
                        "solver_class": row["solver_class"],
                        "status": result.get("status"),
                        "subtrack": row["subtrack"],
                        "validation_status": result.get("validation", {}).get("status"),
                        "witness_validation_result": row["witness_validation_results"].get(backend),
                        "witness_size": result.get("witness_size"),
                    }
                )


def build_payload(
    rows: list[dict[str, Any]],
    *,
    backends: tuple[str, ...],
    timeout_seconds: float,
    profile_dir: Path | None = None,
    profile_format: str = "speedscope",
    profile_duration_seconds: float | None = None,
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
) -> dict[str, Any]:
    return {
        "config": {
            "backend_candidates": list(backends),
            "bucket_thresholds": {
                "assumption_size": ASSUMPTION_SIZE_THRESHOLDS,
                "max_arity": MAX_ARITY_THRESHOLDS,
                "rule_density": RULE_DENSITY_THRESHOLDS,
                "grounded_shape_cost_limit": GROUNDED_SHAPE_COST_LIMIT,
                "validation_cost_limit": VALIDATION_COST_LIMIT,
            },
            "profile_dir": str(profile_dir) if profile_dir is not None else None,
            "profile_duration_seconds": profile_duration_seconds,
            "profile_format": profile_format,
            "clingo_control_args": list(clingo_control_args),
            "collect_clingo_statistics": collect_clingo_statistics,
            "timeout_seconds": timeout_seconds,
        },
        "rows": rows,
        "summary": summarize(rows, backends=backends),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark ABA solver backends by framework shape.")
    parser.add_argument("--instance", action="append", type=Path, default=[])
    parser.add_argument("--timeouts", type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--year", action="append", type=int)
    parser.add_argument("--subtrack", action="append", default=[])
    parser.add_argument("--instance-kind", default="aba")
    parser.add_argument("--backend", action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--profile-dir", type=Path)
    parser.add_argument(
        "--profile-format",
        choices=["flamegraph", "raw", "speedscope", "chrometrace"],
        default="speedscope",
    )
    parser.add_argument("--profile-duration-seconds", type=float)
    parser.add_argument("--clingo-control-arg", action="append", default=[])
    parser.add_argument("--collect-clingo-statistics", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    subtracks = tuple(args.subtrack) or DEFAULT_SUBTRACKS
    backends = tuple(args.backend) or DEFAULT_BACKENDS
    jobs: list[BenchmarkJob] = []
    if args.timeouts is not None:
        rows = json.loads(args.timeouts.read_text(encoding="utf-8"))
        jobs.extend(
            build_jobs_from_manifest(
                rows,
                data_root=args.data_root,
                years=None if args.year is None else set(args.year),
                subtracks=set(subtracks),
                instance_kind=args.instance_kind,
            )
        )
    if args.instance:
        jobs.extend(build_jobs_from_instances(args.instance, root=args.root, subtracks=subtracks))
    if not jobs:
        raise SystemExit("no ABA benchmark jobs selected")
    rows = benchmark_rows(
        jobs,
        backends=backends,
        timeout_seconds=args.timeout_seconds,
        profile_dir=args.profile_dir,
        profile_format=args.profile_format,
        profile_duration_seconds=args.profile_duration_seconds,
        clingo_control_args=tuple(args.clingo_control_arg),
        collect_clingo_statistics=args.collect_clingo_statistics,
    )
    payload = build_payload(
        rows,
        backends=backends,
        timeout_seconds=args.timeout_seconds,
        profile_dir=args.profile_dir,
        profile_format=args.profile_format,
        profile_duration_seconds=args.profile_duration_seconds,
        clingo_control_args=tuple(args.clingo_control_arg),
        collect_clingo_statistics=args.collect_clingo_statistics,
    )
    write_json(args.output_json, payload)
    write_csv(args.output_csv, rows, backends=backends)
    print(json.dumps({"output_json": str(args.output_json), "output_csv": str(args.output_csv), "summary": payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
