---
title: "Approximating operators and semantics for abstract dialectical frameworks"
authors: "Hannes Strass"
year: 2013
venue: "Artificial Intelligence (Elsevier)"
doi_url: "https://doi.org/10.1016/j.artint.2013.09.004"
pages: "39-70"
volume: "205"
affiliation: "Computer Science Institute, Leipzig University, Germany"
---

# Approximating operators and semantics for abstract dialectical frameworks

> **STATUS:** notes in progress. Pages 0-8 (PDF idx) read so far. Continuing read pages 9-31.

## One-Sentence Summary
Strass embeds Brewka & Woltran's abstract dialectical frameworks (ADFs) into the Denecker-Marek-Truszczynski (DMT) approximation-fixpoint-theory (AFT) framework by defining a *characteristic operator* G_Xi for an ADF and deriving all standard semantics (Kripke-Kleene, supported, stable, well-founded, M-/L-supported, M-/L-stable, admissible, complete, preferred, grounded, naive, stage, semi-stable) uniformly as fixpoints of approximations of G_Xi, then uses the resulting algebra to relate ADFs to logic programs and Dung AFs.

## Problem Addressed
- Dung AFs are popular as a target abstraction language but cannot directly express joint support, joint attack, or cyclic positive-support distinctions (supported vs stable model).
- Brewka & Woltran's ADFs generalise AFs but their original semantics (BW-stable, BW-admissible, BW-preferred, BW-well-founded) were defined ad hoc, partly only for *bipolar* ADFs.
- There was no principled, lattice-theoretic, semantics-uniform account of ADFs that could be related to logic programming and to AFs through standard nonmonotonic reasoning machinery.
- Concrete pain point (Example 1.1, "Under pressure"): cyclic positive support in a logic program (n1<-v1, n2<-v2, n1<-n2, n2<-n1) yields supported model {n1,n2} (wrong: causality violated) but stable model {} (correct). AFs lack this distinction; ADFs need to provide it.

## Key Contributions
- Defines the *characteristic operator* G_Xi : 2^S -> 2^S of an ADF Xi=(S,L,C^in) and the canonical (antimonotone-style) approximation G_Xi : 2^S x 2^S -> 2^S x 2^S. *(p.49)*
- Lifts DMT's general framework (Kripke-Kleene, supported, stable, well-founded) plus M-/L-refinements to ADFs in one stroke. *(p.5,49 onwards)*
- Generalises AF admissible/complete/preferred/grounded/naive/stage/semi-stable to ADFs and shows two systematic generalisations exist (a "supported" and a "stable" version). *(p.43)*
- Proves polynomial, faithful, modular (PFM) translation from ADFs to normal logic programs that preserves a whole range of semantics (linear in size). *(p.42)*
- For Dung AFs: ADF-induced operator collapses to Dung's characteristic function; preferred/semi-stable AF extensions correspond one-to-one to M-/L-stable models of the standard LP translation. *(p.43)*
- Proves equivalence (in 4-valued Belnap logic) of two AF->LP translations: standard "attack-as-negation-as-failure" folklore and Dung's original explicit attack/defeat encoding. *(p.43)*

## Methodology
- Lattice-theoretic operator-based approach (Tarski/Knaster + DMT 2000, 2004).
- Build canonical approximation O of an antimonotone operator O via O'(x,y) := (O(y), O(x)); apply DMT machinery to get all semantics uniformly.
- Specialise the recipe to the ADF acceptance-condition lattice 2^S x 2^S.
- Relate to LP via translation that turns each acceptance condition C_s^in into clauses for s.
- Specialise back to AFs to recover/refine known correspondences.

## Key Definitions / Equations (verbatim, from PDF read so far)

### Lattice-theoretic preliminaries (p.43-44)
- *Complete lattice* (L, ⊑): every subset has lub and glb; least element ⊥, greatest ⊤.
- *Monotone* O: x⊑y ⇒ O(x)⊑O(y). *Antimonotone*: x⊑y ⇒ O(y)⊑O(x).
- *Fixpoint* of O: O(x)=x. *Prefixpoint*: O(x)⊑x. *Postfixpoint*: x⊑O(x).
- Tarski-Knaster: monotone O on complete lattice has complete lattice of fixpoints; lfp(O) exists and equals least prefixpoint.

### Approximating operators (p.43)
- Approximation O : L^2 → L^2 acts on pairs (x,y) ∈ L^2 (lower/upper bound, "approximates" the set { z | x ⊑ z ⊑ y }).
- *Consistent* pair: x ⊑ y. *Exact*: x = y.
- *Information ordering* ≤_i on L^2: (x1,y1) ≤_i (x2,y2) iff x1 ⊑ x2 and y2 ⊑ y1. Bilattice (L^2, ≤_i) has least (⊥,⊤).
- *Truth ordering* ≤_t: (x1,y1) ≤_t (x2,y2) iff x1 ⊑ x2 and y1 ⊑ y2.
- *Symmetric* O: O'(x,y) = O''(y,x). *Approximating*: symmetric and ≤_i-monotone.
- For antimonotone O, *canonical approximation*: O'(x,y) := O(y) (so O(x,y) = (O(y), O(x))).

