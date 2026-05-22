# ABA SE-ST Unit mechanism profile

Date: 2026-05-22

Status: planned on experiment branch.

Experiment branch: `exp/aba-se-st-unit-mechanism-profile`

## Hypothesis

`--heuristic=Unit` changes the clingo search shape for the remaining large
sparse/narrow `SE-ST` ABA rows by collapsing choices and restarts, but it does
not solve because the remaining work is still inside clingo's solve phase,
likely propagation, lookahead, unfounded-set handling, or proof search under the
current stable encoding.

## Single Variable

Add exactly one clingo control argument for the representative row:

`--heuristic=Unit`

No source route, encoding, preprocessing, or runner behavior is changed in this
experiment.

## Baseline

Baseline profile is the current main worker path recorded in
`experiments/2026-05-22-aba-se-st-post-diagnostic-pyspy.md`.

Command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-post-diagnostic-pyspy\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.json --output-csv data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.csv
```

Result:

- row status: `profiled`
- reason: `profile_duration_elapsed`
- profile:
  `data\iccma\2025\profiles\aba-se-st-post-diagnostic-pyspy\small\aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`
- dominant stack: `clingo.Control.solve`, `2446` samples
- add: `18` samples
- ground: `20` samples
- Python setup surfaces: single-digit samples

Baseline clingo statistics from
`data\iccma\2025\runs\aba-se-st-option-stats-resweep-baseline.json`:

- status: `timeout`
- choices: `606358`
- conflicts: `517888`
- restarts: `1339`
- solve time: `39.00228691101074`
- models enumerated: `0`

## Fast Contracts

Before interpreting this experiment, verify:

- `uv tool run py-spy --version` succeeds;
- the profile command returns row status `profiled`, `timeout`, or `solved`;
- `backend_results.auto.error` is `null`;
- the raw profile file exists.

The existing Unit statistics row already proves the telemetry side of the
single variable:

- status: `timeout`
- choices: `561`
- conflicts: `44885`
- restarts: `5`
- solve time: `39.0024471282959`
- models enumerated: `0`

## Metric Gate

Run one profiled representative row:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-unit-mechanism-profile\small --profile-format raw --profile-duration-seconds 25 --clingo-control-arg=--heuristic=Unit --output-json data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.json --output-csv data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.csv
```

Expected duration: about 25 seconds plus setup overhead.

## Failure-Analysis Gate

Classify the Unit profile against the baseline profile as exactly one:

- moved out of `clingo.Control.solve`;
- still opaque clingo solve;
- invalid measurement.

If it is still opaque clingo solve, do not run another option matrix. The next
target must be either clingo-internal statistics beyond the current summary or
an encoding constraint that can be measured by choices/conflicts/restarts before
the full five-row benchmark.

## Kill Criteria

Stop after this one profiled Unit row. Do not expand to another row or option
inside this experiment. The result is complete when the profile is classified
and the next target is named from the evidence.

## Promotion Rule

Promote only this experiment record to `main`. Do not promote generated JSON,
CSV, or raw profile artifacts.
