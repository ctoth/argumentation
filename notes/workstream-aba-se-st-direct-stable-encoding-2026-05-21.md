# Workstream: ABA SE-ST Direct Stable ASP Encoding

Date: 2026-05-21

## Requested Outcome

Replace the `SE-ST` single-extension clingo path's use of the complete-set
`pi_com` module with a direct stable-only ASP encoding, then measure whether
that encoding improves the exact five-row timeout cohort.

This is an encoding architecture experiment. It is not Python setup work, not
generic clingo option tuning, not a SAT-engine swap, and not an IPASIR callback
experiment.

## Current Evidence

- `experiments/2026-05-20-direct-asp-sparse-narrow-routing.md` promoted ASP
  routing for large sparse/narrow `SE-ST`; it improved the 10x10 fixture from
  `5/20` solved to `9/20` solved.
- `experiments/2026-05-20-aba-se-st-clingo-solver-shape.md` showed the
  remaining five `SE-ST` timeout rows are clingo-solve dominated:
  - smaller representative: `2450` samples in `clingo.Control.solve`;
  - larger representative: `2416` samples in `clingo.Control.solve`;
  - encoding, add, ground, routing, and validation were tiny.
- `experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md` ran baseline
  plus eleven clingo option variants on the same five rows. Every run remained
  `0/5` solved, `5/5` timeout, with `0` invalid witnesses and `0` runner
  errors.
- `experiments/2026-05-20-glucose4-hard-row-full-profile.md` ruled out Python
  loop-formula micro-optimization for the native SAT route; CDCL solve time
  dominated.
- `experiments/2026-05-20-cadical195-sparse-narrow-engine.md` showed a SAT
  engine swap was weakly positive but not close to the `30s` gate.
- `experiments/2026-05-20-ipasir-up-overhead-probe.md` ruled out an
  all-variable eager IPASIR-UP propagator as the next move.
- `experiments/2026-05-20-sparse-narrow-ipasir-check-model.md` showed the
  narrower check-model callback path timed out and was worse than both current
  `glucose4` and `cadical195`.

The existing stable clingo path is:

- `src/argumentation/aba_incremental.py::AbaIncrementalSolver.find_stable_extension`
  calls `_new_control(extra_program=":- out(X), not defeated(X).")`;
- `_new_control` always loads
  `src/argumentation/encodings/aba_com_incremental.lp`;
- `aba_com_incremental.lp` is `pi_com`, a complete-set module containing
  `derived_from_undefeated/1`, `triggered_by_undefeated/1`,
  `attacked_by_undefeated/1`, and complete/admissibility constraints.

The direct stable facts and page locations are already repo-locatable:

- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md`
  records that Listing 1 defines `pi_common`, and that stable semantics adds
  the constraint forcing every `out` assumption to be defeated.

Before implementation, the executor must read those page images directly and
write the page-image claim into the experiment record. The notes file is only a
locator here; it is not a substitute for page-image reading.

## Target Architecture

For flat ABA stable single-extension, use a stable-only ASP program:

```prolog
in(X) :- assumption(X), not out(X).
out(X) :- assumption(X), not in(X).

supported(X) :- assumption(X), in(X).
supported(X) :- head(R,X), triggered_by_in(R).
triggered_by_in(R) :- head(R,_), supported(X) : body(R,X).

:- in(X), contrary(X,Y), supported(Y).

defeated(X) :- supported(Y), contrary(X,Y).
:- out(X), not defeated(X).

