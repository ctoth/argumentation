---
title: "Declarative Algorithms and Complexity Results for Assumption-Based Argumentation"
authors: "Tuomo Lehtonen, Johannes P. Wallner, Matti Järvisalo"
year: 2021
venue: "Journal of Artificial Intelligence Research (JAIR) 71, 265-318"
doi_url: "https://doi.org/10.1613/jair.1.12479"
pages: 54
---

# Declarative Algorithms and Complexity Results for Assumption-Based Argumentation

## One-Sentence Summary
This paper gives **ASPforABA** — the ICCMA-2023-ABA-track-winning solver — its foundation: a *direct* declarative approach that reasons at the **assumption level via forward-derivability** and encodes ABA (and ABA+) reasoning tasks straight into **answer set programming**, avoiding both specialized dispute-derivation algorithms and translation to abstract AFs, together with new ABA+ complexity results showing preferences raise the complexity of several semantics. *(abstract, Sec 4, Sec 3)*

## Why this is the ASPforABA paper
The implementation described and evaluated here is available at **https://bitbucket.org/coreo-group/aspforaba** (Sec 5.2 / Sec 1). ASPforABA is the ICCMA 2023 ABA-track winner (first across all evaluated ABA problems, ahead of ACBAR). This JAIR article is the extended version of the AAAI 2019 paper (Lehtonen, Wallner, Järvisalo), adding ideal semantics for ABA, `<-grounded` for ABA+, a **corrected** grounded encoding (the AAAI 2019 grounded encoding was erroneous — Remark 1 / Appendix B), full complexity proofs, and a broader evaluation.

## Problem Addressed
Reasoning in structured argumentation (ABA) is harder to implement well than abstract AF reasoning. Prior systems either (a) run **specialized algorithms** — dispute derivations (ABAGRAPH) for credulous admissible/grounded/ideal, or (b) **translate ABA→AF** (ABA2AF, ABAPLUS) and call an AF solver. Both can blow up: an ABA framework can induce exponentially many arguments, so materializing the AF is not polynomially bounded. The paper wants a single, uniform, competitive engine covering admissible, complete, preferred, stable, grounded, ideal (ABA) and `<-stable`, `<-grounded` (ABA+), across credulous/skeptical acceptance and enumeration — while staying within the natural complexity class of each task. *(Sec 1)*

