# Post-Cap150 Solver Frontier Workstreams

## Goal

Drive the ICCMA 2025 cap-150 frontier from the current measured state toward a
smaller, better-understood timeout set without mixing unrelated algorithmic
experiments.

Current measured baseline:

- command:
  `uv run tools\iccma2025_run_native.py --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 --label post-aba-stable-cap150`
- result: 7394 rows, 829 solved, 16 timeout, 6549 skipped
- remaining timeout groups:
  - ABA `SE-PR`: 11
  - ABA `SE-ST`: 1
  - AF `DC-ID`: 2
  - AF `SE-ID`: 2

This workstream starts from repo-local notes, prior benchmark artifacts, and the
algorithms already implemented in the package. I did not reread paper page
images while writing this plan. Before implementing paper-sensitive clauses,
reread the relevant primary paper pages or official solver sources and record
the source range in the red/green commit message.

## Control Rules

- Work on exactly one target family at a time: ABA preferred, ABA stable,
  external ABA comparison, AF ideal, or cap expansion.
- Every implementation slice ends with a measured improvement on a checked-in
  manifest, or a full revert of that slice.
- Do not use full cap expansion as evidence for a solver change until the
  current cap-150 timeout manifest is stable and measured.
- Keep native exact semantics as the oracle only for small generated instances.
- Keep ICCMA rows as performance/conformance smoke evidence, not as the only
  correctness argument.
- Add or update Hypothesis properties before changing production encodings when
  the behavior can be stated independently of a specific benchmark row.
- Commit source slices atomically and with explicit paths only.

## Ordered Workstreams

The dependency order is:

1. Hard-row manifest and benchmark harness.
2. ABA preferred exact CEGAR solver.
3. ABA external ASP comparison.
4. ABA grounded/reduct preprocessing.
5. Stubborn ABA stable row analysis.
6. AF ideal direct formulation.
7. Cap-200 expansion.

Do not execute a later workstream as a substitute for an unfinished earlier
gate unless the later workstream has no dependency on that evidence.

## Workstream 1: Hard-Row Manifest And Metrics

### Purpose

Freeze the current timeout frontier so solver experiments optimize against a
stable target instead of whichever generated CSV happened to be latest.

### Source Inputs

- `data/iccma/timeouts/post-aba-stable-cap150-timeouts.json`
- `data/iccma/2025/runs/iccma-2025-post-aba-stable-cap150.csv`
- `tools/iccma_run_timeout_rows.py`
- `tools/iccma_timeout_corpus.py`

### Deliverables

- A checked-in manifest, for example
  `tests/manifests/iccma2025-cap150-timeouts.json`, containing:
  - year, track, subtrack, instance path, instance kind
  - argument or assumption count
  - rules/contraries or attacks where available
  - SHA-256 of the input file contents
  - baseline status and elapsed seconds
- A reusable runner for exactly the manifest rows.
- A summary report that groups result deltas by subtrack and instance family.

### Gates

- Gate 1.1: manifest order and dependency check passes.
- Gate 1.2: every manifest row resolves to an existing input file.
- Gate 1.3: every manifest hash matches the current local data cache.
- Gate 1.4: a no-code-change rerun reproduces the same timeout group shape,
  allowing ordinary wall-clock variance but not missing rows or malformed rows.

### Hypothesis Properties

- `manifest_entries_resolve_to_unique_rows`: generated manifests with duplicate
  logical row keys are rejected.
- `manifest_hashes_are_content_sensitive`: changing any generated file payload
  changes the computed hash.
- `timeout_summary_is_order_invariant`: shuffling generated row lists preserves
  grouped timeout counts.
- `selected_timeout_rows_filters_exactly`: generated row lists filtered by year
  and subtrack match a simple set-comprehension oracle.

## Workstream 2: ABA Preferred Exact CEGAR Solver

### Purpose

Replace the current ABA preferred single-extension path's dependence on
materialized minimal supports for hard `SE-PR` rows.

### Algorithm Sketch

Use ranked Horn closure for derivability, then enforce admissibility with a
counterexample loop:

- Candidate variables `in[a]` select assumptions.
- Ranked closure variables derive literals from selected assumptions.
- Conflict freedom is encoded as `in[a] -> not derived(contrary(a))`.
- Defense is checked by a separate attacker-support query:
  - find assumptions `x[b]` deriving `contrary(a)` for a selected `a`;
  - require that the candidate does not derive the contrary of any selected
    attacker assumption in `x`;
  - if found, learn that future candidates must counterattack at least one
    assumption in that attacker support.
- Grow admissible candidates to a maximal admissible set using the existing
  preferred growth invariant.

Stable remains a shortcut: if a stable extension satisfying the current
requirements exists, return it because stable implies preferred.

### Deliverables

- A private CEGAR kernel in `argumentation.aba_sat`.
- A public routing change only after the private kernel passes all properties.
- Telemetry fields for CEGAR iterations and learned defense clauses.
- Bench comparison against the current timeout manifest.

### Gates

- Gate 2.1: ranked closure equivalence property passes against deterministic
  ABA closure for small generated frameworks.
