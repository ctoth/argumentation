# Wave A pyright fix — investigation notes

## 2026-05-12

- Branch `experiment/graph-speedup-wave-a-preprocessing`, HEAD `50f9204` (on top of `f827ff1`).
- Prompt claims pyright reports `reportUndefinedVariable` for `_emit_preprocessing_shortcut` (af_sat.py:483,488) and `_projection_facts_for` (aspic_encoding.py:277).
- **OBSERVED: pyright on all four named files = 0 errors, 0 warnings.** Both helpers ARE defined in the committed state:
  - `_emit_preprocessing_shortcut` at af_sat.py:950
  - `_projection_facts_for` at aspic_encoding.py:518
  - imports `AfSimplification`/`simplify_af` (af_sat.py:18) are used (lines 333,344,345,481...).
- So the committed branch has no bug. The prompt was written against a stale/uncommitted state, or `f827ff1` already fixed it.
- Nothing to fix. pytest: `1 failed, 909 passed, 2 skipped` (= Wave A baseline; `test_kernel_ideal_extension_is_admissible` pre-existing; `test_datalog_grounding.py` uncollectable missing `gunray`). No commit needed. Report: `reports/graph-speedup-wave-a-fix.md`.