### Stable operator (Definition 2.1, p.44)
- *Complete stable operator* cO : L → L: cO(y) := lfp( O'(·, y) ).
- *Stable operator* SO : L^2 → L^2: SO(x,y) := (cO(y), cO(x)).

### Standard semantics (Definition 2.2, p.44) for any approximating O on L
| Semantics                              | Defining condition                  |
|----------------------------------------|-------------------------------------|
| Kripke-Kleene                          | lfp(O)                              |
| three-valued supported model (x,y)     | O(x,y) = (x,y)                      |
| two-valued supported model (x,x)       | O(x,x) = (x,x)                      |
| well-founded                           | lfp(SO)                             |
| three-valued stable model (x,y)        | SO(x,y) = (x,y)                     |
| two-valued stable model (x,x)          | SO(x,x) = (x,x)                     |

Inclusion lattice: every two-valued ⇒ three-valued; KK is a 3-valued supported model and equals well-founded for the 3-valued stable case; every 3-valued/2-valued stable is also supported.

### Ultimate approximations (Denecker et al. 2004, p.44)
For consistent (x,y) in (L^2, ≤_i):
$$
\mathcal{U}_O'(x,y) := \prod\{O(z) \mid x \sqsubseteq z \sqsubseteq y\}
$$
$$
\mathcal{U}_O''(x,y) := \bigsqcup\{O(z) \mid x \sqsubseteq z \sqsubseteq y\}
$$
Most precise (≤_i-greatest) approximation of O. Works only for consistent pairs; not symmetric.

### Logic programming (Definition 2.3, p.45)
- Signature A; *not A* := {not a | a∈A}; *Lit(A)* := A ∪ not A.
- Rule: a ← M, M ⊆ Lit(A); M^+ := M ∩ A, M^- := {a∈A | not a ∈ M}; rule *definite* if M^- = ∅.
- *T_Π* operator on (2^A, ⊆), one-step consequence for definite Π.
- 4-valued Belnap setting: (X,Y) ∈ 2^A × 2^A reads atoms in X∩Y as true, A\(X∪Y) as false, Y\X as undefined, X\Y as inconsistent.
- *Approximating operator* T_Π : 2^A × 2^A → 2^A × 2^A:
$$
\mathcal{T}_\Pi(X,Y) := (\mathcal{T}_\Pi'(X,Y), \mathcal{T}_\Pi'(Y,X))
$$
$$
\mathcal{T}_\Pi'(X,Y) := \{ a \in A \mid a \leftarrow M \in \Pi,\ M^+ \subseteq X,\ M^- \cap Y = \emptyset \}
$$
- Consistent fixpoints of T_Π = three-valued supported models. Two-valued supported = T_Π(M)=M.
- *Stable operator* ST_Π yields Gelfond-Lifschitz operator GL_Π(M) = ST_Π'(M,M).
- *Well-founded model* = lfp(ST_Π).
- *M-stable model* (X,Y): ST_Π(X,Y)=(X,Y) and (X,Y) ≤_i-maximal. *L-stable*: Y\X is ⊆-minimal.
- Same maximisation/minimisation criteria define *M-/L-supported models* (p.45).

### Abstract argumentation frameworks (p.45-46)
- AF Θ = (A, R), R ⊆ A×A (attack).
- Attackers_Θ(a) := {b∈A | (b,a)∈R}; Attacked_Θ(S) := {b∈A | ∃a∈S: (a,b)∈R}; *defends*: Attackers_Θ(a) ⊆ Attacked_Θ(S).
- *Characteristic function* F_Θ(S) := {a∈A | S defends a}; ⊆-monotone; lfp = grounded extension.
- *Unattacked* operator U_Θ(S) := A \ Attacked_Θ(S); antimonotone; fixpoints = stable extensions.
- Conflict-free iff S ⊆ U_Θ(S).
- *Complete*: conflict-free fixpoint of F_Θ. *Admissible*: conflict-free with S ⊆ F_Θ(S). *Preferred*: ⊆-maximal complete. *Semi-stable*: complete with ⊆-maximal range E ∪ Attacked_Θ(E). *Naive*: ⊆-maximal conflict-free. *Stage*: conflict-free with ⊆-maximal range.
- Union of AFs: (A1,R1) ∪ (A2,R2) := (A1∪A2, R1∪R2).
- Running AF example θ: A={a,b,c,d}, R={(a,b),(c,d),(d,c)}. Grounded G={a}, two stable E1={a,c}, E2={a,d}; G,E1,E2 are the only complete extensions.

### Abstract dialectical frameworks (Definition 2.4, p.46)
ADF Ξ = (S, L, C):
- S = set of statements
- L ⊆ S × S = set of links; par(s) := {r∈S | (r,s)∈L}
- C = {C_s}_{s∈S}, C_s : 2^{par(s)} → {in, out} (acceptance functions)

Equivalent set representation: C_s^in := {M ⊆ par(s) | C_s(M)=in}; ADF then written (S, L, C^in).
Acceptance conditions also expressible as propositional formulas φ_a over par(a) (two-valued models = C_a^in) or via weights and proof standards.

Running ADF example D (Example 2.1, p.46): S={a,b,c,d}, L={(a,c),(b,b),(b,c),(b,d)}, C_a^in={∅}, C_b^in={{b}}, C_c^in={{a,b}}, C_d^in={∅}.
- a: no parents, always in.
- b: self-supporting (cyclic).
- c: jointly supported by a AND b.
- d: attacked by b (in iff b out).

### BW semantics for ADFs (p.47)
- *Conflict-free*: for all s∈M, M ∩ par(s) ∈ C_s^in.
- *Model*: for each s∈S, s∈M iff M ∩ par(s) ∈ C_s^in.
- Conflict-free sets of D: ∅, {a}, {b}, {d}, {a,b}, {a,d}, {a,b,c}.
- Models of D: M1={a,b,c}, M2={a,d}.
- *Bipolar* ADF (BADF): every link is supporting or attacking.
  - Supporting (r,s): R∈C_s^in ⇒ R∪{r}∈C_s^in.
  - Attacking (r,s): R∪{r}∈C_s^in ⇒ R∈C_s^in.
  - L^+ supporting links, L^- attacking links.
- *BW-stable model* of bipolar Ξ: M is least model of reduced ADF Ξ^M = (S^M, L^M, C^M) where S^M = S∩M, L^M = supporting links restricted, C_s^M(B)=in iff C_s(B)=in.
- Removing R from Ξ: Ξ - R = (S\R, L ∩ (S\R)^2, restricted C^in).
- *BW-admissible* (bipolar): exists R⊆S with no attacks from R to M and M is stable model of Ξ-R.
- *BW-preferred*: ⊆-maximal BW-admissible.
- *BW-grounded operator* Γ_Ξ : 2^S × 2^S → 2^S × 2^S (p.47):
$$
\Gamma'_\Xi(X,Y) := \{s \in S \mid \forall X \subseteq Z \subseteq Y,\ Z \cap par(s) \in C_s^{in}\}
$$
$$
\Gamma''_\Xi(X,Y) := \{s \in S \mid \exists X \subseteq Z \subseteq Y,\ Z \cap par(s) \in C_s^{in}\}
$$
- ≤_i-least fixpoint = *BW-well-founded model*. For D: ({a},{a,b,c,d}) → BW-wf model = {a}.

## §3 Approximating semantics for ADFs (pp.48-58)

### §3.1 The characteristic operator (Definition 3.1, p.48)
For Ξ = (S, L, C^in), define G_Ξ : 2^S × 2^S → 2^S × 2^S by
$$
\mathcal{G}_\Xi(X,Y) := (\mathcal{G}_\Xi'(X,Y), \mathcal{G}_\Xi'(Y,X))
$$
$$
\mathcal{G}_\Xi'(X,Y) := \{ s \in S \mid \exists B \in C_s^{in},\ B \subseteq X,\ (par(s) \setminus B) \cap Y = \emptyset \}
$$
Two-valued one-step consequence: G_Ξ(X) := G_Ξ'(X,X).

**Lemma 3.1 (p.49):** s ∈ G_Ξ(X) iff X ∩ par(s) ∈ C_s^in.
**Proposition 3.2 (p.49):** G_Ξ is ≤_i-monotone (so it is approximating, has fixpoints, and SG_Ξ exists).

### §3.1.1 Conflict-freeness (p.49)
**Proposition 3.3:** M ⊆ S conflict-free for Ξ iff M ⊆ G_Ξ(M) (postfixpoint).

### §3.1.2 Model semantics (p.49-50)
**Proposition 3.4:** M is a model of Ξ iff G_Ξ(M,M) = (M,M). "Two-valued supported model".

### §3.1.3 Stable models (p.50-52)
- **Example 3.1:** ξ with S={a,b}, L={(a,a),(a,b),(b,b)}, C_a^in={{a}}, C_b^in={∅,{a},{b}}. M={b} is a BW-stable model but G_ξ has no two-valued stable model with that lower bound (b's containment in upper bound makes par(b)∩{b}={b}≠∅).
- **Lemma 3.5:** For bipolar Ξ and (M,M) two-valued supported model, G_Ξ'(X,M) ⊆ G_{Ξ^M}(X) for X⊆M.
- **Lemma 3.6:** If M is the least fixpoint of G_Ξ'(·,M), it is the least fixpoint of G_{Ξ^M}.
- **Proposition 3.7 (p.51):** For bipolar Ξ, if (M,M) is a two-valued stable model then M is a BW-stable model. Converse fails.
- **Proposition 3.8 (p.51):** For approximating O on a bilattice, SO(x,x)=(x,x), SO(y,y)=(y,y), x⊑y ⇒ x=y. (Two-valued stable models cannot be in subset relation. ⇒ no approximating operator can reconstruct BW-stable models.)
- **Definition 3.2 (operator-inspired reduct, p.52):** Ξ_M = (S, L, C_M^in) with B ∈ C_{M,s}^in iff B ∈ C_s^in and (par(s)\B) ∩ M = ∅. M is a *stable model* of Ξ iff M is the unique least model of Ξ_M. Works for all ADFs (not just bipolar).
- **Proposition 3.9 (p.52):** (M,M) is a two-valued stable model of G_Ξ iff M is a stable model of Ξ. Equivalence of operator-based and reduct-based definitions.
- **Example 3.3 (p.52):** Re-examining ξ with new reduct: ξ_{M2={a,b}} has C_{M2,b}^in={{a,b}}, whose least model is {a}≠{a,b}, so {a,b} not stable; ξ_{M1={a}} stable as expected.

### §3.1.4 Admissibility (p.52-53)
- **Example 3.4 (p.52):** ξ with S={a,b}, L={(a,b),(b,a)}, C_a^in={{b}}, C_b^in={{a}} (mutually supporting). {a,b} is two-valued supported model but NOT BW-admissible.
- **Example 3.5 (p.53):** Bipolar ξ with S={a,b,c,d}, L={(b,a),(c,a),(d,c)}, C_a^in={∅,{b},{c}}, C_b^in={∅}, C_c^in={{d}}, C_d^in={∅}. M={a,b} is BW-admissible (R={d} with no attacks from R to M). But d is by definition always in, so the BW-admissible condition cannot truly become true. ⇒ BW-admissibility is too liberal (also too restrictive in Ex 3.4).
- **Definition 3.3 (admissible pair, p.53):** Consistent (M,N) is admissible in Ξ iff (M,N) ≤_i G_Ξ(M,N), i.e., M ⊆ G_Ξ'(M,N) (justified lower) and G_Ξ'(N,M) ⊆ N (justified upper). Generalises AF admissibility (proven later); every two-valued supported model is admissible.

### §3.1.5 Preferred semantics (p.53)
- **Theorem 3.10 (p.53):** For approximating O on (L^2,≤_i): any ≤_i-maximal admissible pair is a three-valued supported model (fixpoint). Argumentation-style "preferred ⇒ complete".
- **Corollary 3.11:** Any ≤_i-maximal admissible ADF pair is three-valued supported model.
- ⇒ Two equivalent ADF preferred semantics: M-supported models of G_Ξ (≤_i-maximal fixpoints), or M-stable models of SG_Ξ.

### Well-founded semantics (p.54)
- **Lemma 3.12:** Brewka-Woltran's grounded operator Γ_Ξ is exactly the *ultimate approximation* U_Ξ of G_Ξ (conjectured by Truszczyński in personal communication).
- **Corollary 3.13:** BW-well-founded = ultimate Kripke-Kleene of Ξ.
- BW-wf can differ from lfp(SG_Ξ) (the standard well-founded). For D, ultimate KK = ({a},{a,b,c,d}); lfp(SG_D) = ({a,d},{a,d}) which is also the unique two-valued stable model M2.

### §3.2 ADFs → Logic Programs (p.55-56)
- **Definition 3.4 (standard LP translation):** Π(Ξ) := { s ← (M ∪ not(par(s)\M)) | s∈S, M ∈ C_s^in }.
- Example: D translates to {a←∅, b←b, c←{a,b}, d←not b}.
- **Lemma 3.14 (p.55):** G_Ξ = T_{Π(Ξ)} (operators identical).
- **Theorem 3.15 (p.55):** Ξ and Π(Ξ) coincide on all approximation-operator-based semantics (KK, supported, stable, well-founded, M-/L-versions). Modular w.r.t. disjoint-statement union.
- Translation is polynomial, faithful, modular (PFM) for disjoint-statement unions; not modular when statements overlap (Example 3.7: a supported by {b} in Ξ1, by {c} in Ξ2 — union LP {a←b, a←c} has stable model {a,b,c} but in union ADF acceptance is intersection {b}∩{c}={∅}? actually conjunction {b,c}: a always out).

### §3.3 LPs → ADFs (p.56-57)
- **Definition 3.5 (Brewka-Woltran translation):** Ξ(Π) = (A, L, C^in) with L = {(b,a) | a←M ∈ Π, b ∈ M^+ ∪ M^-}, C_a^in = {B ⊆ par(a) | a←M ∈ Π, M^+ ⊆ B, M^- ∩ B = ∅}. Equivalently φ_a := ⋁_{a←M ∈ Π} (⋀_{m∈M^+} m ∧ ⋀_{m∈M^-} ¬m).
- **NOT modular:** all rules with head a needed.
- **NOT faithful w.r.t. three-valued supported semantics** (Example 3.8: π1 and π2 have same Ξ(π_i) but different 3-valued supported models).
- **Lemma 3.16 (p.56):** T_Π = G_{Ξ(Π)} on two-valued.
- **Corollary 3.17 (p.57):** G_Ξ(X,X)=(X,X) iff T_Π(X,X)=(X,X). Two-valued supported correspondence.
- **Lemma 3.18 (p.57):** SG_{Ξ(Π)}(X,X)=(X,X) implies ST_Π(X,X)=(X,X). Converse fails (Example 3.9: π={a←∅, a←a}).
- Ultimate approximations of T_Π and G_{Ξ(Π)} are identical, so ultimate semantics coincide; standard semantics may differ (cost of ultimate machinery).

## §4 Special case: argumentation frameworks (pp.57-)
- AF lattice (2^A,⊆), bilattice (2^A × 2^A, ≤_i) = 4-valued labellings (in/out/undec/inconsistent).
- **Proposition 4.1 (p.58):** G_{Ξ(Θ)}(X,Y) = (U_Θ(Y), U_Θ(X)). I.e., F_Θ (4-valued AF approximating operator) is the canonical approximation of U_Θ.
- **Lemma 4.2:** SF_Θ = F_Θ (AF characteristic operator IS its own stable operator). Surprising collapse — for AFs, supported = stable, well-founded = Kripke-Kleene.
- Consequence (p.58): "for AFs, Moore expansions and Reiter extensions coincide" — AFs are *less* semantically rich than ADFs/LPs/default-logic/autoepistemic.

### §4.1 Fixpoint semantics for AFs (p.58-59)
- **Lemma 4.3 (= Dung [14, Lemma 45]):** F_Θ = U_Θ^2, so F_Θ^2(X,Y) = (U_Θ^2(X), U_Θ^2(Y)) = (F_Θ(X), F_Θ(Y)).
- **Proposition 4.4:** E ⊆ A is stable extension iff F_Θ(E,E) = (E,E).
- **Proposition 4.5:** E is complete iff for some E'⊆A, (E,E') is consistent fixpoint of F_Θ.
- **Corollary 4.6:** E is grounded iff for some E', (E,E') is ≤_i-least fixpoint of F_Θ.
- **Proposition 4.7:** E is preferred iff for some E', (E,E') is consistent fixpoint with E ⊆-maximal (M-supported/M-stable for F_Θ).
- **Proposition 4.8:** E is semi-stable iff for some E', (E,E') is consistent fixpoint with E'\E ⊆-minimal (L-supported/L-stable).
- **Proposition 4.9:** X is admissible set for Θ iff (X, U_Θ(X)) is admissible pair for F_Θ. ADF-admissibility properly generalises AF-admissibility.
- Connection to Jakobovits & Vermeir [24] 4-valued labellings (in={+}, out={-}, undec={+,-}, irrelevant=∅).

