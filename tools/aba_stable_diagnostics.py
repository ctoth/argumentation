from __future__ import annotations

import argparse
import json
import multiprocessing
from pathlib import Path
import queue
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation.structured.aba import aba_sat
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import Literal
from argumentation.interop.iccma import parse_aba


def stable_diagnostics(
    framework: ABAFramework,
    *,
    z3_timeout_ms: int,
    support_timeout_seconds: float,
    strategy: str,
    force_trivial: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    sccs = _rule_dependency_sccs(framework)
    scc_seconds = time.perf_counter() - started
    if strategy == "integer-rank":
        profile = _rank_strategy_profile(
            framework,
            z3_timeout_ms=z3_timeout_ms,
            force_trivial=force_trivial,
            rank_kind="integer",
        )
    elif strategy == "bitvec-rank":
        profile = _rank_strategy_profile(
            framework,
            z3_timeout_ms=z3_timeout_ms,
            force_trivial=force_trivial,
            rank_kind="bitvec",
        )
    elif strategy == "boolean-ladder":
        profile = _ladder_strategy_profile(
            framework,
            z3_timeout_ms=z3_timeout_ms,
            force_trivial=force_trivial,
        )
    elif strategy == "support-materialized":
        profile = _support_strategy_profile(
            framework,
            z3_timeout_ms=z3_timeout_ms,
            support_timeout_seconds=support_timeout_seconds,
            force_trivial=force_trivial,
        )
    else:
        raise ValueError(f"unknown stable diagnostic strategy: {strategy}")
    return {
        **_framework_shape(framework),
        "strategy": strategy,
        "force_trivial": force_trivial,
        "z3_timeout_ms": z3_timeout_ms,
        "dependency_scc_count": len(sccs),
        "dependency_scc_max_size": max((len(scc) for scc in sccs), default=0),
        "dependency_scc_sizes_desc": sorted((len(scc) for scc in sccs), reverse=True)[:20],
        "scc_seconds": scc_seconds,
        **profile,
    }


def _rank_strategy_profile(
    framework: ABAFramework,
    *,
    z3_timeout_ms: int,
    force_trivial: bool,
    rank_kind: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"in_{aba_sat._literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    solver.set(timeout=z3_timeout_ms)
    if rank_kind == "integer":
        derived = aba_sat._add_ranked_closure_constraints(z3, solver, framework, variables)
        rank_variables = len(framework.language)
        rank_variable_kind = "int"
    elif rank_kind == "bitvec":
        derived = _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables)
        rank_variables = len(framework.language)
        rank_variable_kind = "bitvec"
    else:
        raise ValueError(f"unknown rank kind: {rank_kind}")
    for assumption in sorted(framework.assumptions, key=repr):
        _add_forced_literal_constraints(z3, solver, framework, variables, assumption, force_trivial)
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(derived[framework.contrary[assumption]]),
            )
        )
        solver.add(
            z3.Or(
                variables[assumption],
                derived[framework.contrary[assumption]],
            )
        )
    build_seconds = time.perf_counter() - started
    started = time.perf_counter()
    check = solver.check()
    check_seconds = time.perf_counter() - started
    return {
        "z3_check": str(check),
        "z3_check_seconds": check_seconds,
        "encoding_build_seconds": build_seconds,
        "z3_assertions": len(solver.assertions()),
        "z3_bool_variables": len(variables) + len(derived),
        "z3_rank_variables": rank_variables,
        "z3_rank_variable_kind": rank_variable_kind,
        "support_build_seconds": 0.0,
        "minimal_support_count": None,
    }


def _ladder_strategy_profile(
    framework: ABAFramework,
    *,
    z3_timeout_ms: int,
    force_trivial: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"in_{aba_sat._literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    solver.set(timeout=z3_timeout_ms)
    derived, ladder_variable_count = _add_ladder_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(framework.assumptions, key=repr):
        _add_forced_literal_constraints(z3, solver, framework, variables, assumption, force_trivial)
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(derived[framework.contrary[assumption]]),
            )
        )
        solver.add(
            z3.Or(
                variables[assumption],
                derived[framework.contrary[assumption]],
            )
        )
    build_seconds = time.perf_counter() - started
    started = time.perf_counter()
    check = solver.check()
    check_seconds = time.perf_counter() - started
    return {
        "z3_check": str(check),
        "z3_check_seconds": check_seconds,
        "encoding_build_seconds": build_seconds,
        "z3_assertions": len(solver.assertions()),
        "z3_bool_variables": len(variables) + len(derived) + ladder_variable_count,
        "z3_rank_variables": 0,
        "z3_rank_variable_kind": "boolean-ladder",
        "support_build_seconds": 0.0,
        "minimal_support_count": None,
    }


