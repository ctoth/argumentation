# ABA SE-ST post-diagnostic py-spy

Date: 2026-05-22

Status: completed on experiment branch.

Experiment branch: `exp/aba-se-st-post-diagnostic-pyspy`

## Hypothesis

The clingo timeout diagnostic surface from
`experiments/2026-05-22-aba-clingo-timeout-diagnostics.md` shows that the
remaining five-row `SE-ST` cohort grounds successfully, then spends the full
budget in clingo search with zero enumerated models. A fresh py-spy profile on
the current `main` worker path should confirm whether the dominant runtime is
still `clingo.Control.solve` and whether any Python-side setup, grounding, or
runner overhead has become meaningful after diagnostic timeout plumbing.

## Operational Contract

Profile the real ICCMA worker path through `tools\aba_shape_benchmark.py`, not
an isolated wrapper. The profile gate passes only if:

- py-spy records a raw profile for the representative row;
- the benchmark row status is `profiled`, `timeout`, or `solved`;
- the row has no runner error;
- the experiment record cites the profile path and classifies the dominant
  stack as one of: clingo solve, clingo grounding/add, Python fact encoding,
  preprocessing/simplification, parsing/runner overhead, or inconclusive.

## Representative

Use the same small representative that appears in the five-row diagnostic
cohort:

`ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

## Command

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-post-diagnostic-pyspy\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.json --output-csv data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.csv
```

Expected command duration: about 25 seconds for the profile window plus
benchmark setup overhead.

## Decision Rule

If the dominant stack is still clingo solve, the next production experiment
must change a measured clingo search-shape invariant before the full five-row
benchmark gate. Good candidates are deterministic constraints that reduce
choices/conflicts or an option sweep with clingo statistics as the first gate.

If the dominant stack has moved to Python setup, grounding/add, preprocessing,
or runner overhead, the next experiment must target that measured hot path
instead.

## Promotion Rule

Promote only this experiment record to `main`. Do not promote generated JSON,
CSV, or raw profile artifacts.

## Evidence

Availability check:

```powershell
uv tool run py-spy --version
```

Result: `py-spy 0.4.2`.

Profile command run:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-post-diagnostic-pyspy\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.json --output-csv data\iccma\2025\runs\aba-se-st-post-diagnostic-pyspy-small.csv
```

Result:

- row status: `profiled`
- reason: `profile_duration_elapsed`
- error: `null`
- profile:
  `data\iccma\2025\profiles\aba-se-st-post-diagnostic-pyspy\small\aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

## Profile Classification

Dominant stack: clingo solve.

Hot frames:

- `solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo\control.py:1065) -> _c_call`: `2446` samples
- `find_stable_extension -> _new_control -> ground (clingo\control.py:566)`: `20` samples
- `find_stable_extension -> _new_control -> add (clingo\control.py:320) -> _add2`: `18` samples
- parsing, preprocessing, Python fact encoding, runner setup, and clingo import: single-digit samples each

This matches the earlier profile shape recorded in
`experiments/2026-05-21-aba-se-st-direct-stable-encoding.md`: the hard row is
still overwhelmingly dominated by `clingo.Control.solve`, not Python setup,
grounding, add, parsing, preprocessing, or runner overhead.

## Decision

The current bottleneck has not moved. The next production experiment must
change clingo search shape before the five-row benchmark gate.

The most principled next slice is a clingo-option/statistics experiment with a
first executable gate over one representative row:

- run the same representative with a small option matrix;
- require `collect_clingo_statistics`;
- compare `choices`, `conflicts`, `restarts`, `summary.times.solve`, and row
  status against the diagnostic baseline;
- promote only an option set that reduces clingo search telemetry or solves a
  row without worsening default route behavior.

Do not spend the next slice on Python micro-optimization, parser cleanup,
grounding/add tuning, or another semantic-only encoding deletion; the profiler
does not support those targets.
