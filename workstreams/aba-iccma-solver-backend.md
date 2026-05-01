# ABA ICCMA Solver Backend Workstream

## Goal

Make ICCMA ABA runs use a task-directed solver backend instead of exact native
extension enumeration. The target architecture is:

- `argumentation.iccma_cli` remains the package-local ICCMA command for AF and
  ABA files;
- `tools/iccma2025_run_native.py --backend iccma --iccma-binary "uv run python -m argumentation.iccma_cli"`
  exercises both AF and ABA through the same subprocess contract;
- AF stable SE/DC/DS tasks use SAT by default;
- ABA SE/DC/DS tasks use a scalable backend by default once the backend exists;
- native ABA semantics remain the oracle for small generated frameworks;
- production subprocess adapters perform protocol and local certificate checks,
  while native-oracle checking stays in tests.

## Current State

- AF `SE-ST`, `DC-ST`, and `DS-ST` can solve 100-argument ICCMA 2025 rows
  through the package-local CLI.
- `argumentation.sat_encoding.sat_stable_extension` provides task-directed
  stable witness search for AF without enumerating all extensions.
- `argumentation.iccma_cli` auto-selects the SAT backend for AF stable tasks.
- `argumentation.iccma_cli` parses `p aba` files and prints ICCMA-shaped ABA
  SE/DC/DS outputs.
- `argumentation.solver_adapters.iccma_aba` accepts command lines such as
  `uv run python -m argumentation.iccma_cli`.
- The 2025 runner routes ABA through `argumentation.solver` for both native and
  ICCMA backends.
- ABA stable tasks inside `argumentation.iccma_cli` use the task-directed SAT
  backend. ABA complete/preferred tasks still use native exact semantics.
- Runner progress is logged per row as flushed JSON on stderr.
- `solve_dung_single_extension` and `solve_dung_acceptance` default to
  `backend="auto"`; stable Dung tasks route to SAT, while other semantics route
  to native semantics.
- ABA task-directed solver entry points default to `backend="auto"`, which
  currently resolves to native semantics until a scalable ABA backend exists.

## Target Default Behavior

- `solve_dung_single_extension(..., backend="auto")` and
  `solve_dung_acceptance(..., backend="auto")` select SAT for stable tasks and
  native semantics otherwise.
- Public defaults for task-directed solver entry points use `backend="auto"`.
- Full extension enumeration remains explicit and native by default because the
  package SAT path is task-directed, not a full competition enumerator.
- ABA task-directed entry points may expose `backend="auto"` immediately, but
  until a scalable ABA backend lands, `auto` must resolve to native and must not
  claim ICCMA-scale performance.

## Implementation Plan

### Phase 1: Default Solver Dispatch

Status: completed in the initial workstream setup.

- Add explicit `backend="auto"` handling in task-directed solver entry points.
- Make Dung stable single-extension and acceptance queries select the SAT
  witness search under `auto`.
- Keep `solve_dung_extensions` defaulting to native enumeration.
- Add tests proving default stable single/acceptance calls avoid native
  enumeration on large frameworks.

### Phase 2: ABA Backend Contract

Status: completed for the stable task-directed backend contract. Complete and
preferred remain explicit native fallback paths until Phase 4.

- Introduce a package-level ABA solver backend contract for SE/DC/DS tasks.
- Preserve typed unavailable/process/protocol results for missing optional
  engines and malformed outputs.
- Add small-framework differential tests against native ABA oracles before any
  ICCMA-scale claim.
- Keep unsupported ABA tasks returning typed unavailable before solver
  invocation.

### Phase 3: Task-Directed ABA Stable Solver

Status: completed for flat ABA frameworks.

- Build the flat ABA assumption attack surface from contraries and rules.
- Implement stable ABA SE/DC/DS solving without full extension enumeration.
- For `SE-ST`, return one stable assumption set or `NO`.
- For `DC-ST`, constrain the query to be derivable.
- For `DS-ST`, search for a stable counterexample where the query is not
  derivable.
- Add deterministic fixtures and generated differential tests against native
  ABA on small frameworks.
- Route `argumentation.iccma_cli` ABA stable tasks through this backend under
  `auto`.

### Phase 4: Preferred And Complete ABA

Status: not completed. The workstream leaves complete and preferred ABA on
native semantics until a source-backed ASP/subprocess backend or a tested
package-local encoding is implemented.

- Add preferred and complete ABA task solving only after the stable backend is
  pinned by tests and runner artifacts.
- Prefer a source-backed ASP/subprocess backend if it is materially simpler or
  more faithful than maintaining package-local encodings.
- Keep native enumeration available as the oracle, not the ICCMA-scale path.

### Phase 5: ICCMA Runner Evidence

- Run bounded ICCMA 2025 AF+ABA sweeps with progress logging enabled.
- Record summary artifacts under `data/iccma/2025/runs/`.
- Treat solved row counts as smoke evidence only; correctness claims require
  small-framework differential tests and source-backed protocol checks.

## Test Requirements

- Every backend success path needs a deterministic fixture.
- Every backend success path needs a generated differential test against native
  ABA on small frameworks where a native oracle exists.
- Every unsupported task/semantics pair must return typed unavailable before
  subprocess invocation.
- ICCMA CLI tests must cover AF, ABA, missing-query errors, malformed output,
  and default backend routing.
- Runner tests or smoke runs must prove per-row progress logs flush before the
  final summary.

## Non-Goals

- Do not restore a public `backend="z3"` Dung API.
- Do not claim full ICCMA ABA competitiveness until ABA stable, preferred, and
  complete paths have scalable implementations or external adapters.
- Do not use native exact enumeration as production validation for subprocess
  solver output.
