# IPASIR-UP Check-Only Overhead Probe

Date: 2026-05-20

Status: measured on experiment branch; source change not yet promoted.

Experiment branch: `exp/ipasir-up-model-only-probe`

Evidence commits:
- `ea3ee26` parameterized the IPASIR-UP no-op probe mode.
- `522a116` added the check-only propagator mode.
- `572b026` fixed required iterable-return callbacks for the check-only propagator.

Hypothesis: a lazy IPASIR-UP shape that connects a propagator without observing
all variables and only performs useful work at model-check time has acceptable
baseline overhead, unlike the all-variable observed propagator.

Single variable: attach a minimal `check_model` propagator without calling
`solver.observe(...)`; keep the generated satisfiable CNFs, solver, seeds, and
repeat count from the previous IPASIR-UP probe.

Baseline:
- Command: `uv run tools\probe_ipasir_up_overhead.py --repeat 5 --seed 20260520 --output-json data\iccma\2025\runs\ipasir-up-noop-overhead.json`
- Result: previous all-variable `observe-all` no-op probe had ABA-like synthetic
  median ratio `3.3587038542188545x` versus baseline.

Experiment result:
- Command: `uv run tools\probe_ipasir_up_overhead.py --noop-mode check-only --repeat 5 --seed 20260520 --output-json data\iccma\2025\runs\ipasir-up-check-only-overhead.json`
- Result: `small` median ratio `0.5111921807076023x`; `medium` median ratio
  `1.2289665877835412x`; `aba_like` median ratio `1.2720535161259499x`.
- ABA-like synthetic detail: baseline median `0.611523799947463s`;
  check-only median `0.7778909999178723s`; check-model callback count `1`.

Fast contracts:
- `uv run tools\probe_ipasir_up_overhead.py --noop-mode connect-only --case smoke:30:100:3 --repeat 1 --seed 1`
- `uv run tools\probe_ipasir_up_overhead.py --noop-mode observe-all --case smoke:30:100:3 --repeat 1 --seed 1`
- `uv run tools\probe_ipasir_up_overhead.py --noop-mode check-only --case smoke:30:100:3 --repeat 1 --seed 1`

Metric gate:
- Pass if the ABA-like synthetic `check-only` median ratio is under `1.5x` and
  all runs solve successfully.
- Result: passed at `1.2720535161259499x`.

Outcome: positive.

Decision: continue to a real sparse/narrow stable solver experiment using the
check-model callback shape; do not revive the all-variable observed design.

Generated diagnostics:
- `data\iccma\2025\runs\ipasir-up-connect-only-overhead.json`
- `data\iccma\2025\runs\ipasir-up-check-only-overhead.json`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: true operational overhead experiment.

This record tested the narrower callback shape directly and measured callback
overhead against the previous observe-all baseline. It is a positive feasibility
result for check-model-only overhead, not proof that the real solver route will
win.

Required follow-up: the next real solver experiment must still profile or
telemetry-check the actual sparse/narrow worker path if the metric fails.
