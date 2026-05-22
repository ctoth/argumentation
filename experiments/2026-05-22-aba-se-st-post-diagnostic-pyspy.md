# ABA SE-ST post-diagnostic py-spy

Date: 2026-05-22

Status: planned on experiment branch.

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
