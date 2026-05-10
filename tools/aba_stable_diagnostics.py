from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation import aba_sat
from argumentation.aba import ABAFramework
from argumentation.aspic import Literal
from argumentation.iccma import parse_aba


def stable_diagnostics(
    framework: ABAFramework,
    *,
    z3_timeout_ms: int,
) -> dict[str, Any]:
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"in_{aba_sat._literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    solver.set(timeout=z3_timeout_ms)
    derived = aba_sat._add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(framework.assumptions, key=repr):
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

    started = time.perf_counter()
    check = solver.check()
    elapsed = time.perf_counter() - started
    sccs = _rule_dependency_sccs(framework)
    return {
        "assumptions": len(framework.assumptions),
        "language_literals": len(framework.language),
        "rules": len(framework.rules),
        "z3_timeout_ms": z3_timeout_ms,
        "z3_check": str(check),
        "z3_check_seconds": elapsed,
        "z3_assertions": len(solver.assertions()),
        "z3_bool_variables": len(variables) + len(derived),
        "z3_int_rank_variables": len(framework.language),
        "dependency_scc_count": len(sccs),
        "dependency_scc_max_size": max((len(scc) for scc in sccs), default=0),
        "dependency_scc_sizes_desc": sorted((len(scc) for scc in sccs), reverse=True)[:20],
    }


def _rule_dependency_sccs(framework: ABAFramework) -> list[frozenset[Literal]]:
    graph = {literal: set() for literal in framework.language}
    for rule in framework.rules:
        for antecedent in rule.antecedents:
            graph.setdefault(antecedent, set()).add(rule.consequent)
            graph.setdefault(rule.consequent, set())
    return _tarjan_sccs(graph)


def _tarjan_sccs(graph: dict[Literal, set[Literal]]) -> list[frozenset[Literal]]:
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
    args = parser.parse_args(argv)

    framework = parse_aba(args.instance.read_text(encoding="utf-8"))
    payload = stable_diagnostics(framework, z3_timeout_ms=args.z3_timeout_ms)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
