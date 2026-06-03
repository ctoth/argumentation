# Performance Research

Performance work in this repository is part of the public engineering
contract. A solver optimization is not "done" because it passes semantic tests
or because a benchmark still times out. It must leave executable evidence about
the operational shape it changed.

This document applies to solver, routing, optimization, benchmark, ICCMA, ABA,
SAT, ASP, and worker-process research.

## Required Contract

Before implementing or salvaging a performance route, state at least one
operational contract that can fail before the full benchmark gate. Good
contracts include:

- bounded solver calls;
- route selection or route rejection;
- reduced residual size;
- skipped bad path;
- reduced materialization count;
- stable telemetry shape;
- calibrated wall-clock budget;
- subprocess/profiler evidence that the bottleneck moved.

Semantic correctness is still required, but it is not enough. A full benchmark
may remain the final promotion gate; it must not be the first executable signal
that a route is operationally hopeless.

## Where Contracts Live

Use the smallest executable surface that proves the intended shape:

- `tests/test_performance_contracts.py` for shared calibration helpers,
  opt-in wall-clock smoke contracts, and route-level invariants.
- Solver-specific tests next to the solver surface, for example
  `tests/structured/aba/` for ABA route and telemetry contracts.
- `tests/interop/` for ICCMA runner behavior, timeout-row handling, and trace
  comparison.
- `tests/performance_contracts.py` for reusable budget helpers and environment
  variables.

Wall-clock contracts must be opt-in or calibrated. Deterministic telemetry,
route predicates, solver-call counts, and residual-size contracts should run
normally.

## Calibration

Use the calibration helper rather than hardcoding a raw timing guess:

```powershell
uv run tools\perf_calibrate.py --output .\perf-calibration.json
$env:ARGUMENTATION_PERF_CALIBRATION = ".\perf-calibration.json"
$env:ARGUMENTATION_PERF_CONTRACTS = "1"
uv run pytest tests\test_performance_contracts.py -q
```

The helper records machine shape and median timings for small reference tasks.
`tests/performance_contracts.py` scales opt-in budgets from that payload and
falls back to conservative local budgets when no calibration file is supplied.

## Profiling

Use `py-spy` on the real hot process before abandoning an experiment or
choosing the next optimization. If the heavy work happens in a child solver or
worker process, profiling only the wrapper is not evidence.

Useful patterns:

```powershell
py-spy record -o profile.svg -- uv run tools\run_aba_10x10_fixture.py
py-spy top --pid <worker-or-solver-pid>
```

Keep the profile tied to the route or benchmark row it explains. For ICCMA and
ABA research, pair profiler output with the runner row, subtrack, instance id,
timeout, backend, and route metadata.

## Experiment Records

Experiment records belong in `experiments/`, one file per experiment. Failed
or no-go records must state:

- profiler or operational measurement used;
- baseline or previous profile compared against;
- dominant cost before and after;
- whether the intended operational invariant changed;
- next target named by the evidence.

If a benchmark gate misses and no profiler-backed diagnosis has been recorded,
the status is:

```text
promotion no-go; diagnosis incomplete
```

That is not a complete experiment result, and it is not a true route failure.

## ICCMA And ABA Runner Evidence

The ICCMA 2025 runner and related tools provide benchmark-level evidence:

- `tools/iccma2025_run_native.py` executes task rows and writes JSON/CSV
  artifacts.
- `tools/run_aba_10x10_fixture.py` exercises the tracked ABA hard fixture.
- `tools/aba_shape_benchmark.py` records ABA shape and route telemetry.
- `tools/analyze_aba_route_evidence.py` compares solved/timeout route
  evidence.
- `tools/speedscope_hot_frames.py` extracts hot-frame summaries from profiles.

Use these tools after the focused contract is in place. A benchmark gate may
promote a route, but it should not be the only reason a route was selected.

## Promotion Standard

A performance change is promotable when all of these are true:

1. Semantic tests pass for the affected surface.
2. The operational contract passes and names the intended route or bottleneck.
3. The benchmark or focused runner gate improves, or a profiler-backed record
   explains why promotion is a no-go.
4. Documentation or experiment notes state what changed, what stayed expensive,
   and what evidence should guide the next attempt.

Do not revive failed production paths merely because they pass semantic tests.
Import only the assets that enforce or explain the operational contract: tests,
telemetry, route predicates, calibration helpers, benchmark runner fixes, page
citations, or failure records.
