# ABA Real PrefSat Failed Hypothesis

Date: 2026-05-18

Branch: `experiment/aba-real-complete-labelling-prefsat`

Workflow used: `workstreams/aba-real-complete-labelling-prefsat.md`.

## Verdict

The direct ABA complete-labelling PrefSat implementation satisfied the current
architecture lock and property/regression gates, but it failed the Phase 7 hard
row gate. This is a failed benchmark hypothesis for this implementation of the
paper architecture; it is not evidence that every possible PrefSat-style solver
or every paper-driven decomposition of preferred semantics cannot win.

The implementation did not fail by falling back to the old preferred CEGAR
route. The post-fix T1 `sat` profile contains `real_prefsat_extension`,
`preferred_extension`, `_solve_admissible`, `_attacker_counterexample`, and
`_unanswered_attack_support`, and contains no `_sat_ranked_stable_extension`
frame.

## Paper Claim Tested

The tested claim was that a complete-labelling SAT architecture for preferred
semantics, with candidate growth and subset blocking from Cerutti, Dunne,
Giacomin, and Vallati 2013 and the ArgSemSAT-style implementation surface from
Cerutti, Vallati, and Giacomin 2015, could be applied directly to ABA while
respecting Lehtonen, Wallner, and Jarvisalo 2021's warning not to pay an
exponential AF-translation cost up front.

The implementation also used the Niskanen and Jarvisalo 2020 lesson that solver
state and assumptions matter, but the current direct ABA implementation still
performs expensive repeated SAT checks inside the candidate/adversary loop.

## Contracts Passed

Architecture and substitute-rejection gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_real_prefsat_contract.py
```

Result: `13 passed in 121.05s`.

Regression and operational-contract gate after routing preferred SAT directly
to the real PrefSat path:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Result: `1067 passed, 1 skipped in 110.01s`.

## Target Row Failure

Phase 7 command:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-real-prefsat-targeted.json --output-csv data\iccma\2025\runs\aba-real-prefsat-targeted.csv
```

Primary preferred rows:

| Target | Instance | Result |
|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `auto`, `asp`, and `sat` timed out; validation `not_checked` |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `auto`, `asp`, and `sat` timed out; validation `not_checked` |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `auto`, `asp`, and `sat` timed out; validation `not_checked` |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `auto`, `asp`, and `sat` timed out; validation `not_checked` |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `auto`, `asp`, and `sat` timed out; validation `not_checked` |

No primary preferred target counted as solved because the workstream required
`status == "solved"` and `validation.status == "valid"` for backend `sat` or
`auto`.

Controls were preserved by the existing production routes:

| Control | Result |
|---|---|
| C1 `SE-ST` on `ABAs/aba_2000_0.1_5_5_3.aba` | solved by `sat`/`auto` |
| C2 `SE-PR` on `ABAs/aba_2000_0.1_5_5_7.aba` | solved by `asp`/`auto`; `sat` timed out |
| C3 `SE-ST` on `ABAs/aba_2000_0.1_5_5_7.aba` | solved by `asp`; `sat` timed out |

## Profiler Attribution

Profile command:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --backend sat --subtrack SE-PR --timeout-seconds 30 --profile-duration-seconds 25 --profile-format speedscope --profile-dir data\iccma\2025\profiles\aba-real-prefsat --output-json data\iccma\2025\runs\aba-real-prefsat-t1-profile.json --output-csv data\iccma\2025\runs\aba-real-prefsat-t1-profile.csv
```

The runner produced `worker_bad_json` rows because `py-spy` wrote status text
into the worker output stream, but it did write usable speedscope files. The
T1 `sat` artifact used for attribution was:

`data\iccma\2025\profiles\aba-real-prefsat\aba-SE-PR-sat-aba_2000_0.1_5_5_0.aba-20bddb900dfb.speedscope.json`

Sample facts from that artifact:

- 2498 samples over 24.98 seconds.
- Inclusive counts: `real_prefsat_extension` 2494, `_solve_admissible` 2330,
  `_unanswered_attack_support` 2271, `Z3_solver_check_assumptions` 2099.
- Leaf counts: `Z3_solver_check_assumptions` 2099, far above all Python or
  model-construction leaf frames.
- `_prefsat_add_closure_constraints` appeared during construction, but did not
  dominate the 25-second sample.

The failed T1 run is therefore dominated by SAT checks inside the real PrefSat
admissibility/attacker loop. The immediate slow class is not parsing,
validation, answer checking, eager support materialization, the old stable
precheck, or the old preferred CEGAR path.

## Next Hypothesis

The next hypothesis should not be "try another semantic variant." The direct
real PrefSat loop is spending the hard-row budget in repeated SAT checks over a
large dense flat ABA instance. The next executable workstream should first add
operational contracts for reducing those checks or the problem seen by each
check, then implement one paper-driven structural improvement.

Concrete candidate:

- Use SCC-recursive conditioning and input/query separation before preferred
  maximality, guided by Baroni and Giacomin 2005 and Egly, Gaggl, and Woltran
  2010.
- Preserve Lehtonen, Wallner, and Jarvisalo 2021's direct ABA fact surface:
  do not translate the full ABA instance to AF eagerly.
- Preserve Niskanen and Jarvisalo 2020's solver-engineering discipline:
  measure bounded solver checks, persistent state reuse, and residual-size
  reduction before running the ICCMA hard-row gate.
- The first properties should assert measurable routing and residual effects:
  a dense flat preferred row must not enter the direct full-instance PrefSat
  loop unless decomposition produces no reduction, and solved components must
  reduce the residual assumptions/rules or the route must report why no
  reduction exists.

This failed hypothesis should not be promoted to `main`.
