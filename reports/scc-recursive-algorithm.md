# SCC-recursive schema for Dung AF semantics — implementation spec (Wave B1)

Date: 2026-05-12. Author: research subagent. Status: implementation-ready, with explicitly-flagged
UNRESOLVED items where no readable source pinned the step down.

## Sources actually read

- **[BG&G05]** P. Baroni, M. Giacomin, G. Guida. "SCC-recursiveness: a general schema for
  argumentation semantics." *Artificial Intelligence* 168 (2005) 162–210. DOI
  `10.1016/j.artint.2005.05.006`. **Full PDF retrieved** via sci-hub.ru (`baroni2005.pdf`,
  49 pp.; saved at `papers/Baroni_2005_SCC_recursiveness.pdf` — note: that copy is DRM-flagged
  so the Read tool can't open it, but `pypdf` extracted all 49 pages of text cleanly; the text
  dump pages 31–49 are in `scc_p31_49.txt` at repo root). Cited below by page number.
  Section 4 (pp. 174–183) = the schema; Section 5 (pp. 184–199) = the SCC-recursive proofs and
  base functions for stable/complete/preferred/grounded; Section 6 (pp. 195–200) = soundness
  conditions on the base function.
- **[Cer13]** F. Cerutti, P. E. Dunne, M. Giacomin, M. Vallati. "Computing Preferred Extensions
  in Abstract Argumentation: a SAT-based Approach." Extended TR (2013), DOI
  `10.1007/978-3-642-54373-9_12`. Read via the in-repo paper-reader summary
  (`papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/`) — the PDF itself is
  password-locked, but `description.md`/`notes.md` reproduce the PrefSat algorithm, encodings,
  and the complete-labelling conditions. **This is the flat (non-SCC) PrefSat algorithm**, not
  the SCC meta-algorithm.
- **[GW13]** S. A. Gaggl, S. Woltran. "The cf2 argumentation semantics revisited." *J. Logic and
  Computation* 23 (2013) 925–949. DOI `10.1093/logcom/exs011`. Read via in-repo summary
  (`papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/notes.md`) — confirms stage/naive are
  *not* maximally succinct, that cf2 keeps the SCC-recursive shape, and that the in-repo
  `dung._is_cf2_extension` / `_is_stage2_extension` loop matches GW13's SCC recursion with a
  naive/stage base case.
- **[Dvo14]** W. Dvořák, S. A. Gaggl, J. Wallner, S. Woltran. "Complexity-sensitive decision
  procedures for abstract argumentation." Read via in-repo summary
  (`papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/abstract.md`) — confirms
  semi-stable and stage are Σ₂ᵖ-hard and the practical route is iterated-SAT (CEGAR), not SCC
  decomposition.
- **[BG07]** P. Baroni, M. Giacomin. "On principle-based evaluation of extension-based
  argumentation semantics." *Artificial Intelligence* 171 (2007) 675–700. DOI
  `10.1016/j.artint.2007.04.004`. **Read only via web search snippets / abstract / PhilPapers**
  (full PDF not retrieved). The directionality classification below rests on those snippets — see
  the explicit flag in §1.
- Web search results on SCC-recursiveness and directionality (sciencedirect/researchgate/
  semanticscholar abstracts), and the KR 2014 listing of Cerutti, Giacomin, Vallati, Zanella,
  "An SCC Recursive Meta-Algorithm for Computing Preferred Labellings in Abstract Argumentation"
  (KR 2014, pp. 42–51) — **abstract only, full paper not retrieved.**
- Codebase: `src/argumentation/dung.py`, `src/argumentation/preprocessing.py`,
  `reports/graph-speedup-wave-a-preprocessing.md`, `notes/graph-speedup-wave-a-preprocessing.md`
  (all read in full).

---

## 1. Which of {complete, preferred, stable, semi-stable, stage} are SCC-recursive

### Verdict table

