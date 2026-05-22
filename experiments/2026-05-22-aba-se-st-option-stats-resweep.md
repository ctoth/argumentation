# ABA SE-ST clingo option statistics re-sweep

Date: 2026-05-22

Status: measured on experiment branch; source change not promoted.

Experiment branch: `exp/aba-se-st-option-stats-resweep`

## Hypothesis

The previous clingo option sweep in
`experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md` rejected
several clingo configurations and heuristics by solved-count only, but every
row hit the parent timeout before clingo statistics were returned. The
diagnostic timeout surface now returns interrupted clingo statistics, so a
representative re-sweep can distinguish options that merely still timeout from
options that actually reduce or worsen search shape.

## Operational Contract

Run the real ICCMA worker path on one representative `SE-ST` timeout row with
`--collect-clingo-statistics`. Each row must return either `timeout`, `solved`,
or `profiled` with no runner error. For every timeout, the result must include:

- `solver_metadata.clingo_interrupted = true`;
- `solver_metadata.clingo_timeout_seconds = 39.0`;
- sanitized `solver_metadata.clingo_statistics`;
- clingo search metrics for `choices`, `conflicts`, `restarts`, and
  `summary.times.solve`.

## Representative

`ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

This is the small representative from the current five-row `SE-ST` timeout
cohort and has the current diagnostic baseline:

- status: `timeout`
- choices: `592699`
- conflicts: `506395`
- restarts: `1277`
- solve time: `39.004817962646484`
- models enumerated: `0`

## Option Matrix

Re-run the previous option families on the representative row only:

- baseline default args
- `--configuration=frumpy`
- `--configuration=jumpy`
- `--configuration=tweety`
- `--configuration=handy`
- `--configuration=crafty`
- `--configuration=trendy`
- `--heuristic=Berkmin`
- `--heuristic=Vmtf`
- `--heuristic=Vsids`
- `--heuristic=Unit`
- `--heuristic=None`

## Gate Command Shape

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics [--clingo-control-arg <ARG>] --output-json data\iccma\2025\runs\aba-se-st-option-stats-resweep-<variant>.json --output-csv data\iccma\2025\runs\aba-se-st-option-stats-resweep-<variant>.csv
```

Expected duration is about 39 seconds per variant, plus setup overhead.

## Decision Rule

Promote no production option change unless a variant solves the row or reduces
search metrics materially enough to justify a five-row confirmation. A useful
candidate must improve at least one of `choices`, `conflicts`, or `restarts`
without a matching regression in row status or solve time.

If no option improves the representative search shape, the next experiment
should not be another generic clingo option sweep. It should target stable
encoding/search constraints directly.

## Promotion Rule

Promote only this experiment record to `main`. Do not promote generated JSON or
CSV diagnostics.

## Evidence

Representative baseline command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --output-json data\iccma\2025\runs\aba-se-st-option-stats-resweep-baseline.json --output-csv data\iccma\2025\runs\aba-se-st-option-stats-resweep-baseline.csv
```

Representative option/statistics commands used the command shape above with
one `--clingo-control-arg=<ARG>` at a time. Every representative row timed out
with no runner error and zero enumerated models.

Representative results:

| Variant | Status | Choices | Conflicts | Restarts | Solve seconds | Models |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | timeout | 606358 | 517888 | 1339 | 39.00228691101074 | 0 |
| `--configuration=frumpy` | timeout | 702262 | 597045 | 19 | 39.007930755615234 | 0 |
| `--configuration=jumpy` | timeout | 640740 | 546606 | 1147 | 39.01124954223633 | 0 |
| `--configuration=tweety` | timeout | 609588 | 520766 | 1340 | 39.0120735168457 | 0 |
| `--configuration=handy` | timeout | 663646 | 438620 | 609 | 39.00352668762207 | 0 |
| `--configuration=crafty` | timeout | 663795 | 579670 | 19 | 39.00626564025879 | 0 |
| `--configuration=trendy` | timeout | 620158 | 537512 | 390 | 39.01348114013672 | 0 |
| `--heuristic=Berkmin` | timeout | 679007 | 563537 | 1403 | 39.0157527923584 | 0 |
| `--heuristic=Vmtf` | timeout | 767530 | 594404 | 1521 | 39.00873565673828 | 0 |
| `--heuristic=Vsids` | timeout | 613031 | 524385 | 1346 | 39.00089645385742 | 0 |
| `--heuristic=Unit` | timeout | 561 | 44885 | 5 | 39.0024471282959 | 0 |
| `--heuristic=None` | timeout | 712142 | 520325 | 1232 | 39.014020919799805 | 0 |

The representative matrix was not a clean single-variable experiment, but it
did produce one discriminating signal: `--heuristic=Unit` changed the measured
search shape by orders of magnitude while still missing the solve gate.

Five-row Unit confirmation command:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=--heuristic=Unit --output-json data\iccma\2025\runs\aba-se-st-option-stats-resweep-heuristic-unit-five-row.json --output-csv data\iccma\2025\runs\aba-se-st-option-stats-resweep-heuristic-unit-five-row.csv
```