#show in/1.
#show supported/1.
```

This keeps the common assumption choice, support closure, conflict-freeness,
and stable coverage rules. It deletes the complete/admissibility-only
undefeated-derivation layer from the `SE-ST` witness path.

## Final State

Committed source/test support:

- `src/argumentation/encodings/aba_stable_direct.lp`
  - contains the stable-only program above;
  - does not contain `derived_from_undefeated`,
    `triggered_by_undefeated`, or `attacked_by_undefeated`.
- `src/argumentation/aba_incremental.py`
  - loads `aba_stable_direct.lp` for `find_stable_extension`;
  - no longer implements stable single-extension by calling
    `_new_control(extra_program=":- out(X), not defeated(X).")`;
  - keeps `aba_com_incremental.lp` for complete, preferred, grounded-adjacent,
    and enumeration paths that still need `pi_com`.
- `src/argumentation/aba_asp.py`
  - metadata for stable single-extension records
    `stable_encoding == "direct_stable"`;
  - complete/preferred metadata still records the existing incremental ASP
    paper provenance.
- `tests/test_aba_multishot.py`
  - resource test proves `aba_stable_direct.lp` contains the direct stable
    rules and omits the undefeated complete-layer predicates;
  - stable single-extension still matches native ABA stable semantics on the
    existing hand/random batteries;
  - complete and preferred tests still use `pi_com`.
- `tests/test_aba_sparse_narrow_route_contract.py`
  - stable sparse/narrow auto route still calls clingo multishot and now
    reports `stable_encoding == "direct_stable"`.

Committed experiment record:

`experiments/2026-05-21-aba-se-st-direct-stable-encoding.md`

Generated diagnostics, not committed:

- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.json`
- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.csv`

## Deletion Target

Delete this production stable-witness construction:

```python
ctl = self._new_control(extra_program=":- out(X), not defeated(X).")
```

Replace it with a stable-only control construction that loads
`aba_stable_direct.lp`.

Do not delete `aba_com_incremental.lp`; it remains the `pi_com` module for
complete/preferred paths.

## Owned Paths

Source:

- `src/argumentation/encodings/aba_stable_direct.lp`
- `src/argumentation/aba_incremental.py`
- `src/argumentation/aba_asp.py`

Tests:

- `tests/test_aba_multishot.py`
- `tests/test_aba_sparse_narrow_route_contract.py`

Documentation/records:

- this workstream file
- `experiments/2026-05-21-aba-se-st-direct-stable-encoding.md`

Generated diagnostics:

- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.json`
- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.csv`

## Ordered Phases

### Phase 0: Branch

Verify current branch and tracked-file cleanliness:

```powershell
git branch --show-current
git status --short
```

Create the experiment branch:

```powershell
git switch -c exp/aba-se-st-direct-stable-encoding
```

Gate: no tracked dirty files before branch creation.

### Phase 1: Page-Image Semantics Check

Read the page images directly:

- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`

Record in the experiment file:

- the stable semantics constraint from the page image;
- the fact/input vocabulary needed by the direct stable encoding;
- whether the complete/admissibility undefeated-derivation predicates are
  required for stable single-extension.

Gate:

- do not implement source changes until the experiment record has a
  page-image-backed statement of the stable direct rules;
- do not use `pdftotext` or extracted PDF text for this gate.

### Phase 2: Contract Tests

Add failing tests before implementation:

- `tests/test_aba_multishot.py`
  - `aba_stable_direct.lp` exists and contains the direct stable rules;
  - `aba_stable_direct.lp` does not contain
    `derived_from_undefeated`, `triggered_by_undefeated`, or
    `attacked_by_undefeated`;
  - `find_stable_extension` reports telemetry/metadata identifying
    `direct_stable`;
  - stable single-extension still matches native ABA stable semantics on the
    existing battery.
- `tests/test_aba_sparse_narrow_route_contract.py`
  - sparse/narrow stable auto with clingo available reports
    `stable_encoding == "direct_stable"`.