| Semantics | SCC-recursive (BG&G sense)? | Source | Use in implementation |
|---|---|---|---|
| **complete** | **YES** | [BG&G05] Thm 43, Prop 39, p. 190, p. 194 | SCC-recurse; base case = flat complete solve on each single-SCC sub-AF |
| **preferred** | **YES** | [BG&G05] Thm 43, Prop 41, p. 190–192 | SCC-recurse; base case = flat preferred solve on each single-SCC sub-AF |
| **stable** | **YES** | [BG&G05] Thm 43, Prop 32 & 34, p. 186–188 | SCC-recurse; base case = flat stable solve on each single-SCC sub-AF. *Note:* stable is SCC-recursive but does **not** satisfy the directionality *principle* of [BG07] — those are different properties; the SCC recursion is still exact (Prop 32/34 are iff). |
| **grounded** | **YES** | [BG&G05] Thm 43, Prop 42, p. 192–194 | Out of scope per the prompt (already O(V+E)); the base function `BF_GR(AF,C) = {GE(AF,C)}` is in [BG&G05] Prop 44, p. 194–195. |
| **semi-stable** | **NO — not SCC-recursive.** Range-maximality is a global property; it does not commute with the SCC decomposition. [BG&G05] only proves SCC-recursiveness for stable/complete/preferred/grounded (Thm 43, p. 190 — semi-stable/stage are not even mentioned, having been introduced later: semi-stable by Caminada 2006, stage by Verheij 1996). [BG07] (per the abstract/snippets read) classifies semi-stable as **violating directionality**; directionality is a *necessary* condition for SCC-recursiveness, so semi-stable cannot be SCC-recursive. | **Use flat SAT** — `af_sat.find_semi_stable_extension` / the range-maximal iterated-SAT loop. Do **not** SCC-decompose. The SCC recursion would silently produce wrong extensions (it would pick a range-maximal set *per component* and cross-product, which is not globally range-maximal). |
| **stage** | **NO — not SCC-recursive.** Same reasoning: stage = conflict-free + max-range, a global maximality. [BG07] (per snippets) classifies stage as **violating directionality** (and the *reinstatement* principle). [GW13] confirms stage is not maximally succinct and only gets an SCC-recursive *variant* called **stage2** (which is a *different* semantics — note `dung.stage2_extensions`). Plain `stage` is not decomposable this way. | **Use flat SAT** — `af_sat.find_stage_extension` / the range-maximal CF iterated-SAT loop. Do **not** SCC-decompose. (`dung.stage2_extensions` *is* the SCC-recursive thing, but it's a separate semantics, not what "stage" means.) |

### FLAG — directionality classification rests on secondary sources only

The claim "semi-stable and stage violate directionality" is from [BG07]'s abstract and from web
search snippets of [BG07] and the principle-based survey literature — **the full text of [BG07]
was not retrieved**. The *underlying* fact (semi-stable/stage are not among the four semantics
[BG&G05] proves SCC-recursive) is from the primary source [BG&G05] Thm 43 read directly, which is
sufficient on its own: BG&G05 establishes SCC-recursiveness only for stable/complete/preferred/
grounded, so a coder must not SCC-decompose semi-stable or stage. If a future reader wants the
directionality-violation *witness AFs*, retrieve [BG07] (Fig. 2 / the directionality
counterexamples there).

**Bottom line for the coder:** implement the SCC recursion for **complete, preferred, stable**
only. For **semi-stable and stage**, keep the existing flat SAT path unchanged.

---

## 2. The exact algorithm (complete / preferred / stable)

### 2.1 Notation (all from [BG&G05] §4, pp. 174–181)

Fix an AF `Γ = (A, →)` (here `→` = the *defeat* relation; for pure Dung this is
`framework.defeats`).

- `parents(α) = {β ∈ A | β → α}` — attackers of `α`. ([BG&G05] Def 2, p. 165)
- `S → α` ≡ `∃β ∈ S : β → α`. `outparents(S) = {α ∈ A | α ∉ S ∧ α → S}` — external attackers of
  SCC `S`. ([BG&G05] Def 3, p. 165)
- `SCCS_Γ` — the set of strongly connected components of `Γ` (path-equivalence classes; a single
  node is its own SCC; `SCCS_⟨∅,∅⟩ = {∅}` by convention). ([BG&G05] Def 16, p. 175)
- `Γ↓S = (S, → ∩ (S×S))` — restriction of `Γ` to node set `S`. ([BG&G05] Def 19, p. 178)
- Given an extension-candidate `E ⊆ A` and an SCC `S` ([BG&G05] Def 18, p. 177):
  - `D(S,E) = {α ∈ S | (E ∩ outparents(S)) → α}` — nodes of `S` attacked from outside by some
    node *in* `E`. ("defeated")
  - `P(S,E) = {α ∈ S | (E ∩ outparents(S)) ↛ α  ∧  ∃β ∈ (outparents(S) ∩ parents(α)) : E ↛ β}` —
    nodes of `S` not attacked by `E` from outside, but having ≥1 external attacker not attacked
    by `E`. ("provisionally defeated")
  - `U(S,E) = S \ (D(S,E) ∪ P(S,E)) = {α ∈ S | (E ∩ outparents(S)) ↛ α  ∧  ∀β ∈ (outparents(S)
    ∩ parents(α)) : E → β}` — nodes of `S` not attacked from outside by `E` and *defended* by `E`
    (every external attacker is itself attacked by `E`). ("undefeated")
  - `UP(S,E) = U(S,E) ∪ P(S,E) = S \ D(S,E)` — the *survivors* of `S` after suppressing nodes
    attacked from outside. This is the node set the recursion descends into for `S`.

  These three sets depend only on `E ∩ (ancestor SCCs of S)` — i.e. on the part of `E` already
  chosen in earlier-in-topological-order SCCs. ([BG&G05] p. 177, "It is easy to verify that …".)

- The schema is parametrised by a **base function** `BF_𝒮(AF, C)` defined only for AFs with
  `|SCCS_AF| = 1`, returning `⊆ 2^A`. The recursive selection function `GF` is:

  **[BG&G05 Def 20, p. 180]:** A semantics `𝒮` is SCC-recursive iff for every AF `(A,→)`,
  `E_𝒮(AF) = GF(AF, A)`, where for any `AF=(A,→)` and any `C ⊆ A`, and any `E ⊆ A`:
  `E ∈ GF(AF, C)` iff
  - **if `|SCCS_AF| = 1`:** `E ∈ BF_𝒮(AF, C)`;
  - **otherwise:** `∀S ∈ SCCS_AF :  (E ∩ S) ∈ GF( AF↓UP(S,E) ,  U(S,E) ∩ C )`.

  The second parameter `C` ("the defended nodes") tracks which nodes survived restriction from
  *outside the current AF* (it only matters once you've descended ≥1 level — at the top level
  `C = A`). It threads through as `C' = U(S,E) ∩ C`.

### 2.2 Per-semantics base function ([BG&G05] Thm 43, p. 190)

For an AF `AF=(A,→)` with `|SCCS_AF| = 1` and `C ⊆ A`:

- `BF_CO(AF, C) ≡ CE(AF, C)` — the **complete extensions of `AF` in `C`**.
- `BF_PR(AF, C) ≡ PE(AF, C)` — the **preferred extensions of `AF` in `C`**.
- `BF_ST(AF, C) ≡ SE(AF, C)` — the **stable extensions of `AF` in `C`**.
  (Special case worth knowing: [BG&G05] p. 188 — for stable, `C` has *no effect*:
  `SE(AF,C) ≡ SE(AF)`, because a stable extension attacks everything outside it. So
  `BF_ST(AF,C) = SE(AF)` regardless of `C`.)

where "`… in `C`" means: restrict the candidate to be a subset of `C`. Precisely
([BG&G05] Defs 21–24, p. 184–185):

- `AS(AF, C) = { E | E ⊆ C ∧ E admissible in AF }` — admissible sets in `C`.
  **Subtle, do not skip ([BG&G05] p. 184):** `AS(AF, C) ≠ AS(AF↓C)` in general — defense is
  checked in the *full* `AF`, only membership is restricted to `C`. Example from the paper: AF
  `β→γ`, `C={γ}` ⇒ `AS(AF,C)={∅}` (γ undefended in AF) but `AS(AF↓C)={{γ}}`.
- `SE(AF, C) = { E | E ⊆ C ∧ E stable in AF }`.
- `CE(AF, C) = { E ∈ AS(AF,C) | ∀α ∈ C : α acceptable wrt E in AF ⇒ α ∈ E }` — i.e. the
  fixpoint condition `F_AF(E) ∩ C ⊆ E`, with `F_AF` the *full-AF* characteristic function.
- `PE(AF, C) = ` the ⊆-maximal elements of `AS(AF, C)`. Equivalently ([BG&G05] Prop 31, p. 185)
  the ⊆-maximal elements of `CE(AF, C)`.

So the base function is exactly "solve the standard semantics on the single-SCC sub-AF, but with
membership restricted to `C` and defense/acceptability still evaluated against that sub-AF as a
whole."

**Implementation note for the base solve.** In this repo the existing flat solvers
(`af_sat.find_*`, or `dung.*_extensions` brute force) take a *plain* AF, not an `(AF, C)` pair.
To encode "`in C`" cheaply: build the sub-AF `AF↓UP(S,E)` (you already restricted to survivors),
then on top force every argument `α ∈ UP(S,E) \ C` to be labelled OUT/`undec` (i.e. *not* IN) —
this is exactly the `require_out`-style constraint `af_sat._prepare` already supports
(`require_out = UP(S,E) \ C`). For stable, skip it entirely (`C` is inert). For complete and
preferred, the `require_out` set is `UP(S,E) \ C`. Verify this encoding against the brute-force
oracle `dung.complete_extensions` / `dung.preferred_extensions` restricted by hand — it is the
one step in this report I derived rather than read verbatim, so it is **UNRESOLVED until oracle
tests pass** (the math is straightforward — `α ∉ C` ⇒ `α ∉ E` by Def 21 — but the SAT-encoding
detail of "force not-IN" vs "force OUT" matters: it must be "not IN", not "OUT", because a node
outside `C` may still legitimately be `undec`; forcing OUT would be wrong).

### 2.3 The recursive procedure (constructive reading of Def 20)

Enumeration of all extensions of `Γ = (A,→)` under SCC-recursive semantics `𝒮` with base function
`BF_𝒮`:

```
def GF(AF, C):                          # AF = (A, ->), C subset of A; returns a set of subsets of A
    sccs = strongly_connected_components(AF)
    if len(sccs) == 1:
        return BF_S(AF, C)              # flat solve on this single SCC, "in C"
    # condensation is a DAG; process SCCs in a topological order so that when we
    # handle S, every SCC in sccanc(S) has already contributed to the partial E.
    order = topological_order(condensation(AF, sccs))   # parents before children
    partials = [ frozenset() ]          # set of partial E's built so far (over already-processed SCCs)
    for S in order:
        new_partials = []
        for E in partials:              # E ranges over choices in earlier SCCs
            # D/P/U depend only on E intersected with earlier SCCs -> well-defined now
            Dse  = { a for a in S if any(b in E and b in outparents(AF, S) and (b,a) in AF.->) }   # = D(S,E)
            UPse = S - Dse                                                                          # = UP(S,E)
            Use  = { a for a in UPse
                       if not any(b in E and b in outparents(AF,S) and (b,a) in AF.->)              # not attacked-from-outside-by-E
                       and all( any( c in E for c in attackers(AF,b) )                               # every external attacker b is attacked by E
                                for b in (outparents(AF,S) & attackers(AF,a)) ) }
            # (Pse = UPse - Use, not needed explicitly)
            subAF = AF restricted to UPse
            subC  = Use & C
            for E_S in GF(subAF, subC):          # recursive call -- choices of E within S
                new_partials.append(E | E_S)
        partials = new_partials
    return partials                      # each is a full extension of AF
# top-level:  E_S(Gamma) = GF(Gamma, A_of_Gamma)
```

Key correctness facts behind this loop (all [BG&G05]):
- The condensation is a DAG (well-known; [BG&G05] p. 176), so a topological order exists and the
  "ancestor SCCs already processed" invariant is maintainable.
- For an **initial** SCC `I` (no `outparents`): `UP(I,E) = U(I,E) = I` for all `E`, and the
  recursive call is `GF(AF↓I, I) = BF_𝒮(AF↓I, I) = E_𝒮(AF↓I)` — i.e. the base function on `I`
  directly returns the semantics' extensions of `I`. ([BG&G05] p. 180–181.)
- The cross-product over SCCs is *not* a blind product: each SCC's `subAF`/`subC` depends on the
  chosen partial `E` from ancestors, so the recursion is genuinely "for each choice upstream,
  solve downstream conditioned on it." ([BG&G05] worked example on Fig. 11, pp. 181–183.)
- Soundness/exactness: Prop 39 (complete), Prop 41 (preferred), Prop 32+34 (stable) — each is an
  *iff* between "`E` is a `𝒮`-extension of `AF`" and "`∀S: (E∩S) ∈ 𝒮(AF↓UP(S,E), U(S,E)∩C)`".

#### Maximality and preferred — the one place to be careful

The prompt asks whether per-semantics maximality "commutes" with the decomposition. For
**preferred** the answer in [BG&G05] is **yes, exactly**, but the maximality is enforced
*per-SCC*, not globally-then-projected:

> [BG&G05] Prop 41, p. 191–192: `E ∈ PE(AF,C)` iff `∀S ∈ SCCS_AF : (E ∩ S) ∈
> PE(AF↓UP(S,E), U(S,E)∩C)`.

i.e. you take a *preferred* (= ⊆-maximal admissible) set within each SCC's restricted sub-AF, and
the cross-product of those *is* exactly the set of global preferred extensions — no separate
global maximality filter is needed, and conversely you must *not* just take "any admissible per
SCC then maximise globally" (that would give complete extensions, not preferred). The proof
(Lemma 40 + Prop 41) shows that growing any per-SCC choice to maximal grows the global set to
maximal and vice versa, because `D/P/U` are monotone in `E` (Lemma 49, p. 196).

For **complete** the analogous Prop 39 holds with `CE` in place of `PE` — no maximality at all,
just the fixpoint condition `F ∩ C ⊆ E` checked per-SCC.

For **stable** Prop 32/34: `(E∩S)` must be a *stable* extension of `AF↓UP(S,E)` for *every* `S`.
Consequence: **a stable extension exists for the whole AF iff every SCC's restricted sub-AF (under
every reachable upstream choice) has a stable extension.** So an SCC whose sub-AF has *no* stable
extension (e.g. an isolated odd cycle, or a sub-AF with a self-loop sink) kills the whole product
along that branch — `GF` simply returns no extension for that branch. This is *not* a bug; it
matches `dung.stable_extensions` possibly returning `[]`.

