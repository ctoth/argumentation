# Cap-200 Solver Frontier Execution Checklist

## Baseline

Commands:

```powershell
uv run tools\iccma2025_run_native.py --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 --label post-workstreams-cap150 --no-progress
uv run tools\iccma2025_run_native.py --max-af-arguments 200 --max-aba-assumptions 200 --timeout-seconds 5 --label post-workstreams-cap200 --no-progress
uv run tools\iccma_timeout_corpus.py --csv data\iccma\2025\runs\iccma-2025-post-workstreams-cap200.csv --output-dir data\iccma\timeouts --label post-workstreams-cap200 --checked-manifest tests\manifests\iccma2025-cap200-timeouts.json --input-root data\iccma\2025\extracted\instances
```

Measured cap-150 result:

- total rows: 7394
- solved: 833
- timeout: 12
- skipped: 6549

Measured cap-200 result:

- total rows: 7394
- solved: 1319
- timeout: 49
- skipped: 6026

Cap-200 timeout classes:

- ABA `SE-PR`: 27
- ABA `SE-ST`: 15
- AF heuristics `DS-PR`: 2
- AF heuristics `DS-SST`: 1
- AF main `DS-PR`: 2
- AF main `DS-SST`: 1
- AF main `SE-SST`: 1

## Execution Rules

- Execute this checklist in order.
- Keep `tests\manifests\iccma2025-cap200-timeouts.json` as the source of truth.
- Add properties before changing the corresponding production solver.
- Profile a timeout class before acceptance gating it.
- Use targeted manifest runs first; run the whole cap-200 manifest only after a
  class-specific improvement is kept.
- Keep a slice only if it improves the cap-200 manifest or adds a required
  correctness gate. Otherwise revert the slice.
- Do not count benchmark logs, regenerated diagnostics, or generated summaries
  as solver progress.

## Dependency-Sorted Execution Order

1. Phase 1: Verify The Cap-200 Corpus.
2. Phase 2: ABA Large Stable Closure.
3. Phase 3: ABA Large Preferred Search.
4. Phase 4: AF Semi-Stable And Preferred Unsat Rows.
5. Phase 5: Whole-Manifest Acceptance.

## Phase 1: Verify The Cap-200 Corpus

- [x] Extract timeout rows from `post-workstreams-cap200`.
- [x] Create `tests\manifests\iccma2025-cap200-timeouts.json`.
- [x] Include input SHA-256 for every manifest row.
- [x] Add tests:
  - [x] duplicate logical rows are rejected
  - [x] every manifest row resolves to an existing input file
  - [x] every stored hash matches current file contents
  - [x] timeout summaries are invariant under row order
  - [x] cap-200 timeout group shape matches the measured corpus
- [x] Run:

```powershell
uv run pytest -q tests\test_iccma_run_timeout_rows.py tests\test_iccma_timeout_corpus.py
```

Gate: the checked manifest is reproducible from the cap-200 CSV and the tests
pass.

## Phase 2: ABA Large Stable Closure

Goal: reduce the 15 ABA `SE-ST` cap-200 timeouts.

- [ ] Add Hypothesis properties:
  - [ ] bit-vector stable encoding agrees with native stable enumeration on
    small generated frameworks
  - [ ] large-framework preprocessing preserves stable witness existence
  - [ ] forced assumptions preserve closure and conflict status
  - [ ] any returned `SE-ST` witness is native-stable
- [ ] Profile all `SE-ST` timeout rows:
  - [ ] parse time
  - [ ] preprocessing/support build time
  - [ ] encoding build time
  - [ ] SAT check time
  - [ ] variable/assertion counts
- [ ] Test one mechanism per branch:
  - [ ] stable-specific forced literals
  - [ ] dependency SCC splitting before rank encoding
  - [ ] incremental rank-bound search
  - [ ] external ASP comparison for stable rows
- [ ] Run:

```powershell
uv run pytest -q tests\test_aba.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --subtrack SE-ST --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap200-aba-se-st-rerun.json
```

Gate: ABA `SE-ST` timeout count strictly decreases with no property failure.

## Phase 3: ABA Large Preferred Search

Goal: reduce the 27 ABA `SE-PR` cap-200 timeouts after the stable path is
settled.

- [ ] Add Hypothesis properties:
  - [ ] preferred CEGAR witnesses are native-preferred on small frameworks
  - [ ] learned defense clauses preserve admissible witnesses
  - [ ] preprocessing preserves `require_derived` and `require_not_derived`
  - [ ] stable-shortcut preferred witnesses remain native-preferred
- [ ] Profile all `SE-PR` timeout rows:
  - [ ] closure time
  - [ ] defense counterexample time
  - [ ] number of learned clauses
  - [ ] grow loop iterations
- [ ] Test one mechanism per branch:
  - [ ] reuse stable witness as preferred seed when sound
  - [ ] cache closure ranks across CEGAR iterations
  - [ ] assumption-component decomposition
  - [ ] external ASP fallback comparison
- [ ] Run:

```powershell
uv run pytest -q tests\test_aba.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --subtrack SE-PR --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap200-aba-se-pr-rerun.json
```

Gate: ABA `SE-PR` timeout count strictly decreases with no property failure.

## Phase 4: AF Semi-Stable And Preferred Unsat Rows

Goal: reduce the 7 AF cap-200 timeouts.

- [ ] Add Hypothesis properties:
  - [ ] semi-stable maximal range agrees with native enumeration on small AFs
  - [ ] skeptical preferred answers match native preferred enumeration on small
    AFs
  - [ ] range upper-bound shortcuts preserve satisfiability
  - [ ] unsat cores do not remove a valid witness
- [ ] Profile the AF timeout rows:
  - [ ] repeated high-range checks
  - [ ] preferred attacker checks
  - [ ] stable shortcut checks
  - [ ] range-maximality checks
- [ ] Test one mechanism per branch:
  - [ ] monotone range binary search with learned bounds
  - [ ] SCC/topological pruning for range checks
  - [ ] preferred skeptical unsat certificate reuse
  - [ ] track-neutral cache reuse between main and heuristics rows
- [ ] Run:

```powershell
uv run pytest -q tests\test_solver_encoding.py tests\test_dung.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap200-af-rerun.json
```

Gate: AF timeout count strictly decreases with no property failure.

## Phase 5: Whole-Manifest Acceptance

- [ ] Run the whole cap-200 timeout manifest:

```powershell
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --timeout-seconds 15 --backend auto --output data\iccma\timeouts\cap200-manifest-rerun.json
```

- [ ] Run a fresh cap-200 benchmark under a new label.
- [ ] Update this checklist with the final summary.

Gate: the whole-manifest timeout count decreases, and a fresh cap-200 benchmark
does not regress solved rows.

## Final Verification

- [ ] every checklist item is completed or explicitly deferred with rationale
- [ ] `uv run pytest -q` passes
- [ ] final cap-200 benchmark summary is recorded
- [ ] final timeout manifest is current
- [ ] no source files touched by this checklist are dirty
