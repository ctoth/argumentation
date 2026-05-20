# ABA abcgen Structural Telemetry Workstream

Status: completed on `exp/aba-abcgen-structural-telemetry`.

Workflow actually requested: design the next concrete workstream after the
ICCMA 2025 run showed the remaining ABA hard class is dominated by the
structural family historically labelled `abcgen`, with a secondary AF
timeout-boundary signal. The broad run was intentionally stopped after enough
evidence was collected; this workstream must use the existing event log and
targeted reruns, not another full all-2025 sweep.

## Final State

- The repo has a committed, deterministic hard-ABA 10 timeout / 10 solved
  fixture under `tests/manifests/iccma2025-abcgen-10x10.json`.
- The 20-row fixture is selected from the ICCMA 2025 manifest and event log by
  instance kind, subtrack, row status, and measured structural telemetry.
  The fixture filename may retain `abcgen` as a historical benchmark label, but
  the selection script and all production code must choose rows by structure,
  not by `abcgen`, filenames, parent directories, or ICCMA year.
- ABA structural telemetry is available as a reusable source API and CLI for any
  ABA instance, not only ICCMA:
  - atoms, assumptions, rules, contraries;
  - flatness;
  - rule body width histogram and max body width;
  - rule head fan-in and body-literal fan-out summaries;
  - contrary fan-in/fan-out summaries;
  - assumption-to-atom and rule-to-assumption ratios;
  - directed rule-dependency SCC count and max SCC size;
  - assumption dependency SCC count and max SCC size;
  - closure-growth probes from calibrated assumption samples;
  - native CNF telemetry when a selected row is solved by native CNF.
- The telemetry API is invariant under path, filename, ICCMA year, and input
  ordering where the ABA semantics are unchanged.
- The runner timeout contract is fixed: a row launched with
  `--timeout-seconds 30` cannot complete as solved after 30 seconds of worker
  wall time, and timeout reasons report the configured cap rather than a
  hidden 40 second boundary.
- Py-spy profiles are produced only after telemetry selects representative
  rows. Profiles are diagnostic artifacts and are not committed.
- Completion produces the structural discriminator and measured hot path needed
  for the next solver-optimization workstream. It does not add a new optimizer
  route.

## Current Evidence

- The all-2025 native run was launched with a 30 second solver cap over 7,394
  rows and was stopped by explicit user request after the ABA section and
  enough AF timeout-boundary evidence were present.
- The ABA section completed 1,920 rows: 480 solved, 1,280 skipped for missing
  query-acceptance inputs, and 160 timed out.
- ABA timeout split observed from the completed ABA prefix: 131 rows in the
  benchmark family historically named `abcgen` and 29 generated `aba_*` rows.
- Structural telemetry showed the hard historical benchmark family is the
  `sparse_assumption_language|narrow_rule_bodies` cluster: 131 timeout rows and
  109 solved rows in the stopped event log.
- The first AF timeout class appears at large `admbuster` rows. For
  `AFs/admbuster_2500000.af`, multiple rows timed out around 40 seconds even
  though the configured cap was 30 seconds.
- The stopped event log also contains later AF rows with the same issue,
  including `AFs/afinput_exp_acyclic_indvary2_step2_batch_yyy10_bfs_4_sub05.af`
  at index 2428 timing out at about 40 seconds.
- The event log reports solved AF rows above 30 seconds and timeout
  reasons such as `timeout>40.0`; this is a runner contract issue independent
  of argumentation theory.

## Evidence Source

- Use `data\iccma\2025\runs\native-cnf-main-all-2025-auto-cap30-events.jsonl`
  as the source event log for this workstream.
- The log is intentionally incomplete after the user-requested stop. That is
  acceptable because all ABA rows completed before the stop, and the AF
  evidence needed here is only the runner timeout-boundary defect.
- Do not launch another all-2025 benchmark during this workstream. Every
  execution command must be a unit test, fixture builder run, or targeted
  single-row/profile command named below.

## Paper Page Anchors

Before implementing source code, reread these page images directly:

- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png`
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png`
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-007.png`
- `papers/deKleer_1986_AssumptionBasedTMS/pngs/page-001.png`
- `papers/deKleer_1986_AssumptionBasedTMS/pngs/page-002.png`
- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-002.png`
- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-003.png`

Use Cerutti for the preferred/stable SAT search shape, Dvorak for
complexity-sensitive operational signals, de Kleer for cached assumption-set
and nogood-style representation pressure, and Popescu for ABA dependency,
closure, and structural graph definitions.

## Owned Paths

- `workstreams/aba-abcgen-structural-telemetry.md`
- `src/argumentation/aba_telemetry.py`
- `tools/aba_abcgen_telemetry.py`
- `tools/iccma2025_run_native.py`
- `tests/test_aba_structural_telemetry.py`
- `tests/test_aba_abcgen_telemetry_workstream.py`
- `tests/test_iccma_runner_timeout_contract.py`
- `tests/manifests/iccma2025-abcgen-10x10.json`

## Deletion Targets

- Delete no existing production solver path in this workstream.
- Remove any new production check that branches on `abcgen`, `ABAs/`,
  `iccma`, raw instance basename, parent directory, or contest year.
- Do not commit `.ppm` files, py-spy profiles, raw benchmark event logs,
  regenerated run summaries, or PDF text-extraction output.
- Do not add optimizer routes, fallback wrappers, or compatibility aliases in
  this workstream.

## Hypothesis-Hard Rules

- Contract tests must be authored and run before the production code they
  constrain is implemented.
- A semantic-only property is insufficient for this workstream. Every test group
  must include at least one operational assertion: timeout boundary, no filename
  decision features, deterministic telemetry keys, structural match evidence,
  or bounded fixture counts.
- The fixture-builder contract must fail on a selector that relies on raw
  instance labels. It must inspect the fixture records and prove every
  `decision_features` / `distinctive_features` key is structural telemetry, not
  path identity.
- The runner timeout contract must fail on the current `timeout_seconds + 10.0`
  behavior before `tools/iccma2025_run_native.py` is edited.
- The telemetry property tests must fail on a missing `aba_telemetry` API before
  `src/argumentation/aba_telemetry.py` is added.
- If a contract cannot be made to fail before implementation, stop and repair
  the contract. Do not substitute a benchmark run for the missing property.

## Ordered Phases

1. Branch and baseline gate:
   - Verify the tracked worktree is clean on `main`.
   - Create the dedicated experiment branch
     `exp/aba-abcgen-structural-telemetry`.
   - Leave unrelated untracked files alone.
   - Do not rerun the broad all-2025 benchmark.

2. Paper reread gate:
   - Reread every page image listed in Paper Page Anchors.
   - Record the page anchors in the first test file touched by the workstream
     as comments next to the properties they justify.

3. Timeout-boundary contract:
   - Add a test-owned helper worker that sleeps longer than a configured small
     timeout and writes a valid solved-looking JSON result afterward.
   - Add `tests/test_iccma_runner_timeout_contract.py` proving the runner
     reports `status == "timeout"` and a reason derived from the configured
     timeout, not from an internal 40 second cap.
   - The first run of this test must fail against the current runner because
     `run_or_skip` gives `run_child` hidden slack beyond the configured row cap.
   - Run the timeout test before editing the runner and record the failing
     assertion in the commit message or workstream completion evidence.
   - Fix `tools/iccma2025_run_native.py` so subprocess timeout, profile
     timeout, event reason, and row elapsed boundary all derive from
     `RunConfig.timeout_seconds`.

4. Structural telemetry API:
   - Add `src/argumentation/aba_telemetry.py`.
   - The API accepts the parsed ABA framework object returned by existing
     parser code and returns a JSON-serializable dictionary.
   - The API computes all Final State telemetry fields without invoking Z3,
     PySAT, ASP, py-spy, or an ICCMA runner subprocess.
   - Graph/SCC computation uses explicit indexed adjacency lists; it does not
     infer generator family from filenames.

5. Telemetry property contracts:
   - Add Hypothesis properties for small ABA frameworks:
     - semantic-preserving rule order shuffles leave telemetry equal except for
       fields whose values are explicitly ordered histograms;
     - filename/path/year are absent from telemetry;
     - duplicate syntactic rules do not create fake new atoms or assumptions
       after parsing, and the parsed-framework API reports the semantic rule
       count available at that boundary;
     - SCC and histogram summaries are deterministic across repeated calls.
   - Run these properties before adding `src/argumentation/aba_telemetry.py`;
     the missing API is the required first failure.
   - Add a focused real-instance contract that parses at least one solved and
     one timed-out fixture row and produces positive, bounded telemetry.

6. 10x10 fixture builder:
   - Add `tools/aba_abcgen_telemetry.py`.
   - Inputs:
     `--manifest data\iccma\2025\manifests\iccma-2025-manifest.json`,
     `--event-log data\iccma\2025\runs\native-cnf-main-all-2025-auto-cap30-events.jsonl`,
     and `--sample-out tests\manifests\iccma2025-abcgen-10x10.json`.
   - Filter source rows to `kind == "aba"`, event `instance_kind == "aba"`,
     `status in {"solved", "timeout"}`, and subtracks that actually ran.
   - Construct the hard ABA cluster from structural telemetry over the completed
     ABA prefix. The script may report benchmark source paths in the fixture,
     but it must not use substring tests such as `abcgen` or `aba_` to decide
     cluster membership.
   - Select exactly 10 timeout rows and exactly 10 solved rows from that
     structural cluster.
   - For each timeout row, record one solved match chosen by nearest structural
     telemetry vector over manifest counts and API telemetry, not by filename
     tokens.
   - Each pair record must include `timeout_row`, `solved_row`,
     `shared_features`, `distinctive_features`, and `match_distance`.
   - Each pair record must include `decision_features`; every key in that map
     must be one of the structural telemetry fields emitted by the API.
   - The builder exits nonzero unless every pair has at least one
     non-filename `distinctive_features` entry.

7. Runner targeting and profile gate:
   - Add runner filters `--only-instance` and `--only-subtrack` to
     `tools/iccma2025_run_native.py`.
   - Add tests proving the filters select exact rows and do not alter solver
     behavior for the selected row.
   - Run py-spy only for four representatives selected from the fixture:
     two timed-out preferred/stable rows and their two matched solved rows.
   - Profile commands write under
     `data\iccma\2025\profiles\abcgen-10x10\`; those profiles remain
     uncommitted diagnostics.

8. Structural discriminator gate:
   - Add `tests/test_aba_abcgen_telemetry_workstream.py`.
   - The test loads the committed 10x10 fixture and verifies:
     - exact fixture counts: 10 timeout rows, 10 solved rows, 10 pairs;
     - every row has telemetry;
     - every pair has a nonempty `distinctive_features` set;
     - no distinctive feature key is `instance`, `relative_path`, `basename`,
       `parent`, `archive`, `label`, or `year`;
     - at least one distinctive feature appears in three or more timeout/solved
       pairs.
   - Add a production-path search gate that fails if source code routes on the
     historical benchmark label:
     `rg -n -F -- "abcgen" src tools tests`.
     The only allowed matches are this workstream, the fixture filename, and
     tests that assert the label is not used as a decision feature.
   - If this gate fails, the workstream is not complete and no optimizer
     implementation starts.

9. Verification and promotion:
   - Run the required tests.
   - Verify no generated diagnostics are staged.
   - Promote only the source, test, and curated fixture paths listed in Owned
     Paths to `main` after the branch gates pass.

## Required Commands

```powershell
uv run pytest -q tests\test_iccma_runner_timeout_contract.py
uv run pytest -q tests\test_aba_structural_telemetry.py
uv run tools\aba_abcgen_telemetry.py --manifest data\iccma\2025\manifests\iccma-2025-manifest.json --event-log data\iccma\2025\runs\native-cnf-main-all-2025-auto-cap30-events.jsonl --sample-out tests\manifests\iccma2025-abcgen-10x10.json
uv run pytest -q tests\test_aba_abcgen_telemetry_workstream.py tests\test_aba_structural_telemetry.py tests\test_iccma_runner_timeout_contract.py
rg -n -F -- "abcgen" src tools tests
uv run tools\iccma2025_run_native.py --backend auto --max-af-arguments 100000000 --max-aba-assumptions 100000000 --timeout-seconds 30 --only-instance <fixture-timeout-instance> --only-subtrack <fixture-subtrack> --profile-workers-dir data\iccma\2025\profiles\abcgen-10x10 --profile-worker-subtrack <fixture-subtrack> --label abcgen-profile-one --event-log-path data\iccma\2025\runs\abcgen-profile-one-events.jsonl
```

## Completion Evidence

- Page images listed above were reread directly before source implementation.
- The timeout-boundary and telemetry-property tests were run once before their
  corresponding production code existed or was fixed, and failed for the
  expected reasons.
- The timeout-boundary test failed before the runner fix and passed after it.
- `tests/manifests/iccma2025-abcgen-10x10.json` contains exactly 10 timeout
  rows, 10 solved rows, and 10 structurally matched pairs.
- The fixture builder used the stopped event log and did not require a new
  all-2025 run.
- The structural telemetry properties pass and contain no filename/year route
  dependency.
- The discriminator gate finds at least one non-filename structural feature that
  recurs in three or more timeout/solved pairs.
- Four py-spy profiles exist under
  `data\iccma\2025\profiles\abcgen-10x10\` and are not committed.
- The required pytest command passed:
  `uv run pytest -q tests\test_aba_abcgen_telemetry_workstream.py tests\test_aba_structural_telemetry.py tests\test_iccma_runner_timeout_contract.py tests\test_iccma_runner.py`
  reported 22 passed in 1.63s.
- `rg -n -F -- "abcgen" src tools tests` found no matches in `src` or `tools`;
  matches were limited to the fixture and tests guarding the historical label.
- `git status --short -- <Owned Paths>` is clean after the final commit.
