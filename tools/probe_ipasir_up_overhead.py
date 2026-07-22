from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pysat.engines import Propagator
from pysat.solvers import Solver


@dataclass(frozen=True)
class ProbeCase:
    name: str
    variables: int
    clauses: int
    width: int


DEFAULT_CASES = (
    ProbeCase("small", variables=200, clauses=850, width=3),
    ProbeCase("medium", variables=700, clauses=3000, width=3),
    ProbeCase("aba_like", variables=10_000, clauses=33_000, width=3),
)

NoopMode = Literal["check-only", "connect-only", "observe-all"]


class CountingNoopPropagator(Propagator):
    def __init__(self) -> None:
        super().__init__()
        self.assignments = 0
        self.new_levels = 0
        self.backtracks = 0
        self.check_models = 0
        self.decisions = 0
        self.propagations = 0
        self.reasons = 0
        self.add_clauses = 0

    def on_assignment(self, lit: int, fixed: bool = False) -> None:
        self.assignments += 1

    def on_new_level(self) -> None:
        self.new_levels += 1

    def on_backtrack(self, to: int) -> None:
        self.backtracks += 1

    def check_model(self, model: list[int]) -> bool:
        self.check_models += 1
        return True

    def decide(self) -> int:
        self.decisions += 1
        return 0

    def propagate(self) -> list[int]:
        self.propagations += 1
        return []

    def provide_reason(self, lit: int) -> list[int]:
        self.reasons += 1
        return [lit]

    def add_clause(self) -> list[int]:
        self.add_clauses += 1
        return []

    def counters(self) -> dict[str, int]:
        return {
            "assignments": self.assignments,
            "new_levels": self.new_levels,
            "backtracks": self.backtracks,
            "check_models": self.check_models,
            "decisions": self.decisions,
            "propagations": self.propagations,
            "reasons": self.reasons,
            "add_clauses": self.add_clauses,
        }


class CheckOnlyNoopPropagator(Propagator):
    def __init__(self) -> None:
        super().__init__()
        self.check_models = 0

    def check_model(self, model: list[int]) -> bool:
        self.check_models += 1
        return True

    def provide_reason(self, lit: int) -> list[int]:
        return [lit]

    def add_clause(self) -> list[int]:
        return []

    def counters(self) -> dict[str, int]:
        return {"check_models": self.check_models}


def hidden_assignment_cnf(
    *,
    variables: int,
    clauses: int,
    width: int,
    seed: int,
) -> list[list[int]]:
    rng = random.Random(seed)
    assignment = {
        variable: rng.choice((False, True)) for variable in range(1, variables + 1)
    }
    cnf: list[list[int]] = []
    for _ in range(clauses):
        picked = rng.sample(range(1, variables + 1), width)
        clause: list[int] = []
        satisfied = False
        for variable in picked:
            positive = rng.choice((False, True))
            if assignment[variable] == positive:
                satisfied = True
            clause.append(variable if positive else -variable)
        if not satisfied:
            variable = picked[0]
            clause[0] = variable if assignment[variable] else -variable
        cnf.append(clause)
    return cnf


def run_solver(
    cnf: list[list[int]],
    *,
    variables: int,
    noop_mode: NoopMode | None,
) -> dict[str, Any]:
    propagator: Any | None = None
    started = time.perf_counter()
    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        if noop_mode is not None:
            if noop_mode == "check-only":
                propagator = CheckOnlyNoopPropagator()
            else:
                propagator = CountingNoopPropagator()
            solver.connect_propagator(propagator)
            if noop_mode == "observe-all":
                for variable in range(1, variables + 1):
                    solver.observe(variable)
        status = solver.solve()
        stats = solver.accum_stats()
    elapsed = time.perf_counter() - started
    return {
        "status": bool(status),
        "elapsed_seconds": elapsed,
        "solver_stats": stats,
        "propagator": propagator.counters() if propagator is not None else None,
    }


def summarize_pair(
    *,
    case: ProbeCase,
    seed: int,
    repeat: int,
    noop_mode: NoopMode,
) -> dict[str, Any]:
    cnf = hidden_assignment_cnf(
        variables=case.variables,
        clauses=case.clauses,
        width=case.width,
        seed=seed,
    )
    baseline_runs = [
        run_solver(cnf, variables=case.variables, noop_mode=None) for _ in range(repeat)
    ]
    noop_runs = [
        run_solver(cnf, variables=case.variables, noop_mode=noop_mode)
        for _ in range(repeat)
    ]
    baseline_median = median(run["elapsed_seconds"] for run in baseline_runs)
    noop_median = median(run["elapsed_seconds"] for run in noop_runs)
    overhead_ratio = noop_median / baseline_median if baseline_median > 0 else None
    payload = {
        "case": case.__dict__,
        "seed": seed,
        "repeat": repeat,
        "noop_mode": noop_mode,
        "baseline_runs": baseline_runs,
        "noop_runs": noop_runs,
        "baseline_median_seconds": baseline_median,
        "noop_median_seconds": noop_median,
        "overhead_ratio": overhead_ratio,
    }
    if noop_mode == "observe-all":
        payload["observed_noop_runs"] = noop_runs
        payload["observed_noop_median_seconds"] = noop_median
    return payload


def median(values: list[float]) -> float:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def parse_cases(raw_cases: list[str] | None) -> tuple[ProbeCase, ...]:
    if not raw_cases:
        return DEFAULT_CASES
    cases: list[ProbeCase] = []
    for raw_case in raw_cases:
        name, variables, clauses, width = raw_case.split(":")
        cases.append(
            ProbeCase(
                name=name,
                variables=int(variables),
                clauses=int(clauses),
                width=int(width),
            )
        )
    return tuple(cases)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure PySAT cadical195 IPASIR-UP no-op propagator overhead."
    )
    parser.add_argument("--case", action="append", help="name:variables:clauses:width")
    parser.add_argument(
        "--noop-mode",
        choices=("check-only", "connect-only", "observe-all"),
        default="observe-all",
        help=(
            "check-only attaches a minimal check_model propagator; "
            "connect-only attaches the counting propagator without observed variables; "
            "observe-all also observes every variable."
        ),
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    if args.repeat < 1:
        raise ValueError("--repeat must be positive")
    results = [
        summarize_pair(
            case=case,
            seed=args.seed + index,
            repeat=args.repeat,
            noop_mode=args.noop_mode,
        )
        for index, case in enumerate(parse_cases(args.case))
    ]
    payload = {
        "seed": args.seed,
        "repeat": args.repeat,
        "noop_mode": args.noop_mode,
        "results": results,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