Test command:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py
```

Gate:

- new tests fail before implementation for the missing direct stable resource
  or missing metadata;
- existing complete/preferred tests remain unchanged in intent.

### Phase 3: Direct Stable Encoding Implementation

Implement:

- add `src/argumentation/encodings/aba_stable_direct.lp`;
- add a stable-specific resource constant in `aba_incremental.py`;
- add a stable-specific control constructor that combines ABA facts with
  `aba_stable_direct.lp`;
- change `find_stable_extension` to use that constructor;
- add telemetry/metadata value `stable_encoding == "direct_stable"` for stable
  single-extension results.

Search gates:

```powershell
rg -n -F '_new_control(extra_program=":- out(X), not defeated(X).")' src tests
rg -n -F "derived_from_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "triggered_by_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "attacked_by_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "stable_encoding" src tests
```

Required result:

- first search has no results;
- the three direct-stable forbidden predicate searches have no results;
- `stable_encoding` appears in intentional source/test locations.

### Phase 4: Focused Verification

Run:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py
```

Gate:

- all focused tests pass;
- no generated diagnostics are staged or committed.

Commit the source/test implementation before metric benchmarking.

### Phase 5: Baseline Cohort Manifest

Regenerate the exact five-row cohort:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
```

Validate:

```powershell
jq 'length' data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
jq '[.[] | .subtrack] | unique' data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
```

Gate:

- manifest length is `5`;
- unique subtracks are `["SE-ST"]`.

### Phase 6: Five-Row Metric Gate

Run:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --output-json data\iccma\2025\runs\aba-se-st-direct-stable-encoding-five-row.json --output-csv data\iccma\2025\runs\aba-se-st-direct-stable-encoding-five-row.csv
```

Metric pass requires:

- no runner errors;
- no invalid witnesses;
- solved count greater than `0/5`, or a measured deterministic reduction in
  grounded/search surface that names the next deletion target;
- every solved row has metadata `stable_encoding == "direct_stable"`.

Metric fail requires:

- abandon the source delta;
- record the failed metric in the experiment record;
- do not promote the direct stable route to `main`.

### Phase 7: Regression Gate

Run:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\direct-asp-auto-10x10-shape-manifest.json --backend auto --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-st-direct-stable-encoding-10x10.json --output-csv data\iccma\2025\runs\aba-se-st-direct-stable-encoding-10x10.csv
```

Metric pass requires:

- solved count at least `9/20`;
- invalid witnesses `0`;
- `SE-ST` solved rows routed through clingo report
  `stable_encoding == "direct_stable"`.

Metric fail requires:

- abandon the source delta;
- record the failed metric in the experiment record;
- do not promote the direct stable route to `main`.

### Phase 8: Experiment Record and Promotion

Write:

`experiments/2026-05-21-aba-se-st-direct-stable-encoding.md`

The record must include:

- branch;
- page-image semantics check;
- exact source/test commits;
- exact cohort;
- exact commands;
- focused test result;
- five-row metric result;
- 10x10 regression result;
- invalid witness counts;
- generated diagnostics not committed;
- direct decision:
  - `go`: promote direct stable encoding to `main`;
  - `no-go`: abandon the source delta and move to the next encoding
    architecture workstream.

Promotion rule:

- promote source/test/experiment-record commits to `main` only if Phases 4, 6,
  and 7 pass;
- do not promote generated diagnostics.

## Metric Gates

The workstream is complete when:

- page-image semantics check is recorded;
- direct stable encoding contract tests pass;
- old `pi_com + extra stable constraint` stable-witness construction is gone;
- exact five-row cohort was run;
- 10x10 regression gate was run;
- experiment record states go/no-go.

Kept result threshold:

- direct stable encoding must improve solved count above `0/5` on the five-row
  timeout cohort, or produce a smaller deterministic search surface that names
  the next deletion target, with `0` invalid witnesses.

## Stop Conditions

- Stop if branch creation is blocked by tracked dirty files.
- Stop if page images are unavailable.
- Stop if the page-image semantics check contradicts the direct stable rules
  in this workstream.
- Stop if the five-row manifest is not exactly five `SE-ST` rows.
- Stop if a focused test failure is outside owned paths.
- Stop if any benchmark returns a runner error.
- Stop if any solved row has an invalid witness.
