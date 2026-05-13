# Wave A fix — undefined references left by the preprocessing wiring

You are a coding subagent. Working dir: `C:\Users\Q\code\argumentation`. Current branch should be `experiment/graph-speedup-wave-a-preprocessing` (the previous agent committed `f827ff1` and `50f9204` there). If you are not on it, `git checkout experiment/graph-speedup-wave-a-preprocessing` first. Do NOT branch again — commit your fix on top.

## Context

The previous subagent added an AF preprocessing layer (`src/argumentation/preprocessing.py`, wired into `af_sat.py` and `aspic_encoding.py`). See `reports/graph-speedup-wave-a-preprocessing.md` and `notes/graph-speedup-wave-a-preprocessing.md`. Its work is otherwise good and committed. But Pyright now reports genuine undefined-name errors that the previous agent's "pyright clean" claim missed:

```
src/argumentation/af_sat.py:483:13   "_emit_preprocessing_shortcut" is not defined  [reportUndefinedVariable]
src/argumentation/af_sat.py:488:13   "_emit_preprocessing_shortcut" is not defined  [reportUndefinedVariable]
src/argumentation/aspic_encoding.py:277:19  "_projection_facts_for" is not defined  [reportUndefinedVariable]
```

These are real: a referenced name has no definition. Either the helper was meant to be defined and wasn't, or the call sites should use an existing name (e.g. the recon mentions an existing `_emit_shortcut` / `_emit_preprocessing_shortcut`-adjacent telemetry method in `af_sat.py`; `aspic_encoding.py` may already have a `_projection_facts` that the new code should be calling instead of `_projection_facts_for`). Read the surrounding code and figure out which it is.

Also clean up the avoidable `reportUnusedVariable` / "not accessed" findings the same change introduced where it's trivial and safe (unused imports `AfSimplification` / `simplify_af` in `af_sat.py:18` if they're genuinely unused; unused `args`/`kwargs` in `tests/test_iccma_runner.py:75,111`). Do NOT chase the pre-existing `_admissible_extension` / `_extension` / `pref` / `strict_rule_ids` findings if they predate this change — only touch what Wave A introduced.

## Task

1. Read `src/argumentation/af_sat.py` around lines 470–520 and `src/argumentation/aspic_encoding.py` around lines 260–290 (and wherever `_projection_facts` is defined). Determine the correct fix for each undefined name — define the missing helper, or correct the call to an existing one. Whichever makes the code actually do what the report says it does (emit a telemetry/shortcut signal when preprocessing solved the instance; project facts for the ASP encoding).
2. Apply the fix. Clean the trivial unused-name findings introduced by Wave A.
3. Run `pyright` on `src/argumentation/af_sat.py`, `src/argumentation/aspic_encoding.py`, `src/argumentation/preprocessing.py`, `tests/test_iccma_runner.py` — the `reportUndefinedVariable` errors must be gone.
4. Run the full test suite (`pytest`). Requires `z3-solver` and `clingo` installed (`pip install z3-solver clingo`; `pip install -e .` if needed). Expected baseline per the Wave A report: ~909 passed, 2 skipped, 1 pre-existing failure (`test_kernel_ideal_extension_is_admissible`), plus `test_datalog_grounding.py` failures from the missing `gunray` dep. Your fix must not regress that — ideally the count stays the same or the 1 failure is also fixed if it's actually related (verify against clean `main` before claiming "pre-existing").
5. `git add` the changed files, `git commit` with a clear message referencing this as the Wave A pyright fix. Include the commit hash in your report.
6. Write your report to `reports/graph-speedup-wave-a-fix.md`: what each undefined name actually was, the fix applied, pyright before/after on the four files, test suite result, commit hash.

## Hard stops

- Do NOT modify the preprocessing logic, the reductions, or the wiring behavior — this is a narrow correctness/lint fix only. If fixing the undefined name reveals the wiring is actually broken (e.g. preprocessing isn't being called where the report claims), STOP and report that — do not redesign.
- Do NOT touch ABA/ASPIC solver semantics, SCC code, or anything outside the named files.
