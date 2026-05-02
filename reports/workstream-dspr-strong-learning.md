# Workstream: Strong Learning for AF DS-PR

Author: Codex
Date: 2026-05-02
Status: proposed implementation workstream; no solver code changed in this document

## Scope

This workstream is the focused rescue path for Phase 1 of
`reports/workstream-zero-timeouts-dspr-aba.md`.

It targets the remaining abstract-argumentation skeptical-preferred (`DS-PR`)
timeouts from ICCMA 2017 and 2019. ABA work remains blocked until this AF gate
is solved or explicitly deferred.

The target is direct: replace the weak attacker/witness exclusion loop with a
paper-backed CDAS/PSC learning kernel, update every caller, and delete the old
timeout-causing helper surface. Do not keep a parallel old/new DS-PR production
path.

## Current Evidence

The latest kept improvement is commit `206696a`, which caches the
preferred-skeptical attacker solver and extends SAT trace telemetry with
`loop_index`, `learned_count`, and model fingerprints.

Measured on `A\3\massachusetts_srta_2014-11-13.gml.50.apx`:

- Before cached attacker search: 46 attacker/extension loop iterations in a
  5-second run.
- After cached attacker search: 900 attacker/extension loop iterations in a
  5-second run.
- After cached attacker search: 3,122 attacker searches and 3,121 extension
  checks in a 20-second run, still timeout.
- The 20-second cached trace had 3,122 unique attacker fingerprints and 3,121
  unique witness fingerprints.

Conclusion: rebuilding solver state was a real bottleneck and is fixed. The
remaining bottleneck is not exact duplicate rediscovery. It is weak learning:
the solver enumerates too many distinct admissible attacker/witness patterns.

The attempted witness-growth slice was rejected:

- It reduced outer attacker loops but spent the budget on witness-growth SAT
  checks.
- It still timed out at both 20 seconds and 60 seconds on the hard selected row.
- It was reverted and not committed.

## Paper Basis

- Thimm, Cerutti, Vallati 2021, "Skeptical Reasoning with Preferred Semantics
  in Abstract Argumentation without Computing Preferred Extensions": gives the
  CDAS shape, including admissibility checks over query-containing candidates,
  admissible attackers, and preferred-super-core (`PSC`) reasoning.
- Thimm, Cerutti, Vallati 2021, "Fudge": supports incremental SAT utilities
  and admissibility-based procedures for skeptical preferred reasoning instead
  of preferred-extension enumeration.
- Dvorak, Jarvisalo, Wallner, Woltran 2014, "Complexity-Sensitive Decision
  Procedures for Abstract Argumentation": supports CEGAR-style loops,
  fragment-sensitive shortcuts, and learned exclusions as first-class solver
  state.
- Cerutti, Vallati, Giacomin 2015, "ArgSemSAT-1.0": supports complete
  labellings as the shared SAT surface for stable, grounded, complete,
  preferred, and related semantics.

I did not reread PDF page images while writing this document. This plan uses
the local paper-reader notes and the traces produced in the current repo.

## Target Architecture

Implement a single `PreferredSkepticalTaskSolver` as the production path for
AF `DS-PR`.

The solver owns these persistent utilities:

- `AdmExt(q)`: one incremental admissibility kernel for query-containing
  extension checks.
- `AdmExtAtt(q, learned)`: one incremental attacker/candidate kernel for
  admissible attackers against query-containing candidates.
- `PSC(AF)`: a reusable preferred-super-core computation used by `DS-PR` and
  later by ideal reasoning.
- `LearningStore`: solver-owned SAT clauses and traceable events for every
  learned exclusion, not Python-only lists rebuilt into fresh solvers.

The old helper-shaped DS-PR surface must disappear from production:

- Delete `_admissible_attacker_against_compatible_candidate`.
- Delete ad hoc Python `covered` lists as the learning mechanism.
- Delete any production path that decides `DS-PR` by growing preferred
  extensions.

## Phase 0: Trace Classifier and Regression Corpus

Tests first:

- Add a trace classifier for selected-row JSONL traces.
- Assert the hard transport row is classified as `unique-attacker-churn` under
  the current cached baseline.
- Assert the smaller BA row is classified as `quick-counterexample`.
- Assert trace classification uses `utility_name`, `loop_index`,
  `learned_count`, `model_extension_fingerprint`, and result status.

Implementation:

- Add `tools/iccma_trace_classify.py`.
- Emit deterministic summaries:
  - event counts by utility.
  - unique fingerprint counts by utility.
  - maximum learned count.
  - last loop index.
  - terminal status if paired stdout result is supplied.
- Add tests using small checked-in synthetic JSONL fixtures; do not check in
  huge raw traces.

Done when the classifier proves the current hard-row failure mode without
rerunning ICCMA.

## Phase 1: Paper-Shaped CDAS Contract Tests

Tests first:

- Exhaustively differential-test `DS-PR` against native preferred enumeration
  on generated small AFs.
- Add paper-shaped cases:
  - no admissible set containing `q` implies skeptical preferred false.
  - no admissible attacker pattern implies true.
  - an admissible attacker that cannot be extended with `q` implies false.
  - a query in the preferred super-core is accepted without attacker churn.
  - a query outside the preferred super-core is rejected or routed to CDAS with
    a traceable reason.
