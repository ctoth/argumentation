# ABA SE-ST defeated-out propagation

Date: 2026-05-22

Status: measured on experiment branch; source change not promoted.

Experiment branch: `exp/aba-se-st-defeated-out-propagation`

## Evidence Commits

- `41d2682` record initial experiment plan
- `833ad0f` fast contract for stable defeated-out propagation
- `2feba95` source delta adding stable defeated-out propagation

## Hypothesis

The current stable multishot encoding leaves clingo to learn that an assumption
defeated by the current `in/1` set must be `out/1` through the conflict-free
constraint plus the exactly-one `in/out` choice. Making that implication
explicit as a stable-only propagation rule should reduce the failed-literal /
lookahead proof burden measured in
`experiments/2026-05-22-aba-se-st-lookahead-isolation.md`.

## Single Variable

Add one stable-only rule to the extra program used by `find_stable_extension`
and stable enumeration:

```prolog
out(X) :- defeated(X).
```

Keep the existing stable coverage constraint:

```prolog
:- out(X), not defeated(X).
```

No clingo option, route, preprocessing, or runner behavior changes in this
experiment.

## Baseline

Representative:

`ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

Baseline command from
`experiments/2026-05-22-aba-se-st-lookahead-isolation.md`:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=--heuristic=Vsids --clingo-control-arg=--lookahead=atom --output-json data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.json --output-csv data\iccma\2025\runs\aba-se-st-lookahead-isolation-vsids-atom.csv
```

Baseline result:

- status: `timeout`
- choices: `511`
- conflicts: `48983`
- restarts: `5`
- solve time: `39.009939193725586`
- models enumerated: `0`

## Paper / Code Basis

Read from page images:

- `papers\Lehtonen_2021_IncrementalASP_ABA_pngs\page-000005.png`
- `papers\Lehtonen_2021_IncrementalASP_ABA_pngs\page-000006.png`

Page 6 Listing 1 defines `defeated(X)` from `supported(Y), contrary(X,Y)`.
The current code adds stable coverage separately as
`:- out(X), not defeated(X).`. Since the complete module already has exactly
one of `in(X)` and `out(X)` for each assumption and conflict-free excludes
`in(X)` when `defeated(X)` holds, the rule `out(X) :- defeated(X).` should be
semantically redundant but propagation-relevant.

## Fast Contracts

Before the metric gate:

- add a test proving the stable extra program contains both
  `out(X) :- defeated(X).` and `:- out(X), not defeated(X).`;
- run focused multishot semantic tests that compare the incremental solver to
  native ABA on stable examples;
- run the targeted sparse-route contract that keeps default routing unchanged.

Executed:

```powershell
uv run pytest -q tests\test_aba_multishot.py::test_stable_single_extension_adds_defeated_out_propagation
```

Red before source change: failed because `out(X) :- defeated(X).` was absent.

```powershell
uv run pytest -q tests\test_aba_multishot.py::test_stable_single_extension_adds_defeated_out_propagation tests\test_aba_multishot.py -k "stable and not timeout"
```

Result after source change: `178 passed, 852 deselected in 7.61s`.

```powershell
uv run pytest -q tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py -k "stable or defeated_out"
```

Result: `180 passed, 856 deselected in 7.73s`.

## Metric Gate

