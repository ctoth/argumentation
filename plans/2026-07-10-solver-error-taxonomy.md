# Solver Error Taxonomy Plan

Date: 2026-07-10

Status: Completed on 2026-07-10.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Ensure solver dependency absence is reported as unavailability while invariant,
protocol, and implementation defects remain visible as defects. A broad
`RuntimeError` must not become a false “install z3-solver” diagnosis.

## Current Fault Boundary

The review identified broad catches in `src/argumentation/solving/solver.py`
that route arbitrary `RuntimeError` instances through
`_sat_runtime_unavailable`. At least one legitimate internal invariant failure
in `src/argumentation/solving/af_sat.py` also uses `RuntimeError`, making the
conversion observably unsafe.

## Phase 1: Inventory Existing Error Owners

Before adding any exception type:

1. Inventory result variants and exceptions already used by `solver.py`,
   optional dependency loading, subprocess execution, SAT adapters, ABA, and
   ASPIC routes.
2. Identify the single code location that knows an optional backend is absent.
3. Identify invariant and protocol failures currently represented by
   `RuntimeError`.
4. Prefer an existing precise exception or public result variant. Introduce a
   new exception only when no current owner can express the distinction.
5. Do not create a general solver adapter or compatibility exception hierarchy.

Record the chosen taxonomy in this plan before implementation.

## Taxonomy Decision

Inventory on current `main` found these existing owners:

- `SolverUnavailable` is the public result for an absent optional package or
  an unavailable configured backend.
- `SolverProcessError`, `SolverTimeout`, and `SolverProtocolError` already own
  subprocess exit, timeout, and malformed-output failures respectively.
- SAT implementation invariants in `af_sat.py` and `aba_sat.py` use ordinary
  `RuntimeError`; those errors must retain their traceback and must not be
  converted or retried.
- ASPIC/Clingo and ICCMA adapters already return the precise process,
  unavailable, and protocol result variants. They do not share the unsafe
  `RuntimeError` conversion and require no new conversion layer.
- `core/optional_deps.py` is the single owner that knows a Python import failed
  because an optional package is absent. The native ABA PrefSat loader is the
  only additional direct optional-package import boundary.

No existing exception represents optional Python-package absence. The chosen
internal signal is therefore one narrow `OptionalDependencyUnavailable`
exception owned by `core/optional_deps.py`. It carries the package name and
exact installation guidance. Public solver entry points catch only that type
and convert it to the existing `SolverUnavailable` result. No general solver
exception hierarchy, message sniffing, adapter, or fallback is introduced.

## Required Behavioral Matrix

| Cause | Required public outcome |
|---|---|
| Optional SAT package is not installed | Solver unavailable, with exact dependency guidance |
| Requested optional executable is absent | Solver unavailable or process error according to the existing public contract |
| SAT model violates an internal invariant | Propagated invariant defect or existing solver protocol error, never dependency unavailable |
| Backend returns malformed output | Existing solver protocol error with backend detail |
| Backend process exits/times out | Existing process/timeout result, not dependency unavailable |
| User input is invalid | Existing validation error, not dependency unavailable |

## Red Contracts

1. Force the optional dependency loader to report genuine absence and assert the
   current helpful unavailable result remains intact.
2. Force the SAT finder to raise the invariant failure identified in
   `af_sat.py`; assert that it is not converted into an unavailable result.
3. Inject a generic unexpected `RuntimeError` at each broad catch boundary and
   assert it remains distinguishable from dependency absence.
4. Cover direct SAT, enumerating, acceptance, ABA, and ASPIC entry routes that
   share the conversion logic.
5. Assert malformed backend/protocol output maps to the existing protocol error
   contract rather than the dependency message.

Commit the failing matrix before implementation.

## Green Implementation

1. Raise or return the precise dependency-absence signal at the optional
   dependency owner.
2. Narrow solver catches to that signal only.
3. Route known process and protocol failures through their existing typed
   results.
4. Allow unknown implementation defects to propagate with their original
   traceback unless the public API already has a precise invariant-error
   contract.
5. Remove `_sat_runtime_unavailable` if narrowing makes it redundant. If it
   remains, make its input type precise and ensure it cannot accept arbitrary
   runtime failures.
6. Delete obsolete message-sniffing or catch-all branches; do not preserve them
   as fallbacks.

## Operational Contracts

This is a routing change, so tests must assert which backend path and error
conversion branch ran. Add deterministic call-count/route assertions showing:

- dependency absence stops before a solve attempt;
- invariant failure is not retried or rerouted; and
- no fallback backend silently masks an implementation defect.

Do not use wall-clock timing as the first signal.

## Acceptance Gates

```powershell
uv run pytest -q tests/solving
uv run pytest -q tests -k "solver and (unavailable or protocol or invariant)"
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Use the repository's exact current test locations when executing.

## Done When

- Only genuine dependency absence produces dependency-install guidance.
- Internal invariants and unexpected runtime defects cannot be mislabeled as
  backend unavailability.
- Every solver route in the inventory follows the same explicit matrix.
- Broad catch/message-sniffing fallback paths are absent.
- The route contracts and full gates pass in an isolated committed slice.

## Execution Record

- Optional-dependency signal RED `809f545`; GREEN `73f61ed`.
- Solver routing matrix RED `2627bf1`; GREEN `09da2aa`.
- Direct `load_z3` import-boundary coverage `93035f9`.
- Every former broad catch now catches only
  `OptionalDependencyUnavailable`; ordinary invariant `RuntimeError`s propagate
  after one invocation and are not rerouted.
- Dung enumeration, single-witness, cone acceptance, direct acceptance, and
  enumerated acceptance routes return the exact dependency guidance carried by
  the typed signal.
- ABA sparse, stable, and support routes follow the same distinction, and the
  direct `python-sat` loader raises the typed signal with `python-sat` guidance.
- ASPIC/Clingo and ICCMA retained their existing unavailable, process, timeout,
  and protocol result contracts; no adapter or compatibility hierarchy was
  added.
- `uv run pytest -q tests/solving`: 260 passed, 2 skipped.
- `uv run pytest -q tests -k "solver and (unavailable or protocol or invariant)"`:
  15 passed, 2995 deselected.
- `uv run pyright src`: 0 errors, 0 warnings.
- `uv run lint-imports`: 2 contracts kept, 0 broken.
- `uv run pytest -q`: 3007 passed, 3 skipped, 1 xfailed in 289.03s.
- Source scan found no broad `RuntimeError` catch or obsolete runtime-to-
  unavailable helper in `solving/solver.py`.
