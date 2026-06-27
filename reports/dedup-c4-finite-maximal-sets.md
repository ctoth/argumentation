# dedup-c4: extract `finite.maximal_sets()` and dedupe inclusion-maximal filters

Status: edits in progress (helper + test + call sites). Checks/commit pending.

## Helper contract (added to `src/argumentation/core/finite.py`)

```python
def maximal_sets(candidates: Iterable[frozenset[T]]) -> list[frozenset[T]]:
```

- Keeps each member `x` for which no other member is a strict superset
  (i.e. `not any(x < other for other in candidates)`).
- Preserves input order.
- Does NOT deduplicate (equal sets are not strict subsets of one another, so
  every copy survives). Per-site dedup/sort/tuple wrapping stays at the call site.

## Sites found (all 8 are the identical pattern over the SAME collection they iterate)

| Site | Original | Action |
|------|----------|--------|
| `core/dung.py` ~291 (preferred) | `[e for e in completes if not any(e < o for o in completes)]` | REPLACED → `maximal_sets(completes)` |
| `core/dung.py` ~433 (naive) | over `candidates` | REPLACED → `maximal_sets(candidates)` |
| `core/dung.py` ~592 (prudent preferred) | over `candidates` | REPLACED → `maximal_sets(candidates)` |
| `core/dung.py` ~659 (ideal) | over `candidates`, then `len()==1` check | REPLACED → `maximal = maximal_sets(candidates)` |
| `core/bipolar.py` ~425 (`_maximal_sets`) | over `admissible_sets`, then `sorted(..., key=extension_sort_key)` | REPLACED, sort wrapper kept |
| `core/scc_recursive.py` ~135 (`_base_preferred_in_c`) | over `completes` | REPLACED → `maximal_sets(completes)` (pending) |
| `frameworks/setaf.py` ~116 (preferred) | over `admissibles`, wrapped in `_sorted_extensions(...)` | REPLACED, wrapper kept (pending) |
| `frameworks/caf.py` ~239 (`_maximal_claim_sets`) | over `projected` (already deduped), wrapped in `tuple(...)` | REPLACED, dedup+tuple kept (pending) |

## Left as-is

- `core/dung.py` `_range_maximal_extensions` (~333): compares candidate *ranges*,
  not the candidates themselves — different collection, NOT a `maximal_sets` site.
- `core/scc_recursive.py` `_base_complete_in_c` `(defended & c) <= candidate`: fixpoint
  test, not a maximality filter.
- Various `<=` / `len(...) <= 1` occurrences: not maximality filters.

## Checks / commit

All 8 sites replaced. `_range_maximal_extensions` left as-is (compares ranges, not the
candidates) — documented above.

- `uv run ruff check` (7 changed files): All checks passed!
- `uv run pyright` (7 changed files): 0 errors, 0 warnings, 0 informations
- Targeted pytest tests/core tests/frameworks: pending
- Full suite + lint-imports: pending
- Commit hash: pending