Five-row Unit confirmation:

| Instance | Status | Choices | Conflicts | Restarts | Solve seconds | Models |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba` | timeout | 527 | 43729 | 5 | 39.00313758850098 | 0 |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba` | timeout | 296 | 35694 | 2 | 39.01151466369629 | 0 |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba` | timeout | 333 | 36073 | 2 | 39.013511657714844 | 0 |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba` | timeout | 247 | 30392 | 1 | 39.00134468078613 | 0 |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba` | timeout | 312 | 33401 | 2 | 39.01149559020996 | 0 |

For comparison, the default diagnostic baseline on the same five rows had
roughly 459k-593k choices, 378k-506k conflicts, and 955-1277 restarts per row,
with the same timeout status and zero enumerated models.

## Failure Analysis

Profiler comparison before this experiment:

- `experiments/2026-05-22-aba-se-st-post-diagnostic-pyspy.md` showed the
  current worker path is dominated by `clingo.Control.solve`: `2446` py-spy
  samples in solve, with add, ground, parsing, preprocessing, and Python fact
  encoding at tiny counts.

Operational invariant changed:

- `--heuristic=Unit` collapsed branching and restart metrics on every row.
- The solve-time invariant did not change: every row still exhausted the
  39-second internal clingo budget and enumerated zero models.

Interpretation:

- This is not a generic "bad branching heuristic" problem anymore. The Unit
  heuristic/lookahead path makes very few decisions but still spends the full
  solve budget.
- The remaining mechanism is likely expensive propagation, lookahead, unfounded
  set handling, or proof search inside clingo's solve phase under the current
  stable encoding.
- A production `--heuristic=Unit` route is a no-go by itself because it solves
  zero of five rows, even though it exposes a real search-shape lever.

## Outcome

Weakly positive diagnostic result; production option no-go.

The experiment found the first clingo option that materially changes the hard
`SE-ST` search telemetry, but it did not solve any row and therefore does not
earn promotion as a route change.

## Decision

Do not promote a clingo option change.

Promote this record only, then run the next experiment on the mechanism exposed
by Unit: why does low-choice lookahead search still burn the entire solve
budget?

## Next Target

Next experiment should be a single-variable Unit mechanism profile:

- compare baseline versus `--heuristic=Unit` on the same representative row;
- attach py-spy to the real worker path for both;
- preserve clingo statistics;
- classify whether the hot path remains opaque `clingo.Control.solve`, moves
  to a distinguishable Python-side surface, or requires clingo-level statistics
  beyond the current summary;
- stop after this comparison and choose either an encoding constraint experiment
  or a solver-internal-statistics experiment.

Generated diagnostics were not committed:

- `data\iccma\2025\runs\aba-se-st-option-stats-resweep-*.json`
- `data\iccma\2025\runs\aba-se-st-option-stats-resweep-*.csv`