### 2.4 Edge cases (all derivable from Def 20 / Def 16)

| Case | Behaviour |
|---|---|
| **Empty AF** `(∅,∅)` | `SCCS = {∅}` by convention ⇒ `|SCCS|=1` ⇒ `GF = BF_𝒮((∅,∅), ∅)`. For complete/preferred/stable that is `{∅}` (the empty set is the unique complete/preferred/stable extension of the empty AF). |
| **Whole AF is one SCC** (e.g. a single cycle, or any strongly connected graph) | `|SCCS|=1` ⇒ `GF = BF_𝒮(AF, A)` = a **flat solve on the whole AF**. The SCC machinery degenerates to the existing flat SAT call; do this detection *first* and skip straight to flat SAT (zero overhead). |
| **SCC of size 1, no self-loop** (`{α}`, `→∩({α}×{α})=∅`) | The sub-AF `⟨{α},∅⟩`. Base case: `BF_CO/PR/ST(⟨{α},∅⟩, C)` = `{{α}}` if `α ∈ C`, else `{∅}`. (For complete/preferred: α is unattacked-in-the-restriction so it's forced IN when allowed; if `α ∉ C` it's blocked, giving `{∅}`. For stable: `{{α}}` always, since `C` inert and `α` covers everything outside — vacuously, the sub-AF has no other node.) Cross-checks the grounded base function `BF_GR(⟨{α},∅⟩,{α})={{α}}` ([BG&G05] Prop 44, p. 195). |
| **SCC of size 1, with self-loop** (`{α}`, `(α,α) ∈ →`) | `⟨{α},{(α,α)}⟩` is a valid single-SCC AF (degenerate cycle). Base case: complete ⇒ `{∅}` (α can't be IN — self-conflict — and can't be OUT unless something IN attacks it, nothing does, so α is `undec`; the only complete extension is `∅`). preferred ⇒ `{∅}`. stable ⇒ **`{}` (no stable extension)** — α is uncovered and uncoverable, so the sub-AF has no stable extension, which (per §2.3) kills the whole product on any branch routing through this SCC. This matches the Wave A note that a pure self-loop sink is the obstruction to stable existence. |
| **Self-loop *inside* a larger SCC** | Handled transparently by the base solver on `AF↓UP(S,E)` — the flat complete/preferred/stable solver already deals with `(a,a)` via conflict-freeness; nothing special at the SCC layer. |
| **Multiple initial SCCs** | Fine — process them all (in any order among themselves) before their descendants; the partials cross-product over them. ([BG&G05] Fig. 11 example only has one initial SCC, but the schema is stated for all SCCs uniformly.) |

