# Report B1: delete production-dead bitvec ranked-closure encoder

Task: delete `_add_bitvec_ranked_closure_constraints` in
`src/argumentation/structured/aba/aba_sat.py` and its moot parity test, after grep-proving it is
production-dead.

Branch: `refactor/dedup` (created off `fix/correctness-bugs`).

## 1. Grep evidence — production-dead

Full-repo grep for `_add_bitvec_ranked_closure_constraints`:

```
notes\graph-theory-recon-codebase-2026-05-12.md:28:  ... a BitVec variant `_add_bitvec_ranked_closure_constraints` line 695 exists but appears unused).
tools\aba_stable_diagnostics.py:93:        derived = _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables)
tools\aba_stable_diagnostics.py:312:def _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables):
prompts\dup-scout-aba.md:29:   - `structured/aba/aba_sat.py:2097` (`_add_bitvec_ranked_closure_constraints`)
prompts\dup-scout-aba.md:33:   ... (`_add_bitvec_ranked_closure_constraints`, `_prefsat_*`) ...
prompts\dedup-b1-coder.md: (the task prompt)
src\argumentation\structured\aba\aba_sat.py:2097:def _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables):
reports\dup-scout-aba.md: (scout findings)
tests\structured\aba\test_aba.py:303:    derived = aba_sat._add_bitvec_ranked_closure_constraints(z3, solver, framework, variables)
```

Grep restricted to `src/` (production):

```
src\argumentation\structured\aba\aba_sat.py:2097:def _add_bitvec_ranked_closure_constraints(z3, solver, framework, variables):
```

The ONLY `src/` hit is the definition itself — **no production caller**. Findings:

- `tools/aba_stable_diagnostics.py` has its OWN local redefinition (line 312) and calls that local copy
  (line 93). It does NOT import or call the `aba_sat` version. Out of scope; left untouched.
- The sole caller of the `aba_sat` version was the parity test `test_aba.py:303`.

Conclusion: the scout's dead-code claim is CORRECT. Safe to delete.

## 2. Test that referenced it — keep/delete decision

The reference was `tests/structured/aba/test_aba.py:303`, inside
`test_bitvec_ranked_closure_matches_native_closure`. Full test (quoted):

```python
@given(flat_aba_frameworks(), st.data())
@settings(deadline=10000, max_examples=40)
def test_bitvec_ranked_closure_matches_native_closure(
    framework: ABAFramework,
    data: st.DataObject,
) -> None:
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    selected = data.draw(st.frozensets(st.sampled_from(assumptions)))
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"test_bv_in_{index}")
        for index, assumption in enumerate(assumptions)
    }
    solver = z3.Solver()
    derived = aba_sat._add_bitvec_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption, variable in variables.items():
        solver.add(variable == (assumption in selected))

    assert solver.check() == z3.sat
    model = solver.model()
    ranked_closure = frozenset(
        literal
        for literal, variable in derived.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )

    assert ranked_closure == native_aba._closure(framework, selected)
```

Decision: **DELETE the whole test.** Its single purpose is to validate the dead bitvec encoder — it
builds a solver via `_add_bitvec_ranked_closure_constraints` and asserts the result matches
`native_aba._closure`. It exercises no other live encoder/path. With the encoder gone the test is moot.

Note: the live Int-rank encoder retains its own equivalent coverage via the still-present
`_add_ranked_closure_constraints` parity test (`test_aba.py:274`), so no coverage is lost.

## 3. Orphaned-helper check

`_add_bitvec_ranked_closure_constraints` used two private helpers: `_literal_key` and
`_rules_by_consequent`. Both remain live after deletion:

- `_rules_by_consequent` — still called by the live Int encoders at `aba_sat.py:1968` and `:2029`, and
  has its own dedicated test `test_rules_by_consequent_groups_rules_deterministically`
  (`test_aba.py:318`).
- `_literal_key` — still called at many live sites (`aba_sat.py:581, 636, 1344, 1723, 1921, 1961, ...`).

No helper becomes orphaned. Scope kept tight; nothing else deleted.

## 4. Deletion diff stat

```
 src/argumentation/structured/aba/aba_sat.py | 63 -----------------------------
 tests/structured/aba/test_aba.py            | 29 -------------
 2 files changed, 92 deletions(-)
```

Post-deletion grep for `_add_bitvec_ranked_closure_constraints` in `src/` and `tests/`: **No matches
found.** Runtime confirmation:

```
HAS_ATTR: False     # hasattr(aba_sat, '_add_bitvec_ranked_closure_constraints')
```

## 5. ABA suite result (pasted)

`uv run python -m pytest tests/structured/aba -q`

```
........................................................................ [  5%]
... (truncated dots) ...
....................................                                     [100%]
1332 passed in 222.18s (0:03:42)
```

1332 passed, 0 failed, 0 skipped. (No pre-existing skips in this suite.)

## 6. Pyright result (pasted)

Changed production file — clean:

`uv run python -m pyright src/argumentation/structured/aba/aba_sat.py`

```
0 errors, 0 warnings, 0 informations
```

Both changed files:

`uv run python -m pyright src/argumentation/structured/aba/aba_sat.py tests/structured/aba/test_aba.py`

```
  ...test_aba.py:88:50  - error: Argument of type "frozenset[object]" ... "derives" (reportArgumentType)
  ...test_aba.py:95:54  - error: Argument of type "frozenset[object]" ... "derives" (reportArgumentType)
  ...test_aba.py:320:24 - error: "AssumptionSet | None" ... "attacks" (reportArgumentType)
  ...test_aba.py:321:27 - error: Operator "-" not supported for ... "AssumptionSet | None" (reportOperatorIssue)
  ...test_aba.py:346:45 - error: "AssumptionSet | None" ... "admissible" (reportArgumentType)
  ...test_aba.py:348:9  - error: Operator "<" not supported for "None" (reportOptionalOperand)
6 errors, 0 warnings, 0 informations
```

These 6 errors are PRE-EXISTING in the test file and unrelated to this deletion. Proof: running pyright
on the test file at the base (my change stashed) reported **7 errors** — the same 6 PLUS one that my
deletion REMOVED:

```
  ...test_aba.py:88:50  - error: frozenset[object] ... "derives"
  ...test_aba.py:95:54  - error: frozenset[object] ... "derives"
  ...test_aba.py:303:23 - error: "_add_bitvec_ranked_closure_constraints" is not a known attribute of module
                                  "argumentation.structured.aba.aba_sat" (reportAttributeAccessIssue)
  ...test_aba.py:349:24 - error: AssumptionSet | None ... "attacks"
  ...test_aba.py:350:27 - error: Operator "-" ... AssumptionSet | None
  ...test_aba.py:375:45 - error: AssumptionSet | None ... "admissible"
  ...test_aba.py:377:9  - error: Operator "<" not supported for "None"
7 errors, 0 warnings, 0 informations
```

The deletion introduced ZERO new pyright errors and removed one (the dangling attribute-access on the
now-deleted function). Net pyright count went 7 -> 6. The production file `aba_sat.py` is fully clean.

## 7. Commit

Commit hash: `4aaefd37175e7558338a1d50af862a1329887435` (branch `refactor/dedup`).

Commit touches only the two intended files:

```
 src/argumentation/structured/aba/aba_sat.py | 63 -----------------------------
 tests/structured/aba/test_aba.py            | 29 -------------
 2 files changed, 92 deletions(-)
```
