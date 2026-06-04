# B6 report: centralize the `_load_z3` z3 loaders into one core loader

Branch: `refactor/dedup`. Commit: `75d129b`.

## STEP 1 — findings (confirmed against disk)

`grep "def _load_z3" / "import z3" / "requires z3"` across `src` found FOUR z3 loaders, not 5.
Their contracts differ:

| # | Location | Shape | Exact message / behavior |
|---|----------|-------|--------------------------|
| 1 | `solving/af_sat.py:1611` `def _load_z3()` | returns module, RAISES | `RuntimeError("SAT solving requires z3-solver")` |
| 2 | `structured/aba/aba_sat.py:2415` `def _load_z3()` | returns module, RAISES | `RuntimeError("ABA stable SAT solving requires z3-solver")` |
| 3 | `probabilistic/epistemic.py:582` inline in `_linear_solver()` | RAISES (no named loader) | `RuntimeError("linear epistemic constraint reasoning requires z3-solver")` |
| 4 | `dynamics/optimization.py:282` `def _import_z3() -> Any | None` | returns `None`, does NOT raise | caller checks `z3 is None` -> `OptimizationResult(status="unavailable", trace={"reason": "z3-solver is not importable"})` |

Original bodies (1-3, all catch `ImportError` and chain via `from exc`):

```python
# af_sat
def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("SAT solving requires z3-solver") from exc
    return z3

# aba_sat
def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("ABA stable SAT solving requires z3-solver") from exc
    return z3

# epistemic._linear_solver (inline)
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("linear epistemic constraint reasoning requires z3-solver") from exc
```

Messages **DIFFER per caller** -> the core loader is parametrized by `feature`.

### Test references (`grep _load_z3 / _import_z3 in tests/`)
- `tests/structured/aba/test_aba.py:268`: `z3 = aba_sat._load_z3()` — direct attribute access. `aba_sat._load_z3` MUST remain a module attribute.
- `tests/dynamics/test_optimization.py:180`: `monkeypatch.setattr(optimization, "_import_z3", lambda: None)` — `_import_z3` MUST keep its name AND None-returning contract.
- No `monkeypatch.setattr(...,"_load_z3",...)` anywhere.

### Divergence decision (reported, not a blocking stop)
`optimization._import_z3` (#4) is NOT one of the "try/except that returns the z3 module ... raises on absence" loaders the task describes: it returns `None` and its caller relies on that. It is also monkeypatched by name. Folding it into a raising loader would change behavior. So it is left UNTOUCHED and centralization covers the three RAISING loaders (1-3). This is fully behavior-preserving and consistent with the task's "raises on absence" scope; no design question required.

## STEP 2 — the core loader

New `src/argumentation/core/optional_deps.py` (core is the lowest layer per the import-linter `layers` contract, so all four upper layers may import it — no upward import):

```python
def load_z3(feature: str) -> Any:
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(f"{feature} requires z3-solver") from exc
    return z3
```

`import z3` stays INSIDE the function -> lazy import preserved.

### How each caller delegates (message + lazy import preserved)
- `af_sat.py`: `from argumentation.core.optional_deps import load_z3`; local `def _load_z3(): return load_z3("SAT solving")`. **Thin local delegator** kept (preserves the `_load_z3` attribute; safe default).
- `aba_sat.py`: same pattern, `def _load_z3(): return load_z3("ABA stable SAT solving")`. Delegator kept because `test_aba.py` calls `aba_sat._load_z3()`.
- `epistemic.py`: `_linear_solver` now does `z3 = load_z3("linear epistemic constraint reasoning")`. No local `_load_z3` name existed and no test references one, so the call is inlined (no delegator needed). Message preserved via the `feature` arg.

The import+raise logic now lives in exactly ONE place (core). `f"{feature} requires z3-solver"` reproduces each original string verbatim.

## STEP 3 — verification (all `uv run`, output pasted)

### pyright (5 files)
```
$ uv run python -m pyright src/argumentation/core/optional_deps.py src/argumentation/solving/af_sat.py src/argumentation/structured/aba/aba_sat.py src/argumentation/probabilistic/epistemic.py src/argumentation/dynamics/optimization.py
0 errors, 0 warnings, 0 informations
```

### Behavioral message-preservation probe (z3 import blocked via builtins.__import__)
```
af_sat._load_z3: msg='SAT solving requires z3-solver' EXACT=True chained_from_ImportError=True
aba_sat._load_z3: msg='ABA stable SAT solving requires z3-solver' EXACT=True chained_from_ImportError=True
epistemic._linear_solver: msg='linear epistemic constraint reasoning requires z3-solver' EXACT=True chained_from_ImportError=True
```
(Importing all three modules with z3 blocked SUCCEEDED -> confirms no module-level z3 import; lazy import intact.)

### Regression suites
```
$ uv run python -m pytest tests/solving tests/structured/aba tests/probabilistic tests/dynamics tests/test_import_boundaries.py -q
1649 passed, 2 skipped in 223.17s (0:03:43)
```
(The 2 skips are pre-existing.)

### import-linter
```
$ uv run lint-imports
Layered architecture KEPT
gradual and ranking are independent KEPT
Contracts: 2 kept, 0 broken.
```

## Line endings / numstat
All edited files are FULLY CRLF (verified pre- and post-edit; 0 lone-LF lines):
af_sat 1631/1631, aba_sat 2448/2448, epistemic 865/865. New `optional_deps.py` is 24/24 CRLF.

`git show --numstat 75d129b`:
```
24	0	src/argumentation/core/optional_deps.py
2	4	src/argumentation/probabilistic/epistemic.py
2	5	src/argumentation/solving/af_sat.py
2	5	src/argumentation/structured/aba/aba_sat.py
```
Proportional: +24 new file; the three edits each add 1 import line + collapse a 5-6-line body to 1-2 lines. No whole-file churn. (`git diff --check` deliberately NOT used as an EOL signal — it false-flags every CRLF line in this repo.)

## Commit
`75d129b refactor: centralize z3 lazy-import in core.optional_deps` (4 files changed, 30 insertions(+), 14 deletions(-)).

## Out of scope — noticed
- `dynamics/optimization.py:_import_z3()` — different (None-returning) contract, monkeypatched by name in `tests/dynamics/test_optimization.py:180`. Intentionally NOT centralized. If a future batch wants it unified, the core helper would need a non-raising variant (e.g. `try_import_z3() -> module | None`) and the test patch target would have to be reconsidered.
- `_load_clingo` / `_load_pysat_solver` exist alongside these loaders but are explicitly deferred by the task; untouched.