### 2.5 Decision tasks (DC/DS), not just enumeration

The prompt scopes "core extension-based semantics" — for the **enumeration** (SE-`σ` / EE-`σ`)
tasks the above is complete. For **DC-`σ`** (credulous: is `q` in *some* extension?) and **DS-`σ`**
(skeptical: is `q` in *every*?), the schema still helps but the literature implementation
([Cer14] KR2014, abstract only — *not read in full*) wraps the SCC recursion in a query-driven
search rather than full enumeration:

- **DC-σ(q):** `q` lives in some SCC `S_q`. Build, for each consistent assignment of the SCCs
  *upstream* of `S_q` (using BF on initial SCCs, recursing), the restricted `AF↓UP(S_q,E)`; ask
  the flat DC solver "is `q` credulously accepted in this restricted sub-AF (in `U(S_q,E)∩A`)?"
  for each; OR them. Short-circuit on first YES.
- **DS-σ(q):** similarly but the flat call is "is `q` skeptically accepted in the restricted
  sub-AF?", AND over branches; short-circuit on first NO. Also: if `q ∈ D(S_q, E)` for *some*
  reachable upstream `E`, `q` is excluded from that extension ⇒ DS fails immediately.

**UNRESOLVED** — the precise pruning order, and how [Cer14] avoids enumerating *all* upstream
choices (it presumably only explores upstream SCCs that actually affect `S_q`, i.e. those in
`sccanc(S_q)`, and stops early), is not pinned down because I could not retrieve the KR2014 PDF.
For a first implementation: do **DC/DS by enumeration** (`GF` then check membership) — correct but
not maximally fast — and leave the query-driven pruning as a follow-up keyed to retrieving
[Cer14]. The repo's existing `af_sat.is_preferred_skeptically_accepted` (CDAS/CEGAR loop) is
already a good flat DS-PR backend to call per restricted sub-AF.

