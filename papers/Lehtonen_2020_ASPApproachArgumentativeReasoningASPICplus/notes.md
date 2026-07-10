---
title: "An Answer Set Programming Approach to Argumentative Reasoning in the ASPIC+ Framework"
authors: "Tuomo Lehtonen, Johannes P. Wallner, Matti Järvisalo"
year: 2020
venue: "Proc. 17th International Conference on Principles of Knowledge Representation and Reasoning (KR 2020), Main Track, pp. 636-646"
doi_url: "https://doi.org/10.24963/kr.2020/63"
pages: 11
---

# An Answer Set Programming Approach to Argumentative Reasoning in the ASPIC+ Framework

## One-Sentence Summary
The same group's ASP-encoding recipe applied to **ASPIC+**: rephrase the semantics of an ASPIC+ instantiation (strict + defeasible rules, axioms + ordinary premises, no preferences) over **assumptions** = pairs `(P, D)` of ordinary premises and defeasible rules, prove σ-assumptions correspond exactly to σ-extensions of the AF the theory induces, and encode those assumption-level conditions as composable ASP modules — avoiding the exponential blow-up of first building all arguments. *(abstract, Sec 3, Sec 5)*

## Why we hold this paper
It is the **ASPIC+ sibling of ASPforABA** (`Lehtonen_2021_DeclarativeAlgorithmsComplexityABA`), fetched as a bonus while chasing the ASPforABA solver description. It is the closest open-access statement of the group's "reason at the level of defeasible elements + direct ASP encoding" methodology, and it shows the encoding of the three ASPIC+ attack forms — material the ABA paper does not cover. Useful if the project's structured-argumentation work extends past ABA toward ASPIC+.

## The ASPIC+ instantiation (Sec 2)
- **Argumentation theory** `T = (L, R, n, ⁻, K)`: language `L` of atoms, rules `R = R_d ∪ R_s` (defeasible `⇒` and strict `→`), a partial naming function `n : R_d → L`, contrary map `⁻ : L → 2^L`, knowledge base `K = K_n ∪ K_p` (axioms `K_n` + ordinary premises `K_p`). Arguments are finite derivation trees. *(Def 1-4)*
- **Three attack forms** (Def 5): `A` **undercuts** `B` if `Conc(A)` is a contrary of a defeasible rule name used in `B`; `A` **rebuts** `B` if `Conc(A)` contraries the conclusion of a defeasible sub-argument of `B`; `A` **undermines** `B` if `Conc(A)` contraries an ordinary premise of `B`. Attacks only land on defeasible parts.
- Semantics are given by translating `T` to the corresponding AF and taking cf/adm/com/prf/stb there. *(Def 6-7)*

