# Wave C2b — clingo multi-shot incremental CEGAR for ABA (ASPforABA reproduction)

Date: 2026-05-12. Branch `experiment/graph-speedup-wave-a-preprocessing`.
Commit: **`466d38da013cbdbcb89974e306b8720efd74df5d`**.

Implements **§2.3b** of `reports/aba-incremental-spec.md` — the clingo multi-shot
incremental CEGAR loop, the reproduction of Lehtonen, Wallner, Järvisalo, *Harnessing
Incremental Answer Set Solving for Reasoning in Assumption-Based Argumentation*,
TPLP 2021 (arXiv:2108.04192), **Algorithm 1**. §1 (`simplify_aba`) and §2.3a (the
Z3 preferred-growth refactor) were done by Wave C2a (`reports/graph-speedup-wave-c2a-aba-preprocessing.md`)
and are not touched here. UNRESOLVED-F of the spec is settled below.

The clingo Python multi-shot API **is** usable here (`clingo` 5.8.0 is installed,
`clingo.Control` works) — incremental solving was implemented for real, no faked
subprocess loop.

## What was built

### `encodings/aba_com_incremental.lp` — module π_com (Listing 1)

Transcribed verbatim from L21-TPLP **Listing 1** (paper p.6). The paper writes
`triggered by in`/`derived from undefeated`/`attacked by undefeated` with embedded
spaces; clingo predicates can't have spaces, so those become
`triggered_by_in`/`derived_from_undefeated`/`attacked_by_undefeated` (the only
notational change). `head(R, )` (some head exists) is written `head(R,_)`. The
conditional-literal bodies (`supported(X) : body(R,X)` = "for all X with
`body(R,X)`, `supported(X)`") are clingo's standard "all body atoms supported ⇒
rule triggers" idiom — a rule with empty body triggers vacuously, which is
correct for ABA facts. `#show in/1.` `#show supported/1.` so models report the
complete assumption set and what it derives.

**UNRESOLVED-F (does `encodings/aba_complete.lp` already have this predicate
shape?): NO.** `aba_complete.lp` uses precomputed `support_*` facts and a
`{ selected(A) }` choice over `derived/1`; Listing 1 is a pure forward-derivation
formulation over `in/out/supported/triggered_by_*/defeated/derived_from_undefeated/attacked_by_undefeated`.
A new resource file was needed. The existing enumeration `.lp` files were not
edited (the subprocess path stays the oracle).

The expected facts (`assumption/1`, `head/2`, `body/2`, `contrary/2`) are exactly
the L21-TPLP `ABA(F)` definition and are a subset of what
`argumentation.aba_asp.encode_aba_theory` already emits (it also emits `rule/1`,
`body_count/2`, `assumption_literal/2`, `support_*/2` — π_com ignores them), so no
new fact encoder was needed.

### `src/argumentation/aba_incremental.py` — `AbaIncrementalSolver`

One `clingo.Control` per query; `ABA(F) ∪ π_com` added to a `base` part and
grounded once. (NB: clingo cannot retract grounded rules, and the `constr(out(I))`
refinement clauses are *query-specific* — they encode "dominated with respect to
*this* `s`" — so a fresh `Control` per preferred query is the correct scoping, per
spec §2.4. The complete/stable methods reuse one `Control` since their solve is a
single shot.)

* **`is_skeptically_accepted_preferred(query)`** — L21-TPLP **Algorithm 1**, the
  DS-PR (Π₂ᴾ) task, the timeout cluster the recon flags:
  * `query` not in the language ⇒ never forward-derivable ⇒ not skeptically
    accepted (any preferred set is a counterexample; one is produced).
  * Line 2: `solve(assumptions=[(supported(s), False)])` — a complete set not
    deriving `s`. UNSAT on the first try ⇒ all complete sets derive `s` ⇒ YES.
  * Lines 5–7 (inner loop): grow the candidate to a ⊆-maximal complete set still
    not deriving `s`. Each step adds `constr(out(I)) = :- out(a1), …, out(ak).`
    (the OUT assumptions) as a fresh re-grounded `#program refine_n` part — this
    bans `I` and its subsets — then `solve(assumptions=[(in(a), True) for a ∈ I] +
    [(supported(s), False)])` finds a proper superset still not deriving `s`. The
    greedy growth is sufficient because the chain is monotone and only subsets of
    the current chain are ever banned, so the fixed point is ⊆-maximal among
    not-deriving-`s` complete sets.
  * Line 8: `solve(assumptions=[(in(a), True) for a ∈ I])` (no `supported(s)`
    ban). The accumulated `constr(out(I))` clauses force any model to be a *proper*
    superset of `I`; such a superset is complete and (by the maximality just
    established) must derive `s` ⇒ `I` is dominated ⇒ not preferred ⇒ loop back to
    Line 2 (the subset-blocking clauses stay in `Π`). UNSAT ⇒ `I` is a preferred
    assumption set not deriving `s` ⇒ NO, with `I` as the counterexample.
  * Edge case: if `out(I)` is empty (`I` = all assumptions), `constr(out(I))` is
    the unconditional `:- ` which makes `Π` permanently unsatisfiable; the loop
    detects this and returns `I` (no proper superset exists, so `I` is preferred).
* **`enumerate_preferred()` / `find_preferred_extension()`** — L21-TPLP
  **Algorithm 4** (Appendix A): Algorithm 1 with the query and Line 8 omitted —
  after the inner growth loop the candidate is preferred; collect it; the
  `constr(out(I))` ban ensures the next outer iteration produces a fresh one.
* **`enumerate_complete()` / `enumerate_stable()`** — a single `Control.solve`
  enumerating all answer sets of `ABA(F) ∪ π_com` (stable adds `:- out(X), not
  defeated(X).`, i.e. every OUT assumption is attacked by the IN-set — the stable
  condition on top of complete). Grounded delegates to `aba.grounded_extension`
  (already fast, the reference).
* **`is_credulously_accepted_complete/stable(query)`** — `solve(assumptions=[(supported(s),
  True)])` over π_com (+ the stable constraint). Credulous-preferred coincides with
  credulous-complete for derivable sentences, so this covers DC under preferred too.
* **`IncrementalTelemetry`** — counts `refinement_clauses` / `outer_iterations` /
  `inner_iterations` / `solver_calls`; the spy hook the tests assert on (so
  "the loop iterates" is checked structurally, not via timing).

clingo `Model` objects are only valid inside the `on_model` callback, so all
extraction (`{a : in(a) ∈ model}`) happens inside the callback and `_solve_one`
returns the assumption set, never a stale `Model` (a first cut crashed with an
access violation on this; fixed).

### Wiring into `aba_asp.solve_aba_with_backend` (the dispatcher)

* `backend in {"asp", "clingo"}` + flat `ABAFramework` + semantics ∈
  {complete, stable, preferred, grounded} ⇒ `_solve_multishot` (Algorithm 1 fast
  path for `task="skeptical"`+`preferred`+`query`; Algorithm 4 / single-shot
  enumeration otherwise + the shared task projection). This **replaces** the
  enumerate-then-filter `subprocess.run` path as the default.
* The legacy subprocess `clingo` enumerate-then-filter path is preserved as
  **`backend="clingo_subprocess"`** — kept as a differential oracle, unchanged.
* `admissible` keeps the subprocess path (there is no π_com-style module for it,
  and it isn't in the timeout cluster — out of scope per the hard stops).
* **Composition with C2a:** `solve_aba_with_backend` runs `simplify_aba` first
  (Wave C2a) on a non-trivial framework; the residual is then solved by
  `_solve_multishot` (so the two layers compose exactly like Wave A's AF reduct +
  SCC recursion). For DS-PR specifically, a new `_solve_simplified_ds_pr` applies
  the preprocessing lift rules — `query ∈ fixed_in` ⇒ YES; `query ∈ fixed_out` ⇒
  NO with a lifted residual preferred set as counterexample; `query ∈ Th(fixed_in)`
  ⇒ YES; `query ∉ residual.language` ⇒ NO with a lifted counterexample; otherwise
  Algorithm 1 on the residual, counterexample lifted back — so the incremental
  CEGAR loop is the default for DS-PR with preprocessing on **and** off.
* `simplify=False` opt-out preserved end to end.

Per the hard stops: the Dung AF is not materialised, ABA is not routed through the
AF SCC layer, `admissible`/ABA+ are not gated, `preprocessing.py`/`scc_recursive.py`
were only read.

## Test results

* **`tests/test_aba_multishot.py` — 1012 tests, all pass** (~2 min). Covers:
  * Enumeration `complete`/`stable`/`preferred`/`grounded`: `AbaIncrementalSolver`
    output **==** `aba.py` brute force **==** `aba_sat.support_extensions` **==**
    the wired `backend="asp"` path (simplify on **and** off), on an 8-framework
    hand battery (mutual attack, deterministic chains, self-attacking assumption,
    conjunctive bodies, derived sentences, and the two random instances found to
    need multi-round DS-PR) + 120 random flat ABAs.
  * Enumeration **==** `backend="clingo_subprocess"` (the legacy path), battery +
    40 random.
  * DS-PR (Algorithm 1): answer **==** "`query` derived by every preferred set of
    `aba.py`", and the returned counterexample is a real preferred set not
    deriving the query; **==** the `backend="asp"` path (simplify on/off, metadata
    confirms `algorithm == "L21-TPLP-Alg1"`); **==** `backend="clingo_subprocess"`;
    battery + 120 random; query over all assumptions, all contraries, derived
    sentences, and a not-in-language sentence.
  * DC: `is_credulously_accepted_complete/stable` **==** "derivable from some
    complete/stable set" + the wired path; battery + 120 random.
  * The CEGAR loop iterates: a 5-assumption framework where DS-PR(a4) ⇒ NO only
    after ≥2 `constr(out(I))` clauses (asserted via `IncrementalTelemetry`); a
    3-assumption framework where DS-PR(a1) ⇒ YES only after ≥2 *outer* iterations
    (a maximal-not-deriving complete set dominated by a deriving superset); and
    `enumerate_preferred` over the three-cycle (≥2 outer iterations).
  * The π_com resource is Listing 1 (every rule of Listing 1 present verbatim).
* **`simplify=False` regression:** every enumeration / DC / DS-PR oracle test
  asserts the `simplify=False` arm alongside `simplify=True`. No existing ABA
  telemetry test changed behaviour, so no `simplify=False` surgery was needed on
  the existing suite.
* **Full suite** (`python -m pytest tests/ --ignore=tests/test_datalog_grounding.py`,
  z3-solver + clingo installed): **`1 failed, 2632 passed, 2 skipped`**. The one
  failure is the documented pre-existing `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible`
  (a latent `find_ideal_extension` bug, unrelated to ABA — failed identically on
  the post-C2a baseline). Post-C2a baseline was `1 failed, 1620 passed, 2 skipped`
  with the same exclusion — so **no regression, +1012 new tests**.
* **Lint:** `ruff check` clean on every touched file.

### pyright output for touched files

```
$ pyright src/argumentation/aba_incremental.py src/argumentation/aba_asp.py tests/test_aba_multishot.py
0 errors, 0 warnings, 0 informations
```

## Before/after benchmark

No ICCMA cap-100 corpus in-repo (recon: `bench/` is README + `asp_vs_sat.py` +
`instance_gen.py` only). Two synthetic DS-PR generators (`tmp_work/bench_c2b.py`,
not committed — it lives under the throwaway `tmp_work/`):

* **`pref_heavy(k)`** — `k` independent mutual-attack assumption pairs (so ~`3^k`
  complete assumption sets) plus a "spoiler" assumption `s` (every `a_i` derives
  `contrary(s)`) and a `goal` sentence derived from each `b_i`, from `s`, and from
  `a_0`. `goal` is derived by every preferred set ⇒ DS-PR(goal) = YES — but only
  *after* the CEGAR loop inspects and prunes the maximal-not-deriving candidates
  that arise during the growth. The subprocess path instead enumerates all
  `aba_admissible.lp` answer sets (≈`2^(2k+1)`) and post-filters.
* **`no_help(k)`** — a deterministic chain whose only preferred set is the whole
  chain; DS-PR on a sentence derived by it resolves in one CEGAR round (the seed
  immediately grows to the unique preferred set, Line 8 UNSAT). The no-help
  control.

Wall-clock per query, min of 3 runs after warm-up. BEFORE = `backend="clingo_subprocess"`
(the legacy enumerate-then-filter), AFTER = `backend="asp"` (multi-shot Algorithm 1),
both with `simplify=False` so the comparison is purely the solving change.

### DS-PR — preferred-refinement-heavy (≈`3^k` complete sets)

| k | #assumptions | answer | BEFORE subprocess (ms) | AFTER multi-shot (ms) | speedup |
|---:|---:|:---:|---:|---:|---:|
| 2 | 5 | YES | 113.9–123.8 | 4.1 | ~30× |
| 3 | 7 | YES | 120.6 | 5.5 | ~22× |
| 4 | 9 | YES | 121.5 | 7.2 | ~17× |
| 5 | 11 | YES | 124.3–126.6 | 8.6–9.0 | ~14× |
| 6 | 13 | YES | 148.7–154.2 | 10.6–11.0 | ~14× |

### DS-PR — no-help control (unique preferred set, single CEGAR round)

| k | #assumptions | answer | BEFORE subprocess (ms) | AFTER multi-shot (ms) | speedup |
|---:|---:|:---:|---:|---:|---:|
| 5 | 5 | YES | 113.9 | 2.2 | ~52× |
| 8 | 8 | YES | 116.7 | 2.4 | ~48× |
| 10 | 10 | YES | 162.2 | 2.8 | ~59× |

**Honest reading:** the AFTER numbers grow gently with `k` (the CEGAR loop visits
few candidates); the BEFORE numbers are dominated by process-spawn + the
`aba_admissible.lp` `2^n` enumerate-then-filter even on the "no-help" chains, so
even the *control* shows a large multiplier — there is no instance where the
legacy path is competitive, because it is structurally `2^n`+subprocess. What the
control establishes is that the multi-shot path has **no pathological overhead** —
a single-round DS-PR is ~2 ms regardless of `k`. (For instances the legacy path
already handled in a few ms — tiny frameworks — the multi-shot path is in the same
ballpark; the gate keeps it transparent either way.) No absolute claim transfers to
the ICCMA timeout files (none in-repo), but the structure — replacing a
`2^n`+subprocess enumerate-then-filter with a CEGAR loop that visits a handful of
candidates — is exactly the L21-TPLP result, and the oracle tests confirm the
answers are identical.

## Files

* `src/argumentation/aba_incremental.py` — new, `AbaIncrementalSolver` + `IncrementalTelemetry`.
* `src/argumentation/encodings/aba_com_incremental.lp` — new, Listing 1.
* `src/argumentation/aba_asp.py` — `_solve_multishot`, `_solve_simplified_ds_pr`,
  dispatcher routing, `backend="clingo_subprocess"` alias.
* `tests/test_aba_multishot.py` — new, 1012 tests.

Commit: `466d38da013cbdbcb89974e306b8720efd74df5d`.
