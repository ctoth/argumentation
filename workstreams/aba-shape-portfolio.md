# ABA Shape Portfolio Workstream

## Goal

Build a shape-driven ABA single-extension benchmark and use it to choose solver
portfolio rules from framework structure, not from filenames, generator names,
or ICCMA-specific labels.

The target architecture is:

- ICCMA rows are reproducible benchmark inputs, not solver logic.
- Portfolio decisions are based only on parsed framework shape, task, semantics,
  and cheap preprocessing/closure statistics.
- Any backend routing rule added after this workstream must be explainable from
  shape fields that can be computed for arbitrary ABA frameworks.
- Benchmark output remains diagnostic unless explicitly promoted.
- Solver improvements land in reusable encodings, preprocessing, routing, or
  backend integrations.

## Current Evidence

Relevant committed improvements:

- `52cb484` routes ABA preferred witnesses through multishot clingo.
- `0ac957f` routes ABA stable witnesses through multishot clingo.
- `5b91f33` uses first-model ABA multishot witnesses.
- `37148ed` uses lean ABA facts for multishot clingo.

Measured stale cap-200 ABA timeout replay after lean facts:

- `aba/single-extension/preferred`: 22 solved / 5 timeout.
- `aba/single-extension/stable`: 10 solved / 5 timeout.

Remaining common hard core:

- large flat ABA frameworks with 200 assumptions and about 5k rules in the
  residual replay corpus;
- same residual rows time out for preferred and stable single-extension under
  current `auto`;
- direct stable shortcut experiment did not improve this core and was not
  promoted.

## Non-Negotiable Rules

- Do not parse filenames except to locate and read input files.
- Do not infer generator parameters from filenames.
- Do not route on contest track names, row order, directory names, or benchmark
  labels.
- Do not add ICCMA-only solver behavior.
- Do not add routing rules before benchmark evidence exists for the shape bucket.
- Do not count generated JSON, CSV, logs, profiles, or reports as source
  progress.
- Keep generated benchmark artifacts uncommitted unless explicitly requested.
- Use `uv run ...` for every Python entrypoint and test command.
- A returned witness must pass backend-independent validation before it is used
  as evidence for a routing rule.

## Shape Fields

`tools/aba_shape_benchmark.py` must compute these fields from the parsed ABA
framework only:

- `assumptions`
- `language_literals`
- `rules`
- `contraries`
- `distinct_contrary_literals`
- `avg_rule_arity`
- `max_rule_arity`
- `zero_body_rules`
- `rules_per_head_max`
- `rules_per_head_avg`
- `rules_per_contrary_max`
- `rules_per_contrary_avg`
- `assumption_to_language_ratio`
- `rule_to_assumption_ratio`
- `grounded_fixed_in`
- `grounded_fixed_out`
- `residual_assumptions`
- `residual_rules`
- `preprocessing_collapsed`

Optional later fields, only after the required fields are stable:

- closure density estimate from sampled assumption sets
- dependency SCC count and max SCC size
- contrary-target in-degree distribution
- cheap stable-obstruction count

## Solver Classes

The benchmark must report solver class independently of ICCMA naming:

- `aba/single-extension/preferred`
- `aba/single-extension/stable`
- later: `aba/skeptical-acceptance/preferred`
- later: `aba/credulous-acceptance/*`

ICCMA subtracks may be used only as input metadata that maps into the solver
class.

## Dependency-Sorted Execution Order

1. Phase 1: Shape Extraction Library.
2. Phase 2: Benchmark Job Builder.
3. Phase 3: Backend Runner Matrix.
4. Phase 4: Shape Bucket Summary.
5. Phase 5: Portfolio Proposal Gate.
6. Phase 6: Optional Portfolio Implementation.
7. Phase 7: Acceptance Reruns.

## Phase 1: Shape Extraction Library

Goal: add a reusable ABA shape extractor with no benchmark coupling.

- [ ] Add `tools/aba_shape_benchmark.py`.
- [ ] Add `compute_aba_shape(framework)` or equivalent pure helper.
- [ ] Parse ABA inputs through existing parser code.
- [ ] Compute all required shape fields.
- [ ] Compute grounded reduct fields through existing ABA preprocessing.
- [ ] Add tests for tiny hand frameworks:
  - [ ] zero rules
  - [ ] unary rules
  - [ ] mixed arity rules
  - [ ] repeated heads
  - [ ] repeated contrary literals
  - [ ] non-collapsing grounded reduct
  - [ ] collapsing grounded reduct
- [ ] Run:

```powershell
uv run pytest -q tests\test_aba_shape_benchmark.py
```

Gate: shape extraction tests pass and no field depends on path text.

## Phase 2: Benchmark Job Builder

Goal: create benchmark jobs from explicit paths or timeout manifests.

- [ ] Support explicit `--instance` paths.
- [ ] Support `--timeouts tests\manifests\iccma2025-cap200-timeouts.json`.
- [ ] Support filters:
  - [ ] `--year`
  - [ ] `--subtrack`
  - [ ] `--instance-kind aba`
- [ ] Map task/subtrack metadata into solver class.
- [ ] Preserve original path only as locator metadata.
- [ ] Add tests:
  - [ ] manifest rows become benchmark jobs
  - [ ] duplicate logical rows are de-duplicated or reported deterministically
  - [ ] path strings do not contribute to shape fields
  - [ ] solver class mapping is stable