Run the same representative row and options as the lookahead isolation
baseline:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=--heuristic=Vsids --clingo-control-arg=--lookahead=atom --output-json data\iccma\2025\runs\aba-se-st-defeated-out-propagation-vsids-atom.json --output-csv data\iccma\2025\runs\aba-se-st-defeated-out-propagation-vsids-atom.csv
```

Pass condition for expanding to five rows: solve the row, reduce solve time, or
reduce conflicts materially versus `48983` without increasing choices/restarts.

Measured result:

- status: `timeout`
- reason: `clingo solve exceeded 39.000s`
- choices: `541`
- conflicts: `49851`
- restarts: `4`
- solve time: `39.00374221801758`
- models enumerated: `0`
- clingo problem size: `98225` atoms, `54872` bodies, `118935` rules,
  `144089` eqs

This misses the pass condition. It does not solve the row, does not reduce
solve time in a meaningful way, and increases both choices and conflicts versus
the lookahead-isolation baseline.

## Failure-Analysis Gate

If the row still times out and conflicts/solve time do not materially improve,
record this as a true no-go: the explicit defeated-to-out propagation did not
change clingo's lookahead proof burden.

Executed profiler command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --collect-clingo-statistics --profile-dir data\iccma\2025\profiles\aba-se-st-defeated-out-propagation --profile-format raw --profile-duration-seconds 25 --clingo-control-arg=--heuristic=Vsids --clingo-control-arg=--lookahead=atom --output-json data\iccma\2025\runs\aba-se-st-defeated-out-propagation-profile-vsids-atom.json --output-csv data\iccma\2025\runs\aba-se-st-defeated-out-propagation-profile-vsids-atom.csv
```

Profiler result:

- status: `profiled`
- reason: `profile_duration_elapsed`
- elapsed: `24.741871499922127`
- profile path:
  `data\iccma\2025\profiles\aba-se-st-defeated-out-propagation\aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`
- raw profile shape: `14` folded stack lines
- top visible stacks:
  - `clingo.Control.add` / `_add2`: `11` samples
  - `clingo.Control.ground`: `10` samples
  - `clingo.Control.solve` / `_c_call`: `6` samples

Compared against:

- `experiments/2026-05-22-aba-se-st-lookahead-isolation.md`, which isolated
  `--lookahead=atom` as the mechanism behind the Unit-like telemetry collapse.
- `experiments/2026-05-22-aba-se-st-unit-mechanism-profile.md`, where the
  worker profile showed the dominant visible cost in `clingo.Control.solve`
  / `_c_call`.

Interpretation:

The intended invariant did not improve. The explicit stable rule left the same
route, same residual ABA shape, same unsolved representative row, same
one-worker clingo solve call, and essentially the same clingo problem size.
Solver telemetry worsened slightly: choices rose from `511` to `541` and
conflicts rose from `48983` to `49851`.

The py-spy profile did attach to the real worker process, not just the wrapper.
However, this particular raw profile is sparse and should not be overread as a
precise native-time attribution. The operational conclusion is still strong
because the clingo statistics and metric gate show no propagation benefit: the
bottleneck did not move to Python preprocessing or routing, and the attempted
`defeated -> out` encoding shortcut did not shrink the lookahead proof burden.

Next target from evidence:

Do not add more stable-only consequences of `defeated/1`. The next experiment
should target the upstream generation of `defeated/1` / `supported/1` itself or
the residual structure before clingo sees the stable witness problem. The
current result says the expensive part is not the final `out/1` consequence; it
is proving the defeated/supported structure under the candidate `in/1` set.

## Kill Criteria

Stop after the one representative metric gate unless the pass condition is met.
Do not add more propagation rules in this experiment.

## Promotion Rule

Promote source only if semantic tests pass and the metric gate improves. Always
promote the experiment record once measured. Do not commit generated JSON/CSV
diagnostics.

## Outcome

Negative.

## Decision

Abandon the source/test delta on
`exp/aba-se-st-defeated-out-propagation`; promote only this experiment record to
`main`.

## Generated Diagnostics

- `data\iccma\2025\runs\aba-se-st-defeated-out-propagation-vsids-atom.json`
- `data\iccma\2025\runs\aba-se-st-defeated-out-propagation-vsids-atom.csv`
- `data\iccma\2025\runs\aba-se-st-defeated-out-propagation-profile-vsids-atom.json`
- `data\iccma\2025\runs\aba-se-st-defeated-out-propagation-profile-vsids-atom.csv`
- `data\iccma\2025\profiles\aba-se-st-defeated-out-propagation\aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

These generated diagnostics were not committed.