- Add trace-contract tests for the hard-row selected runner:
  - no fresh attacker solver rebuild per loop.
  - learned clauses increase monotonically.
  - every loop has either a learned exclusion or a terminal result.

Implementation:

- Introduce `PreferredSkepticalTaskSolver`.
- Move the cached attacker solver behind that class.
- Keep public `is_preferred_skeptically_accepted(...)` as a thin call into the
  task solver.
- Preserve streamed `SATCheck` telemetry for every SAT check.

Done when small AF semantics and DS-PR trace contracts pass.

## Phase 2: Preferred Super-Core Kernel

Tests first:

- Differential-test `PSC(AF)` against preferred-extension enumeration on small
  generated AFs.
- Assert `PSC(AF)` is a subset of every preferred extension.
- Assert arguments outside `PSC(AF)` are not immediately accepted for `DS-PR`.
- Assert `PSC(AF)` emits bounded trace events on selected timeout rows.

Implementation:

- Implement `PreferredSuperCoreSolver`.
- Use admissible-attack removal as described by the Thimm/Cerutti/Vallati
  notes:
  - start from all arguments.
  - iteratively remove arguments attacked by admissible sets.
  - remove internally undefended arguments until a fixed point.
- Share the same admissibility kernel shape with ideal reasoning, but do not
  rewrite ideal until the DS-PR gate is passing.

Done when `PSC(AF)` is correct on generated AFs and acts as a zero-churn fast
path for any selected row/query it can decide.

## Phase 3: Strong Learned Exclusions

Tests first:

- Create a reduced AF fixture that reproduces high unique-attacker churn.
- Assert the new learning store blocks a region, not just one exact attacker
  fingerprint.
- Assert learned clauses are permanent in the attacker kernel.
- Assert selected-row traces contain `preferred_skeptical_learn_*` events.

Implementation:

- Replace subset-of-witness blocking with named learned exclusion families:
  - `learn_witness_region`: block attackers already covered by a
    query-compatible admissible witness.
  - `learn_candidate_region`: block candidate/attacker combinations that
    repeat the same CDAS-relevant attack relation.
  - `learn_psc_region`: block attackers irrelevant to arguments already fixed
    by `PSC(AF)`.
- Emit a non-SAT trace event or SATCheck-compatible metadata for every learned
  exclusion family.
- Keep learned clauses in the persistent attacker solver.

Done when the hard transport row shows a material reduction in outer loop count
or solves under the selected runner. A material reduction means at least a 3x
drop in attacker-search loops at the same timeout cap with no solved-row
regression.

## Phase 4: Fragment-Sensitive Shortcuts

Tests first:

- Detect acyclic AFs, self-attack-only dead zones, SCC-local query components,
  and unattacked query arguments.
- Differential-test each shortcut against native preferred enumeration on small
  generated AFs.
- Assert shortcuts emit traceable `preferred_skeptical_shortcut_*` utilities.

Implementation:

- Add query-local preprocessing before CDAS:
  - remove self-attacking arguments that cannot appear in admissible sets.
  - restrict to SCCs that can affect the query where semantics allow.
  - decide grounded-in/preferred-in trivial positives.
  - decide undefended/self-attacking query trivial negatives.
- Do not approximate. Every shortcut must have a proof-backed test.

Done when at least one ICCMA DS-PR timeout row is solved by a shortcut or the
trace classifier proves no selected timeout row matches the implemented
fragments.

## Phase 5: AF Timeout Gate

Execution:

1. Run targeted solver tests:
   `uv run pytest tests\test_solver_encoding.py -q`
2. Run timeout corpus/runner tests:
   `uv run pytest tests\test_iccma_timeout_corpus.py tests\test_iccma_run_selected.py -q`
3. Run selected 2017/2019 DS-PR timeout rows from
   `data/iccma/timeouts/range-max-inclusion-cap100-timeouts.json`.
4. Run full cap-100 2017 and 2019.

Success criteria:

- At least one current 2017 DS-PR timeout row solves before this workstream can
  be called partially successful.
- Full success is:
  - 2017 DS-PR timeouts: `16 -> 0`.
  - 2019 DS-PR timeouts: `7 -> 0`.
- No regression in the smaller selected BA row.
- Trace summaries show bounded CDAS growth or a named residual blocker for
  every remaining timeout row.

If this gate fails, stop and classify the remaining rows by trace family. Do
not move to ABA.

## Stop Conditions

Stop immediately and report if:

- Two consecutive DS-PR learning slices produce no kept selected-row
  improvement.
- A slice passes small tests but worsens the smaller BA selected row.
- A slice only changes trace shape without solving a row or producing a kept
  measured reduction.
- The paper notes are insufficient to justify a learning rule. In that case,
  reread the relevant PDF page images before implementing the rule.

## Expected Outcome

Cached attacker search removed the obvious per-iteration waste. This workstream
attacks the remaining search-width problem by moving from per-witness blocking
to paper-backed CDAS/PSC learning regions.

The realistic near-term win is not "all DS-PR rows solved" in one slice. The
first hard gate is one current 2017 timeout row solved under the selected-row
runner. Once that is achieved, the same trace classifier should guide the full
2017/2019 timeout cleanup.