def _support_strategy_profile(
    framework: ABAFramework,
    *,
    z3_timeout_ms: int,
    support_timeout_seconds: float,
    force_trivial: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    support_result = _minimal_supports_with_timeout(
        framework,
        timeout_seconds=support_timeout_seconds,
    )
    support_seconds = time.perf_counter() - started
    if support_result["status"] != "success":
        return {
            "z3_check": None,
            "z3_check_seconds": 0.0,
            "encoding_build_seconds": 0.0,
            "z3_assertions": 0,
            "z3_bool_variables": 0,
            "z3_rank_variables": 0,
            "z3_rank_variable_kind": "none",
            "support_build_seconds": support_seconds,
            "support_build_status": support_result["status"],
            "support_build_reason": support_result["reason"],
            "support_timeout_seconds": support_timeout_seconds,
            "minimal_support_count": None,
        }
    supports = support_result["supports"]
    started = time.perf_counter()
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"in_{aba_sat._literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    solver.set(timeout=z3_timeout_ms)
    for assumption in sorted(framework.assumptions, key=repr):
        _add_forced_literal_constraints(z3, solver, framework, variables, assumption, force_trivial)
        attacked = aba_sat._any_support_selected(
            z3,
            variables,
            supports.get(framework.contrary[assumption], frozenset()),
        )
        solver.add(z3.Implies(variables[assumption], z3.Not(attacked)))
        solver.add(z3.Or(variables[assumption], attacked))
    build_seconds = time.perf_counter() - started
    started = time.perf_counter()
    check = solver.check()
    check_seconds = time.perf_counter() - started
    return {
        "z3_check": str(check),
        "z3_check_seconds": check_seconds,
        "encoding_build_seconds": build_seconds,
        "z3_assertions": len(solver.assertions()),
        "z3_bool_variables": len(variables),
        "z3_rank_variables": 0,
        "z3_rank_variable_kind": "none",
        "support_build_seconds": support_seconds,
        "support_build_status": "success",
        "support_build_reason": None,
        "support_timeout_seconds": support_timeout_seconds,
        "minimal_support_count": sum(len(values) for values in supports.values()),
    }


def _framework_shape(framework: ABAFramework) -> dict[str, int]:
    return {
        "assumptions": len(framework.assumptions),
        "language_literals": len(framework.language),
        "rules": len(framework.rules),
    }


def _minimal_supports_with_timeout(
    framework: ABAFramework,
    *,
    timeout_seconds: float,
) -> dict[str, Any]:
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_minimal_supports_worker,
        args=(framework, result_queue),
    )
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.kill()
        process.join()
        return {
            "status": "timeout",
            "reason": f"support_build_timeout>{timeout_seconds}",
        }
    if process.exitcode != 0:
        return {
            "status": "error",
            "reason": f"support_build_exit>{process.exitcode}",
        }
    try:
        payload = result_queue.get_nowait()
    except queue.Empty:
        return {
            "status": "error",
            "reason": "support_build_no_result",
        }
    return payload


def _minimal_supports_worker(
    framework: ABAFramework,
    result_queue,
) -> None:
    try:
        supports = aba_sat._minimal_supports(framework)
    except BaseException as exc:  # pragma: no cover - child process diagnostic path
        result_queue.put({
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
        })
        return
    result_queue.put({
        "status": "success",
        "reason": None,
        "supports": supports,
    })


def _add_forced_literal_constraints(z3, solver, framework, variables, assumption, enabled: bool) -> None:
    if not enabled:
        return
    if aba_sat.derives(framework, frozenset(), framework.contrary[assumption]):
        solver.add(z3.Not(variables[assumption]))
    elif not aba_sat.derives(framework, framework.assumptions, framework.contrary[assumption]):
        solver.add(variables[assumption])


