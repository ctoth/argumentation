from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation.structured.aba.aba import ABAFramework, derives
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from argumentation.iccma import parse_aba, write_aba


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CalibrationRecord:
    name: str
    status: str
    repeat: int
    elapsed_seconds: float | None = None
    median_seconds: float | None = None
    operations: int | None = None
    operations_per_second: float | None = None
    reason: str | None = None


def literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def calibration_framework(size: int = 48) -> ABAFramework:
    assumptions = tuple(literal(f"a{index}") for index in range(size))
    contraries = {assumption: literal(f"ca{index}") for index, assumption in enumerate(assumptions)}
    chain = tuple(literal(f"x{index}") for index in range(size))
    rules = {
        Rule((assumptions[index],), chain[index], "strict")
        for index in range(size)
    }
    rules.update(
        Rule((chain[index - 1], assumptions[index]), chain[index], "strict")
        for index in range(1, size)
    )
    return ABAFramework(
        language=frozenset(assumptions) | frozenset(contraries.values()) | frozenset(chain),
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def timed_record(
    name: str,
    repeat: int,
    operation: Callable[[], int | None],
) -> CalibrationRecord:
    durations: list[float] = []
    operations = 0
    for _ in range(repeat):
        start = time.perf_counter()
        count = operation()
        durations.append(time.perf_counter() - start)
        if count is not None:
            operations += count
    elapsed = sum(durations)
    median = statistics.median(durations)
    return CalibrationRecord(
        name=name,
        status="ok",
        repeat=repeat,
        elapsed_seconds=round(elapsed, 9),
        median_seconds=round(median, 9),
        operations=operations or None,
        operations_per_second=round(operations / elapsed, 3) if operations and elapsed > 0 else None,
    )


def skipped_record(name: str, repeat: int, reason: str) -> CalibrationRecord:
    return CalibrationRecord(name=name, status="skipped", repeat=repeat, reason=reason)


def python_integer_loop() -> int:
    total = 0
    operations = 250_000
    for value in range(operations):
        total = (total + value * 3) % 1_000_003
    if total < 0:
        raise AssertionError("unreachable negative total")
    return operations


def aba_parse_operation(text: str) -> Callable[[], int]:
    def run() -> int:
        framework = parse_aba(text)
        return len(framework.rules) + len(framework.assumptions)

    return run


def aba_closure_operation(framework: ABAFramework) -> Callable[[], int]:
    assumptions = frozenset(sorted(framework.assumptions, key=repr)[:12])
    target = sorted(framework.language, key=repr)[-1]

    def run() -> int:
        derives(framework, assumptions, target)
        return len(framework.rules)

    return run


def clingo_operation() -> CalibrationRecord | None:
    if importlib.util.find_spec("clingo") is None:
        return None
    import clingo

    program = """
        { chosen(1..18) }.
        ok :- 9 { chosen(1..18) }.
        :- not ok.
        #show chosen/1.
    """

    def run() -> int:
        control = clingo.Control(["--models=1", "--warn=none"])
        control.add("base", [], program)
        control.ground([("base", [])])
        result = control.solve()
        if not result.satisfiable:
            raise AssertionError("calibration clingo problem unexpectedly unsat")
        return 18

    return timed_record("clingo_small_solve", 1, run)


def z3_operation() -> CalibrationRecord | None:
    if importlib.util.find_spec("z3") is None:
        return None
    import z3

    def run() -> int:
        variables = [z3.Bool(f"x_{index}") for index in range(32)]
        solver = z3.Solver()
        solver.add(z3.PbGe([(variable, 1) for variable in variables], 16))
        solver.add(z3.PbLe([(variable, 1) for variable in variables], 24))
        if solver.check() != z3.sat:
            raise AssertionError("calibration z3 problem unexpectedly unsat")
        return len(variables)

    return timed_record("z3_small_check", 1, run)


def calibration_payload(*, repeat: int) -> dict[str, Any]:
    framework = calibration_framework()
    aba_text = write_aba(framework)
    records = [
        timed_record("python_integer_loop", repeat, python_integer_loop),
        timed_record("aba_parse", repeat, aba_parse_operation(aba_text)),
        timed_record("aba_closure", repeat, aba_closure_operation(framework)),
    ]
    clingo_record = clingo_operation()
    if clingo_record is None:
        records.append(skipped_record("clingo_small_solve", repeat, "clingo package unavailable"))
    else:
        records.append(clingo_record)
    z3_record = z3_operation()
    if z3_record is None:
        records.append(skipped_record("z3_small_check", repeat, "z3 package unavailable"))
    else:
        records.append(z3_record)
    return {
        "schema_version": SCHEMA_VERSION,
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repeat": repeat,
        "benchmarks": [asdict(record) for record in records],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate local performance budgets.")
    parser.add_argument("--output", type=Path, help="Optional path to write calibration JSON.")
    parser.add_argument("--repeat", type=int, default=3, help="Number of repeats for core probes.")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress text; JSON is still emitted.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.repeat < 1:
        raise SystemExit("--repeat must be >= 1")
    payload = calibration_payload(repeat=args.repeat)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        if not args.quiet:
            print(f"wrote calibration to {args.output}", file=sys.stderr)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
