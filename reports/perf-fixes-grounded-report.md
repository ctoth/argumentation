# Grounded Performance Fix Report

Workflow used: `prompts/perf-fixes-grounded.md`.

## Changes

- `src/argumentation/dung.py`
  - Replaced `grounded_extension`'s iterative characteristic-function loop with the standard grounded labelling algorithm.
  - Added `_targets_index(defeats)` as the forward adjacency view, while leaving `_attackers_index`, `defends`, `characteristic_fn`, `admissible`, `range_of`, and enumeration semantics unchanged.
  - Before: repeated fixpoint rounds over every argument, with defence checks scanning the current extension.
  - After: build attackers/targets indexes once, seed unattacked arguments as IN, mark attacked arguments OUT, decrement live attacker counts, and return the IN-labelled arguments.

- `src/argumentation/bipolar.py`
  - `bipolar_grounded_extension` now computes `derived_set_defeats(framework)` once and delegates to `argumentation.dung.grounded_extension` on a `DungArgumentationFramework` over that closure.
  - Added optional keyword parameters for precomputed defeat closure and attackers index on `defends` and `characteristic_fn`.
  - Updated in-package loop callers to reuse the precomputed closure/index through private helpers, including `_maximal_sets`, `bipolar_complete_extensions`, `stable_extensions`, and admissibility checks.
  - Public signatures were only extended with optional keyword parameters; no existing required parameter or return type was removed.

- `tests/test_grounded_perf_equivalence.py`
  - Added private reference fixpoint implementations for Dung grounded semantics and bipolar grounded semantics over `derived_set_defeats`.
  - Added fixed Dung cases: empty, single node, 2-cycle, 3-cycle, chain, Tweety/penguin-style case, node attacked by a 2-cycle, self-loop, and existing grounded fixtures mirrored from the suite.
  - Added 50 seeded pseudo-random Dung AFs, sizes 1-30 with varied density.
  - Added fixed and 50 seeded pseudo-random BAFs with varied attack/support edges.
  - Added a 50,004-node sparse chain-plus-cycles smoke test asserting sub-second `grounded_extension`.

## Test Results

- Before changes: `uv run pytest -q` -> `803 passed, 2 skipped in 73.65s`.
- Focused plus existing Dung/Bipolar targeted tests after the final source adjustment: `uv run pytest -q tests/test_grounded_perf_equivalence.py tests/test_dung.py tests/test_bipolar_semantics.py tests/test_dung_extensions_workstream.py` -> `103 passed in 11.39s`.
- After changes: `uv run pytest -q` -> `806 passed, 2 skipped in 68.14s`.

The after count is three higher because of the new test module. Existing tests still pass with no new failures.

## Microbenchmark

Synthetic graph shape: repeated six-node groups containing a three-node reinstatement chain and a three-node directed cycle. Old runs used a 2.0 second cap per size.

| nodes | old fixpoint | new labelling |
| ---: | ---: | ---: |
| 600 | 0.0362s (200 IN) | 0.0005s (200 IN) |
| 2,400 | 0.7584s (800 IN) | 0.0020s (800 IN) |
| 4,800 | >2.0s timeout | 0.0053s (1,600 IN) |
| 50,004 | not run | 0.1425s (16,668 IN) |

The scaling smoke test independently measured the 50,004-node case under the same sub-second acceptance bar.

## Judgement Calls

- Bipolar grounded delegates to Dung grounded instead of duplicating the labelling loop. There is no import cycle: `dung.py` does not import `bipolar.py`.
- I threaded the precomputed bipolar defeat closure through private helpers used by repeated conflict, safety, and admissibility checks. This preserves public helper signatures while avoiding closure recomputation in enumeration loops.
- I did not change `pyproject.toml`, `uv.lock`, public return types, Dung enumeration semantics, or bipolar preferred/stable enumeration semantics.
- No commit was made.