### §4.1 (cont'd) JV-labellings (p.60)
- **Definition 4.1 (Jakobovits-Vermeir):** JV-labelling l : A → 2^{+,-} satisfying: (1) -∈l(a) ⇒ ∃b: (b,a)∈R, +∈l(b); (2) +∈l(a) ⇒ ∀(b,a)∈R: -∈l(b); (3) +∈l(a) ⇒ ∀(a,c)∈R: -∈l(c). *Total* iff l(a)≠∅.
- **Proposition 4.10 (p.60):** (X,Y) corresponds to JV-labelling iff X = F_Θ'(X,Y) and Y ⊆ F_Θ''(X,Y); consistent iff JV-labelling total.
- Pairs (X,Y) corresponding to JV-labellings characterised by (X,Y) ≤_t F_Θ(X,Y) and F_Θ(X,Y) ≤_i (X,Y).

### §4.2 AF → LP translations (p.60-63)
- **§4.2.1 Standard translation (p.61):** Π(Θ) := { a ← not Attackers_Θ(a) | a ∈ A }. NOT modular w.r.t. arguments (LP rule for a depends on all attackers); IS modular w.r.t. statements after going via Ξ(Θ). Finite bodies iff finitary AF.
- **Corollary 4.11:** F_Θ = T_{Π(Θ)}.
- **Lemma 4.12:** T_{Π(Θ)} = F_Θ = SF_Θ = ST_{Π(Θ)}.
- **Theorem 4.13 (p.61) — main correspondence for standard translation:** For any AF Θ:
  1. grounded ext = Kripke-Kleene model of Π(Θ) = well-founded model of Π(Θ);
  2. complete ext = 3-valued supported models of Π(Θ) = 3-valued stable models of Π(Θ);
  3. preferred ext = M-supported = M-stable models of Π(Θ);
  4. semi-stable ext = L-supported = L-stable models of Π(Θ);
  5. stable ext = 2-valued supported = 2-valued stable models of Π(Θ).
  (Items 2,3,4 new beyond Wu et al.)

