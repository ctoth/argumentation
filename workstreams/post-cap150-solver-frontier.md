# Post-Cap150 Solver Frontier Execution Checklist

## Baseline

Command:

```powershell
uv run tools\iccma2025_run_native.py --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 --label post-aba-stable-cap150
```

Measured result:

- total rows: 7394
- solved: 829
- timeout: 16
- skipped: 6549

Remaining timeout classes:

- ABA `SE-PR`: 11
- ABA `SE-ST`: 1
- AF `DC-ID`: 2
- AF `SE-ID`: 2

## Execution Rules

- Execute the checklist in order.
- Work on one solver family at a time.
- Add properties before changing the corresponding production solver.
- Each implementation slice must end with a targeted timeout rerun.
- Keep the slice only if it improves the checked timeout manifest or provides a
  required correctness gate. Otherwise revert it.
- Before using a paper-specific rule, reread the relevant primary paper pages or
  solver source and cite that source in the commit message or notes.

## 1. Freeze The Timeout Manifest

- [x] Create `tests/manifests/iccma2025-cap150-timeouts.json` from
  `data/iccma/timeouts/post-aba-stable-cap150-timeouts.json`.
- [x] Include for each row: year, track, subtrack, instance kind, instance path,
  size fields, status, reason, elapsed seconds, and input SHA-256.
- [x] Add a small manifest validation helper or test-local function.
- [x] Add tests:
  - [x] duplicate logical rows are rejected
  - [x] every manifest row resolves to an existing input file
  - [x] every stored hash matches current file contents
  - [x] timeout summaries are invariant under row order
  - [x] year/subtrack filtering matches a simple oracle
- [x] Run:

```powershell
uv run pytest -q tests\test_iccma_timeout_corpus.py tests\test_iccma_run_timeout_rows.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap150-manifest-baseline-rerun.json
```

Gate: the rerun preserves the same timeout group shape, allowing normal elapsed
time variance.

## 2. ABA Preferred CEGAR Solver

Goal: reduce ABA `SE-PR` timeouts without materializing all minimal supports.

- [x] Add Hypothesis properties:
  - [x] ranked closure equals deterministic ABA closure for small frameworks
  - [x] preferred witness returned by the new path is native-preferred on small
    frameworks
  - [x] returned witness preserves required assumptions
  - [x] `require_derived` and `require_not_derived` agree with deterministic
    derivability
  - [x] stable shortcut witness is a native preferred extension
- [x] Implement a private CEGAR preferred witness path:
  - [x] candidate assumption set through ranked Horn closure
  - [x] conflict-free constraint
  - [x] defense counterexample query
  - [x] learned clause blocking the counterexample
  - [x] growth loop to a maximal admissible set
- [x] Route `SE-PR` through the new path only after properties pass.
- [x] Run:

```powershell
uv run pytest -q tests\test_aba.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --subtrack SE-PR --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap150-aba-se-pr-cegar-rerun.json
```

Gate: ABA `SE-PR` timeout count strictly decreases, or the implementation is
reverted. Result: 2 of 11 frozen `SE-PR` timeout rows solved at 15 seconds;
remaining `SE-PR` timeouts decreased from 11 to 9.

## 3. ABA External ASP Comparison

Goal: find out whether ASPforABA/clingo solves rows the package Z3 path misses.

- [x] Reread ASPforABA local README/source for supported tasks and CLI contract.
- [x] Add comparison-only adapter or tool wiring.
- [x] Add tests:
  - [x] missing binary returns typed unavailable
  - [x] timeout/nonzero/malformed output are distinguishable
  - [x] generated flat ABA frameworks round-trip through ICCMA ABA I/O
  - [x] generated accepted external witnesses pass local task validation
- [x] Run the timeout manifest through the ASP path.

Gate: produce a report identifying which current ABA timeouts the ASP path
solves. Do not make it default unless the correctness tests pass and the
manifest result improves. Result: `reports/cap150-aspforaba-comparison.md`
records that ASPforABA solved all 11 frozen `SE-PR` timeout rows at 15 seconds.

## 4. ABA Grounded Preprocessing

Goal: shrink preferred search before CEGAR.

- [x] Reread ABA sources before deleting or reducing any assumptions.
- [x] If source support is not clear, only force grounded assumptions; do not
  delete anything.
