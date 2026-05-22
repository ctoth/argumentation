# ABA SE-ST clingo option statistics re-sweep

Date: 2026-05-22

Status: planned on experiment branch.

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
