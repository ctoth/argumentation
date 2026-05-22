# ABA SE-ST lookahead isolation

Date: 2026-05-22

Status: measured on experiment branch; source change not promoted.

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

## Experiment Result

Command run:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=--heuristic=Vsids --clingo-control-arg=--lookahead=atom --output-json data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.json --output-csv data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.csv
```

Result:

- status: `timeout`
- reason: `clingo solve exceeded 39.000s`
- error: `null`
- control args: `--models=0 --warn=none --heuristic=Vsids --lookahead=atom`
- choices: `511`
- conflicts: `48983`
- restarts: `5`
- solve time: `39.009939193725586`
- models enumerated: `0`

Grounded problem shape stayed the same as the existing Unit/default diagnostic
rows:

- `problem.lp.atoms = 98225`
- `problem.lp.bodies = 53472`
- `problem.lp.rules = 117535`
- `problem.lp.eqs = 141293`
- `problem.generator.vars = 6666`
- `problem.generator.constraints = 3273`
- `problem.generator.complexity = 31315`

Comparison:

| Variant | Status | Choices | Conflicts | Restarts | Solve seconds | Models |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `--heuristic=Vsids` | timeout | 613031 | 524385 | 1346 | 39.00089645385742 | 0 |
| `--heuristic=Vsids --lookahead=atom` | timeout | 511 | 48983 | 5 | 39.009939193725586 | 0 |
| `--heuristic=Unit` | timeout | 561 | 44885 | 5 | 39.0024471282959 | 0 |

## Interpretation

The Unit signal is lookahead/failed-literal driven.

Adding `--lookahead=atom` to plain `Vsids` reproduces the Unit shape: choices
and restarts collapse by roughly three orders of magnitude, while solve time and
timeout status do not improve. The grounded program did not shrink, so this is
not a grounding or encoding-size effect. It is clingo spending the full budget
inside solve while failed-literal/lookahead probing avoids ordinary branching.

## Outcome

Positive mechanism isolation; production option no-go.

This experiment identifies the mechanism behind the previous Unit signal. It
does not solve the row and does not justify a production clingo option change.

## Decision

Do not run more lookahead/heuristic variants in this track. The mechanism is
now sufficiently identified for the next step: the encoding must make the
lookahead/proof obligation smaller.

## Next Target

Run one stable-encoding experiment with an operational contract against this
representative row:

- single variable: add one deterministic constraint or derived predicate family
  to reduce unsupported/circularly unsupported `in/1` candidates;
- fast contract: the generated stable program changes measurably while
  semantic equivalence holds on focused ABA tests;
- metric gate: with `--heuristic=Vsids --lookahead=atom`, the representative
  row must reduce conflicts or solve time against this record before any
  five-row gate;
- failure analysis: if it still times out, compare choices/conflicts/restarts
  and state whether the encoding changed the lookahead proof burden.

Generated diagnostics were not committed:

- `data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.json`
- `data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.csv`