- Gate 2.2: every returned preferred witness is admissible.
- Gate 2.3: every returned preferred witness is maximal admissible on small
  generated frameworks.
- Gate 2.4: for generated frameworks where native preferred enumeration is
  feasible, the CEGAR witness is a member of the native preferred set.
- Gate 2.5: manifest run strictly reduces `SE-PR` timeouts or the slice is
  reverted.
- Gate 2.6: no existing fast ABA rows regress by more than 2x median elapsed
  time on a checked-in fast-row sample.

### Hypothesis Properties

- `ranked_closure_matches_native_closure`: for flat ABA frameworks up to a
  bounded assumption/rule count, every selected assumption set produces the
  same derived literals as the deterministic closure function.
- `cegar_rejects_undefended_candidate`: generated attacker/candidate pairs
  where an attacker derives a contrary and is not counterattacked are rejected.
- `cegar_learned_clause_blocks_same_counterexample`: after learning from a
  defense counterexample, the same candidate/counterexample pair is unsat.
- `preferred_witness_is_native_preferred`: for generated small frameworks, a
  returned CEGAR preferred witness is in `aba.preferred_extensions`.
- `preferred_none_matches_native_empty`: if the CEGAR solver returns no
  preferred extension on a generated small framework, native preferred
  enumeration is empty.
- `stable_shortcut_returns_preferred_member`: when a stable shortcut returns a
  witness, native preferred enumeration contains that witness.
- `required_assumptions_are_preserved`: generated `require_assumptions` subsets
  are included in every returned witness or the solver returns no witness.
- `query_constraints_match_derivability`: generated `require_derived` and
  `require_not_derived` constraints agree with deterministic derivability.

## Workstream 3: ABA External ASP Comparison

### Purpose

Determine whether the remaining ABA rows are primarily package-Z3 encoding
misses or algorithmic misses by comparing against a source-backed ASP solver
path.

### Candidate Sources

- Existing `scratch/sources/aspforaba/aspforaba`
- Existing `argumentation.solver_adapters.clingo`
- Existing `argumentation.aba_asp`
- Existing ICCMA ABA parser/writer and subprocess adapter

Before production routing, verify the ASPforABA command-line contract against
its local source and README. Do not infer unsupported semantics.

### Deliverables

- A benchmark-only adapter or tool path for ASPforABA/clingo.
- A comparison report on the checked-in timeout manifest.
- Optional production adapter only after correctness and availability behavior
  are pinned.

### Gates

- Gate 3.1: missing binary returns typed unavailable, not an exception.
- Gate 3.2: nonzero exit, timeout, and malformed output are distinguishable.
- Gate 3.3: small generated ABA outputs match native oracles for supported
  tasks.
- Gate 3.4: external solver witness certificates pass local verification.
- Gate 3.5: manifest comparison identifies which remaining timeouts are solved
  by external ASP and records elapsed time.

### Hypothesis Properties

- `external_witness_is_closed_conflict_free_and_task_valid`: generated
  externally shaped witnesses are accepted only when they satisfy the requested
  ABA task.
- `malformed_output_never_success`: generated non-ICCMA output strings do not
  produce success results.
- `roundtrip_aba_preserves_framework`: generated flat ABA frameworks round-trip
  through ICCMA ABA I/O without changing assumptions, rules, or contraries.
- `adapter_supported_tasks_match_table`: generated task/semantics pairs route
  only when declared supported.

## Workstream 4: ABA Grounded/Rebuttal Reduct Preprocessing

### Purpose

Shrink hard ABA preferred instances before maximal-admissible search.

### Algorithm Sketch

- Compute grounded ABA assumptions using a deterministic fixpoint.
- Force grounded assumptions into preferred candidates.
- Remove assumptions defeated by the grounded closure where doing so is
  semantically justified.
- Run preferred solving on the reduct and lift the witness back.

The exact reduct rule must be checked against ABA primary definitions before
implementation. If the source does not justify the deletion rule, only force
grounded assumptions and skip deletion.

### Deliverables

- A preprocessing function that returns forced assumptions and a reduced
  framework.
- Differential tests against native preferred enumeration on small frameworks.
- Manifest run comparing preferred CEGAR with and without preprocessing.

### Gates

- Gate 4.1: grounded assumptions are included in every native preferred
  extension for generated small flat ABA frameworks.
- Gate 4.2: lifted reduct witnesses are preferred extensions of the original
  framework.
- Gate 4.3: preprocessing never changes the answer on generated small
  acceptance tasks.
- Gate 4.4: manifest run strictly reduces elapsed time or timeout count when
  composed with Workstream 2, or remains optional/default-off.

### Hypothesis Properties

- `grounded_subset_of_every_preferred`: generated small frameworks satisfy
  `grounded <= preferred` for every native preferred extension.
- `forced_grounded_witness_matches_native`: any returned witness containing the
  forced grounded set is a native preferred member.
- `reduct_lift_preserves_derivability_for_query`: generated query literals have
  the same derivability result before and after reduct/lift when the reduct is
  declared applicable.
- `preprocess_idempotent`: applying preprocessing twice yields the same forced
  set and reduced framework.

## Workstream 5: Stubborn ABA Stable Row