- **§4.2.2 Dung's translation (p.61-63):** Define -A := {-a | a∈A}, A^± := A ∪ -A.
  $$\Pi_D(\Theta) := \{ a \leftarrow not\ \text{-}a \mid a \in A \} \cup \{ \text{-}a \leftarrow b \mid (b,a) \in R \}$$
  Modular w.r.t. arguments AND attacks; bodies always finite. Argument a accepted (atom a) unless defeated (atom -a); -a true if attacked by some accepted argument.
- **Definition 4.3 (coherent pair, p.62):** (S*,P*) ⊆ A^± × A^± coherent iff for all a∈A: a∈S* iff -a∉P*, and a∈P* iff -a∉S*. Lift co(S,P) := (S ∪ -P̄, P ∪ -S̄). co(S,P) is coherent.
- **Theorem 4.14 (p.62):** T_Π(S,P) = (S,P) iff T_{Π_D}(co(S,P)) = co(S,P). Maps fixpoints of T_Π to those of T_{Π_D} via co(·).
- **Proposition 4.15:** Coherent pairs are the *only* fixpoints of T_{Π_D}.
- **Theorem 4.16 (p.63):** Same five-item correspondence as Theorem 4.13 but for Dung's translation Π_D(Θ).

### §4.3 LP → AF (p.63)
- Dung's two translations (Sections 4.3.1, 4.3.2 of Dung 1995):
  - First: polynomial, faithful w.r.t. 2-valued supported models and KK semantics, NOT modular, NOT faithful w.r.t. 2-valued stable models. Counter-example: π={a←a} has only 2-v stable model ∅, but its AF ({a,¬a}, {(a,¬a),(¬a,a)}) has two stable extensions.
  - Second: at least exponential in |A|.
