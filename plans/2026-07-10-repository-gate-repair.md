# Repository Gate Repair Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Restore the pre-remediation repository baseline to green without mixing in any
semantic library change. The review recorded two failures from
`uv run pytest -q`: one stale ICCMA timeout expectation and one documentation
boundary-path test covering five relocated modules.

## Scope Boundary

This plan may change only the failing test expectations and the stale
documentation paths they validate. It must not alter timeout production logic,
package ownership, ranking semantics, solver behavior, or public APIs.

## Slice A: ICCMA Timeout Budget Contract

### Current discrepancy

- `tools/iccma2025_run_native.py` reserves five seconds from the external
  timeout budget before passing time to the internal solve path.
- `tests/interop/test_iccma_runner.py` still expects `39` from a `40` second
  budget, while the production contract yields `35`.

### Execution

1. Inspect Git history for the five-second reserve and confirm that it is an
   intentional production contract, not an unreviewed regression.
2. Add or update the narrow test so it specifies the reserve explicitly and
   covers every production branch that applies the same budget calculation.
3. Keep the reserve in one production owner; do not duplicate the arithmetic
   into a new helper merely to satisfy the test.
4. Run the narrow ICCMA runner tests and commit this slice before continuing.

### Acceptance

```powershell
uv run pytest -q tests/interop/test_iccma_runner.py
```

- The test names and assertions make the five-second reserve visible.
- A future change to the reserve fails a focused contract.
- No production file changes unless history proves the implementation is the
  stale side of the discrepancy.

## Slice B: Package-Boundary Documentation Paths

### Current discrepancy

`docs/argumentation-package-boundary.md` names former source paths for the Dung,
AF-revision, probabilistic, tree-decomposition, and preference owners.

### Execution

1. Inventory the current owner of every symbol named in the failing table.
2. Replace each stale path with the exact current owner. Where a former module
   was split across multiple owners, list each real owner instead of naming a
   synthetic umbrella module.
3. Do not move modules or create compatibility files to make the documentation
   true.
4. Run the documentation boundary tests and commit this slice separately.

### Acceptance

```powershell
uv run pytest -q tests/test_documentation_boundaries.py
```

- Every documented path exists.
- Every named symbol is owned at the documented path.
- No old path is retained as a shim.

## Baseline Gate

After both commits:

```powershell
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

The full suite must pass before any semantic remediation begins. If another
failure appears, record whether it was pre-existing and stop this plan from
silently widening into unrelated cleanup.

## Done When

- Both review-recorded gate failures are closed.
- The full baseline suite is green.
- The two fixes exist as independently attributable Git slices.
- Production semantics and package ownership are unchanged.
