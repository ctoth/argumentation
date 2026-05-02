# Workstream: Toward Zero ICCMA Cap-100 Timeouts

Author: Codex
Date: 2026-05-02
Status: proposed implementation workstream; no solver code changed in this document

## Evidence Level

This plan is based on local `paper-reader` notes in `papers/`, existing local
reports, and the cap-100 ICCMA runs completed on 2026-05-02. I did not reread
PDF page images in this turn.

The range-maximal SAT workstream did not materially change solved counts:
2017, 2019, and 2025 were unchanged, while 2023 improved by one solved row.
The timeout rows explain why: the remaining AF timeouts are concentrated in
skeptical preferred reasoning (`DS-PR`), and the 2023/2025 timeout mass is
mostly ABA. Stage and semi-stable are no longer the main cap-100 blocker.

Current cap-100 timeout profile:

| Year | Timeout count | Dominant timeout family |
| --- | ---: | --- |
| 2017 | 16 | AF `DS-PR` |
| 2019 | 7 | AF `DS-PR` |
| 2023 | 83 | ABA `SE-PR`, `SE-ST`, plus larger ABA clusters |
| 2025 | 54 | ABA `DC-*`, `DS-*`, `SE-*` on selected ABA files |

## Paper Basis

- Thimm, Cerutti, Vallati 2021, "Skeptical Reasoning with Preferred Semantics
  in Abstract Argumentation without Computing Preferred Extensions": defines
  `AC(AF)`, `PSC(AF)`, and the `CDAS` algorithm for `DS-PR`; the key point is
  to avoid preferred-extension construction and instead use admissible-set SAT
  utilities.
- Thimm, Cerutti, Vallati 2021, "Fudge": gives the implementation rationale:
  use incremental SAT, standard reductions for easy tasks, and novel
  admissibility-based encodings for `DS-PR` and ideal.
- Dvorak, Jarvisalo, Wallner, Woltran 2014, "Complexity-Sensitive Decision
  Procedures for Abstract Argumentation": supports CEGAR-style SAT oracle
  loops, learned exclusions, and fragment/shortcut checks rather than one
  monolithic second-level encoding.
- Cerutti, Vallati, Giacomin 2015, "ArgSemSAT-1.0": supports complete
  labellings as the shared SAT surface for complete, preferred, grounded, and
  stable reasoning.
- Toni 2014, "A tutorial on assumption-based argumentation": supports
  assumption-level semantics, flat ABA computation, and goal-directed dispute
  derivations rather than generating full Dung AFs unnecessarily.
- Lehtonen, Wallner, Jarvisalo 2019/2020/2024 as summarized in local ASP
  backend notes: supports assumption/defeasible-rule search spaces and ASP
  encodings for ABA/ASPIC-style systems, avoiding explicit argument
  enumeration.

## Target Architecture

Make cap-100 timeouts boring by replacing the two current timeout surfaces
directly:

1. AF `DS-PR` uses a direct CDAS-style skeptical-preferred solver by default.
2. ABA ICCMA tasks use an assumption-level backend by default, not a path that
   expands or enumerates more structure than the task needs.
3. The runner keeps streaming per-call telemetry for every row, including AF SAT
   utilities and ABA backend utility events.
4. The old timeout-causing production paths are deleted or routed only through
   the new kernels. Passing tests while both paths coexist is not completion.

Do not raise the cap as part of this workstream. A higher cap should come after
cap-100 has no unexplained timeouts.

## Phase 0: Timeout Corpus and Repro Harness

Tests first:

- Add a checked-in timeout fixture manifest generated from the latest cap-100
  result CSVs:
  - 2017 `DS-PR`: all 16 rows.
  - 2019 `DS-PR`: all 7 rows.
  - 2023 ABA timeout clusters.
  - 2025 ABA timeout clusters.
- Add selected-row runner tests that can execute one AF timeout row and one ABA
  timeout row with a low timeout and capture streamed utility events.
- Add a summary tool that groups timeout rows by year, track, subtrack,
  instance, argument/assumption count, rule count, and query.

Implementation:

- Add `tools/iccma_timeout_corpus.py`.
- Emit deterministic JSON fixtures under `data/iccma/timeouts/`.
- Refuse to call the workstream successful unless every timeout fixture has
  either solved or been explicitly classified as out-of-scope by a later user
  decision.

Done when the timeout corpus is reproducible from CSV outputs and targeted
tests fail if any selected timeout row silently skips instrumentation.

## Phase 1: Direct AF `DS-PR` CDAS Kernel

Tests first:

- Differential-test `DS-PR` against native preferred enumeration on exhaustive
  small AFs.
- Add paper-shaped examples from Thimm/Cerutti/Vallati: no admissible set
  containing the query means skeptical preferred is false; no admissible
  attacker pattern means true; an attacker that cannot be extended together
  with the query means false.
- Add structural trace assertions on current 2017/2019 timeout rows:
  `preferred_skeptical_adm_ext_att` must not repeat unboundedly without a
  learned exclusion.

Implementation:

