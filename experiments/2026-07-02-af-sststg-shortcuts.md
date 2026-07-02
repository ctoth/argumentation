# AF SST/STG Dvořák Fragment Shortcuts (stable-first + acyclic)

Date: 2026-07-02

Status: in progress (derivations written before implementation, per protocol).

Experiment branch: `exp/af-sststg-shortcuts` (off main at `57da538`)

Scout groundwork: `notes-af-sststg-scout.md` (main checkout root).
Paper: `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/notes.md`
(context: `papers/Pu_2017_ArgmatSatApplyingSATSolver/notes.md`).

## Hypothesis

The SST/STG SAT path (`RangeMaximalTaskSolver`, `af_sat.py`) runs the same
range-maximal CEGAR loop on every instance, with the bounded high-range
shortcut *disabled* on large dense graphs (`_shortcut_probe_limit` returns 0
for >=160 args and >=8x density). Dvořák 2014's complexity-sensitive
dispatch — decide from a lower-complexity fragment when the instance is in
one — is unimplemented. Two sound fragment shortcuts (stable-first and
acyclic) should decide many SST rows (including dense ER/crusti rows that
currently bypass all shortcuts) with one or two NP-oracle calls instead of a
binary search + maximality loop, with zero answer changes.

## Derivations (written before implementation)

Notation: AF `F = (A, R)` (in-code: the *residual* framework after
`_prepare`/`simplify_af`). For a set `S ⊆ A`, `range(S) = S ∪ S⁺` where
`S⁺ = {b | S → b}` (Dvořák 2014 p.56, `S_R⁺`; in-code `range_of` /
`add_range_definition`, the Pu 2017 `r = x + R⁺(x)` vector).

In-code base semantics (established on the kernel before the loop):

- SST: base = complete labelling (`add_complete_labelling`), which includes
  conflict-freeness w.r.t. the `attacks` relation when present
  (`conflict_relation`, `af_sat.py:162-176`).
- STG: base = conflict-free (`add_conflict_free`), same conflict relation.
- Semi-stable extensions = complete extensions with ⊆-maximal range;
  stage extensions = conflict-free sets with ⊆-maximal range (Dvořák 2014
  p.56 Def. 3; in-code `_is_range_maximal`).

### Lemma 0 (full-range base sets are exactly the stable extensions of the encoding)

A base set `E` with `range(E) = A` means: `E` satisfies the base constraints
and every `a ∈ A \ E` is attacked (via `defeats`) by `E`. That is precisely
the in-code stable encoding `add_stable_coverage` (conflict-freeness w.r.t.
`conflict_relation` + the coverage clause `a ∈ E ∨ ∃ attacker ∈ E`, which is
literally the range variable forced true, `af_sat.py:225-251`). For
base = conflict-free this is the textbook stable definition. For
base = complete: every stable extension is complete (Dvořák 2014 p.56 recalls
`stb ⊆ sem ⊆ prf ⊆ com`), and conversely a complete extension with full range
is conflict-free and attacks all outsiders, hence stable. So for BOTH bases:

> full-range base extensions of the kernel = stable extensions.

### Derivation 1 — STABLE-FIRST (semi-stable AND stage)

**Claim.** If at least one base extension with `range = A` exists, then the
range-maximal base extensions are exactly the base extensions with
`range = A`. Consequently `sem(F) = stb(F)` (base = complete) and
`stg(F) = stb(F)` (base = conflict-free) whenever `stb(F) ≠ ∅`.

**Proof (first principles).** Let `E*` be a base extension with
`range(E*) = A`. For any base extension `E` with `range(E) ⊊ A`,
`range(E) ⊊ A = range(E*)`, so `E` is not range-maximal. And any `E` with
`range(E) = A` is trivially ⊆-maximal. ∎

Paper anchor: Dvořák 2014 p.56 (`stb(F) ⊆ sem(F)`; Def. 3: `sem`/`stg` =
maximal-range complete/conflict-free sets). The stable-first idea is the
`k=0` case of the paper's `k`-stable-consistent fragment (Def. 10 / Thm. 1,
p.59: bounded range-gap ⇒ `P^NP` procedures) and is the depth-0 probe of the
CEGARTIX `SHORTCUTS_σ` (p.61-62, shortcut depth `d`).

