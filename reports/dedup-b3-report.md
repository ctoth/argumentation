# Dedup B3 report — remove naive `_prefsat_closure`, repoint to canonical `_closure`

**Branch:** `refactor/dedup`
**Result:** EQUIVALENT → dedup performed (naive body removed, callers repointed).

## The two signatures

Both functions live in the `structured.aba` package (intra-package, no layering issue).

Removed (naive, was `aba_sat.py:2084`):
```python
def _prefsat_closure(framework: ABAFramework, extension: AssumptionSet) -> frozenset[Literal]:
    derived = set(extension)
    changed = True
    while changed:                       # O(rules²) forward Horn fixpoint
        changed = False
        for rule in framework.rules:
            if all(antecedent in derived for antecedent in rule.antecedents):
                if rule.consequent not in derived:
                    derived.add(rule.consequent)
                    changed = True
    return frozenset(derived)
```

Canonical (worklist, `aba.py:255`):
```python
def _closure(framework: ABAFramework, premises: AssumptionSet) -> frozenset[Literal]:
    ... # waiting-list / remaining-count worklist, single pass + queue drain
    return frozenset(closure)
```

**Contract match:** identical signature `(ABAFramework, AssumptionSet) -> frozenset[Literal]`.
Both seed the result with `set(<seed>)`, so the **seed is included** in the output. Both compute the
forward Horn closure of that seed under `framework.rules`. The only difference is algorithmic
(naive O(rules²) re-scan vs. worklist) — same fixed point, so substitution is behavior-preserving.

## Equivalence probe (load-bearing evidence)

Two independent runs, both BEFORE relying on the swap.

### Run 1 — temporary hypothesis test (both functions present)
3 hypothesis tests, 1400 total examples, comparing `aba_sat._prefsat_closure(...)` vs
`native_aba._closure(...)`:
- arbitrary language-subset seeds (600 ex),
- single-literal seeds mirroring the `aba_sat.py:98` caller (400 ex),
- every assumption-subset seed mirroring the `:904`/`:1537` callers (400 ex).

```
$ uv run python -m pytest tests/structured/aba/test_prefsat_closure_equivalence_probe.py -q
...                                                                      [100%]
3 passed in 2.34s
```

### Run 2 — standalone probe vs. a verbatim copy of the REMOVED naive body
(This is the form Codex can re-prove at the parent commit.)

```python
def naive_prefsat_closure(framework, extension):
    # Verbatim copy of the REMOVED _prefsat_closure body.
    derived = set(extension)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(a in derived for a in rule.antecedents):
                if rule.consequent not in derived:
                    derived.add(rule.consequent); changed = True
    return frozenset(derived)
# hypothesis: flat_aba_frameworks(max_assumptions=4, max_rules=8), arbitrary language-subset seed
# assert naive_prefsat_closure(fw, seed) == native_aba._closure(fw, seed), max_examples=1000
```

```
$ uv run python -c "...probe..."
EQUIVALENCE PROBE PASSED: naive(removed) == native_aba._closure over 1000 samples
```

No mismatch on any of the 2400 samples. The functions are exactly equivalent.

## The swap (REMOVE, not delegate)

Signatures were identical, so the naive function was **removed entirely** and all callers repointed
directly at the canonical `_closure`.

- `src/argumentation/structured/aba/aba_sat.py`
  - import: added `_closure` to `from argumentation.structured.aba.aba import ...`.
  - `_singleton_closure_attack_count` (line ~98): `_prefsat_closure(...)` → `_closure(...)`.
  - `RealPrefSatTracer.result` (line ~904): `_prefsat_closure(...)` → `_closure(...)`.
  - `NativeCnfPrefSatTracer.result` (line ~1537): `_prefsat_closure(...)` → `_closure(...)`.
  - deleted the 11-line naive `_prefsat_closure` definition.
- `tools/aba_shape_benchmark.py`
  - 4th caller (line ~1058): `aba_sat._prefsat_closure(...)` → `native_aba._closure(...)`
    (module already imported as `native_aba`); removed the now-unused local `import aba_sat`.

`git diff --stat`: `aba_sat.py` 5 ins / 20 del net (−15 LOC), `aba_shape_benchmark.py` 1 ins / 3 del.
`grep _prefsat_closure src/ tools/` → no remaining references in production/tool code.

## Verification (all via `uv run`)

Full ABA suite:
```
$ uv run python -m pytest tests/structured/aba -q
1332 passed in 235.80s (0:03:55)
```

Prefsat / shape contract tests (perf-contract surface):
```
$ uv run python -m pytest tests/structured/aba/test_aba_real_prefsat_contract.py \
    tests/structured/aba/test_aba_decomposed_prefsat_contract.py \
    tests/structured/aba/test_aba_native_cnf_prefsat.py \
    tests/structured/aba/test_aba_sparse_narrow_route_contract.py \
    tests/structured/aba/test_aba_shape_contract.py -q
39 passed in 4.82s
```
(naive O(rules²) → worklist: strictly faster, no contract regression.)

Pyright on the primary changed file:
```
$ uv run python -m pyright src/argumentation/structured/aba/aba_sat.py
0 errors, 0 warnings, 0 informations
```

Pyright on `tools/aba_shape_benchmark.py` reports 5 errors at lines 199/372/376/377 — all
**pre-existing** (verified by running pyright on `git show HEAD:tools/aba_shape_benchmark.py`,
which showed the same 5 plus the now-resolved `_prefsat_closure` attribute error). My one-line
change introduced zero new pyright errors and removed one.

## Commit
`ef261a13cc523240cd4f2df880c0d89255e29405` on `refactor/dedup`
("refactor: dedup naive _prefsat_closure into canonical _closure").

## Out of scope — noticed
- `tools/aba_shape_benchmark.py` has 5 pre-existing pyright type errors (lines 199, 372, 376, 377)
  unrelated to closure dedup: a `float | int` passed where `int` is declared, and a
  `list[Literal]` assigned to a `list[tuple[Literal, bool]]`-typed variable. Not touched.