def _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    rank_bits = max(1, (rank_bound + 1).bit_length())
    rank_bound_value = z3.BitVecVal(rank_bound, rank_bits)
    derived = {
        literal: z3.Bool(f"der_{aba_sat._literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.BitVec(f"rank_bv_{aba_sat._literal_key(literal)}", rank_bits)
        for literal in literals
    }
    rules_by_consequent = {
        literal: [
            rule
            for rule in sorted(framework.rules, key=repr)
            if rule.consequent == literal
        ]
        for literal in literals
    }

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


def _add_ladder_closure_constraints(z3, solver, framework, variables):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    rules_by_consequent = {
        literal: [
            rule
            for rule in sorted(framework.rules, key=repr)
            if rule.consequent == literal
        ]
        for literal in literals
    }
    ladder = {
        (literal, rank): z3.Bool(f"ladder_{rank}_{aba_sat._literal_key(literal)}")
        for literal in literals
        for rank in range(rank_bound + 1)
    }
    derived = {
        literal: z3.Bool(f"der_{aba_sat._literal_key(literal)}")
        for literal in literals
    }

    for literal in literals:
        base_terms = []
        if literal in framework.assumptions:
            base_terms.append(variables[literal])
        if any(not rule.antecedents for rule in rules_by_consequent[literal]):
            base_terms.append(z3.BoolVal(True))
        solver.add(
            ladder[(literal, 0)]
            == (z3.Or(*base_terms) if base_terms else z3.BoolVal(False))
        )
    for rank in range(1, rank_bound + 1):
        for literal in literals:
            support_terms = [ladder[(literal, rank - 1)]]
            for rule in rules_by_consequent[literal]:
                antecedents = tuple(rule.antecedents)
                if not antecedents:
                    support_terms.append(z3.BoolVal(True))
                    continue
                support_terms.append(
                    z3.And(*(ladder[(antecedent, rank - 1)] for antecedent in antecedents))
                )
            solver.add(ladder[(literal, rank)] == z3.Or(*support_terms))
    for literal in literals:
        solver.add(derived[literal] == ladder[(literal, rank_bound)])
    return derived, len(ladder)


def _rule_dependency_sccs(framework: ABAFramework) -> list[frozenset[Literal]]:
    graph = {literal: set() for literal in framework.language}
    for rule in framework.rules:
        for antecedent in rule.antecedents:
            graph.setdefault(antecedent, set()).add(rule.consequent)
            graph.setdefault(rule.consequent, set())
    return _tarjan_sccs(graph)


def _tarjan_sccs(graph: dict[Literal, set[Literal]]) -> list[frozenset[Literal]]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(graph) * 2 + 100))
    index = 0
    stack: list[Literal] = []
    on_stack: set[Literal] = set()
    indices: dict[Literal, int] = {}
    lowlinks: dict[Literal, int] = {}
    sccs: list[frozenset[Literal]] = []

    def strongconnect(node: Literal) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for successor in sorted(graph.get(node, set()), key=repr):
            if successor not in indices:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[successor])

        if lowlinks[node] == indices[node]:
            component: set[Literal] = set()
            while True:
                successor = stack.pop()
                on_stack.remove(successor)
                component.add(successor)
                if successor == node:
                    break
            sccs.append(frozenset(component))

    for node in sorted(graph, key=repr):
        if node not in indices:
            strongconnect(node)
    return sccs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose the current ABA stable SAT encoding.")
    parser.add_argument("instance", type=Path)
    parser.add_argument("--z3-timeout-ms", type=int, default=15_000)
    parser.add_argument("--support-timeout-seconds", type=float, default=60.0)
    parser.add_argument(
        "--strategy",
        choices=("integer-rank", "bitvec-rank", "boolean-ladder", "support-materialized"),
        default="integer-rank",
    )
    parser.add_argument("--force-trivial", action="store_true")
    args = parser.parse_args(argv)

    started = time.perf_counter()
    framework = parse_aba(args.instance.read_text(encoding="utf-8"))
    parse_seconds = time.perf_counter() - started
    payload = stable_diagnostics(
        framework,
        z3_timeout_ms=args.z3_timeout_ms,
        support_timeout_seconds=args.support_timeout_seconds,
        strategy=args.strategy,
        force_trivial=args.force_trivial,
    )
    payload["parse_seconds"] = parse_seconds
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