**Soundness of the dispatch actually implemented** (must match the existing
loop's contract, which checks range-maximality *globally*, i.e. without the
`require_in`/`require_out` query constraints — scout §1):

Let `Q` be the query constraints (`required_in`/`required_out`, where
`require_out q` = `q ∉ E`, verified at `af_sat.py:258-261`). The existing
loop returns a base extension `E` such that (`E ⊨ Q`) AND (`E` is globally
range-maximal), or `None` when no such `E` exists.

1. Probe W: full-range base extension satisfying `Q`
   (`required_range = A` + `Q`). If SAT, the witness has `range = A`, so it
   is globally range-maximal and satisfies `Q` → returning it is exactly a
   valid loop answer.
2. If W is UNSAT and `Q` is nonempty, probe G: full-range base extension
   with NO query constraints. If SAT, stable extensions exist, so by the
   Claim every globally range-maximal base extension has `range = A`; probe W
   showed none of those satisfies `Q` → the correct answer is `None`.
3. If both are UNSAT (or `Q` empty and W UNSAT — then W *is* G), no stable
   extension exists; the fragment does not apply → fall back to the
   unmodified range-maximal loop.

Task soundness: SE-SST/SE-STG use `Q = ∅`; DC uses `require_in=q` (answer =
witness exists); DS uses `require_out=q` (answer = no counterexample). All
three only depend on the loop contract preserved above.

