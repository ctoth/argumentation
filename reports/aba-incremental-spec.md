# Wave C1 — Spec: well-founded preprocessing + incremental CEGAR for ABA solving

Date: 2026-05-12. Read-only recon; no code changed. Author: research subagent.

Sources actually read for this spec:
- `papers/Lehtonen_2021_IncrementalASP_ABA.pdf` — Lehtonen, Wallner, Järvisalo, *Harnessing Incremental Answer Set Solving for Reasoning in Assumption-Based Argumentation*, TPLP (arXiv:2108.04192). Read §1–5 + Appendix A. Cited below as **L21-TPLP §x** / **Alg.1** / **Listing 1**.
- `src/argumentation/aba.py` (408 ll), `src/argumentation/aba_sat.py` (1111 ll), `src/argumentation/aba_asp.py` (355 ll), `src/argumentation/solver_adapters/clingo.py` (333 ll), `src/argumentation/solver_adapters/__init__.py`, dir listing of `src/argumentation/solver_adapters/`.
- `reports/graph-speedup-wave-a-preprocessing.md` (the AF grounded-reduct precedent — `simplify_af`/`AfSimplification`/`lift` shape).
- `notes/graph-theory-recon-codebase-2026-05-12.md` — ABA recon lines 25–69 (the timeout profile: 2023 → 83 ABA SE-PR/SE-ST timeouts; 2025 → 54 ABA DC/DS/SE timeouts at cap-100; ABA path is SAT-Z3 for complete/preferred via `aba_sat.py`, subprocess-clingo for the `.lp` ASP path via `aba_asp.py`).
- The JAIR-2021 extended version (Lehtonen, Wallner, Järvisalo, *Declarative Algorithms and Complexity Results for ABA*, JAIR 71:265–318) was **not** obtained in full — only its abstract via web. Where this spec would need it (the exact `com` module derivation lemmas, the WCP fragment), that is flagged UNRESOLVED below; do not treat anything attributed to "JAIR-2021" here as verified beyond the abstract and what L21-TPLP re-states.

---

## 0. What the current ABA path actually is (verified from source)

Three reasoning surfaces for flat ABA in this repo:

1. **Brute-force reference** — `aba.py`: `complete_extensions`, `preferred_extensions`, `stable_extensions`, `grounded_extension`, `well_founded_extension`, `ideal_extension`, `naive_extensions`. All iterate `_all_subsets(framework.assumptions)` (powerset) — exponential, only viable on tiny instances. `grounded_extension` (aba.py:196) is the `def_operator` least-fixpoint loop and is *not* exponential. `well_founded_extension` (aba.py:205) is implemented as `frozenset.intersection(*complete_extensions(...))` — i.e. it currently *enumerates all complete extensions* (exponential), it does **not** use the grounded fixpoint.

2. **Support-mask reference + Z3 SAT** — `aba_sat.py`:
   - `_minimal_supports(framework)` (aba_sat.py:862) — fixpoint computing, for each language literal, the set of `⊆`-minimal assumption sets that forward-derive it. This is the key precomputed structure; it can blow up (one literal can have exponentially many minimal supports) but in practice is the engine of the SAT path.
   - `support_extensions` (aba_sat.py:13) — brute-force over `1<<len(assumptions)` masks using `_SupportState` (stable/complete/preferred). Reference oracle.
   - `AssumptionKernel` (aba_sat.py:52) — a clingo-program builder for single-extension stable/admissible/preferred. `_solve_selected` (aba_sat.py:255) builds a **fresh `clingo.Control` per call**, `add`+`ground`+`solve` once, throws it away. Used by `sat_stable_extension`, and by `preferred_extension` (which tries `stable_extension` first as a shortcut, then `admissible_extension(maximize=True)` — clingo `#maximize`).
   - `sat_support_extension` (aba_sat.py:347) — the Z3 path for `complete`/`preferred`. For `complete`: builds one Z3 `Solver`, adds admissible + complete constraints over `in_*` assumption vars using `_any_support_selected` disjunctions over `_minimal_supports`, one `check()`. For `preferred`: either a strict-superset growth loop (lines 412–428, uses `solver.push()/pop()` for the "find a strict superset" subquery), or `_sat_preferred_extension_satisfying` (seed → call back into `sat_support_extension("preferred")` → check constraints → loop), or `_sat_preferred_cegar_extension` (aba_sat.py:481).
   - **The CEGAR loop** is `_sat_admissible_cegar_extension` (aba_sat.py:508), wrapped by `_sat_preferred_cegar_extension` (aba_sat.py:481) for preferred (call admissible-CEGAR repeatedly, each time requiring the current set ⊆ and at least one outside assumption, until no strict superset). Inside `_sat_admissible_cegar_extension`:
     - one `z3.Solver()` is created (aba_sat.py:519);
     - `_add_ranked_closure_constraints` (aba_sat.py:634) adds `der_*` Bool + `rank_*` Int vars encoding forward-derivation with a ranking to break cyclic support;
     - for each assumption: `Implies(in, Not(der[contrary]))` (conflict-freeness-ish);
     - then `while solver.check() == z3.sat:` — get model → candidate assumption set + its closure → `_defense_counterexample` (aba_sat.py:564): for each `target` in the candidate, is there an attacker support (subset of assumptions not counter-attacked by the candidate's closure) deriving `contrary(target)`? `derives` + `_shrink_attack_support` shrink it. If a counterexample `(target, attack_support)` is found, **`solver.add(...)`** a refinement clause (`Not(in[target])` if support empty, else `Or(Not(in[target]), *(der[contrary(a)] for a in attack_support))`) and loop. So **the Z3 solver instance IS reused across CEGAR iterations** (it's `add`-only, monotone, which Z3 handles incrementally internally). What is *not* reused: the `_sat_preferred_cegar_extension` wrapper throws away the whole `_sat_admissible_cegar_extension` solver and builds a brand-new Z3 solver for each "grow to a strict superset" step (aba_sat.py:486, 496 each call `_sat_admissible_cegar_extension` fresh). And nothing is reused across *queries* (each `sat_support_extension`/`sat_support_acceptance` call rebuilds everything from `_minimal_supports` up).