- Strass conjectures NO polynomial+modular+faithful translation exists from LPs to AFs (because supported≠stable for LPs but supported=stable for AFs).

## §5 General semantics for approximating operators (p.63-67)
Section synthesises a uniform operator-based vocabulary.

### §5.1 Admissible (Definition 5.1, p.63)
Consistent (x,y) ∈ L^2 admissible for O iff (x,y) ≤_i O(x,y). Equiv to Denecker et al. *O-reliable* pairs.

### §5.2 Semi-stable (p.64)
Requires a "negation" ·^{-1} : L → L on (L, ⊑) with: (x^{-1})^{-1} = x; (x ⊔ y)^{-1} = x^{-1} ⊓ y^{-1}; (x ⊓ y)^{-1} = x^{-1} ⊔ y^{-1} (de Morgan). For sets, complement w.r.t. universe.
- **Definition 5.2:** consistent (x,y) is *L-supported* iff fixpoint of O and y ⊓ x^{-1} is ⊑-minimal; *L-stable* iff fixpoint of SO and y ⊓ x^{-1} is ⊑-minimal. Generalises semi-stable.

### §5.3 Conflict-free (p.64-65)
- **Definition 5.3:** Consistent (x,y) is *conflict-free* iff x ⊑ O''(x,y) ⊑ y. Asymmetric: only the upper bound must improve.
- Alternative (rejected): require x ⊑ O'(x,y) ⊑ y instead. Counter-Example 5.2 shows this fails to generalise AF conflict-free sets.
- **Example 5.1 (Odd cycle):** θ = ({a,b,c}, {(a,b),(b,c),(c,a)}). Conflict-free pairs: (∅,{a,b,c}), ({a},{a,b,c}), ({b},{a,b,c}), ({c},{a,b,c}), ({a},{c,a}), ({b},{a,b}), ({c},{b,c}).
- **Proposition 5.1:** Admissible ⇒ conflict-free.
- **Proposition 5.2 (p.65):** X conflict-free in AF iff (X, U_Θ(X)) is conflict-free pair.
- **Proposition 5.3:** Conflict-free pair = Caminada's conflict-free labelling [7, Def 3].

### §5.4 Naive (Definition 5.4, p.65)
Consistent (x,y) is *M-conflict-free* iff ≤_i-maximal among conflict-free pairs.
- **Proposition 5.4 (p.66):** X is naive extension of AF iff (X, U_Θ(X)) is M-conflict-free pair.

### §5.5 Stage (p.66)
- **Proposition 5.5:** (X,Y) is argumentation stage [Verheij] iff Y = U_Θ(X).
- **Definition 5.5:** Consistent (x,y) is *L-conflict-free* iff y ⊓ x^{-1} is ⊑-minimal among conflict-free pairs.
- **Proposition 5.6:** X is stage extension of AF iff (X, U_Θ(X)) is L-stage pair of F_Θ.

### Master Table 1 (p.67, operator-based semantics — verbatim)

| Notion | Defining condition |
|---|---|
| conflict-free pair (x,y) | x ⊑ O''(x,y) ⊑ y |
| M-conflict-free pair (x,y) | conflict-free AND ≤_i-maximal |
| L-conflict-free pair (x,y) | conflict-free AND y ⊓ x^{-1} ⊑-minimal |
| admissible/reliable pair (x,y) | (x,y) ≤_i O(x,y) |
| Kripke-Kleene | lfp(O) |
| three-valued supported model (x,y) | O(x,y)=(x,y) |
| M-supported model (x,y) | fixpoint AND ≤_i-maximal |
| L-supported model (x,y) | fixpoint AND y ⊓ x^{-1} ⊑-minimal |
| two-valued supported model (x,x) | O(x,x)=(x,x) |
| well-founded | lfp(SO) |
| three-valued stable model (x,y) | SO(x,y)=(x,y) |
| M-stable model (x,y) | SO-fixpoint AND ≤_i-maximal |
| L-stable model (x,y) | SO-fixpoint AND y ⊓ x^{-1} ⊑-minimal |
| two-valued stable model (x,x) | SO(x,x)=(x,x) |

### Fig. 1 (p.67) inclusion lattice
Subset relations (arrow = "⊆"):
- two-valued stable → two-valued supported → three-valued supported (complete) → conflict-free → admissible
- L-stable (semi-stable) ⊆ L-supported (semi-stable) ⊆ L-conflict-free (stage)
- M-stable (preferred) ⊆ M-supported (preferred) ⊆ M-conflict-free (naive)
- well-founded (grounded) ⊆ three-valued stable
- Kripke-Kleene (grounded) ⊆ three-valued supported
- All M-/L-/2-valued versions ⊆ corresponding 3-valued