### Purpose

Understand and attack the single remaining ABA `SE-ST` timeout:
`ABAs/aba_500_0.1_10_5_7.aba`.

### Candidate Approaches

- Profile ranked closure encoding size and Z3 check time.
- Try Boolean-rank ladder or bounded bit-vector ranks instead of integer ranks.
- Try SCC decomposition over rule dependency graph before stable solving.
- Try failed-literal/unit propagation for assumptions whose contraries are
  facts or unavoidable.

### Gates

- Gate 5.1: a diagnostic script records variable counts, constraint counts,
  rule-dependency SCCs, and SAT check time for the stubborn row.
- Gate 5.2: any encoding change preserves all existing stable differential
  properties.
- Gate 5.3: the stubborn row solves under the same 15-second targeted timeout
  or the slice is reverted.
- Gate 5.4: no solved ABA stable manifest row regresses into timeout.

### Hypothesis Properties

- `stable_rank_encoding_matches_native`: generated small frameworks produce a
  stable witness iff native stable enumeration is nonempty.
- `rank_variant_equivalent`: integer-rank and any proposed rank-ladder/bit-vector
  encoding agree on generated small frameworks.
- `scc_decomposition_preserves_stable`: decomposed solving returns a witness
  that native stable enumeration accepts.
- `forced_literal_simplification_preserves_stability`: generated simplification
  rules preserve stable existence and witness validity.

## Workstream 6: AF Ideal Direct Solver

### Purpose

Replace the current AF ideal loop for dense cycle instances where repeated
admissible-attacker removal times out.

### Candidate Approaches

- Direct ideal membership test using preferred-skeptical machinery.
- CEGAR over admissible subsets constrained below every preferred extension.
- Compute candidate ideal set from skeptical preferred core, then maximize
  admissible subset of that core.
- Reuse existing preferred skeptical solver only when it reduces total SAT
  checks on the manifest.

### Deliverables

- A private ideal solver variant behind an internal switch.
- A diagnostic trace comparing old ideal loop checks with new checks.
- Routing change only after manifest improvement.

### Gates

- Gate 6.1: generated small AF ideal witnesses match `dung.ideal_extension`.
- Gate 6.2: returned ideal witness is admissible.
- Gate 6.3: returned ideal witness is contained in every native preferred
  extension on generated small frameworks.
- Gate 6.4: no admissible strict superset of the returned witness is contained
  in every native preferred extension on generated small frameworks.
- Gate 6.5: both `afinput_exp_cycles_depvary_step6_batch_yyy02.af` ideal rows
  solve under the targeted timeout, or the slice is reverted.

### Hypothesis Properties

- `ideal_matches_native`: generated AFs up to bounded size return exactly
  `dung.ideal_extension`.
- `ideal_is_admissible`: every returned ideal extension is admissible.
- `ideal_below_all_preferred`: every returned ideal extension is a subset of
  every preferred extension.
- `ideal_maximal_under_preferred_core`: no generated admissible strict superset
  stays below all preferred extensions.
- `ideal_acceptance_matches_extension_membership`: `DC-ID` and `DS-ID`
  acceptance answers match membership/nonmembership in the unique ideal
  extension.

## Workstream 7: Cap-200 Expansion

### Purpose

Only after the cap-150 timeout frontier is reduced or explicitly classified,
expand the measurement surface.

### Gates

- Gate 7.1: cap-150 manifest has no unknown timeout class, only known-deferred
  classes with written rationale.
- Gate 7.2: full cap-150 run is reproducible under the current default backend.
- Gate 7.3: cap-200 run uses a new label and does not overwrite cap-150
  artifacts.
- Gate 7.4: new timeout manifest is generated and checked for dependency order
  before implementation starts.

### Hypothesis Properties

- `cap_manifest_monotonicity`: generated cap-N and cap-M manifests with N <= M
  preserve inclusion of eligible rows.
- `cap_filter_respects_af_and_aba_limits`: generated manifest rows obey the
  independent AF argument and ABA assumption limits.
- `summary_delta_accounts_for_all_rows`: generated old/new summaries produce
  deltas whose totals equal the row-count difference.

## Global Verification Commands

Focused commands:

```powershell
uv run pytest -q tests\test_aba.py
uv run pytest -q tests\test_solver_encoding.py tests\test_dung_ideal_admissibility.py
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --timeout-seconds 15 --backend auto --output data\iccma\timeouts\candidate-rerun.json
```

Full gates:

```powershell
uv run pytest -q
uv run tools\iccma2025_run_native.py --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 --label candidate-cap150
uv run tools\iccma_timeout_corpus.py --csv data\iccma\2025\runs\iccma-2025-candidate-cap150.csv --output-dir data\iccma\timeouts --label candidate-cap150
```

## Stop Conditions

- Stop and revert if two consecutive slices on the same target produce no kept
  timeout reduction or validated correctness improvement.
- Stop if a solver change only improves generated diagnostics and does not
  improve source behavior or manifest results.
- Stop before paper-sensitive implementation if the relevant primary pages or
  source files have not been reread.
- Stop before dependency pinning if the dependency reference is local-only or
  not available from a shared remote.