3. **ASP-fact subprocess path** — `aba_asp.py`: `encode_aba_theory` emits ASP facts (including the precomputed minimal supports as `support_*` facts) → `solve_aba_with_backend` dispatches to `solver_adapters/clingo.py:run_extension_enumeration_protocol`, which shells out to a `clingo` *binary* (or `python -m clingo`) over `encodings/aba_{admissible,complete,stable}.lp`, parses stdout, post-filters (max for preferred, min for grounded). This is **not** the incremental Python clingo API — it's `subprocess.run`, one shot, full enumeration. `preferred` here = enumerate all complete (`aba_admissible.lp` actually — see aba_asp.py:142–143 maps `preferred`→`admissible` module) then `_maximal_extensions`. `grounded` = enumerate complete then `_minimal_extensions[:1]`. Commit `8ab2a6f` ("Load clingo through optional dependency helper") only changed how the clingo *module* is imported in `aba_sat.py:_load_clingo` (aba_sat.py:1097) — it did not add multi-shot solving.

4. **`auto` backend** (`solver.py`, per recon) routes ABA complete/preferred/stable to the SAT path; `grounded` always native (`aba.grounded_extension`, already fast). ABA+ has no ASP backend (aba_asp.py:97–106 returns `unavailable_backend`).

5. **No structural preprocessing exists for ABA.** No grounded reduct, no SCC peeling, no fixing of forced-in/forced-out assumptions before the SAT/ASP solve. Recon line 29 confirms.

The timeout cluster the recon points at (`reports/workstream-zero-timeouts-dspr-aba.md`: 83 ABA timeouts in ICCMA-2023 = SE-PR/SE-ST clusters; 54 in ICCMA-2025 = DC/DS/SE on selected ABA files) is on this path.

---

## 1. Well-founded / grounded preprocessing for ABA (the analog of Wave A's grounded reduct)

### 1.1 The mathematical object

