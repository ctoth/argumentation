# Task: make `grounded_extension` (Dung and bipolar) scale — pure performance, identical output

## Why

A downstream project (`../meanings`) builds a ~160,000-node, ~678,000-edge directed graph and wants to run argumentation semantics on it. `argumentation.dung.grounded_extension` and `argumentation.bipolar.bipolar_grounded_extension` are *correct* but algorithmically pathological — they do not finish on graphs of that size (killed after >200s, still in early iterations). The grounded extension is a polynomial-time object; a textbook O(V+E) labelling computes it. This task replaces the two slow implementations with the standard fast algorithm, **with byte-for-byte identical results** on every input.

This is a *performance* change, not a *semantics* change. Do not change any public API signature, any return type, or the set returned for any input. Do not touch enumeration semantics (`complete_extensions`, `preferred_extensions`, `stable_extensions`, `_all_subsets`, the bipolar `*_preferred_extensions`/`stable_extensions`) — those are inherently exponential and out of scope. Do not add an SCC/divide-and-conquer dispatcher — also out of scope.

## Fix A — `src/argumentation/dung.py`: `grounded_extension`

Current implementation iterates the characteristic function to a fixpoint; each round calls `defends(S, a)` for every argument, and `defends` scans `S` per attacker — so a round is O(E·|S|), |S| grows to n, there are O(n) rounds → roughly O(n²·E). Replace the body of `grounded_extension` with the standard linear grounded labelling:

- Need two adjacency views of `framework.defeats`: attackers-of (`_attackers_index`, already exists) and attacked-by (the forward view: source → set of targets). Build the forward view once.
- `live_attackers[a] = in-degree(a)` (number of attackers of `a`). A node with `live_attackers == 0` is IN; enqueue all such.
- Process the queue:
  - pop `a`; if already labelled, continue; label `a` IN.
  - for each `b` with `(a, b) ∈ defeats`: if `b` not already OUT: label `b` OUT; for each `c` with `(b, c) ∈ defeats`: `live_attackers[c] -= 1`; if `live_attackers[c] == 0` and `c` unlabelled: enqueue `c`.
- Return `frozenset` of the IN-labelled arguments. Anything not IN is OUT or UNDEC (not in the grounded extension).

Self-loops: a node `(a, a) ∈ defeats` has itself as an attacker, so `live_attackers[a] >= 1` and it is never seeded IN — it ends UNDEC unless some *other* IN node attacks it (→ OUT). That matches Dung grounded semantics; keep it.

Leave `characteristic_fn`, `defends`, `admissible`, `_attackers_index`, `range_of`, `complete_extensions`, etc. exactly as they are — only `grounded_extension`'s body changes (you may add a private helper, e.g. `_grounded_labelling`, in the same module). Anything elsewhere that calls `grounded_extension` (ideal/eager extensions, preferred-via-grounded paths, SAT-encoding sanity checks) must keep working unchanged.

## Fix B — `src/argumentation/bipolar.py`: `bipolar_grounded_extension` (and stop the per-call closure recompute)

`bipolar.defends()` recomputes `_defeat_closure(framework.defeats, framework.supports)` — itself a fixpoint over the whole graph — *and* rebuilds the attackers index on **every call**, and `bipolar_grounded_extension` calls `defends` n times per round. Fix:

- In `bipolar_grounded_extension`: compute the derived Cayrol defeat closure **once** (use the existing `derived_set_defeats(framework)` / `_defeat_closure(framework.defeats, framework.supports)`), then delegate to the now-fast `dung.grounded_extension` on `ArgumentationFramework(arguments=framework.arguments, defeats=<the closure>)` — or, if constructing a `dung.ArgumentationFramework` here is awkward (import cycles, normalization), inline the same linear labelling over the precomputed closure. Result must equal the current `bipolar_grounded_extension` output for every input.
- Give `bipolar.defends` and `bipolar.characteristic_fn` an optional keyword parameter for a precomputed closure (and/or precomputed attackers index) — default `None`, computed on demand exactly as now — so callers that loop (e.g. `bipolar_complete_extensions`, the admissibility checks inside `_maximal_sets`) can compute it once and pass it through. This is an additive, backward-compatible change to those signatures. Update the in-package callers to pass the precomputed value.

Do not change `cayrol_derived_defeats`, `_defeat_closure`, `set_defeats`, `support_closure`, the `*_admissible` predicates' *meaning*, or the enumeration functions.

## Tests you must add (`tests/`)

1. **Equivalence on small instances** — a new test (e.g. `tests/test_grounded_perf_equivalence.py`): for a corpus of small AFs (hand-picked: empty, single node, 2-cycle, 3-cycle, chain, the "Tweety/penguin" classic, a node attacked by a 2-cycle, a self-loop, plus ~50 pseudo-random AFs with seeded RNG, sizes 1–30, density varied), assert the new `grounded_extension` equals the *reference* fixpoint computation (keep a small private fixpoint implementation in the test, or compute the expected value by hand for the fixed ones) — and that it equals the old behaviour on the existing fixtures used elsewhere in the suite. Do the same for `bipolar_grounded_extension` with a corpus of small BAFs (varying support and attack edges).
2. **Scaling smoke test** — a test (marked slow / behind an env flag if the suite has such a convention; otherwise just keep it bounded) that builds a synthetic ~50k–100k-node sparse digraph and asserts `grounded_extension` returns in well under a second. (You don't have the OEWN data; a synthetic chain-plus-cycles graph at that size is sufficient to catch a quadratic regression.)
3. Make sure the **existing** `../argumentation` test suite still passes (`uv run pytest -q`). Report the before/after pass counts.

## Output

Write a report to `reports/perf-fixes-grounded-report.md` with: exactly what you changed (files, functions, before/after algorithm), the equivalence-test design and result, the existing-suite pass count before and after, a microbenchmark (old vs new `grounded_extension` on a few sizes — old will time out; show where), and any judgement calls you made (e.g. how you handled the bipolar→Dung delegation, any signature additions). Do not commit. Do not change `pyproject.toml`/`uv.lock` unless a test genuinely needs a dep already present (it shouldn't — zero-dep library, pytest is the only test dep).

## Acceptance bar

- `new grounded_extension(af) == old grounded_extension(af)` for every af in the equivalence corpus and every existing fixture.
- `new bipolar_grounded_extension(baf) == old bipolar_grounded_extension(baf)` likewise.
- Existing test suite: same pass count, no new failures.
- `grounded_extension` on a 50k+-node sparse graph: sub-second.
- No public-API signature removed or changed (additive optional kwargs on `bipolar.defends`/`bipolar.characteristic_fn` are fine).
