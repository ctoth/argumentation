# Code roast: what sucks about `formal-argumentation` (2026-06-03)

Task: read the source (ignoring existing notes/) and find everything wrong with the package.
Method: 5 parallel analyst agents over subsystems + personal verification of the 4 worst claims.

## Verified correctness bugs (I ran/read these myself)
1. `aba_asp.py:712` `_reject_id_collisions` — `len(mapping)==len(set(mapping))` is ALWAYS true
   (set of dict = its keys). Guard is dead, yet wired in (lines 53-54). Lossy `_literal_id`
   sanitizer means colliding ids silently overwrite → corrupt ASP encoding, no error. RAN: True.
2. `iccma_af.py:260` — `subprocess.run(timeout=...)` with no `except TimeoutExpired`; sibling
   `iccma_aba.py:201` catches it. AF solver timeout crashes the caller.
3. `af_sat.py:1603` + `labelling.py:319` — two recursive `_is_acyclic` DFS closures, RecursionError
   on ~1000-node chain. Commit ca0b0f5 just made finite SCC iterative but missed these. Already
   diverged (list/unsorted vs set/sorted).
4. `epistemic.py:633` — fixed 10k-iter projection `break`s on non-convergence and returns the
   infeasible point as valid, no flag.

## Architecture
- No public API: root + all subpackage __init__ are 1 line, no __all__/re-exports. Public surface =
  deep paths (`argumentation.structured.aba.aba_sat`). 0.3.0 broke every import path; will recur.
- `solver.py` (1275 LOC) god-dispatcher imports whole package; `try→find_X→except RuntimeError→
  "z3 unavailable"` repeated ~13x. `except RuntimeError` conflates missing-dep with real invariant bugs.

## Duplication (biggest theme)
- Dung machinery copy-pasted per framework (setaf.py:41 = full copy of core/dung.py). No shared
  "finite semantics over generic attack relation" abstraction.
- Horn forward-closure: 6 impls. Stable SAT encoding: 4. Z3 ranked-closure encoder: 3.
- `_all_subsets`, `extensions_for` dispatch, `_resolve_command`, code→name semantics tables all dup'd
  3-4x, several already drifted (one table has CF2, twin doesn't).

## aba_sat.py (2527 LOC) = benchmark dumping ground
- 5 independent solver families in one file; ~250+ lines test-only/dead.
- `aba_route_policy.py:9` hardcodes papers/.../page-NNN.png paths into runtime route_metadata;
  RealPrefSatResult ships "rejected_substitutes" bench notes. Telemetry woven into hot loops.
- Magic thresholds (>150, >25.0, >=700) split across 2 files, re-checked independently.

## Brute force with no guard
- stage/cf2/naive/ideal extensions, sat_encoding (1<<n), exact_enumeration, all of enforcement.py
  iterate 2^n with no cap. Only complete_labellings + matt_toni guard. Inconsistent.

## Packaging / hygiene
- `[grounding]` extra UNINSTALLABLE via pip: gunray only in [tool.uv.sources], 404 on PyPI (verified).
- 302MB/372 files papers/ + 108 tracked scratch files (notes/experiments/prompts) in repo.
  sdist excludes them so dist is clean, but history is polluted.
- Test markers documented (unit/property/differential) but ~85% unmarked, no --strict-markers.

## Lower severity
- Stringly-typed semantics/task/backend/strategy; no Enum/Literal. equational scheme="min" != minimum.
- Any-soup at all z3/pysat boundaries; public compute_probabilistic_acceptance(*args:Any,**kwargs:Any).
- Citations as callable names (af_revision: baumann_2015_kernel). Lying params (del simplify, del framework).
- @functools.cache on free Argument functions = unbounded global, not thread-safe.

## What's actually good
- No bare except/print/global/sys.path. Deterministic sorted() discipline. Excellent soundness
  docstrings in preprocessing.py/scc_recursive.py. finite.py/reduct.py clean. README example verified live.

## Verdict
Mathematically serious, micro-disciplined library trapped in an uncleaned ICCMA-benchmark repo.
Optimized to win a benchmark, not to be imported by a stranger.

## Next step
Reported to Q. Offered to fix the 4 red bugs (small, surgical, independently shippable) — awaiting
direction on which slice to implement. No code changed yet (this was a read/audit task).