### Table 2 (p.68) AF / Op / ADF correspondence
| Operator-based | AF semantics | ADF semantics |
|---|---|---|
| **conflict-free pair** | conflict-free set/lab. | conflict-free set/**pair** |
| **M-conflict-free pair** | naive extension | **M-conflict-free pair** |
| **L-conflict-free pair** | stage extension | **L-conflict-free pair** |
| reliable pair | admissible set | **admissible pair** |
| Kripke-Kleene semantics | grounded extension | **Kripke-Kleene semantics** |
| ultimate Kripke-Kleene | grounded extension | BW-well-founded model |
| three-valued supported model | complete extension | **three-valued supported model** |
| **M-supported model** | preferred extension | **M-supported model** |
| **L-supported model** | semi-stable extension | **L-supported model** |
| two-valued supported model | stable extension | (two-valued supported) model |
| well-founded semantics | grounded extension | **well-founded semantics** |
| three-valued stable model | complete extension | **three-valued stable model** |
| **M-stable model** | preferred extension | **M-stable model** |
| **L-stable model** | semi-stable extension | **L-stable model** |
| two-valued stable model | stable extension | **two-valued stable model** |

(Bold = newly defined in this paper.)

### Fig. 2 (p.68) Relative expressiveness of NMR formalisms
- Solid = polynomial+faithful+modular (PFM) translation that preserves all operator-based semantics.
- Dotted = polynomial but non-modular, faithful only w.r.t. 2-valued (BW-)stable.
- Hierarchy: AFs → ADFs → LPs → DL → AEL.
  - AFs → ADFs: solid (Brewka-Woltran [3]).
  - AFs → LPs: solid (Theorem 4.16 / Strass).
  - ADFs → LPs: solid (Theorem 3.15 / Strass).
  - ADFs → AFs: dotted (Brewka et al. [4]).
  - LPs → ADFs: dotted (Brewka-Woltran [3]).
  - LPs → DL: solid (Marek-Truszczyński → Denecker et al.).
  - DL → AEL: solid (Konolige → Denecker et al.).

## §6 Conclusion (p.67-69)
- ADFs embedded into DMT lattice-theoretic AFT framework.
- Standard ADF semantics reconstructed; new admissible/preferred/semi-stable/stage/naive defined for non-bipolar ADFs.
- ADF↔LP equivalence via standard translation (PFM).
- AF↔LP via standard translation (Wu et al. extended) and Dung's translation (new); both equivalent.
- AFs are *less* expressive than LPs/ADFs (supported = stable, well-founded = KK collapse).

### Future work
- ADF union when statements overlap (Example 3.7).
- Compare BW ultimate semantics (Brewka et al. [5]) with Strass's semantics.
- New default/AEL semantics (admissible, preferred, semi-stable, stage).
- New LP semantics (conflict-free, admissible, naive, stage).
- Computational complexity of new ADF semantics.

## Parameters / Operators / Quantities

| Name | Symbol | Domain | Page | Notes |
|------|--------|--------|------|-------|
| Approximating operator | O | L^2 → L^2 | p.43 | symmetric & ≤_i-monotone |
| Information ordering | ≤_i | on L^2 | p.43 | (x1,y1)≤_i(x2,y2) iff x1⊑x2, y2⊑y1 |
| Truth ordering | ≤_t | on L^2 | p.43 | (x1,y1)≤_t(x2,y2) iff x1⊑x2, y1⊑y2 |
| Stable operator | SO | L^2 → L^2 | p.44 | SO(x,y) := (cO(y), cO(x)); cO(y) := lfp(O'(·,y)) |
| Ultimate approximation | U_O | L^2 → L^2 | p.44 | U_O'(x,y) = ⊓{O(z) | x⊑z⊑y}, U_O''(x,y) = ⊔{O(z) | x⊑z⊑y} |
| LP one-step (4-val) | T_Π | 2^A × 2^A → 2^A × 2^A | p.45 | T_Π'(X,Y) = {a | a←M, M^+⊆X, M^-∩Y=∅} |
| AF characteristic | F_Θ | 2^A → 2^A | p.46 | F_Θ(S) = {a | S defends a}; lfp = grounded |
| AF unattacked | U_Θ | 2^A → 2^A | p.46 | A \ Attacked_Θ(S); fixpoints = stable |
| AF 4-valued operator | F_Θ (= F_Θ) | 2^A × 2^A → 2^A × 2^A | p.58 | Canonical approximation of U_Θ |
| ADF characteristic | G_Ξ | 2^S × 2^S → 2^S × 2^S | p.48 | G_Ξ'(X,Y) = {s | ∃B∈C_s^in: B⊆X, (par(s)\B)∩Y=∅} |
| BW grounded operator | Γ_Ξ | 2^S × 2^S → 2^S × 2^S | p.47 | = ultimate U_Ξ (Lemma 3.12) |
| Stable reduct | Ξ_M | ADF | p.52 | C_{M,s}^in = {B∈C_s^in | (par(s)\B)∩M=∅} |
| Standard ADF→LP | Π(Ξ) | LP | p.55 | {s ← M ∪ not(par(s)\M) | s∈S, M∈C_s^in} |
| Standard AF→LP | Π(Θ) | LP | p.61 | {a ← not Attackers(a) | a∈A} |
| Dung's AF→LP | Π_D(Θ) | LP over A^± | p.61 | {a ← not -a} ∪ {-a ← b | (b,a)∈R} |
| Coherent lift | co(S,P) | A^± pair | p.62 | (S ∪ -P̄, P ∪ -S̄) |

## Methods & Implementation Details
- **ADF representation:** triple (S, L, C^in) where each C_s^in ⊆ 2^{par(s)}; alternatively propositional formula φ_s over par(s) such that 2-valued models = C_s^in. *(p.46)*
- **Computing G_Ξ(X,Y):** for each s∈S, scan C_s^in for B ⊆ X with (par(s)\B) ∩ Y = ∅. Worst case |S| × |C_s^in| × |par(s)| but tractable per statement. *(p.48)*
- **Stable reduct algorithm (Definition 3.2, p.52):** Build Ξ_M; compute least model of Ξ_M (well-defined since reduct admits unique least model only when M is stable; in general use ST_Π or iterate G_{Ξ_M}). Check equality to M.
- **AF semantics via F_Θ:** all major semantics (grounded, stable, complete, preferred, semi-stable, admissible) computable as fixpoints/maximal/minimal fixpoints of single 4-valued operator F_Θ(X,Y) = (U_Θ(Y), U_Θ(X)). *(p.58-59)*
- **Conflict-free as postfixpoint:** M ⊆ G_Ξ(M). *(p.49)*
- **Standard translation Π(Ξ) algorithm:** for each s∈S, for each M∈C_s^in, emit clause s ← (M ∪ not(par(s)\M)). Linear in size. *(p.55)*
- **Dung translation Π_D(Θ) algorithm:** for each a∈A emit a ← not -a; for each (b,a)∈R emit -a ← b. Linear in |A|+|R|. *(p.61)*
- **Translation equivalence check:** wrap a fixpoint S of T_Π into co(S,P) to get fixpoint of T_{Π_D}; project back via -A. *(Theorem 4.14, p.62)*

## Figures of Interest
- **Fig. 1 (p.67):** Inclusion lattice of operator-based semantics (16 nodes). Master diagram for the framework.
- **Fig. 2 (p.68):** Relative expressiveness graph AFs → ADFs → LPs → DL → AEL with PFM (solid) and weaker (dotted) translations. Locates AFs and ADFs in the NMR landscape.

## Limitations
- Translation Π : ADF → LP is **not modular** when statements overlap (Example 3.7, p.56). Future work to define ADF union for shared statements.
- Translation Ξ : LP → ADF (Brewka-Woltran) is **not faithful** w.r.t. 3-valued supported semantics (Example 3.8, p.56). Faithful only for 2-valued supported and ultimate semantics.
- LP → ADF stable-model preservation: only one direction (every Ξ(Π) stable model is Π stable model, NOT vice versa) — Example 3.9, p.57.
- BW-stable models cannot be reconstructed by *any* approximating operator under Definition 2.1 (Proposition 3.8, p.51) because they can be in subset relation. Strass's operator-based stable models are mutually incomparable.
- BW-admissible (Brewka-Woltran) is simultaneously too restrictive (Example 3.4) and too permissive (Example 3.5). Strass's Definition 3.3 fixes both.
- Computational complexity of new ADF semantics not analysed (left as future work).
- LP → AF: Strass conjectures NO PFM translation exists.

## Arguments Against Prior Work
- **Brewka-Woltran ADF semantics (BW-admissible, BW-preferred, BW-stable, BW-well-founded):** ad hoc, defined only for bipolar ADFs (except BW-well-founded), suffer from Examples 3.4/3.5 anomalies; BW-stable cannot be captured by any approximating operator. *(p.51-53)*
- **Brewka et al. [4] (ADF→AF translation):** depends on chosen ADF semantics; not modular when adding new statements (must retranslate); need separate translation for each semantics. *(p.42)*
- **Wu et al. [43]:** showed complete-ext = 3-valued stable models for AFs but did not address supported semantics or motivate the choice of "standard" translation. *(p.61)*
- **Caminada-Amgoud [8]:** identified anomalies in translations into AFs (cyclic-support pitfalls); Strass shows ADFs avoid these natively. *(p.40,42)*
- **Van Gijzel-Prakken [40] (Carneades→AF via ASPIC+):** even though it can deal with cycles, only one unique stable/preferred/complete/grounded extension; semantic richness lost; user can't choose to accept/reject cyclic positive dependencies. *(p.41)*
- **Dung's translations LP→AF (1995):** first translation polynomial+faithful only for 2-valued supported and KK, not modular and not faithful for 2-valued stable; second translation exponential. *(p.63)*

## Design Rationale
- **Why approximation theory:** Tarski-Knaster gives lattice of fixpoints of monotone O; Denecker et al. lift this to approximations on bilattice (L^2,≤_i) so a single algebraic recipe yields KK/supported/stable/well-founded semantics for any operator-defined formalism. ADFs naturally fit because acceptance conditions induce a 2-valued operator G_Ξ. *(p.43-44)*
- **Why 4-valued Belnap pairs (X,Y):** allows in/out/undec/inconsistent labels; consistent pairs (X⊆Y) = 3-valued labellings; lower bound = "definitely in" lower bound, upper bound = "possibly in" upper bound. *(p.43)*
- **Asymmetric conflict-free (Definition 5.3):** chose x ⊑ O''(x,y) ⊑ y over alternative x ⊑ O'(x,y) ⊑ y because the alternative fails to generalise AF conflict-free sets (Example 5.2). The asymmetry "any *in* statement must have a reason not to be *out*, and any *out* statement must have a reason to be *out*" — only upper bound improvement is required. *(p.65)*
- **Operator-inspired reduct (Definition 3.2) over BW-style:** works for *all* ADFs (not just bipolar); coincides with operator-based 2-valued stable models (Proposition 3.9). *(p.52)*
- **Two preferred-semantics candidates equivalent:** "argumentation way" (maximally admissible) and "logic-programming way" (M-supported = maximal 3-valued supported) coincide (Theorem 3.10). *(p.53)*
- **Why standard AF→LP wins over Dung's:** standard simpler, more uniform; Dung's more complex but modular w.r.t. attacks. Both produce equivalent semantics (Theorems 4.13 ↔ 4.16 + Theorem 4.14). *(p.61-63)*
- **Why ADFs as abstraction language:** ADFs are at least as expressive as AFs, at most as expressive as LPs (sweet spot); they natively distinguish supported vs stable (cyclic positive support), which AFs cannot. *(p.42)*

## Testable Properties
- **Prop 3.2:** G_Ξ is ≤_i-monotone for every ADF Ξ. *(p.49)*
- **Prop 3.3:** M conflict-free ⇔ M ⊆ G_Ξ(M). *(p.49)*
- **Prop 3.4:** M model of Ξ ⇔ G_Ξ(M,M) = (M,M). *(p.49)*
- **Prop 3.7:** For bipolar Ξ, two-valued stable model ⇒ BW-stable model. *(p.51)*
- **Prop 3.8:** SO(x,x)=(x,x), SO(y,y)=(y,y), x⊑y ⇒ x=y (operator-based 2-valued stable models incomparable). *(p.51)*
- **Prop 3.9:** Operator-based 2-valued stable model ⇔ reduct-based stable model (Definition 3.2). *(p.52)*
- **Theorem 3.10:** Any ≤_i-maximal admissible pair is a 3-valued supported model. *(p.53)*
- **Lemma 3.12:** Brewka-Woltran's Γ_Ξ = ultimate approximation U_Ξ of G_Ξ. *(p.54)*
- **Theorem 3.15:** ADF Ξ and standard LP Π(Ξ) coincide on all approximation-operator-based semantics. *(p.55)*
- **Lemma 4.2:** SF_Θ = F_Θ for any AF (operator collapse). *(p.58)*
- **Theorem 4.13:** 5-item AF↔LP correspondence under standard translation. *(p.61)*
- **Theorem 4.14:** T_Π(S,P)=(S,P) iff T_{Π_D}(co(S,P))=co(S,P). *(p.62)*
- **Theorem 4.16:** Same 5-item AF↔LP correspondence under Dung's translation. *(p.63)*
- **Prop 5.1:** Any admissible pair is conflict-free. *(p.65)*
- **Prop 5.2:** AF X conflict-free ⇔ (X, U_Θ(X)) conflict-free pair. *(p.65)*
- **Prop 5.4:** AF naive ⇔ M-conflict-free pair. *(p.66)*
- **Prop 5.6:** AF stage ⇔ L-conflict-free pair. *(p.66)*

## Relevance to Project
This paper is the canonical reference for:
1. **ADF semantics infrastructure.** Any implementation of ADF reasoning in the argumentation/ codebase should follow this paper's operator-based scheme: build G_Ξ, derive complete/preferred/grounded/stable via fixpoint computation on the bilattice. Avoid BW's ad hoc reduct definitions outside bipolar ADFs.
2. **PFM translation ADF↔LP (Theorem 3.15).** Justifies routing ADF reasoning through ASP solvers via Π(Ξ). Modular per disjoint statements; in our codebase this fits the ASP-backend workstream (notes/workstream-asp-backend-2026-05-01.md and reports/workstream-asp-backend.md). The translation is linear, parsable, and faithful — a strong implementation target.
3. **Theorem 4.13 / 4.16.** Five-item AF↔LP correspondence is the textbook foundation for ASP encodings of AFs (Egly-Gaggl-Woltran [15] in our collection — task #9). Strass extends Wu et al. by adding preferred (3), semi-stable (4), and stable (5) — directly relevant to our preferred/semi-stable workstreams.
4. **Operator collapse for AFs (Lemma 4.2: SF_Θ = F_Θ).** Important when translating reasoning techniques between AFs and ADFs: AFs cannot distinguish supported from stable; ADFs can. Our codebase's Dung-skeptical and ADF reasoning paths must respect this asymmetry.
5. **Conflict-free pair definition (asymmetric upper-bound improvement, Definition 5.3).** Justifies a particular labelling-based conflict-freeness check. Distinct from labelling intuitions in some QBAF/gradual literature.
6. **Lemma 3.12 (BW-well-founded = ultimate KK).** Tells us BW-grounded is the *ultimate* approximation, not the standard one — has implementation cost implications (ultimate is harder to compute).
7. **Coherent-pair lifting (Definition 4.3 / Theorem 4.14).** Relevant if argumentation/ ever needs to bridge between Dung-style and standard-style LP encodings.

## Open Questions
- [ ] How to define ADF union when constituent ADFs share statements? (Example 3.7) Is there a representation-independent merging operator?
- [ ] How do Strass's semantics compare to Brewka et al.'s [5] *ultimate* ADF semantics?
- [ ] Computational complexity (data complexity, combined complexity) of M-supported / L-supported / M-stable / L-stable / 3-valued supported / 3-valued stable for ADFs?
- [ ] Do the new conflict-free / admissible / naive / stage semantics for LPs coincide with any semantics from Eiter et al. [16] (paracoherent ASP)?
- [ ] Is there *any* polynomial-faithful-modular translation LP → AF? (Strass conjectures no.)

## Notable References Cited (key citation keys)
- [3] Brewka & Woltran 2010 — original ADF paper (KR 2010).
- [4] Brewka, Dunne & Woltran 2011 — ADF→AF translation (IJCAI).
- [5] Brewka, Ellmauthaler, Strass, Wallner, Woltran 2013 — ADFs revisited / ultimate semantics (IJCAI).
- [11] Denecker, Marek, Truszczyński 2000 — *Approximations, stable operators...* (foundational AFT).
- [12] Denecker, Marek, Truszczyński 2003 — uniform semantic treatment of default + autoepistemic (AIJ 143).
- [13] Denecker, Marek, Truszczyński 2004 — ultimate approximation (Inf. Comput. 192).
- [14] Dung 1995 — original AF paper (AIJ 77).
- [15] Egly, Gaggl, Woltran 2010 — answer-set encodings for AFs (Argument & Comp. 1).
- [18] Fitting 2002 — fixpoint semantics for LPs (Theor. Comput. Sci. 278).
- [22] Gottlob 1995 — translating default into AEL (J. ACM 42).
- [24] Jakobovits & Vermeir 1999 — robust 4-valued AF labellings (J. Log. Comput. 9).
- [25] Janhunen 1999 — intertranslatability of nonmonotonic logics.
- [27] Marek-Truszczyński 1989 — stable LPs and default theories.
- [38] Tarski 1955 — lattice-theoretic fixpoint theorem.
- [41] Verheij 1996 — argumentation stages.
- [43] Wu, Caminada, Gabbay 2009 — complete extensions = 3-v stable models in LPs.

## Quotes Worth Preserving
- "Generally speaking, it is at the heart of an abstraction to remove information; it is at the heart of a *good* abstraction to remove *irrelevant* information." *(p.41)*
- "Translated into logic programming language, we have that in Dung-style argumentation, supported and stable models coincide, and well-founded semantics equals Kripke-Kleene semantics. Put in different terms of default and autoepistemic logics: for argumentation frameworks, Moore expansions and Reiter extensions coincide!" *(p.58)*
- "It is not entirely clear how to define the union of two ADFs that share statements." *(p.69, future work)*

## Reading Progress
- DONE: pages 0-31 (all). Cover, intro, background §2, ADF semantics §3, AF special case §4, general semantics §5 with master Table 1 / Fig. 1, conclusion §6 with Table 2 / Fig. 2, references.

## Current Blocker
None. Notes complete.