- Replace the current preferred-skeptical loop with a `PreferredSkepticalTaskSolver`.
- Keep one incremental `AfSatKernel` for admissibility constraints.
- Implement the CDAS utility surface:
  - `AdmExt(required_in)` for admissible extensions containing the query.
  - `AdmExtAtt(candidate_with_query, excluded_patterns)` for admissible
    attackers of a query-containing admissible candidate.
  - `AdmExt(attacker union query)` for the paper's rejection test.
- Store learned admissible counter-patterns as explicit blocking clauses, not
  as Python-only memory that forces identical SAT rediscovery.
- Stream one `SATCheck` per oracle call with utility names matching the CDAS
  surface.

Done when all existing generated `DS-PR` tests pass and at least one current
2017 timeout row solves under the selected-row runner.

## Phase 2: Preferred Super-Core and Ideal Sharing

Tests first:

- Differential-test ideal extension and `DS-PR` on generated small AFs after
  the CDAS rewrite.
- Assert `SE-ID` does not call preferred-extension enumeration.
- Assert `DS-PR` and ideal share the admissible utility layer without leaking
  row/query state.

Implementation:

- Implement the Thimm/Cerutti/Vallati `PSC(AF)` computation as a reusable
  preferred-super-core helper.
- Rebuild ideal on the CDIS route: iteratively remove arguments attacked by
  admissible sets, then remove internally undefended arguments.
- Reuse the same admissibility SAT kernel and learned attack queries where
  possible.

Done when ideal remains green and no production `SE-ID` or `DS-PR` path grows
preferred extensions unless explicitly requested by a test-only oracle.

## Phase 3: AF Timeout Gate

Execution:

1. Run targeted AF solver tests.
2. Run selected 2017/2019 `DS-PR` timeout rows.
3. Run full cap-100 2017 and 2019.

Success criteria:

- 2017 `DS-PR` timeouts: `16 -> 0`.
- 2019 `DS-PR` timeouts: `7 -> 0`.
- No regression in solved counts for 2023/2025.
- Trace counts show bounded CDAS utility growth, not repeated attacker churn.

If the AF gate fails, stop and classify the remaining AF rows by utility trace
before touching ABA.

## Phase 4: ABA Assumption-Level Backend

Tests first:

- Differential-test flat ABA assumption-level admissible, complete, preferred,
  stable, grounded, ideal, skeptical preferred on small generated ABA
  frameworks against the existing brute-force/reference path.
- Add one 2023 ABA timeout row and one 2025 ABA timeout row as selected
  regression fixtures.
- Assert ABA rows stream per-utility events just like AF SAT rows.

Implementation:

- Add an `AbaTaskSolver` that works over assumptions as the primary variables.
- Precompute minimal support or derivability information once per ABA row.
- Implement task-specific assumption-level checks:
  - stable: selected assumptions do not attack themselves and attack every
    outside assumption where required by the semantics.
  - preferred: admissible plus subset-maximality through an incremental
    strict-superset query.
  - skeptical preferred: CDAS-shaped assumption-level analogue where possible.
  - complete/grounded: assumption-level closure/defense checks without
    full argument enumeration.
- Keep ASP/Clingo as an optional second implementation path only if the existing
  subprocess adapter can consume a complete encoding file; otherwise do not
  add a dependency or half-wire a backend.

Done when the selected 2023/2025 ABA timeout rows solve or expose a smaller,
named missing primitive.

## Phase 5: ABA Timeout Gate

Execution:

1. Run targeted ABA tests.
2. Run selected 2023/2025 ABA timeout rows.
3. Run cap-100 2023 and 2025.

Success criteria:

- 2023 timeouts fall materially below 83.
- 2025 timeouts fall materially below 54.
- No AF solved-count regression.
- Every remaining ABA timeout is grouped by missing primitive, not merely by
  row name.

## Phase 6: Zero-Timeout Gate and Raise-Cap Decision

Execution:

1. Run cap-100 for 2017, 2019, 2023, and 2025.
2. Compare against `range-max-inclusion-cap100`.
3. If all cap-100 rows under supported tracks solve, run cap-150 or cap-200.

Success criteria:

- Cap-100 has zero timeouts for supported tracks.
- Skips are only cap/filter skips, missing-data skips, or explicitly unsupported
  competition tasks.
- The runner result summaries and utility logs are committed or documented.

## Non-Goals

- Do not solve cap-500 before cap-100 is clean.
- Do not add a local-path dependency pin.
- Do not introduce a second solver stack unless it is complete enough to run a
  timeout fixture end to end.
- Do not replace paper-backed exact procedures with approximate shortcuts.
- Do not claim a paper reread unless page images were actually reread.

## Expected Result

The AF `DS-PR` slice should remove the 2017 and 2019 cap-100 timeout rows if
the Thimm/Cerutti/Vallati CDAS characterization maps cleanly onto the current
Z3 kernel. The ABA slice is larger and riskier, but the timeout rows are
clustered enough that an assumption-level backend should produce visible gains
before any cap increase.