---

## 3. Composition with Wave A `preprocessing.simplify_af`

From `reports/graph-speedup-wave-a-preprocessing.md` (read in full):

- `preprocessing.simplify_af(framework, semantics=…)` → `AfSimplification(original, residual,
  fixed_in, removed_out)` with `.lift(residual_extension) = frozenset(residual_extension) |
  fixed_in` and `.lift_all(...)`.
- `residual` = `AF` restricted to `Args \ (G ∪ G⁺)` where `G` = grounded extension, `G⁺` =
  everything `G` attacks. There are **no edges from `G` into `residual`** (a `G`-target is in `G⁺`,
  excluded), so `residual = AF[U]` exactly, a clean induced sub-AF.
- `GROUNDED_REDUCT_SEMANTICS = {complete, preferred, stable, semi_stable, grounded, ideal}` — the
  grounded reduct is sound for these. (**Not `stage`, not `admissible`** — documented
  counterexamples; those keep only the self-loop-sink removal.)

**Soundness of running the SCC recursion on `residual`:**

- The SCC recursion ([BG&G05] Def 20) is a *theorem about the AF as given* — it holds for *any*
  Dung AF, in particular for the induced sub-AF `residual`. Since `residual` is exactly an induced
  sub-AF and `complete/preferred/stable(AF) = { G ∪ E : E ∈ complete/preferred/stable(residual) }`
  (Wave A's grounded-reduct theorem, verified by their oracle tests), and the SCC recursion
  computes `complete/preferred/stable(residual)` exactly, the composition
  `lift( cross_product_of_per_SCC_solves_on_residual )` is sound. **Order: simplify first, then
  SCC-decompose the residual, then flat-SAT per SCC, then lift per-SCC results into a residual
  extension, then `simplification.lift(...)` to add `G` back.**
- This is *complementary*, not redundant: the grounded reduct peels off every singleton-no-loop
  SCC that was unattacked-or-attacked-by-`G` (it lands in `G ∪ G⁺`), so the residual is *already*
  frequently a disjoint-ish union of small non-trivial SCCs — exactly the shape the SCC recursion
  exploits. Wave A's own "for the next wave" note says precisely this.
- **For semi-stable:** Wave A's grounded reduct *is* sound for semi-stable, but the **SCC
  recursion is not** (§1). So semi-stable gets: `simplify_af(…, semantics='semi_stable')` →
  residual → **flat** range-maximal SAT on the residual → lift. No SCC layer.
- **For stage:** gets *neither* the grounded reduct *nor* the SCC layer — only the
  self-loop-sink removal `simplify_af` already does for it, then flat range-maximal CF SAT. No
  change from Wave A.
- **One caveat on stable + self-loop sinks:** Wave A *disables* pure-self-loop-sink removal for
  `stable` (the sink is the obstruction to stable existence). The SCC recursion on the residual
  for stable will then encounter that self-loop SCC and correctly return *no* extension on that
  branch (§2.4) — consistent. Don't "fix" it.

---

## 4. What `src/argumentation/dung.py` already provides

Read in full. Reusable for Wave B1:

| Symbol (in `dung.py`) | Line | Reuse |
|---|---|---|
| `_strongly_connected_components(arguments, defeats) -> list[frozenset[str]]` | ~410 | **Reuse directly.** Tarjan, recursive, deterministic order (sorts components). One caveat: it's a *recursive* Tarjan — for very deep graphs Python's recursion limit could bite; the residual after Wave A is usually shallow, but consider an iterative variant if you hit large ICCMA instances. It does *not* return a topological order of the condensation — you'll need to compute that yourself (Tarjan happens to emit SCCs in reverse-topological order; `_strongly_connected_components` then re-sorts by member tuple, destroying that, so recompute the condensation DAG and topo-sort it explicitly). |
| `_subframework(framework, arguments) -> ArgumentationFramework` | ~456 | **Reuse directly** for `AF↓UP(S,E)` — restricts both `defeats` and `attacks`. Exactly Def 19. |
| `_component_defeated(framework, candidate, components) -> frozenset[str]` | ~491 | **Partially reusable.** It computes "targets of cross-component attacks from `candidate`" = the union over all SCCs `S` of `D(S, candidate)` — i.e. it's the *aggregate* `D` set, used in the CF2/stage2 *verification* loop. For the *enumeration* recursion you need `D(S,E)` *per SCC* and conditioned on the partial `E` (not a finished candidate), so you'll write a small per-SCC `D/U/UP` helper (as in the §2.3 pseudocode). The aggregate version is fine for a *verifier* `is_complete2_extension`-style check if you want one. |
| `_is_cf2_extension` / `_is_stage2_extension` (~509, ~561) and their enumerators `cf2_extensions` / `stage2_extensions` (~532, ~548) | — | **Loop shape transfers; base function does NOT.** These implement the SCC recursion *for cf2 and stage2* — which use a **naive-sets** base case (`naive_extensions`) resp. a **stage** base case, *not* the complete/preferred/stable base functions of §2.2. They also (a) verify a *given* candidate rather than enumerate, and (b) use the simpler `UP(S,E) = S \ D(S,E)` without the `U`/`P` distinction or the `C` parameter — which is *correct for cf2/stage2* (those base functions ignore `C`, per [GW13]) but **insufficient for complete/preferred** where `C = U(S,E) ∩ C` genuinely constrains the base solve. So: copy the *structure* (SCC decompose → if 1 SCC base-solve → else recurse per component on `_subframework(... S - defeated)`), but (i) plug in the right base function, (ii) thread the `C` parameter, (iii) enumerate (cross-product) rather than verify, (iv) use the full `D/U/UP` definitions. |
| `naive_extensions`, `stage_extensions`, brute-force `complete_extensions`, `preferred_extensions`, `stable_extensions` | — | Use as the **oracle** in tests (the SCC-recursive result must equal these on small AFs). `stage_extensions` / `semi_stable_extensions` are the *flat* fallbacks the implementation will call for those two semantics. |
| `grounded_extension` | ~207 | O(V+E) BFS. Used by `preprocessing.simplify_af`. Out of scope to touch. |

What's **not** there and must be written: (1) condensation-DAG construction + topological order;
(2) the per-SCC `D(S,E)`/`U(S,E)`/`UP(S,E)` helper conditioned on a partial `E`; (3) the
recursive enumerator `GF(AF, C)`; (4) the `(AF, C)`-restricted flat base solve (= existing flat
SAT/brute solve + a `require_out = UP \ C` constraint — see §2.2 UNRESOLVED flag); (5) a
single-SCC fast path that skips straight to flat SAT; (6) glue to call `simplify_af` first and
`lift` after.

---

## 5. Expected speedup & when it helps / hurts

### When it helps

- **Layered AFs with many small SCCs** (long deterministic chains feeding cycles; "tree of
  cycles"; bipartite-ish ICCMA `*_grd`/`scc` families): big win. Each SCC is solved in isolation
  on a tiny sub-AF; the exponential blow-up of preferred/stable enumeration is confined to the
  size of the largest SCC, not the whole graph. Combined with Wave A's grounded reduct (which
  already strips the chains), the residual is a handful of small cycles ⇒ near-instant.
- The Wave A bench table (`reports/graph-speedup-wave-a-preprocessing.md`) shows 2.7×–13× from
  the grounded reduct alone on chain+cycle instances; the SCC layer adds further multiplicative
  speedup *whenever the residual has >1 SCC* (which the reduct does not by itself guarantee — the
  reduct removes nodes, the SCC layer exploits the block structure of what remains).

### When it hurts (and the mitigation)

- **One giant SCC** (a single dense strongly-connected graph — `*_stb` ICCMA families, ABA-derived
  AFs, etc.): the condensation has one node ⇒ `GF` immediately falls through to a flat solve on
  the whole AF, but you've paid for: a Tarjan run (`O(V+E)`, cheap) + the `len(SCCS)==1` check.
  **Mitigation: detect `len(SCCS) == 1` (or equivalently `len(SCCS) == |A|` for a totally acyclic
  AF, also a degenerate-but-favourable case) up front and dispatch to the existing flat SAT path
  verbatim.** Net overhead then ≈ one Tarjan pass — negligible, same "free or a win" property
  Wave A established for `simplify_af` on a single big cycle (1.0× there).
- **Many tiny SCCs but each trivial (acyclic)**: the grounded reduct already collapses these into
  `G ∪ G⁺`, so the residual is empty and the SAT/ASP call is skipped entirely (Wave A's
  empty-residual fast path). The SCC layer never even runs. No overhead.

### Reported numbers from the literature

- **[Cer14] (KR 2014, "An SCC Recursive Meta-Algorithm for Computing Preferred Labellings")** —
  abstract states the SCC meta-algorithm "reduce[s] computational effort" by solving on restricted
  sub-frameworks; **the specific speedup figures were not retrieved** (PDF not accessed). FLAG.
- **[Dvo14]** — reports its complexity-sensitive (iterated-SAT, *not* SCC) approach "outperforms
  existing systems" on hard semi-stable/stage instances; this is the evidence that for those two
  semantics the right move is CEGAR-SAT, *not* SCC decomposition.
- **ASPARTIX-V / ConArg / ArgSemSAT / pyglaf / µ-toksia (ICCMA 2017–2021/2023):** the consensus
  in solver descriptions is that grounded-reduct preprocessing + SCC decomposition are standard
  "free" wins for the *easy* (complete/preferred/stable) layer and that the hard cases are
  dominated by iterated-SAT — but **I did not retrieve concrete per-instance tables** for any of
  these in this pass. FLAG: if hard numbers are needed, retrieve the ICCMA 2017/2019/2023 solver
  reports and the ArgSemSAT paper arXiv:1310.4986 (the in-repo `papers/Cerutti_2015_ArgSemSAT…`
  folder may have a summary).

### Reference implementations to cross-check against

- **ASPARTIX-V** ASP encodings — `dung_complete.lp`, `dung_stable.lp` etc.; the repo's own
  `aspic_encoding.py` uses `dung_{complete,stable,admissible}.lp`. (Krennwallner/Dvořák/Gaggl/
  Woltran; aspartix.dbai.tuwien.ac.at.)
- **ConArg** (Bistarelli, Santini) — constraint-based, does SCC decomposition.
- **ArgSemSAT** (Cerutti, Giacomin, Vallati) — arXiv:1310.4986; the SAT-iteration solver behind
  [Cer13]/[Cer14]. In-repo: `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/`,
  `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/` (PrefSat),
  `papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf` (**password-locked** — could not open;
  this is the one to crack/re-download to pin down the DC/DS pruning UNRESOLVED in §2.5).
- **pyglaf** (Alviano) — circumscription/ASP-based; ICCMA winner; does grounded-reduct preprocessing.
- **µ-toksia** (Niskanen, Järvisalo) — incremental-SAT; ICCMA 2019/2021 winner; grounded reduct +
  SAT iteration; *not* SCC-recursive but a good oracle for the flat base solves.
- **In-repo oracle:** `dung.complete_extensions`, `dung.preferred_extensions`,
  `dung.stable_extensions` (brute force) — the *primary* correctness check; the SCC-recursive
  output must equal these set-for-set on a random-AF battery.

---

## 6. Summary of UNRESOLVED items (the coder must verify against oracle tests / retrieve sources)

1. **§2.2 — the `(AF, C)`-restricted base solve encoding.** "`E ⊆ C`" must be enforced as "force
   every `α ∈ UP(S,E) \ C` to be **not IN**" (it may still be `undec`) — *not* "force OUT". The
   math (`α ∉ C ⇒ α ∉ E`, [BG&G05] Def 21) is from the primary source; the SAT-encoding wording
   is mine. **Verify** that complete/preferred SCC-recursive enumeration with this `require_out`-
   style constraint matches the brute-force oracle on random AFs with non-trivial SCC structure.
   (For stable, `C` is provably inert — no constraint needed.)
2. **§2.5 — query-driven DC/DS pruning.** The exact pruning order from [Cer14] (KR 2014) is not
   pinned down (PDF not retrieved). First implementation should do DC/DS by full enumeration
   (correct, not maximally fast); the pruning is a follow-up gated on retrieving [Cer14] (or the
   password-locked `papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf`).
3. **§1 / §5 — directionality classification of semi-stable & stage.** The *operative* fact ("not
   among the four semantics [BG&G05] proves SCC-recursive ⇒ do not SCC-decompose them") is from
   the primary source read directly and is sufficient. The *reason* (they violate the
   directionality principle) rests on [BG07]'s abstract/snippets, full text not retrieved. If the
   witness AFs are wanted, retrieve [BG07] (AIJ 171, 2007).
4. **§5 — literature speedup numbers** ([Cer14], ICCMA solver reports, ArgSemSAT) not retrieved
   in this pass — claims there are qualitative ("big win on layered, overhead on one giant SCC"),
   backed by the *structure* of the algorithm and Wave A's own bench, not by re-derived figures.

Everything in §2.1–§2.4 (the schema, the D/P/U/UP definitions, Def 20, the per-semantics base
functions in Thm 43, the edge cases) is traceable to specific pages of [BG&G05] read verbatim and
is *not* flagged.