## Assumption-level rephrasing (Sec 3) — the key idea
- An **assumption** is a pair `(P, D)` with `P ⊆ K_p`, `D ⊆ R_d`. Derivability `(P,D) ⊢_T x` = derivable using only those defeasible elements plus all axioms/strict rules; deductive closure `Th_T(P,D)`. An argument is **based on** `(P,D)` if its defeasible rules ⊆ `D` and ordinary premises ⊆ `P`. *(Def 9)*
- **Attack on assumptions** (Def 10): `(P,D)` attacks `p ∈ K_p` if a contrary of `p` is in `Th_T(P,D)`; attacks `r ∈ R_d` if a contrary of the rule name or of its head is derivable. `att(P,D)` = all attacked elements.
- **Defense** (Def 11): `(P,D)` defends `x` if the "everything-not-attacked-by-`(P,D)`" assumption `(K_p \ att(P,D), R_d \ att(P,D))` does not attack `x`. `def(P,D)` = defended elements.
- **σ-assumptions** (Def 12): conflict-free (`(P,D)` doesn't attack its own elements) + all rules in `D` applicable; then admissible iff `(P,D) ⊆ def(P,D)`; complete iff admissible + contains everything defended (except non-applicable rules); stable via the usual "attacked or in" over `K_p`; preferred = ⊆-maximal admissible.
- **Correspondence (Theorem 5):** for `σ ∈ {adm, com, prf, stb}`, `(P,D)` is a σ-assumption iff `E = {A | A based on (P,D)}` is a σ-extension of the AF; and every σ-extension `E` gives the σ-assumption `(Prem_d(E), DefRules(E))`. Credulous/skeptical justification then reduces to existence/universality of a σ-assumption deriving the query (Prop 6).

## ASP encodings (Sec 5)
Framework facts `AT(T)`: `axiom/premise/head/body/strict_head/strict_body/contrary` (rules get names via an extension `n′` of `n`). Query added as `query(a)`.
- **Module `common`** (Listing 1): guess `in/out` over premises + defeasible rules (axioms/strict rules always in); compute `supported` (derivable) via `applicable_by_in`; compute `defeated` from the three contrary-based attack rules (Lines 14-16); enforce conflict-freeness (`:- in(X), defeated(X)`); and build `supported_by_undefeated` for the not-attacked elements. This one module carries the derivation + attack machinery for all semantics.
- **`stb`** (Listing 2): no premise is out-and-undefeated; no rule out-but-applicable-by-undefeated.
- **`adm`** (Listing 3): compute `defeated_by_undefeated`; forbid any `in` element that is attacked by the undefeated set.
- **`com`** (Listing 4): additionally compute `supported_by_defended` (what the defended set derives) and force everything defended to be in.
- **Preferred**: `adm` under **ASPRIN** with a subset-maximality preference over `in`.
Correctness: `(P,D)` is a σ-assumption iff there is an answer set `M` with `P∪D = {x ∈ K_p ∪ R_d | in(x) ∈ M}`; query constraints capture credulous (`:- not derivable(query)`) and skeptical acceptance.

## Complexity (Sec 4)
For this ASPIC+ instantiation: credulous justification is **NP-complete** under admissible/complete/stable/preferred (they coincide credulously); skeptical is **coNP-complete** under stable and **Π₂ᵖ-complete** under preferred (Prop 7). The ASP encodings match these classes (single guess-and-check for NP tasks; ASPRIN optimization for the Π₂ᵖ preferred task), and crucially avoid first generating an exponential number of arguments.

## Experiments (Sec 6)
CLINGO v5.4.0 + ASPRIN v3.1.0, 600 s / 8 GB. Random ATs with up to **5500 atoms** (25% defeasible rules, 25% of atoms/rules with a contrary, 20% premises, varying axiom fraction 0.5-10%). The approach solves most instances up to **~3000 atoms** across adm/com/stb credulous, stable skeptical, and preferred enumeration; some solved up to 5500. **Fewer axioms → harder** instances (more defeasible structure). *(Table 1, Fig 2)*

## Parameters / Configuration

| Name | Where | Value | Notes |
|------|-------|-------|-------|
| ASP solver | build | CLINGO 5.4.0 | default settings |
| Optimization backend | preferred | ASPRIN 3.1.0 | subset-maximal `in` |
| Time / memory (eval) | experiment | 600 s / 8 GB | — |
| Benchmark size | eval | up to 5500 atoms | 25% defeasible, 20% premises |

## Relevance to Project
Secondary/optional reference. The project's structured-argumentation focus is ABA (see `Lehtonen_2021_DeclarativeAlgorithmsComplexityABA`), but this paper is the reference if that ever generalizes to ASPIC+:
1. **Same encoding methodology, richer formalism** — confirms the assumption-level ASP recipe transfers from ABA to ASPIC+, and shows the exact encoding of undercut/rebut/undermine attacks (the part ABA doesn't have).
2. **`common` + add-on module structure** — reinforces the "shared derivation surface + thin per-semantics constraints" organization already adopted for AF SAT and recommended for the ABA solver.
3. **Complexity map for ASPIC+** (NP credulous, Π₂ᵖ skeptical-preferred) for routing decisions if ASPIC+ is added.
4. **No preferences yet** — a known gap; any ASPIC+ work must add preference handling (cf. ABA+ in the sibling paper).

## Related Work Worth Reading
- Lehtonen, Wallner, Järvisalo (2021, JAIR), *Declarative Algorithms and Complexity Results for ABA* — the ABA counterpart and the ASPforABA foundation (`Lehtonen_2021_DeclarativeAlgorithmsComplexityABA`).
- Modgil & Prakken (2013, 2018) — the ASPIC+ framework being instantiated.
- Egly, Gaggl, Woltran (2010) — ASP encodings for abstract AFs (ASPARTIX), the methodological ancestor; in the collection as `Egly_2010_Answer-setProgrammingEncodingsArgumentation`.
- Brewka et al. (2015) — ASPRIN, used for preferred.

## Open Questions / Notes for Us
- [ ] Only relevant if the project targets ASPIC+; ABA is the current structured focus.
- [ ] Preference handling absent here — would need the ABA+/reverse-attack ideas from the sibling paper.