## ABA background (Sec 2) — what you need
- **ABA framework** `F = (L, R, A, ⁻)`: language `L` (atoms), inference rules `R` of form `a0 ← a1,…,an`, assumptions `A ⊆ L`, and a contrary map `⁻ : A → L`. This work uses the **flat LP fragment**: `L` atomic, all finite, no rule head is an assumption. *(Def 1, Assumption 1)*
- **Forward-derivability** `X ⊢ s`: `s` derivable from assumption set `X` by forward chaining of rules. The paper deliberately uses forward-derivability (not tree-derivability) because it maps cleanly to ASP support rules. For ABA (no preferences) the two coincide; for ABA+ they coincide only under specific semantics (which is what makes the ABA+ encodings possible). *(Sec 2)*
- **Attacks at the assumption level**: an assumption set attacks assumption `b` if it derives the contrary `b̄`. Semantics (cf/adm/com/prf/stb/grd/ideal) are defined as conditions on **assumption sets**, not arguments. *(Sec 2)*
- **ABA+** adds a preference order `≤` over assumptions; preferences turn some attacks into **reverse attacks** (a less-preferred attacker's attack is reversed). `<-stable`, `<-grounded` are the studied semantics. *(Sec 2)*

## The ASP approach (Sec 4) — the core of the solver
General shape: `A` is a σ-assumption set of `F` iff there is an answer set `M` of `σ ∘ ABA(F)` with `A = {a | in(a) ∈ M}`, where `σ` is the ASP module for the semantics and `ABA(F)` encodes the framework. Ideal and ABA+ `<-grounded` are the exceptions — they use an ASP solver as a subprocedure inside a larger algorithm. *(Sec 4.2)*

### Framework + query representation (Sec 4.2.1)
`ABA(F)` = facts `assumption(a).`, `head(i,b).`, `body(i,b).` (rule index `i` links head/body), `contrary(a,b).`. A query sentence `s` is added as `query(s).`.

### Module `common` (Listing 1) — conflict-free sets + derivations
```
in(X)        :- assumption(X), not out(X).
out(X)       :- assumption(X), not in(X).
supported(X) :- assumption(X), in(X).
supported(X) :- head(R,X), triggered_by_in(R).
triggered_by_in(R) :- head(R,_), supported(X) : body(R,X).
defeated(X)  :- supported(Y), contrary(X,Y).
:- in(X), defeated(X).
```
Lines 1-2 guess the in/out assumption subset. Lines 3-5 compute **forward support** (`supported` = derivable from `in`), using a conditional literal `supported(X) : body(R,X)` to fire a rule only when its whole (variable-length) body is supported. Line 6 marks assumptions whose contrary is derived (defeated). Line 7 enforces conflict-freeness. This one module is shared across stable/admissible/complete.

### Credulous & skeptical acceptance constraints (Sec 4.2.3)
- Credulous: `:- not supported(X), query(X).` — no answer set unless the query is derived from the guessed set. Program is UNSAT iff query not credulously accepted.
- Skeptical: `:- supported(X), query(X).` — counterexample check; program is UNSAT iff query *is* skeptically accepted (i.e. no σ-set avoids deriving it). This "solve for a counterexample, UNSAT ⇒ accepted" pattern is the ASP analogue of mu-toksia's CEGAR skeptical loop.

### Semantics modules (Sec 4.2.4)
- **Stable** `stb = common ∪ { :- out(X), not defeated(X). }` — every out assumption must be attacked.
- **Admissible** `adm = common ∪ adm′` (Listing 2): compute what the **undefeated** assumptions (`not defeated`) derive; if the undefeated set attacks an `in` assumption, forbid it (`:- in(X), attacked_by_undefeated(X).`). Mirrors "A is admissible iff the set of assumptions not attacked by A does not attack A".
- **Complete** `com = adm ∪ { :- out(X), not attacked_by_undefeated(X). }` — nothing defended may be left out.
- **Preferred**: run `adm` under **ASPRIN** with `#preference(p1, superset){in(X):assumption(X)}. #optimize(p1).` — return only ⊆-maximal admissible sets. ASPRIN's built-in querying gives credulous/skeptical preferred directly.

### Grounded (Sec 4.2.5, Listing 3) — explicit fixpoint iteration
Based on Lemma 7: the grounded set is `I_{|A|}` of the sequence `S_i = (I_i, D_i, U_i)` with `I_i = A \ att(U_{i-1})`, `D_i = att(I_i)`, `U_i = A \ D_i`. The encoding indexes every predicate by iteration `I` (0..|A|-1) and recomputes support/defeat/undefeated per iteration; `in(X,|A|)` is the grounded set. **Note Remark 1: the AAAI-2019 grounded encoding was wrong; this is the corrected one.**

### Ideal (Sec 4.3, Algorithm 1) — ASP-as-subroutine
Adapts Dunne (2009). (1) Get assumptions **not** credulously accepted under admissible via CLINGO **cautious mode** (intersection of all answer sets) on `adm`; complement gives an over-approximation `A_PSA`. (2) Iteratively remove from `Σ` any assumption attacked by assumptions not attacked by `Σ`, until fixpoint = the ideal set. Only step 1 is NP; the refinement loop is polynomial. **Remark 2: Dunne's original Alg 3 Lines 8-9 were incorrect; this paper corrects them (Appendix C).**

### ABA+ (Sec 4.4) — preference-aware modules
`ABA+(F) = ABA(F) ∪ {preferred(x,y). | y ≤ x}`; module `prefs` (Listing 4) encodes transitivity + strict/non-strict preference.
- **`<-stable`** (Listing 5, `stb+ = common ∪ stb+ ∪ prefs`): derive **normal `<`-attacks** by restricting each attacker to assumptions **not less preferred** than the target (`preferredly_supported(X,Y)`), then check **reverse `<`-attacks** among the not-normally-attacked assumptions; Line 10 enforces every out assumption is normally or reversely `<`-attacked. Uses forward-derivability only (Lemma 8), and each check is polytime (Prop 11).
- **`<-grounded`** (Listing 6, subroutine): iterative ASP calls with a `suspect`/`other` guess to find defended assumptions under preferences.

## Complexity results (Sec 3, Tables 2-3) — routing-relevant
- **ABA (LP fragment):** verification of admissibility **P-complete**; credulous under admissible **NP-complete**; all grounded problems **in P**; skeptical preferred **Π₂ᵖ-complete** (standard, Table 2).
- **ABA+ (new results):** verifying admissibility is **coNP-complete** (coNP-hard already under complete/grounded); credulous acceptance under admissibility is **Σ₂ᵖ-complete** — a jump over ABA. Under the fundamental-lemma property, `<-grounded` is computable in polytime with an NP-oracle. **`<-stable` has the same complexity as stable in ABA** (no jump) — which is exactly why its ASP encoding stays a single-shot guess-and-check. *(Table 3)*

## Empirical results (Sec 5, Tables 6-7)
- **Systems compared:** ASP approach (ASPforABA) vs ABA2AF (translation + CLINGO), ABAGRAPH (dispute derivations, SICStus Prolog), ABAPLUS (ABA+ translation). CLINGO 5.2.2, ASPRIN v3, 600 s / 32 GB.
- **Head-to-head (Table 6):** the ASP approach has **zero timeouts** and tiny cumulative runtimes on every problem/semantics, while competitors time out heavily (ABAGRAPH 393/401 on admissible enumeration; ABA2AF ~1/3 timeouts on preferred). Smallest gap is ABA preferred, where ASP median is ~3/4 of ABA2AF but cumulative runtime <1/10.
- **Scalability (Table 7, Fig 3):** ASP routinely solves ABA frameworks up to **~3000 sentences** (credulous adm/com/stb) and ABA+ up to **~1000 sentences** — vs ≤90 sentences for prior systems. A `stb` vs `stb-alt` (Caminada & Schulz 2017) encoding comparison is included.

## Parameters / Configuration

| Name | Where | Value | Notes |
|------|-------|-------|-------|
| ASP solver | build | CLINGO 5.2.2 | grounder+solver |
| Optimization backend | preferred | ASPRIN v3 | subset-maximal `in` |
| Reasoning mode (ideal) | Alg 1 | CLINGO cautious | intersection of answer sets |
| Grounded iterations | Listing 3 | `|A|` | explicit fixpoint index |
| Time / memory (eval) | experiment | 600 s / 32 GB | — |
| Derivability | encodings | forward | not tree-derivability |

## Relevance to Project
This is the **primary implementation reference for the project's ABA workstream** (the `notes/aba-*` and `reports/aba-*` files; the ABA DC-CO routing work on the current branch). Concretely:
1. **Assumption-level, translation-free reasoning.** The project should reason directly over assumptions and rules rather than materializing arguments — the `common` module (guess in/out, forward `supported`, `defeated`, conflict-free) is a near-drop-in specification for an ABA solving core, whether targeting ASP or, by analogy, a SAT encoding.
2. **The acceptance-constraint pattern.** Credulous = `not supported(query)` constraint; skeptical = counterexample `supported(query)` constraint with UNSAT ⇒ accepted. This is the ABA analogue of the SAT/CEGAR skeptical loop in `Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner`, and clarifies how DC/DS routes should be structured for ABA.
3. **Semantics as thin add-ons.** stable/adm/complete differ by one or two rules over `common`; preferred = subset-maximization; grounded = explicit fixpoint iteration; ideal = cautious-mode + refinement loop. This decomposition is the template for organizing the project's ABA semantic dispatch and matches the "shared surface + task-directed add-ons" direction taken for AF SAT.
4. **Corrected algorithms.** Use the **corrected grounded encoding** (Remark 1 / App B) and **corrected ideal algorithm** (Remark 2 / App C) — the AAAI 2019 / Dunne 2009 originals are buggy. Directly relevant to the ABA correctness bugs tracked in `notes/aba-sat-required-assumptions-bug.md` and `notes/aba-completion-sat-bottleneck-2026-05-20.md`.
5. **Complexity-aware routing.** grounded ∈ P (compute the fixpoint, no search); credulous-admissible NP (single guess-and-check); skeptical-preferred Π₂ᵖ (needs the optimization/counterexample machinery); ABA+ credulous-admissible Σ₂ᵖ. This tells the solver which tasks can be cheap and which genuinely need the heavy path.

## Related Work Worth Reading
- Lehtonen, Wallner, Järvisalo (2019, AAAI), *Reasoning over ABA frameworks via direct ASP encodings* — the conference version this extends (note its grounded encoding is erroneous; use this JAIR version).
- Lehtonen, Wallner, Järvisalo (2020, KR), *An ASP approach to argumentative reasoning in the ASPIC+ framework* — the sibling paper applying the same assumption-based ASP method to ASPIC+; in the collection as `Lehtonen_2020_ASPApproachArgumentativeReasoningASPICplus`.
- Bondarenko, Dung, Kowalski, Toni (1997) — the ABA framework and its LP fragment.
- Craven & Toni (2016), ABAGRAPH; Lehtonen et al. (2017), ABA2AF; Bao et al. (2017), ABAPLUS — the baseline systems beaten here.
- Dunne (2009) — the ideal-set algorithm adapted (with correction) in Alg 1.
- Čyras & Toni (2016), ABA+ — the preference extension.
- Niskanen & Järvisalo (2020), mu-toksia — the AF-level counterpart from the same group (`Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner`).

## Open Questions / Notes for Us
- [ ] Should the project's ABA solver target ASP (CLINGO/ASPRIN, as here) or reuse the existing SAT backend with an assumption-level encoding? This paper argues ASP wins for ABA; weigh against the SAT infrastructure already built for AFs.
- [ ] Port the **corrected grounded fixpoint** and **corrected ideal loop** — cross-check against the project's ABA grounded/ideal paths for the same bugs.
- [ ] ABA+ support (`<-stable`/`<-grounded`) is out of scope for ICCMA main ABA track but the reverse-attack complexity jump (Σ₂ᵖ) is worth noting before any preference work.