- [x] Add Hypothesis properties:
  - [x] grounded extension is a subset of every native preferred extension
  - [x] preprocessing is idempotent
  - [x] lifted witnesses are native preferred extensions
  - [x] query derivability is preserved after lift
- [x] Compose preprocessing with the preferred CEGAR path.
- [x] Run the ABA `SE-PR` manifest again.

Gate: timeout count or elapsed time improves. Otherwise keep it default-off or
revert. Result: reverted. The forced-grounded slice timed out all 11 frozen
`SE-PR` rows at 15 seconds, regressing the CEGAR result of 9 timeouts. Revert
commits: `3db2924` and `6873dfa`.

## 5. Stubborn ABA Stable Row

Target: `ABAs/aba_500_0.1_10_5_7.aba` under `SE-ST`.

- [x] Add diagnostics for variable count, constraint count, rule dependency
  SCCs, and SAT check time.
- [x] Maintain an experiment matrix with branch name, mechanism, compatibility,
  targeted test result, diagnostic profile result, 15-second acceptance gate
  result, and promotion decision.
- [x] For known timeout rows, profile before acceptance gating:
  - [x] phase timings: parse, preprocessing/support build, encoding build, SAT
    check
  - [x] encoding shape: variables by kind, assertions/constraints, SCC sizes
  - [x] solver result and reason at diagnostic caps such as 60, 150, and 300
    seconds
  - [x] comparison against the current baseline profile under the same caps
- [ ] Test individual mechanisms on experiment branches:
  - [x] Boolean rank ladder
  - [x] bit-vector rank
  - [ ] SCC decomposition
  - [x] forced-literal simplification
  - [x] support-materialized stable encoding
- [ ] Test compatible combinations before declaring failure:
  - [ ] forced literals plus Boolean rank ladder
  - [x] forced literals plus bit-vector rank
  - [ ] forced literals plus support-materialized stable encoding
  - [ ] SCC decomposition plus the best non-SCC encoding
- [x] Add properties:
  - [x] stable witness existence matches native stable enumeration on small
    frameworks
  - [x] new rank encoding agrees with current rank encoding on small frameworks
  - [x] simplification preserves stable witnesses
- [ ] Run diagnostic profiles for every matrix entry.
- [x] Run the 15-second targeted stable-row acceptance gate only for entries
  whose profile improves a measured bottleneck or reaches a lower diagnostic
  cap than baseline.
- [x] Run the whole timeout manifest only for a matrix winner.

Gate: the stable row solves under the same timeout and no solved stable row
regresses. Failed individual branches are preserved for inspection and possible
combination testing; they are not deleted unless explicitly requested.

Result so far: promoted bit-vector rank closure in `57a5c98`. The target
`SE-ST` row solves at 15 seconds, and the whole frozen manifest remains at 6
solved / 10 timeouts with no stable-row regression. Remaining Workstream 5
items are SCC decomposition and combinations involving mechanisms that were
individually rejected on measured bottlenecks.

## 6. AF Ideal Solver

Goal: reduce AF `DC-ID` and `SE-ID` timeouts.

- [ ] Add Hypothesis properties:
  - [ ] ideal extension equals `dung.ideal_extension` on small generated AFs
  - [ ] returned ideal set is admissible
  - [ ] returned ideal set is contained in every preferred extension
  - [ ] no admissible strict superset stays below all preferred extensions
  - [ ] `DC-ID` and `DS-ID` answers match membership in the unique ideal
    extension
- [ ] Try a direct ideal formulation or preferred-core CEGAR path.
- [ ] Run only AF ideal manifest rows first, then the whole manifest.

Gate: AF ideal timeout count decreases, or the slice is reverted.

## 7. Cap-200 Expansion

Do this only after the cap-150 timeout manifest is reduced or every remaining
timeout class is explicitly deferred with rationale.

- [ ] Run a fresh cap-150 benchmark and confirm the current default result.
- [ ] Run cap-200 under a new label.
- [ ] Extract timeout corpus.
- [ ] Create the next checked manifest.
- [ ] Start a new checklist for the cap-200 frontier.

## Final Verification

Before declaring this checklist complete:

- [ ] every checklist item is completed or explicitly deferred with rationale
- [ ] `uv run pytest -q` passes
- [ ] final cap-150 benchmark summary is recorded
- [ ] final timeout manifest is current
- [ ] no source files touched by the checklist are dirty
