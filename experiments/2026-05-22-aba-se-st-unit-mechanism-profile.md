# ABA SE-ST Unit mechanism profile

Date: 2026-05-22

Status: measured on experiment branch; source change not promoted.

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

## Experiment Result

Py-spy availability:

```powershell
uv tool run py-spy --version
```

Result: `py-spy 0.4.2`.

Profile command run:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-unit-mechanism-profile\small --profile-format raw --profile-duration-seconds 25 --clingo-control-arg=--heuristic=Unit --output-json data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.json --output-csv data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.csv
```

Result:

- row status: `profiled`
- reason: `profile_duration_elapsed`
- error: `null`
- elapsed: `25.354729900020175`
- profile:
  `data\iccma\2025\profiles\aba-se-st-unit-mechanism-profile\small\aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

Unit hot frames:

- `solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo\control.py:1065) -> _c_call`: `2454` samples
- `find_stable_extension -> _new_control -> add (clingo\control.py:320) -> _add2`: `16` samples
- `find_stable_extension -> _new_control -> ground (clingo\control.py:566)`: `10` samples
- parsing, preprocessing, Python fact encoding, resource loading, and runner
  setup: single-digit samples each

## Classification

Still opaque clingo solve.

Compared with the baseline profile, Unit did not move the Python-visible hot
path out of `clingo.Control.solve`:

- baseline solve samples: `2446`
- Unit solve samples: `2454`
- baseline add/ground samples: `18` / `20`
- Unit add/ground samples: `16` / `10`

The operational invariant from
`experiments/2026-05-22-aba-se-st-option-stats-resweep.md` remains important:
Unit collapses choices/restarts/conflicts dramatically, but py-spy cannot see
inside the remaining clingo solve time. The next target is therefore not
Python, parsing, preprocessing, grounding, or another clingo option matrix.

## Outcome

Negative for Python-visible mechanism movement; positive for target selection.

The experiment proves that the Unit signal is internal to clingo solve. The
next useful experiment must either expose finer clingo solve telemetry or alter
the stable encoding so the already-measured choices/conflicts/restarts change
and the solve budget shrinks.

## Decision

Do not promote a route or option change.

Promote this record only.

## Next Target

Run an encoding-side operational experiment, not another option sweep:

- single variable: add one deterministic stable-encoding constraint family;
- fast contract: the generated clingo program changes in a measurable way and
  still passes semantic tests;
- metric gate: representative row with `--collect-clingo-statistics` must
  reduce Unit-era conflicts or solve time before any five-row gate;
- failure analysis: if it still times out, compare stats against this record
  and state whether the encoding constraint changed the internal clingo search
  shape.

Candidate mechanism to inspect before implementation: constraints that
deterministically remove unsupported or circularly unsupported `in/1`
assignments before clingo's lookahead spends the full budget proving them away.

Generated diagnostics were not committed:

- `data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.json`
- `data\iccma\2025\runs\aba-se-st-unit-mechanism-profile-small.csv`
- `data\iccma\2025\profiles\aba-se-st-unit-mechanism-profile\small\*.raw.txt`
