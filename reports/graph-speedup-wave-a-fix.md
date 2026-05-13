# Wave A pyright fix — report

Date: 2026-05-12
Branch: `experiment/graph-speedup-wave-a-preprocessing`
HEAD at start and end: `50f9204` (on top of `f827ff1` "Add AF grounded-reduct preprocessing layer (Wave A)")

## Verdict: nothing to fix — committed branch is already correct

The prompt was written against a stale or uncommitted snapshot. In the committed branch state, the `reportUndefinedVariable` errors do not exist, and the named helpers are defined:

- **`_emit_preprocessing_shortcut`** — defined at `src/argumentation/af_sat.py:950` as a module-level function `(framework, trace_sink, metadata, utility_name, *, accepted) -> None` that emits a `SATCheck` telemetry record (`result="accepted"/"rejected"`, zero solver cost) when preprocessing settled the instance. The call sites at `af_sat.py:483,488` (inside `is_preferred_skeptically_accepted`) reference it correctly. It does exactly what the Wave A report describes.
- **`_projection_facts_for`** — defined at `src/argumentation/aspic_encoding.py:518` as `(framework) -> tuple[str, ...]`; the pre-existing `_projection_facts(projection)` (line 514) now delegates to it. The new Wave A call at `aspic_encoding.py:295` (`facts=_projection_facts_for(residual_framework)`) references it correctly — projecting facts for the simplified residual framework before handing it to clingo.
- The imports `AfSimplification` / `simplify_af` at `af_sat.py:18` are used (e.g. `af_sat.py:333,344,345,481,698`).
- The line numbers cited in the prompt for `aspic_encoding.py` (277) and partially for `af_sat.py` do not match the committed code's actual call sites (295; 483/488 do match), consistent with the prompt being against an earlier draft.

The hard-stop ("if fixing the undefined name reveals the wiring is actually broken, STOP and report") does not apply because the wiring is not broken — there is no undefined name to fix.

## pyright (before == after, no changes made)

```
$ python -m pyright src/argumentation/af_sat.py src/argumentation/aspic_encoding.py \
                    src/argumentation/preprocessing.py tests/test_iccma_runner.py
0 errors, 0 warnings, 0 informations
```

Also clean across the whole `src/argumentation/` and `tests/` trees for these files (no `reportUnusedVariable`, no `reportUndefinedVariable`). The "trivial unused-name cleanup" the prompt mentions (unused `AfSimplification`/`simplify_af` imports, unused `args`/`kwargs` in `tests/test_iccma_runner.py:75,111`) is not present either — those imports are used, and `tests/test_iccma_runner.py:75,111` produce no pyright findings.

## Test suite

```
$ python -m pytest -q --ignore=tests/test_datalog_grounding.py
1 failed, 909 passed, 2 skipped in 77.61s
FAILED tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible
```

- `909 passed, 2 skipped, 1 failed` — matches the baseline stated in `reports/graph-speedup-wave-a-preprocessing.md` exactly. `test_kernel_ideal_extension_is_admissible` is the documented pre-existing failure (unrelated to Wave A).
- `tests/test_datalog_grounding.py` is uncollectable (`ModuleNotFoundError: No module named 'gunray'`) — pre-existing missing optional dep, ignored as in the baseline.

## Commit

No commit made — there is no source change to commit. The only working-tree additions are this report and `notes/graph-speedup-wave-a-fix.md` (untracked notes, per project convention).
