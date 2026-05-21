# ABA SE-ST clingo statistics and option sweep

Date: 2026-05-20

Branch: `exp/aba-se-st-clingo-stats-option-sweep`

Workstream: `notes/workstream-aba-se-st-clingo-stats-option-sweep-2026-05-20.md`

## Hypothesis

The exact five remaining large sparse/narrow `SE-ST` ABA timeout rows might be
solvable by a bounded clingo configuration or heuristic change. If not, the
result should rule out production clingo-option changes and move the next
workstream to stable-encoding architecture.

## Source and test commits

- `c177ad3` Add clingo diagnostic multishot contracts
- `a27ea3d` Assert default sparse narrow clingo diagnostics
- `5510e95` Add ICCMA clingo diagnostic pass-through contracts
- `94ac06a` Add clingo control args and statistics telemetry
- `0dab53f` Thread clingo diagnostics through ABA ASP metadata
- `7bf4275` Expose clingo diagnostics on ABA single extension
- `8f5b277` Pass clingo diagnostics through ICCMA ABA worker
- `b29729f` Add clingo diagnostics to ABA shape benchmark jobs
- `2ec0a36` Accept clingo diagnostic kwargs in route contract

## Cohort

Generated from the validated 10x10 run:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
```

Validation:

```powershell
jq 'length' data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
jq '[.[] | .subtrack] | unique' data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
```

Result:

- length: `5`
- subtracks: `["SE-ST"]`

Rows:

- `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

## Verification

Focused test gate:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py tests\test_iccma_runner.py
```

Result:

- red gate before implementation: `5 failed, 1046 passed`
- final gate after implementation: `1051 passed`

Search gates:

```powershell
rg -F 'Control(["--models=0", "--warn=none"])' src tests
rg -F "collect_clingo_statistics" src tools tests
rg -F "clingo_control_args" src tools tests
```

Result:

- inline hard-coded `Control(["--models=0", "--warn=none"])`: no results
- diagnostic statistics and control-argument plumbing: present in source,
  tools, and tests

## Baseline command

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --output-json data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-baseline.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-baseline.csv
```

Baseline result:

- solved: `0`
- timeout: `5`
- invalid witnesses: `0`
- runner errors: `0`
- clingo statistics rows: `0`

## Option commands

Each variant used this command shape:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg=<ARG> --output-json data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-<VARIANT>.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-<VARIANT>.csv
```

The exact `<ARG>` and `<VARIANT>` pairs were:

- `--configuration=frumpy`: `configuration-frumpy`
- `--configuration=jumpy`: `configuration-jumpy`
- `--configuration=tweety`: `configuration-tweety`
- `--configuration=handy`: `configuration-handy`
- `--configuration=crafty`: `configuration-crafty`
- `--configuration=trendy`: `configuration-trendy`
- `--heuristic=Berkmin`: `heuristic-berkmin`
- `--heuristic=Vmtf`: `heuristic-vmtf`
- `--heuristic=Vsids`: `heuristic-vsids`
- `--heuristic=Unit`: `heuristic-unit`
- `--heuristic=None`: `heuristic-none`

`--heuristic=Unit` emitted clingo's informational warning:
`Heuristic 'Unit' implies lookahead. Using 'atom'.`
It was not a rejection and did not produce a runner error.

## Results

| Variant | Solved | Timeout | Invalid witnesses | Runner errors | Clingo statistics rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 0 | 5 | 0 | 0 | 0 |
| `--configuration=frumpy` | 0 | 5 | 0 | 0 | 0 |
| `--configuration=jumpy` | 0 | 5 | 0 | 0 | 0 |
| `--configuration=tweety` | 0 | 5 | 0 | 0 | 0 |
| `--configuration=handy` | 0 | 5 | 0 | 0 | 0 |
| `--configuration=crafty` | 0 | 5 | 0 | 0 | 0 |
| `--configuration=trendy` | 0 | 5 | 0 | 0 | 0 |
| `--heuristic=Berkmin` | 0 | 5 | 0 | 0 | 0 |
| `--heuristic=Vmtf` | 0 | 5 | 0 | 0 | 0 |
| `--heuristic=Vsids` | 0 | 5 | 0 | 0 | 0 |
| `--heuristic=Unit` | 0 | 5 | 0 | 0 | 0 |
| `--heuristic=None` | 0 | 5 | 0 | 0 | 0 |

No row solved in any run, so every witness validation status was `not_checked`.
Clingo statistics were unavailable for every benchmark row because the runner
terminated each worker at the timeout boundary before `Control.solve` returned.

## Decision

No-go for a production clingo-option change.

Every tested clingo configuration and heuristic variant remained `0/5` solved
with the same timeout shape as baseline. The sweep did not expose a deterministic
search-statistics pattern or a concrete clingo option worth promoting.

## Next workstream

Move to stable ABA encoding architecture.

The next workstream should target the current `SE-ST` stable encoding itself,
not Python setup and not generic clingo option selection. The executable
contract should compare a concrete encoding deletion or rewrite against this
record's baseline:

- exact same five-row cohort;
- `0` invalid witnesses;
- solved count better than `0/5`, or a smaller deterministic grounded/search
  surface that names the next deletion target;
- no default production route change unless the metric gate passes.

## Generated diagnostics

Generated diagnostics were intentionally not promoted:

- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-timeouts.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-baseline.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-baseline.csv`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-configuration-*.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-configuration-*.csv`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-heuristic-*.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-heuristic-*.csv`