Gate: job builder tests pass and the JSON job model has no filename-derived
feature fields.

## Phase 3: Backend Runner Matrix

Goal: run the same ABA framework through candidate backends with identical task
and timeout settings.

Default backend candidates:

- `auto`
- `asp`
- `sat`

Later candidates, only after they are source-backed and locally validated:

- direct stable ASP candidate
- external ASPforABA comparison
- experimental branch candidates

Required behavior:

- [ ] Run each `(instance, solver_class, backend)` with a configured timeout.
- [ ] Store command, return status, reason, elapsed seconds, witness size, and
  raw result.
- [ ] Validate witnesses through backend-independent checks when possible.
- [ ] Mark timeout/unknown as timeout/unknown, never as unsat.
- [ ] Continue other backend runs when one backend times out.
- [ ] Add tests:
  - [ ] best solved backend is selected by elapsed time
  - [ ] timeout rows do not become best backend
  - [ ] witness validation failure is distinct from solver timeout
  - [ ] backend command construction uses explicit task and backend

Gate: a smoke matrix can run on two tiny ABA files and produce deterministic
JSON/CSV.

Smoke command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\aba_100_0.1_10_10_9.aba --backend auto --backend asp --backend sat --timeout-seconds 5 --output-json data\iccma\2025\runs\aba-shape-smoke.json --output-csv data\iccma\2025\runs\aba-shape-smoke.csv
```

## Phase 4: Shape Bucket Summary

Goal: summarize outcomes by structural buckets, not benchmark names.

Required buckets:

- assumption size: `small`, `medium`, `large`
- rule density: `sparse`, `medium`, `dense`
- max arity: `low`, `medium`, `high`
- preprocessing: `collapsed`, `not_collapsed`
- solver class

Initial bucket thresholds must be explicit constants in the tool and reported
in the output config. They may be changed only with a measured rationale.

- [ ] Add bucket computation.
- [ ] Add summary by solver class.
- [ ] Add summary by backend.
- [ ] Add summary by shape bucket.
- [ ] Add tests for bucket boundary values.
- [ ] Add tests that summaries are order-invariant.

Gate: the same benchmark rows produce the same summary regardless of input row
order.

## Phase 5: Portfolio Proposal Gate

Goal: convert benchmark evidence into a proposed shape-based rule, not into
production routing yet.

- [ ] Run the stale ABA single-extension timeout corpus:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --year 2025 --subtrack SE-PR --subtrack SE-ST --backend auto --backend asp --backend sat --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-shape-cap200-single-extension.json --output-csv data\iccma\2025\runs\aba-shape-cap200-single-extension.csv
```

- [ ] Produce a diagnostic report under `reports/` only if explicitly requested.
- [ ] Identify shape buckets where one backend dominates.
- [ ] Identify shape buckets where all current backends time out.
- [ ] Identify rows where witness validation fails, if any.
- [ ] Write a short proposal in the benchmark JSON:
  - [ ] candidate rule
  - [ ] shape predicates used
  - [ ] evidence rows
  - [ ] failures / counterexamples
  - [ ] confidence level

Gate: at least one proposed rule is supported by more than one row and no
counterexample in the same shape bucket.

## Phase 6: Optional Portfolio Implementation

Goal: implement only evidence-backed production routing.

This phase is blocked until Phase 5 produces a specific rule.

- [ ] Create an experiment branch before production routing changes.
- [ ] Add routing tests for the exact shape predicate.
- [ ] Add correctness tests for every backend selected by the predicate.
- [ ] Implement the minimal production routing rule.
- [ ] Do not include filenames, paths, row ids, or benchmark labels in routing.
- [ ] Run targeted benchmark rows for the affected shape bucket.

Gate: timeout count decreases for the affected shape bucket and no existing
solver-class tests fail.

## Phase 7: Acceptance Reruns

- [ ] Rerun stale ABA single-extension timeout corpus.
- [ ] Rerun the whole cap-200 timeout manifest.
- [ ] Run a fresh cap-200 benchmark only after the timeout manifest improves.
- [ ] Record final numbers in this workstream.

Commands:

```powershell
uv run tools\iccma_post_router_workstream.py --label post-shape-portfolio-aba --skip-cap-run
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --timeout-seconds 30 --backend auto --data-root data\iccma --output data\iccma\2025\runs\post-shape-portfolio-cap200-timeouts.json
uv run tools\iccma2025_run_native.py --max-af-arguments 200 --max-aba-assumptions 200 --timeout-seconds 25 --label post-shape-portfolio-cap200 --no-progress
```

Gate: fresh timeout counts improve without reducing solved counts.

## Final Verification

- [ ] every checklist item is completed or explicitly deferred with rationale
- [ ] no production route uses filename, generator, path, or contest label
- [ ] benchmark JSON records bucket thresholds and backend candidates
- [ ] `uv run pytest -q tests\test_aba_shape_benchmark.py` passes
- [ ] any production routing change has targeted solver tests
- [ ] final timeout-manifest rerun result is recorded
- [ ] source files touched by the workstream are clean