Note the stable-first probes subsume the loop's depth-0 ("full range")
shortcut probe: after W fails, a full-range probe with the same constraints
can never succeed later (later iterations only *add* blocking constraints),
so the empty missing-set probe in `_high_range_shortcut` is removed as
redundant. Unlike the old probe, stable-first also runs in the dense-graph
regime where `_shortcut_probe_limit` is 0 — that is the intended new
behavior (Dvořák's point: fragment dispatch before the expensive loop).

### Derivation 2 — ACYCLIC (semi-stable AND stage, stage derived explicitly)

**Claim.** If `F` is acyclic (w.r.t. `defeats`) and the conflict relation
equals the defeat relation (`attacks is None or attacks == defeats`), then
the grounded extension `G` of `F` satisfies:
`com(F) = {G}`, `stb(F) = {G}`, `sem(F) = {G}`, and `stg(F) = {G}`.

**Proof (first principles + Dung 1995).** A finite acyclic AF is
well-founded (no infinite attack sequence exists because every attack path
is simple and bounded by `|A|`). By Dung 1995 (Theorem 30): a well-founded
AF has exactly one complete extension, which is grounded, preferred, and
stable. So `com(F) = {G}` and `G ∈ stb(F)`.

- Semi-stable: `sem(F) ⊆ com(F) = {G}` and `sem(F) ≠ ∅` for finite AFs
  (a maximal-range complete extension exists because `com(F) ≠ ∅` and `A` is
  finite), hence `sem(F) = {G}`.
- Stable: `stb(F) ⊆ com(F) = {G}` and `G ∈ stb(F)`, hence `stb(F) = {G}`.
- **Stage (derived separately, as required):** `G ∈ stb(F)` means `G` is
  conflict-free with `range(G) = A`. By Derivation 1's Claim applied to
  base = conflict-free, the maximal-range conflict-free sets are exactly the
  full-range ones, i.e. `stg(F) = stb(F) = {G}`. (Equivalently: for every
  conflict-free `S` with `range(S) ⊊ A`, `range(G) = A` strictly dominates
  it.) So the stage acyclic shortcut does NOT need — and does not use — the
  grounded reduct; it needs only "acyclic ⇒ grounded is stable ⇒ stage =
  stable = {grounded}". The documented counterexample against adding stage
  to `GROUNDED_REDUCT_SEMANTICS` (`preprocessing.py:83-88`: AF with a
  self-loop `(a,a)`) is *not* acyclic, so it is outside this fragment and
  untouched by this shortcut. `GROUNDED_REDUCT_SEMANTICS` is not modified.

Paper anchor: Dvořák 2014 p.57 (Table 2 / §subclasses): on acyclic AFs the
`prf`/`sem`/`stg` acceptance problems drop to polynomial time. The paper also
warns (Prop. 8-12, pp.58-59) that distance-1-from-acyclic already restores
full hardness — hence the dispatch tests exact acyclicity only.

**Gate on `attacks == defeats`:** `grounded_extension` is computed over
`defeats` only (`core/dung.py:176-186`), while the kernel's conflict-freeness
uses `attacks` when present (Modgil & Prakken convention,
`core/dung.py:41-46`). With `attacks ⊋ defeats`, `G` need not satisfy the
kernel's base constraints, so the equalities above can fail for the encoded
semantics. The shortcut therefore fires only when the conflict relation is
the defeat relation (the ICCMA AF case; `attacks is None` in all parsed
benchmark frameworks).

**Query handling.** The unique extension is `G`; with constraints `Q`:
answer `G` if `required_in ⊆ G` and `required_out ∩ G = ∅`, else `None`.
This matches the loop contract (the unique globally range-maximal extension
either satisfies `Q` or no extension does).

**Placement note (SST vs STG).** For SST, `simplify_af` already applies the
grounded reduct, so acyclic instances usually reach the finder with an empty
residual; the shortcut then fires trivially on the empty residual (which is
acyclic) and skips kernel construction. For STG, the grounded reduct is
deliberately NOT applied (stage counterexample above), so the acyclic
shortcut is the first stage-specific fragment dispatch and does real work.

## Single Variable

One theme: Dvořák-style fragment dispatch in front of the SST/STG
range-maximal loop. Two shortcuts, each justified above:

1. Acyclic dispatch in `find_semi_stable_extension` / `find_stage_extension`
   (before kernel construction), gated on `attacks is None or
   attacks == defeats`; answers from `grounded_extension(residual)`;
   trace utility names `semi_stable_acyclic_grounded` /
   `stage_acyclic_grounded`.
2. Stable-first dispatch in `RangeMaximalTaskSolver.find_extension` (after
   the base-feasibility check, before the CEGAR loop); trace utility names
   `{semi_stable,stage}_stable_first_witness` and
   `{semi_stable,stage}_stable_first_global`; the now-redundant depth-0
   full-range probe is removed from `_high_range_shortcut`
   (`*_full_range_shortcut` trace label disappears).

Out of scope (unchanged): the range encoding (already Pu 2017's `r=x+R⁺(x)`),
the binary-search seed machinery, blocking clauses, preprocessing
(`GROUNDED_REDUCT_SEMANTICS` untouched), preferred/CDAS paths, ABA.

## Fast Contracts

(to be filled after implementation)

- `uv run pytest tests/solving`
- `uv run pytest tests/interop`
- Trace-test updates preserve assertion strength (same coverage of the new
  intended sequence); differential gates
  `tests/solving/test_solver_encoding.py` (native-oracle property tests for
  sem/stg) and `tests/solving/test_solver_differential.py` unmodified.

## Metric Gate

Same-command before/after, SST subtracks only. **STG has no ICCMA 2025 bench
subtrack rows in the data root (`DEFAULT_AF_SUBTRACKS` contains no `-STG`
subtrack and no STG `.results` directories exist); STG is covered by tests
only.**

```
uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack DC-SST --only-subtrack DS-SST --only-subtrack SE-SST --backend auto --max-af-arguments 320 --timeout-seconds 15 --label af-sststg-<baseline|shortcuts>
```

Baseline label `af-sststg-baseline` run on unmodified main (57da538) before
any edit. Kill criteria: any baseline-solved row lost or answer changed;
>10% total-time regression on baseline-solved rows. Named target rows to
report individually: `ER_300_50_8` DS-SST (hard @120s in recalibration),
`ER_200_20_3` DS-SST (solved 79.6s@120s), crusti DS-SST family.

(results to be filled)

## Interpretation

(to be filled)

## Decision

(to be filled)
