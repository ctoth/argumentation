# ABA SE-ST lookahead isolation

Date: 2026-05-22

Status: planned on experiment branch.

Experiment branch: `exp/aba-se-st-lookahead-isolation`

## Hypothesis

The `--heuristic=Unit` signal from
`experiments/2026-05-22-aba-se-st-option-stats-resweep.md` comes primarily from
lookahead/failed-literal detection, not from Unit's broader Smodels-like
branching behavior. If that is true, adding `--lookahead=atom` to an existing
non-Unit heuristic should collapse choices and restarts toward the Unit profile.

## Single Variable

Add exactly one clingo control argument to an existing measured variant:

`--lookahead=atom`

The comparison is against the already measured `--heuristic=Vsids` row. This
experiment runs `--heuristic=Vsids --lookahead=atom` on the same representative
row.

## Baseline

Representative:

`ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

Existing `--heuristic=Vsids` result from
`data\iccma\2025\runs\aba-se-st-option-stats-resweep-heuristic-vsids.json`:

- status: `timeout`
- choices: `613031`
- conflicts: `524385`
- restarts: `1346`
- solve time: `39.00089645385742`
- models enumerated: `0`

Existing `--heuristic=Unit` result from
`data\iccma\2025\runs\aba-se-st-option-stats-resweep-heuristic-unit.json`:

- status: `timeout`
- choices: `561`
- conflicts: `44885`
- restarts: `5`
- solve time: `39.0024471282959`
- models enumerated: `0`

## Fast Contracts

The result must include:

- `backend_results.auto.status` in `{timeout, solved, profiled}`;
- `backend_results.auto.error = null`;
- `solver_metadata.clingo_control_args` containing `--heuristic=Vsids` and
  `--lookahead=atom`;
- `solver_metadata.clingo_statistics`;
- search metrics for choices, conflicts, restarts, solve time, and enumerated
  models.

## Metric Gate

Run exactly one representative row:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=--heuristic=Vsids --clingo-control-arg=--lookahead=atom --output-json data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.json --output-csv data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.csv
```

Expected duration: about 39 seconds plus setup overhead.

## Decision Rule

If `Vsids + lookahead=atom` collapses choices/restarts toward Unit while still
timing out, the Unit signal is lookahead/failed-literal driven and the next
target should be stable-encoding constraints that reduce what failed-literal
probing has to prove.

If it behaves like plain `Vsids`, Unit's broader heuristic behavior is the
measured lever, but still no production option is promoted because Unit solved
zero of five rows.

## Kill Criteria

Stop after this one row. Do not run more heuristics, more lookahead modes, or a
five-row confirmation in this experiment.

## Promotion Rule

Promote only this experiment record to `main`. Do not promote generated JSON or
CSV diagnostics.