For a Dung AF, Wave A fixes `G = grounded extension` IN and `G⁺ = G's victims` OUT, then solves on `AF[Args \ (G ∪ G⁺)]` (`reports/graph-speedup-wave-a-preprocessing.md` §"Reductions implemented" #1; standard µ-toksia/pyglaf preprocessing). The ABA analog operates on **assumptions and sentences**, not abstract arguments:

- **Definition (well-founded / grounded ABA extension).** `aba.py:grounded_extension` (aba.py:196) computes `G_ABA` as the least fixpoint of `def_operator` starting from `∅`: `def_operator(F, X) = { α ∈ A : X defends {α} }`, iterated to fixpoint. This is the **grounded assumption set** of `F`. It is unique, and (flat ABA, equivalence of ABA semantics with Dung on the constructed AF — Bondarenko et al. 1997; Toni 2014, both cited in `aba.py` module docstring) `G_ABA = ∩ { complete assumption sets of F }`. **Source for "G_ABA equals the intersection of complete sets":** `aba.py:well_founded_extension` (aba.py:205–209) encodes exactly this identity (`frozenset.intersection(*complete_extensions(...))`), and the docstring's Bondarenko-1997/Toni-2014 citations underwrite it. L21-TPLP Appendix (Alg.3 discussion, line "Enumeration also finds the <-grounded assumption set, which is defined as the intersection of all <-complete sets") restates the same identity for ABA+ → it specializes to ABA. **Verified.**

- **The two derived sets to fix.** Let `Th(G_ABA)` be the forward-deductive closure of `G_ABA` (= `aba_sat.AssumptionKernel.closure(G_ABA)`, aba_sat.py:143, or `aba._closure`, aba.py:254). Define:
  - **`FIXED_IN := G_ABA`** — assumptions in every complete/preferred/stable/ideal extension. (Justification: `G_ABA = ∩ complete`; preferred ⊇ some complete ⊇ `G_ABA`; stable ⊇ `G_ABA` because every stable set is complete; ideal ⊆ ∩ preferred but ⊇ `G_ABA`? — **see UNRESOLVED-A below; ideal ⊇ grounded is true (ideal is the maximal admissible subset of ∩ preferred, and grounded is admissible and ⊆ ∩ preferred), but confirm the residual lift for ideal against the oracle.**)
  - **`FIXED_OUT := { α ∈ A : contrary(α) ∈ Th(G_ABA) }`** — assumptions whose contrary is *already derivable from the grounded set alone*, i.e. assumptions attacked by `G_ABA`. These are the ABA analog of `G⁺`. They cannot appear in any conflict-free superset of `G_ABA`, hence are OUT in every complete/preferred/stable extension (each of which contains `G_ABA` and is conflict-free). **Source for the "attacked by grounded ⇒ out" step:** the AF analog in `reports/graph-speedup-wave-a-preprocessing.md` table ("`G⁺` disjoint from all stable", etc.) plus the standard correspondence (an assumption `α` with `contrary(α) ∈ Th(G_ABA)` maps to an argument attacked by an unattacked-derivable argument, hence OUT). The ABA-direct statement (every complete extension `E ⊇ G_ABA` and is conflict-free, so `α ∈ FIXED_OUT ⇒ α ∉ E`) follows immediately from `def_operator`'s definition + conflict-freeness. **I consider this verified for {complete, preferred, stable}; flag for the oracle.**

- **What this is NOT.** It is **not** "the assumptions in every *complete assumption set*" beyond `G_ABA` — there is no cheap polynomial characterization of "in every preferred set but not in grounded" (that's the coNP/Π₂ part the CEGAR loop is for). `FIXED_IN`/`FIXED_OUT` are exactly the *polynomially-computable* fixed part. The remaining residual still needs the full solver.

### 1.2 Algorithm

```
simplify_aba(F, *, semantics) -> AbaSimplification:
  if semantics not in GROUNDED_REDUCT_ABA_SEMANTICS:        # gate, see 1.4
      return AbaSimplification.trivial(F)
  G   = aba.grounded_extension(F)                            # least fixpoint of def_operator; aba.py:196 — already in repo, O(rules · assumptions) per round, ≤ |assumptions| rounds.  (Could be sped up with closure-style worklist but correctness first.)
  ThG = closure(F, G)                                        # aba._closure / AssumptionKernel.closure — worklist, O(size of rules); aba.py:254 / aba_sat.py:143
  fixed_in  = G
  fixed_out = { α ∈ F.assumptions : F.contrary[α] ∈ ThG }
  survivors = F.assumptions - fixed_in - fixed_out
  # Build residual ABA framework F' over `survivors`:
  #   - assumptions'      = survivors
  #   - contrary'         = F.contrary restricted to survivors
  #   - rules'            = F.rules with antecedents in fixed_in deleted (those antecedents are unconditionally derivable),
  #                         and any rule whose antecedents include a fixed_out assumption... -- SEE UNRESOLVED-B.
  #   - language'         = literals reachable in rules'
  return AbaSimplification(original=F, residual=F', fixed_in=fixed_in, fixed_out=fixed_out)

AbaSimplification.lift(residual_extension) = frozenset(residual_extension) | fixed_in
AbaSimplification.lift_all(...)            = de-duplicated order-stable map of lift over a collection
AbaSimplification.is_trivial              = (fixed_in == ∅ and fixed_out == ∅)
```

Mirrors Wave A's `simplify_af` / `AfSimplification(residual, fixed_in, removed_out, lift, lift_all, is_trivial)` shape (`reports/graph-speedup-wave-a-preprocessing.md` §"What was built"). Suggested module: `src/argumentation/aba_preprocessing.py`; suggested constant `GROUNDED_REDUCT_ABA_SEMANTICS`.

**Complexity:** `grounded_extension` is polynomial (the `def_operator` loop). The expensive `aba.def_operator` (aba.py:138) currently calls `_defends` which iterates `_all_subsets` — **that is exponential.** UNRESOLVED-C: the coder must either (a) keep using the brute-force `grounded_extension` only when `|assumptions|` is small, or (b) replace the grounded fixpoint with a *support-mask-based* `def_operator` (the `_SupportState` machinery in aba_sat.py:768 already has `defends(mask, α)` at aba_sat.py:822 — a grounded fixpoint over masks is polynomial *in the number of minimal supports*, which is the same cost class as the rest of the SAT path). Recommend (b): a small `grounded_assumption_set_via_supports(F)` that fixpoints `mask |= {α : _SupportState.defends(mask, α)}`. This is the honest computation and matches the SAT path's cost model. **Flag for the coder; do not ship the `_all_subsets` `grounded_extension` as a preprocessing primitive on large instances.**

### 1.3 How a residual solution lifts back

`extension_on_F = simplification.lift(extension_on_residual) = extension_on_residual ∪ fixed_in`. For enumeration: `lift_all`. For acceptance:
- DC (credulous) of sentence/assumption `q`: if `q` is an assumption in `fixed_in` → YES immediately; if `q` is an assumption in `fixed_out` → ... **NO is wrong in general** (a sentence-`q` derivable from `fixed_out`-using rules could still be derived another way; even an assumption in `fixed_out` is by definition not in any complete/stable/preferred extension, so credulous-NO *is* correct for an *assumption* query under those semantics — but a *sentence* query needs the full residual solve). So: assumption-query in `fixed_in` → YES; assumption-query in `fixed_out` → NO (for complete/stable/preferred); otherwise solve on residual and lift; for sentence queries, always solve on residual with `q`'s derivation possibly straddling — UNRESOLVED-D: the cleanest correct rule is "a sentence `q` is credulously accepted in `F` iff `q ∈ Th(fixed_in)` OR `q` is credulously accepted in `F'` (with the residual encoding aware that `fixed_in` is unconditionally derivable)". Mirror exactly what Wave A did for `is_preferred_skeptically_accepted` (`reports/graph-speedup-wave-a-preprocessing.md`: query in `fixed_in` → accept, query in `removed_out` → reject, else CDAS on residual) — but for *sentences* there is no `removed_out` analog, so a sentence is never "rejected by preprocessing", only "accepted by preprocessing if in `Th(fixed_in)`" or "deferred to residual".
- DS (skeptical, preferred): symmetric; an assumption query in `fixed_out` → NO (some extension omits it); in `fixed_in` → still must check the residual is non-trivially-OK? No — `fixed_in` ⊆ every extension, so an assumption in `fixed_in` is skeptically accepted iff a preferred extension exists, which for flat ABA always does → YES. Sentence queries: skeptically accepted iff every preferred extension derives it; if `q ∈ Th(fixed_in)` → YES; else defer to residual. **Flag for the oracle.**

### 1.4 Per-semantics gate (the analog of Wave A's `GROUNDED_REDUCT_SEMANTICS`)

| ABA semantics | grounded reduct sound? | reasoning |
|---|---|---|
| **grounded** | trivially — answer *is* `fixed_in`, residual's grounded set is `∅` by construction; just return `(fixed_in,)` and skip the solver. Mirrors Wave A "grounded" row. |
| **complete** | **yes** — `complete(F) = { fixed_in ∪ E : E ∈ complete(F') }`. `fixed_in = ∩ complete`, `fixed_out` disjoint from all. (Verified modulo the residual-construction question UNRESOLVED-B.) |
| **preferred** | **yes** — maximal complete; constant offset `fixed_in` preserves maximality (same argument as Wave A's "preferred" row). |
| **stable** | **yes** — every stable assumption set is complete, hence ⊇ `fixed_in`; and a stable set attacks everything outside it, in particular it does attack/exclude `fixed_out` consistently. Coverage transfers (Wave A "stable" row, analog). **One caveat to confirm against the oracle:** a self-attacking-style obstruction to *existence* of a stable extension in ABA would be an assumption `α` with `contrary(α) ∈ Th({α} ∪ anything-forced)` — Wave A had to gate self-loop-sink removal off for stable for exactly this reason. Here we only ever *force* `fixed_in` (= grounded, which is conflict-free) and *exclude* `fixed_out`; we never *delete* a problematic assumption from the universe, so the stable-existence obstruction is preserved. **I believe stable is safe; flag it as the highest-risk row for the oracle.** |
| **ideal** | **yes, with care** — ideal ⊆ ∩ preferred (all preferred contain `fixed_in`, exclude `fixed_out`) and ideal ⊇ grounded `= fixed_in` (grounded is admissible and ⊆ ∩ preferred). So `ideal(F) = fixed_in ∪ ideal(F')`. Wave A's "ideal" row is the precedent. UNRESOLVED-A: confirm `ideal ⊇ grounded` is used correctly and that the residual ideal computation isn't tripped by the same latent bug Wave A flagged in `find_ideal_extension` — there's no `aba_sat` ideal SAT path today, only the exponential `aba.ideal_extension` (aba.py:212), so "ideal" preprocessing has nothing downstream to feed yet; **lower priority**. |
| **admissible** | **NO** — `∅` is admissible, so `adm(F) ≠ { fixed_in ∪ E }`. Same exclusion as Wave A. ABA admissible enumeration is the exponential `_reference_extensions(...,"admissible")` path (aba_asp.py:260) + the `aba_admissible.lp` clingo path — leave it alone, or give it only a *no-op* simplification. |
| **complete/preferred/stable for ABA+** (with preferences) | **UNRESOLVED-E** — `<-grounded` is the intersection of `<-complete` sets (L21-TPLP Alg.3 discussion), so an analogous fixed-IN exists, but `<-attacks` are not the simple attacks (reverse attacks via preferences — L21-TPLP Def.1) so the `fixed_out` computation `contrary(α) ∈ Th(...)` is *not* the right notion (it ignores reverse attacks and the `<` filter on supports). Do **not** apply this preprocessing to `ABAPlusFramework` in the first cut. The repo's ABA+ path is brute-force / unavailable anyway. |

So the analog constant: `GROUNDED_REDUCT_ABA_SEMANTICS = {"grounded", "complete", "preferred", "stable", "ideal"}` — and do **not** include `"admissible"`, and do **not** apply to ABA+.

### 1.5 Soundness summary / citation chain

- `G_ABA = ∩ complete sets of F`, `G_ABA` ⊆ every preferred/stable set: Bondarenko, Dung, Kowalski, Toni 1997 + Toni 2014 tutorial (cited in `aba.py` module docstring); operationalized in `aba.py:grounded_extension` / `well_founded_extension`. L21-TPLP restates the grounded = ∩-complete identity (Appendix, Alg.3 discussion).
- `fixed_out` (= `{α : contrary(α) ∈ Th(G_ABA)}`) ∉ any conflict-free superset of `G_ABA`: immediate from forward-derivation + the definition of attack in flat ABA (`aba.py:attacks`, aba.py:96) — an attacked assumption can't co-exist with its attacker in a conflict-free set.
- The residual-lift identity `complete(F) = {fixed_in ∪ E : E ∈ complete(F')}` is the ABA mirror of Wave A's verified AF identity; **the ABA proof is not in any paper I read** — it should be checked by the differential oracle (§4), which is exactly how Wave A validated its AF version (`reports/graph-speedup-wave-a-preprocessing.md` §"Validity ... all verified by the new oracle tests"). **This is the principal UNRESOLVED item; flagged, not invented.**

### 1.6 UNRESOLVED list for the coder

- **UNRESOLVED-A** — `ideal ⊇ grounded` and the residual-lift for ideal. Low priority (no downstream ideal SAT path). Settle against `aba.ideal_extension` on small instances.
- **UNRESOLVED-B** — exact residual-`rules'` construction. The safe, definitely-correct choice: **don't rewrite rules at all**; keep `F.rules` and `F.language` unchanged in the residual, only change `assumptions'` and `contrary'` to the `survivors` set, then *add* the fact that every `fixed_in` assumption is forced and every `fixed_out` assumption is forbidden as solver-side constraints (the `AssumptionKernel` already supports `require_assumptions`; add a `forbid_assumptions`). I.e., the "residual" is the *same* framework with the search space pinned — this is provably equivalent to the AF reduct's `AF[U]` and avoids any rule-rewriting subtlety. Trade-off: smaller search-space win, no language shrink. **Recommend this conservative form for v1; the rule-rewriting form is a follow-up.** (Wave A could afford the literal restriction because there were no rules; ABA has rules, so be conservative.)
- **UNRESOLVED-C** — `grounded_extension`/`def_operator` is exponential as written (`_defends` over `_all_subsets`). Use a support-mask grounded fixpoint instead (the `_SupportState.defends` machinery, aba_sat.py:822). Spec'd above as `grounded_assumption_set_via_supports`.
- **UNRESOLVED-D / -E** — sentence-query lift rules; ABA+ exclusion. Above.

---

## 2. Incremental CEGAR for the ABA solve

### 2.1 What the current loop rebuilds vs. reuses (cited)

- **Within one `_sat_admissible_cegar_extension` call (aba_sat.py:508–561):** the Z3 `Solver` *is* reused across CEGAR iterations — refinement clauses are `solver.add(...)` (aba_sat.py:551, 555–559), the loop is `while solver.check() == z3.sat:`. Z3 keeps learned clauses across `add`+`check` (monotone API), so this is already incremental in the Z3 sense. ✅ Nothing to do here.
- **Across the preferred "grow to strict superset" steps (`_sat_preferred_cegar_extension`, aba_sat.py:481–505):** ❌ each iteration of the `while True:` loop calls `_sat_admissible_cegar_extension(...)` fresh (aba_sat.py:486, 496) — a **brand-new Z3 solver, brand-new `_add_ranked_closure_constraints`** (the expensive part: `O(|literals|)` Int rank vars + `O(|rules|)` implications + per-non-assumption-literal disjunction over its defining rules, aba_sat.py:647–691). On a framework with `k` assumptions this rebuilds the closure encoding up to `k` times. **This is the main fix target.**
- **Across queries (DC/DS for different sentences, or enumeration):** ❌ everything from `_minimal_supports` (aba_sat.py:862 — itself a fixpoint, potentially the dominant cost) through the Z3 encoding is rebuilt per call. `sat_support_acceptance` (aba_sat.py:317) → `sat_support_extension` → fresh `_minimal_supports`, fresh solver. `support_acceptance` (aba_sat.py:288) for the *reference* path enumerates *all* extensions then scans. ❌.
- **The clingo path** (`aba_asp.py` + `solver_adapters/clingo.py`): one-shot `subprocess.run` over a `.lp` file (clingo.py:112). ❌ no multi-shot. The `AssumptionKernel._solve_selected` (aba_sat.py:255) uses the *Python* `clingo` module but still `Control(...)`+`add`+`ground`+`solve` once per call and discards. ❌.

### 2.2 The L21-TPLP incremental scheme (what to mirror)

L21-TPLP §3.1, **Algorithm 1** (skeptical acceptance under preferred, the 2ᴾ-complete task — exactly the SE-PR/DS-PR cluster the recon flags), is the canonical structure:

```
Π := ABA(F) ∪ com                                  # one ASP program, built once
while  Π ∪ {constr(supported(s))}  is satisfiable:  # outer: find a complete set NOT deriving s ... wait — Alg.1 line 2 finds one that DOES derive? re-read:
   # L21-TPLP Alg.1: line 2 loop = "find a complete assumption set deriving s? no —"
   #   precisely (paper §3.1): line 2 generates a complete set; on first failure all complete sets derive s ⇒ return YES;
   #   else add constr(out(I)) to Π (rules out I and its subsets), then inner loop grows I to a ⊆-maximal complete set still not... 
   #   — the paper's wording (verbatim): "first generating a complete assumption set within the framework that does not derive the queried sentence s (Line 2)"; then "iteratively generate proper supersets ... not deriving s (loop starting in Line 5)"; on inner termination I is a preferred-among-not-deriving-s candidate; Line 8 checks "Π ∪ in(I) unsatisfiable" ⇒ I is genuinely preferred ⇒ counterexample ⇒ return NO; if satisfiable, I is dominated, loop back to Line 2 with the subset-blocking constr still in Π.
   ...
return YES   (resp. NO when a counterexample found)
```

Key incremental facts (L21-TPLP §4, "implemented using the incremental Python interface of Clingo v5.4.0 ... CEGAR procedures based on incremental ASP solving"):
1. **One `clingo.Control`, ground once, `solve` repeatedly under assumptions / with added constraints.** The program `Π = ABA(F) ∪ com` is added & grounded once; each iteration either (a) adds a *ground* constraint `constr(out(I))` / `constr(supported(s))` via `Control.add` + re-`ground` of the new bit, or (b) — better — passes the per-iteration hypotheses as **`solve(assumptions=[...])`** (clingo's assumption literals = IPASIR-style), so nothing is permanently added and re-`ground` is avoided. L21-TPLP uses the multi-shot interface for the *permanent* `constr(out(I))` accumulation (the abstraction-refinement clauses are monotone, like the Z3 `add`s) and `solve(assumptions=...)` for the *transient* `in(I)` / `supported(s)` checks.
2. **The `check` ASP module is a *separate* `Control`** (Alg.2 `check := ABA+(F) ∪ ...` is a distinct program) but its facts `undefeated(I) ∪ in(I)` change every iteration → it's rebuilt per iteration *as facts*, while the *encoding part* (the `.lp` modules) is added once and `ground` is parameterized. (L21-TPLP §3.3–3.4 use Clingo program *parts* with parameters — `#program check(...).` — grounded per-call with the iteration's constants. This is the multi-shot `Control.ground([("check", [args])])` pattern, Kaminski et al. 2020.)
3. **Stronger abstraction = fewer iterations.** L21-TPLP §4: weaker abstraction averaged 1148 iterations vs 12 with the stronger (for `<-complete`). The lesson: incremental solving alone is good, but the *abstraction strength* dominates iteration count. (Their `prune` module, Listing 6.) For *ABA* (not ABA+) preferred, Alg.1's abstraction is "complete assumption sets" — already quite strong; the win is purely the incremental reuse + not re-grounding `ABA(F) ∪ com` per candidate.

### 2.3 The exact change to make in this repo

**Two independent sub-changes; pick the lower-risk one first.**

**(2.3a) Z3 path — reuse the closure encoding across the preferred growth loop.** In `_sat_preferred_cegar_extension` (aba_sat.py:481), instead of calling `_sat_admissible_cegar_extension` fresh each grow-step, build **one** Z3 `Solver` with the ranked-closure encoding + conflict-freeness once, then between grow-steps use `solver.push()/pop()` to add/retract the transient hypotheses (`require current ⊆ selected`, `require ≥1 outside selected`) — the *permanent* CEGAR refinement clauses (the defense counterexamples) stay below the push level and accumulate. Concretely: refactor `_sat_admissible_cegar_extension` into `_AdmissibleCegarSolver` (a small class holding `z3.Solver`, `variables`, `derived` dicts) with a method `solve(*, require_assumptions, require_any_assumption) -> AssumptionSet | None` that does `push()` → add transient constraints → run the `while check()==sat:` refinement loop → on return `pop()` (keeping the refinement clauses? — **no**: defense counterexamples found while a transient `require X ⊆` is in force are still globally valid clauses about `in[target]`/`der[contrary]`, so they should be added at the *base* level, i.e. via a deferred list applied below `push`, or simply use a *second* solver-less queue of clauses re-added each `solve`. Cleanest: keep two lists — `permanent_clauses` (grows forever, re-added is unnecessary because they're below push) and let `push/pop` only manage the `require_*` literals. Add permanent clauses with `solver.add` *before* any `push`, or accept that once added they persist regardless of push level (Z3 `add` after `push` is popped — so you must add CEGAR clauses while at base level: collect them during the inner loop, `pop`, then `add` them, then next `push`).) Net effect: the `O(|literals| + |rules|)` ranked-closure encoding is built **once per query** instead of **once per grow-step**. Expected: removes a `×k` factor (k = #assumptions in the final preferred set) from preferred SE/DS on instances with long defense chains.

**(2.3b) Clingo path — switch the ABA ASP backend from subprocess to multi-shot, implementing Alg.1.** This is the bigger, higher-payoff change and the one that mirrors ASPforABA directly. New module e.g. `src/argumentation/aba_incremental.py` (or extend `AssumptionKernel`):
   - Build `Π = ABA(F) ∪ com` once as text (the `ABA(F)` facts are essentially `aba_asp.encode_aba_theory`'s `assumption/head/body/contrary` facts — L21-TPLP `ABA(F)` definition, §3.1; the `com` module is L21-TPLP **Listing 1** verbatim — that listing should be added as `encodings/aba_com_incremental.lp` since the existing `encodings/aba_complete.lp` is the *enumeration* variant, not necessarily the `in/out/supported/triggered_by` shape Alg.1 needs — **the coder must diff the existing `.lp` against Listing 1; UNRESOLVED-F**).
   - `ctl = clingo.Control(); ctl.add("base", [], Π); ctl.ground([("base",[])])`.
   - Outer/inner loop of Alg.1: `ctl.solve(assumptions=[(clingo.Function("supported",[s_id]), True)])` for the transient query check; for the permanent `constr(out(I))` refinement, accumulate into a `#program refine(...)` part grounded incrementally, **or** simpler — maintain the blocked-subsets as `ctl.add("refine"+str(n), [], ":- " + ",".join("in("+a+")" for a in out_I_complement?) ...)` — actually `constr(out(I))` = `:- out(a1), ..., out(ak).` over the assumptions that were OUT in `I`; add it as a new tiny program part and re-`ground` just that part. (Kaminski et al. 2020 multi-shot pattern; L21-TPLP §4.)
   - For DS-PR specifically: Alg.1 lines 2–9 exactly. For SE-PR (find one preferred set): Alg.4 (Appendix A) — same loop, omit the query and Line 8, report `in(I)` after the inner loop. For enumeration: Alg.4 full, collect each.
   - For complete/stable (NP, not 2ᴾ): no CEGAR needed — a single `ctl.solve` over `ABA(F) ∪ com` (+ a `:- not supported(s).` for DC, etc.). The incremental win there is only "reuse `ctl` across multiple queries on the same `F`" (see 2.4).

**Recommendation:** do **(2.3a)** first (small, contained, no new files, immediate win on the Z3 preferred path which is the `auto` default for ABA preferred per recon). Then **(2.3b)** as a second deliverable — it's the one that actually reproduces the ICCMA-winning algorithm, but it's a new module + a new `.lp` + multi-shot clingo plumbing.

### 2.4 Reuse across queries on the same framework

Yes — and this is cheap once 2.3b exists. A `AbaIncrementalSolver(F)` object holds the grounded `ctl` (with `Π = ABA(F) ∪ com` grounded once, and — composed with §1 — pinned by `fixed_in`/`fixed_out` as `:- not in(α).` / `:- in(α).` ground facts). Then:
- DC(s) = `ctl.solve(assumptions=[(supported(s), True)])` is SAT? (NP fragment — complete/admissible) — O(1) extra programs.
- DS(s) under preferred = run the Alg.1 loop, but the **`constr(out(I))` clauses accumulated in a previous DS query on a *different* `s` are NOT valid to keep** (they encode "this complete set is dominated *with respect to deriving the old s*") — so the *refinement* clauses must be scoped per-query (use a `#program` part you can't un-ground... clingo can't retract grounded rules). **Practical answer: keep one persistent `ctl` for the NP queries (complete/stable/admissible DC/DS/SE — fully reusable), and spin a *fresh* `ctl` per preferred-2ᴾ query** (the refinement clauses are query-specific). This still saves the `_minimal_supports` recomputation and the `ABA(F)`-fact construction across queries. (The Z3 path 2.3a has the same property — the ranked-closure encoding is query-independent and reusable; the CEGAR refinement clauses are not.) **L21-TPLP does not discuss cross-query reuse explicitly** — this paragraph is engineering, flagged as such; the only hard claim is "the query-independent encoding part can be built once," which is just the multi-shot grounding model.

### 2.5 Expected win

L21-TPLP §4 reports the incremental-ASP CEGAR "clearly outperforms" the Asprin-based approach for DS-PR on ABA, scaling to |L|=8000; and "dominates ABAplus" on ABA+ enumeration (Table 1: 0 timeouts vs 9, mean 0.1s vs 15s). No absolute numbers transfer to this repo (different baseline). Honest expectation for *this* repo: (2.3a) removes a multiplicative `#assumptions` factor on preferred SE/DS Z3 solves → should clear some of the 2023 SE-PR cluster; (2.3b) replaces the one-shot subprocess-clingo enumerate-then-filter with the targeted CEGAR loop → the big win, but unverified here. **No benchmark was run for this spec — no ICCMA cap-100 corpus in-repo (recon line 63: `bench/` = README + `asp_vs_sat.py` + `instance_gen.py` only).** The coder must run `bench/asp_vs_sat.py` (ABA chains) before/after and, if available, the ICCMA-2023/2025 ABA subsets that produced the 83/54 timeouts.

---

## 3. What to keep flat / not touch

- **Don't materialize the Dung AF.** `aba.py:aba_to_dung` (aba.py:232) is `O(|arguments|²)` and `|arguments|` is the powerset of assumptions × closure — recon §(d) and `reports/workstream-zero-timeouts-dspr-aba.md` Phase 4 / Toni 2014 both flag "generating full Dung AFs unnecessarily" as the thing to avoid. The assumption-level SAT/ASP path exists precisely to skip this. Keep it that way; do **not** route ABA solving through the AF SCC layer (`reports/graph-speedup-wave-b2-scc-impl.md`) — the assumption-level framework is not an AF.
- **Don't gate `admissible` (or ABA+) through the grounded reduct** — §1.4. Leave the `_reference_extensions(...,"admissible")` and `aba_admissible.lp` paths and the brute-force `aba.py` reference functions exactly as they are; they're the oracle.
- **Don't replace `aba.grounded_extension` itself** — it's correct and (the `def_operator` issue aside) it's the reference. *Add* a support-mask grounded fixpoint as a *new* function for the preprocessing hot path; keep the old one for differential testing.
- **`_minimal_supports`** can blow up — but it's load-bearing for the whole SAT/ASP-fact path. Don't touch its semantics; if anything, *cache* it on the new incremental-solver object so repeated queries don't recompute it. (Not a correctness change.)
- **The `_SupportState` brute-force `support_extensions`** — leave as the reference oracle.
- **`encodings/aba_{admissible,complete,stable}.lp`** — leave them; add a *new* `aba_com_incremental.lp` (Listing 1) rather than editing the enumeration encodings, so the existing subprocess path keeps working as a fallback / oracle.

---

## 4. Test oracle — the equivalence the coder must assert

The repo has the differential infrastructure: `tests/test_aba.py`, `tests/test_aba_asp_differential.py`, `tests/test_aba_bondarenko_examples.py`, `tests/test_aba_dung_correspondence.py`, `tests/test_aba_iccma_io.py`, `tests/test_aba_plus_cyras_2016.py`, `tests/test_aba_toni_2014_tutorial.py`; and `src/argumentation/solver_differential.py` (capability matrix incl. ABA rows, `solver_differential.py:144–150`). Mirror Wave A's `tests/test_preprocessing.py` discipline (`reports/graph-speedup-wave-a-preprocessing.md` §"Test results": structural-invariant battery + random instances + oracle-equivalence vs both the brute-force reference *and* the unsimplified solver, incl. require_in/out).

**New file `tests/test_aba_preprocessing.py` must assert:**
1. **Structural invariants of `simplify_aba`** on a battery (an ABA with a non-trivial grounded set; an ABA whose grounded set is `∅` → `is_trivial`; an ABA with an assumption attacked by grounded → it's in `fixed_out`; the Bondarenko/Toni-2014 tutorial frameworks; ~80–120 random flat ABAs from `bench/instance_gen.py`-style generation): `fixed_in == aba.grounded_extension(F)`; `fixed_in ∩ fixed_out == ∅`; `fixed_in ∪ fixed_out ∪ survivors == F.assumptions`; `lift(∅) == fixed_in`; `lift_all` dedup/order-stable.
2. **Oracle-equivalence, per gated semantics `{grounded, complete, preferred, stable}`** (ideal optional): for every framework in the battery + N random ones,
   - `lift_all(solve_on_residual(simplification.residual, semantics)) == aba.{semantics}_extensions(F)` (set equality of the family of extensions), AND
   - `== solve_with_simplify_off(F, semantics)` (the existing unsimplified path: `support_extensions` / `sat_support_extension` / `solve_aba_with_backend(backend="asp")` as available).
   - For acceptance: `DC(F, semantics, q)` and `DS(F, "preferred", q)` with `simplify=True` agrees with `sat_support_acceptance(...)` / `support_acceptance(...)` and with the brute-force `aba.py` reference, for q ranging over all assumptions *and* a sample of derivable sentences.
3. **Incremental-CEGAR equivalence** (independent of preprocessing): the new incremental solver (Z3 2.3a refactor and/or clingo 2.3b multi-shot) returns, for SE-PR / DS-PR / SE-CO / SE-ST / DC / DS, results equal to the *current* `aba_sat.py` / `aba_asp.py` paths on the battery + random instances. I.e. `_sat_preferred_cegar_extension_new(F) ` produces a preferred assumption set ⇔ the old one does, and the set is preferred (`aba.preferred_extensions` membership). For the clingo Alg.1 path: `DS_PR_incremental(F, s) == (s ∈ ⋂ aba.preferred_extensions(F))` on small F, and `== solve_aba_with_backend(F, backend="asp", semantics="preferred", task="skeptical", query=s).answer` on larger F.
4. **`simplify=False` regression**: every existing ABA test still passes; existing telemetry/encoding tests that assert "which internal SAT/ASP calls ran" get `simplify=False` (same surgery Wave A did — `reports/graph-speedup-wave-a-preprocessing.md` §"Existing suite").

Run baseline first: `python -m pytest tests/ -k aba` on clean branch, record pass count, then on the branch.

---

## 5. Effort estimate & recommended split

| Piece | Effort | Risk |
|---|---|---|
| §1 `aba_preprocessing.py` (`simplify_aba`/`AbaSimplification`/`lift`, `GROUNDED_REDUCT_ABA_SEMANTICS`, support-mask grounded fixpoint, the *conservative* "pin the search space" residual form) | ~1 day | medium — the residual-lift identity needs the oracle to confirm; the gate is the safety net |
| §1 wiring: `simplify` param on `sat_support_extension` / `sat_support_acceptance` / `solve_aba_with_backend` / `AssumptionKernel`, lift on the way out, empty-residual short-circuit | ~0.5 day | low (mirrors Wave A's `_prepare` helper) |
| §2.3a Z3 preferred-growth incremental refactor (`_AdmissibleCegarSolver` class, push/pop for transient hypotheses, base-level CEGAR clause accumulation) | ~1 day | medium — getting the push/pop vs permanent-clause layering right |
| §2.3b clingo multi-shot Alg.1 (`aba_incremental.py`, `aba_com_incremental.lp` from Listing 1, multi-shot grounding, the outer/inner loop, SE/DS/enum variants) | ~2–3 days | medium-high — new `.lp` must match the algorithm's predicates (UNRESOLVED-F); multi-shot clingo plumbing; `auto` backend routing |
| §4 `tests/test_aba_preprocessing.py` + incremental-equivalence tests + telemetry-test surgery | ~1 day | low |

**Recommended split: two coders.**
- **Coder 1 — preprocessing** (§1 + its wiring + the preprocessing half of §4). Self-contained, mirrors Wave A almost line-for-line. Lands first; can be merged independently.
- **Coder 2 — incremental CEGAR** (§2.3a, then §2.3b, + the incremental half of §4). §2.3a is a quick standalone win; §2.3b is the ASPforABA reproduction. Coordinate only at the `auto`-backend routing point and at `tests/test_aba_preprocessing.py` (shared file — split by `class`).
- They compose: the incremental solver should accept an already-simplified residual (`solve_on(simplification.residual)`), so Coder 2 takes a dependency on Coder 1's `AbaSimplification.residual` shape but nothing more.

Single-coder fallback: do §1 + §2.3a only (~3 days, low risk, real wins), defer §2.3b to a follow-up — that still hits the recon's stated blocker (the Z3 preferred path is `auto`'s default for ABA preferred).

---

## Open questions surfaced (consolidated, for whoever picks this up)

- **UNRESOLVED-A** ideal ⊇ grounded + residual-lift for ideal — low priority, no downstream ideal SAT path.
- **UNRESOLVED-B** residual `rules'` construction — **recommend the conservative "pin the search space, don't rewrite rules" form for v1.**
- **UNRESOLVED-C** `aba.grounded_extension`/`def_operator` is exponential as written (`_defends` over `_all_subsets`) — use a support-mask grounded fixpoint instead; spec'd.
- **UNRESOLVED-D** sentence-query (vs assumption-query) lift rules under DC/DS — spec'd a candidate, oracle must confirm.
- **UNRESOLVED-E** ABA+ (`<-attacks`, reverse attacks) — do **not** apply this preprocessing to `ABAPlusFramework` in v1.
- **UNRESOLVED-F** does `encodings/aba_complete.lp` already have the `in/out/supported/triggered_by/defeated/derived_from_undefeated/attacked_by_undefeated` predicate shape of L21-TPLP Listing 1, or is a new `aba_com_incremental.lp` needed? Coder 2 must diff them.
- The JAIR-2021 paper was not read in full; if a question reduces to "what exactly does the `com` module do / what's the WCP fragment", obtain `https://www.jair.org/index.php/jair/article/view/12479` before guessing.

Sources: [Lehtonen, Wallner, Järvisalo, TPLP 2021 (arXiv:2108.04192)](https://www.cambridge.org/core/journals/theory-and-practice-of-logic-programming/article/harnessing-incremental-answer-set-solving-for-reasoning-in-assumptionbased-argumentation/36006A2FD643DB686276D2516240F955) — read; [Lehtonen, Wallner, Järvisalo, JAIR 71:265–318 (2021)](https://jair.org/index.php/jair/article/view/12479) — abstract only.
