"""Preregistered ICCMA 2023 SE-PR Clingo configuration discriminator.

Runs the production direct solver API sequentially for the frozen interleaved
configuration order and independently checks every returned preferred witness.
Writes a reusable JSON diagnostic after every run so a fail-closed nonzero exit
still leaves the completed evidence collected up to that point.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any, Final

from argumentation.interop.iccma import parse_aba
from argumentation.solving.solver import _auto_aba_backend_for_framework
from argumentation.structured.aba._closure import horn_closure
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_asp import ABAQueryResult, solve_aba_with_backend
from argumentation.structured.aba.aba_incremental import DEFAULT_CLINGO_CONTROL_ARGS
from argumentation.structured.aba.aba_kernel import AssumptionKernel

DEFAULT_INSTANCE: Final = Path(
    "data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_1.aba"
)
DEFAULT_OUTPUT: Final = Path(
    "data/iccma/2023/runs/probe2-clingo-config-triage.json"
)
SOLVE_CAP_SECONDS: Final = 15.0
MEDIAN_SURVIVAL_SECONDS: Final = 8.0
EVERY_RUN_SURVIVAL_SECONDS: Final = 9.0
TELEMETRY_KEYS: Final = (
    "solver_calls",
    "outer_iterations",
    "inner_iterations",
    "refinement_clauses",
)


@dataclass(frozen=True)
class Arm:
    """One preregistered Clingo control configuration."""

    name: str
    control_args: tuple[str, ...]

    @property
    def effective_control_args(self) -> tuple[str, ...]:
        return DEFAULT_CLINGO_CONTROL_ARGS + self.control_args


ARMS: Final = (
    Arm("default", ()),
    Arm("handy", ("--configuration=handy",)),
    Arm("crafty", ("--configuration=crafty",)),
    Arm("trendy", ("--configuration=trendy",)),
)
RUN_ORDER: Final = ARMS * 3


@dataclass(frozen=True)
class WitnessCheck:
    """Independent preferred-witness verdict and its component facts."""

    valid: bool
    reason: str
    witness_size: int | None
    subset_ok: bool
    closed_ok: bool
    conflict_free: bool
    defends: bool
    admissible: bool
    proper_admissible_superset_found: bool | None
    proper_superset_size: int | None
    checker_elapsed_seconds: float


@dataclass(frozen=True)
class ProbeRun:
    """One measured direct-API invocation."""

    order_index: int
    repeat: int
    arm: str
    user_control_args: tuple[str, ...]
    effective_control_args: tuple[str, ...]
    solve_status: str
    elapsed_seconds: float
    solver_calls: int | None
    outer_iterations: int | None
    inner_iterations: int | None
    refinement_clauses: int | None
    witness_check: WitnessCheck
    correct: bool
    error: str | None


@dataclass(frozen=True)
class ArmSummary:
    """Preregistered aggregate and survival calculation for one arm."""

    arm: str
    correct_runs: int
    elapsed_median_seconds: float
    elapsed_min_seconds: float
    elapsed_max_seconds: float
    elapsed_spread_seconds: float
    telemetry_medians: dict[str, float]
    telemetry_ranges: dict[str, tuple[int, int]]
    survives: bool


def _telemetry(result: ABAQueryResult) -> tuple[dict[str, int | None], str | None]:
    counts: dict[str, int | None] = {}
    errors: list[str] = []
    for key in TELEMETRY_KEYS:
        value = result.metadata.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            counts[key] = None
            errors.append(f"invalid {key}={value!r}")
        else:
            counts[key] = value
    return counts, "; ".join(errors) or None


def _failed_check(reason: str) -> WitnessCheck:
    return WitnessCheck(
        valid=False,
        reason=reason,
        witness_size=None,
        subset_ok=False,
        closed_ok=False,
        conflict_free=False,
        defends=False,
        admissible=False,
        proper_admissible_superset_found=None,
        proper_superset_size=None,
        checker_elapsed_seconds=0.0,
    )


def _extract_witness(result: ABAQueryResult) -> AssumptionSet:
    if result.status != "success":
        raise ValueError(f"solver status is {result.status!r}, not success")
    if len(result.extensions) != 1:
        raise ValueError(f"expected exactly one extension, got {len(result.extensions)}")
    witness = result.extensions[0]
    if result.accepted_assumptions != witness:
        raise ValueError("accepted_assumptions does not match the returned extension")
    return witness


def _check_preferred_independent(
    framework: ABAFramework,
    witness: AssumptionSet,
) -> WitnessCheck:
    """Check flat-ABA admissibility and maximality via independent surfaces."""
    started = time.perf_counter()
    assumptions = framework.assumptions
    subset_ok = witness <= assumptions
    closure = horn_closure(witness, framework.rules)
    closed_ok = (closure & assumptions) == witness
    conflict_free = not any(
        framework.contrary[assumption] in closure for assumption in witness
    )

    attacked = frozenset(
        assumption
        for assumption in assumptions
        if framework.contrary[assumption] in closure
    )
    unattacked = assumptions - attacked
    unattacked_closure = horn_closure(unattacked, framework.rules)
    defends = not any(
        framework.contrary[assumption] in unattacked_closure
        for assumption in witness
    )
    admissible = subset_ok and closed_ok and conflict_free and defends

    outside = assumptions - witness
    proper_superset: AssumptionSet | None = None
    if admissible and outside:
        proper_superset = AssumptionKernel.from_framework(
            framework
        ).admissible_extension(
            require_assumptions=witness,
            require_any_assumption=outside,
        )
    proper_superset_found = proper_superset is not None
    valid = admissible and not proper_superset_found
    reasons: list[str] = []
    if not subset_ok:
        reasons.append("witness contains a non-assumption")
    if not closed_ok:
        reasons.append("witness is not closed")
    if not conflict_free:
        reasons.append("witness is not conflict-free")
    if not defends:
        reasons.append("witness does not defend every member")
    if proper_superset_found:
        reasons.append("independent kernel found a proper admissible superset")
    return WitnessCheck(
        valid=valid,
        reason="preferred-valid" if valid else "; ".join(reasons),
        witness_size=len(witness),
        subset_ok=subset_ok,
        closed_ok=closed_ok,
        conflict_free=conflict_free,
        defends=defends,
        admissible=admissible,
        proper_admissible_superset_found=proper_superset_found,
        proper_superset_size=None if proper_superset is None else len(proper_superset),
        checker_elapsed_seconds=time.perf_counter() - started,
    )


def _run_once(
    framework: ABAFramework,
    arm: Arm,
    *,
    order_index: int,
) -> ProbeRun:
    started = time.perf_counter()
    try:
        result = solve_aba_with_backend(
            framework,
            backend="clingo",
            semantics="preferred",
            task="single-extension",
            clingo_control_args=arm.control_args,
            clingo_solve_timeout_seconds=SOLVE_CAP_SECONDS,
        )
    except Exception as exc:  # fail closed while preserving the sweep
        elapsed = time.perf_counter() - started
        reason = f"solver exception: {type(exc).__name__}: {exc}"
        return ProbeRun(
            order_index=order_index,
            repeat=(order_index // len(ARMS)) + 1,
            arm=arm.name,
            user_control_args=arm.control_args,
            effective_control_args=arm.effective_control_args,
            solve_status="exception",
            elapsed_seconds=elapsed,
            solver_calls=None,
            outer_iterations=None,
            inner_iterations=None,
            refinement_clauses=None,
            witness_check=_failed_check(reason),
            correct=False,
            error=reason,
        )

    elapsed = time.perf_counter() - started
    telemetry, telemetry_error = _telemetry(result)
    recorded_args = result.metadata.get("clingo_control_args")
    args_error = None
    if recorded_args != arm.effective_control_args:
        args_error = (
            f"effective control args mismatch: expected {arm.effective_control_args!r}, "
            f"got {recorded_args!r}"
        )

    if result.status != "success":
        check = _failed_check(f"no witness because solver status is {result.status!r}")
        witness_error = check.reason
    else:
        try:
            witness = _extract_witness(result)
            check = _check_preferred_independent(framework, witness)
            witness_error = None if check.valid else check.reason
        except Exception as exc:  # checker failures are closed failures
            witness_error = f"checker exception: {type(exc).__name__}: {exc}"
            check = _failed_check(witness_error)

    errors = [
        error
        for error in (telemetry_error, args_error, witness_error)
        if error is not None
    ]
    error_text = "; ".join(errors) or None
    return ProbeRun(
        order_index=order_index,
        repeat=(order_index // len(ARMS)) + 1,
        arm=arm.name,
        user_control_args=arm.control_args,
        effective_control_args=arm.effective_control_args,
        solve_status=result.status,
        elapsed_seconds=elapsed,
        solver_calls=telemetry["solver_calls"],
        outer_iterations=telemetry["outer_iterations"],
        inner_iterations=telemetry["inner_iterations"],
        refinement_clauses=telemetry["refinement_clauses"],
        witness_check=check,
        correct=result.status == "success" and check.valid and error_text is None,
        error=error_text,
    )


def _summary(arm: Arm, runs: list[ProbeRun]) -> ArmSummary:
    elapsed = [run.elapsed_seconds for run in runs]
    telemetry_medians: dict[str, float] = {}
    telemetry_ranges: dict[str, tuple[int, int]] = {}
    telemetry_complete = True
    for key in TELEMETRY_KEYS:
        values = [getattr(run, key) for run in runs]
        if any(value is None for value in values):
            telemetry_complete = False
            continue
        integers = [value for value in values if value is not None]
        telemetry_medians[key] = float(statistics.median(integers))
        telemetry_ranges[key] = (min(integers), max(integers))
    median = statistics.median(elapsed)
    maximum = max(elapsed)
    correct_runs = sum(run.correct for run in runs)
    survives = (
        len(runs) == 3
        and correct_runs == 3
        and telemetry_complete
        and median <= MEDIAN_SURVIVAL_SECONDS
        and maximum < EVERY_RUN_SURVIVAL_SECONDS
    )
    return ArmSummary(
        arm=arm.name,
        correct_runs=correct_runs,
        elapsed_median_seconds=median,
        elapsed_min_seconds=min(elapsed),
        elapsed_max_seconds=maximum,
        elapsed_spread_seconds=maximum - min(elapsed),
        telemetry_medians=telemetry_medians,
        telemetry_ranges=telemetry_ranges,
        survives=survives,
    )


def _payload(
    instance: Path,
    framework: ABAFramework,
    runs: list[ProbeRun],
) -> dict[str, Any]:
    summaries = [
        _summary(arm, [run for run in runs if run.arm == arm.name])
        for arm in ARMS
        if len([run for run in runs if run.arm == arm.name]) == 3
    ]
    survivors = [summary.arm for summary in summaries if summary.survives]
    return {
        "probe": "ICCMA 2023 Round 1 probe 2: Clingo configuration discriminator",
        "instance": str(instance),
        "framework": {
            "assumptions": len(framework.assumptions),
            "rules": len(framework.rules),
            "language": len(framework.language),
        },
        "backend": "clingo",
        "semantics": "preferred",
        "task": "single-extension",
        "jobs_equivalent": 1,
        "clingo_version": version("clingo"),
        "solve_cap_seconds": SOLVE_CAP_SECONDS,
        "median_survival_seconds": MEDIAN_SURVIVAL_SECONDS,
        "every_run_survival_seconds": EVERY_RUN_SURVIVAL_SECONDS,
        "fixed_order": [arm.name for arm in RUN_ORDER],
        "runs": [asdict(run) for run in runs],
        "summaries": [asdict(summary) for summary in summaries],
        "survivors": survivors,
        "unique_survivor": survivors[0] if len(survivors) == 1 else None,
    }


def _write_output(
    output: Path,
    instance: Path,
    framework: ABAFramework,
    runs: list[ProbeRun],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(_payload(instance, framework, runs), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    instance: Path = args.instance
    output: Path = args.output
    framework = parse_aba(instance.read_text(encoding="utf-8"))
    if not isinstance(framework, ABAFramework):
        raise TypeError(f"expected flat ABAFramework, got {type(framework)!r}")
    route = _auto_aba_backend_for_framework(
        "auto",
        "preferred",
        task="single-extension",
        framework=framework,
    )
    if route != "asp":
        raise AssertionError(f"expected the production auto route to be asp, got {route!r}")

    runs: list[ProbeRun] = []
    for order_index, arm in enumerate(RUN_ORDER):
        print(
            f"RUN {order_index + 1:02d}/{len(RUN_ORDER)} "
            f"repeat={(order_index // len(ARMS)) + 1} arm={arm.name}",
            flush=True,
        )
        run = _run_once(framework, arm, order_index=order_index)
        runs.append(run)
        _write_output(output, instance, framework, runs)
        print(
            f"  status={run.solve_status} correct={run.correct} "
            f"elapsed={run.elapsed_seconds:.6f}s "
            f"telemetry={run.solver_calls}/{run.outer_iterations}/"
            f"{run.inner_iterations}/{run.refinement_clauses} "
            f"error={run.error!r}",
            flush=True,
        )

    payload = _payload(instance, framework, runs)
    print(json.dumps(payload["summaries"], indent=2, sort_keys=True))
    survivors = payload["survivors"]
    if len(survivors) != 1:
        print(
            f"FAIL-CLOSED: expected exactly one survivor, got {survivors!r}",
            flush=True,
        )
        return 1
    print(f"UNIQUE SURVIVOR: {survivors[0]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
