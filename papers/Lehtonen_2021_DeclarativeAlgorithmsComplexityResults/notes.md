---
title: "Declarative Algorithms and Complexity Results for Assumption-Based Argumentation"
authors: "Tuomo Lehtonen, Johannes P. Wallner, Matti Jarvisalo"
year: 2021
venue: "Journal of Artificial Intelligence Research"
doi_url: "https://doi.org/10.1613/jair.1.12479"
pages: "265-318"
---

# Declarative Algorithms and Complexity Results for Assumption-Based Argumentation

## One-Sentence Summary
This paper gives direct ASP encodings for reasoning in the logic-programming fragment of ABA and ABA+ and establishes new complexity results, especially showing that reverse attacks in ABA+ raise the complexity of several central reasoning and verification tasks. *(p.265-p.285)*

## Problem Addressed
Abstract argumentation algorithms had received extensive attention, but structured argumentation systems such as ABA remained less developed both algorithmically and complexity-theoretically, despite the internal structure of arguments making reasoning harder and more implementation-sensitive. *(p.266-p.267)*

Existing ABA solvers before this work either used specialized dispute derivations, such as ABAGRAPH, or translated ABA to abstract argumentation frameworks, such as ABA2AF and ABAPLUS. The paper targets a direct declarative route that encodes ABA reasoning tasks in ASP without first translating to AFs. *(p.267)*

The complexity of ABA+ with preferences was not fully established. The authors specifically study how reverse attacks induced by preferences affect verification and acceptance problems under standard ABA+ semantics. *(p.268, p.276-p.285)*

## Key Contributions
- Direct ASP-based computational approach for the commonly studied logic-programming fragment of ABA, covering ABA semantics admissible, complete, preferred, stable, grounded, and ideal, and ABA+ stable and grounded semantics. *(p.267-p.268)*
- Empirical evaluation, reported later in the paper, against available ABA/ABA+ systems, with an implementation released at `https://bitbucket.org/coreo-group/aspforaba`. *(p.267)*
- New complexity results for ABA+, including coNP-completeness of verifying <-admissibility, coNP-hardness of verifying <-complete and <-grounded sets, Sigma_2^P-completeness of credulous reasoning under <-admissibility, NP/coNP-completeness for <-stable reasoning, and Delta_2^P bounds for grounded reasoning under an FL-property restriction. *(p.268, p.276-p.285)*
- Formal properties used by the ASP encodings, including attacked-assumption characterizations, polynomial computation of ABA grounded semantics, equivalence constraints for tree- and forward-derivability, and polynomial checks for several types of ABA+ attacks. *(p.277-p.282)*

## Study Design (empirical papers)

## Methodology
The paper is theoretical and algorithmic. It first fixes a finite flat ABA fragment corresponding closely to ground normal logic programs, formalizes ABA and ABA+ semantics over assumption sets, establishes complexity and structural properties, then uses these properties as the basis for ASP encodings and an empirical solver evaluation. *(p.268-p.285)*

## Key Equations / Statistical Models

ABA framework:

$$
F = (\mathcal{L}, \mathcal{R}, \mathcal{A}, \overline{\ })
$$

Where: `\mathcal{L}` is a formal language or set of sentences, `\mathcal{R}` is a set of inference rules over `\mathcal{L}`, `\mathcal{A} \subseteq \mathcal{L}` is a non-empty set of assumptions, and `\overline{\ }` maps assumptions to their contraries in `\mathcal{L}`. *(p.269)*

Rule head and body:

$$
\mathrm{head}(r)=\{a_0\}, \qquad \mathrm{body}(r)=\{a_1,\ldots,a_n\}
$$

Where: a rule `r` has the form `a_0 <- a_1,...,a_n`, with all `a_i` in `\mathcal{L}`. *(p.268-p.269)*

LP-fragment correspondence:

$$
\mathcal{L} = HB \cup HB_{not}, \qquad \mathcal{R} = \pi, \qquad \mathcal{A}=HB_{not}, \qquad \overline{not\ a}=a
$$

Where: `HB` is a set of atoms, `HB_{not} = {not a | a in HB}`, and `\pi` is a ground normal logic program over `HB`. The paper generalizes this fragment by allowing more sentences and non-contrary sentences while preserving the same complexity as the LP fragment. *(p.269-p.270)*

Deductive closure:

$$
Th_{\mathcal{R}}(X)=\{a \in \mathcal{L} \mid X \vdash_{\mathcal{R}} a\}
$$

Where: `X` is an assumption set and `\vdash` is forward derivability under rules `\mathcal{R}`. *(p.272)*

Attacked assumptions:

$$
att(E)=\{a \in \mathcal{A} \mid E \text{ attacks } \{a\}\}
$$

Where: `E` is a set of assumptions; this set is central for polynomial checks of admissibility and completeness in ABA. *(p.278)*

ABA grounded-semantics iteration:

$$
S_0=(\emptyset, att(\emptyset), \mathcal{A}\setminus att(\emptyset))
$$

$$
S_i=(I_i,D_i,U_i), \qquad I_i=\mathcal{A}\setminus att(U_{i-1}), \quad D_i=att(I_i), \quad U_i=\mathcal{A}\setminus D_i
$$

Where: `I`, `D`, and `U` abbreviate in, defeated, and undefeated assumptions. The final `I_{|\mathcal{A}|}` is the grounded assumption set. *(p.279)*

3-CNF to ABA+ reduction:

$$
\phi = c_1 \land \cdots \land c_m
$$

$$
red(\phi)=(\mathcal{L},\mathcal{R},\mathcal{A},\overline{\ },\leq)
$$

Where: `\phi` is a Boolean 3-CNF formula over variables `X={x_1,...,x_n}`, and `red(\phi)` is the ABA+ framework used for hardness proofs. *(p.282-p.283)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| JAIR article page count | - | pages | 54 | 265-318 | 265 | The paper spans JAIR pages 265-318. |
| ABA framework component count | - | components | 4 | - | 269 | ABA is represented as language, rules, assumptions, and contrary mapping. |
| ABA+ framework component count | - | components | 5 | - | 274 | ABA+ adds a preorder over assumptions. |
| Grounded iteration bound | `|\mathcal{A}|` | iterations | - | 0 to `|\mathcal{A}|` | 279 | Grounded computation reaches a fixpoint after at most one new assumption per iteration. |
| 3-CNF clause width | - | literals/clause | 3 | max 3 | 282 | Hardness reductions use classical 3-CNF unsatisfiability. |
| Reduction rule count | `|\mathcal{R}|` | rules | `5|X|+|C|+1` | polynomial | 283 | For Reduction 1, five rules per variable, one per clause, and one extra rule. |
| Reduction sentence count | `|\mathcal{L}|` | sentences | `5|X|+4` | polynomial | 283 | Sentence vocabulary size in the constructed ABA+ framework. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| ABA complete credulous acceptance | complexity | NP-complete | - | - | LP fragment of ABA | 279 |
| ABA complete skeptical acceptance | complexity | in P | - | - | LP fragment of ABA | 279 |
| ABA grounded credulous/skeptical acceptance | complexity | in P | - | - | LP fragment of ABA | 278-p.279 |
| ABA+ <-stable verification | complexity | in P | - | - | LP fragment of ABA+ | 282 |
| ABA+ <-stable credulous acceptance | complexity | NP-complete | - | - | LP fragment of ABA+ | 282 |
| ABA+ <-stable skeptical acceptance | complexity | coNP-complete | - | - | LP fragment of ABA+ | 282 |
| ABA+ <-admissible verification | complexity | coNP-complete | - | - | LP fragment of ABA+ | 285 |
| ABA+ <-complete verification | complexity | coNP-hard | - | - | LP fragment of ABA+ | 285 |
| ABA+ <-grounded verification | complexity | coNP-hard | - | - | LP fragment of ABA+ | 285 |

## Methods & Implementation Details
- The paper focuses on finite flat ABA frameworks: `\mathcal{L}` is a set of atoms, `\mathcal{L}`, `\mathcal{R}`, and `\mathcal{A}` are finite, every rule body is finite, rules are explicit input, and rule heads cannot be assumptions. This rules out derived assumptions and supports polynomial derivability checks. *(p.269)*
- Under the LP-fragment correspondence, assumptions are default-negated atoms and contraries map `not a` to `a`. The considered fragment is a minor generalization of LP ABA, allowing more sentences and names while preserving the same complexity. *(p.269-p.270)*
- Tree derivability uses finite rooted labeled proof trees whose leaves are assumptions (or `T` for empty bodies), internal nodes map surjectively to rules, child labels equal the rule body, and node labels equal rule heads. Tree derivations are stricter because all assumptions and rules in the witness tree are required. *(p.271-p.272)*
- Forward derivability uses a sequence of rules `(r_1,...,r_n)` where the final head is the derived sentence and each rule body is already in the assumptions or earlier heads. Forward derivations allow redundant assumptions and rules. *(p.271-p.272)*
- Proposition 1: for ABA without preferences, tree and forward derivability correspond. If `X` tree-derives `s`, then `X` forward-derives `s`; if `X` forward-derives `s`, then some `X' subseteq X` and `R subseteq \mathcal{R}` tree-derive `s`. *(p.272)*
- ABA attack: assumption set `A` attacks assumption set `B` if some subset of `A` tree-derives the contrary of an assumption in `B`; equivalently, `A` forward-derives the contrary of some `b in B`. *(p.272)*
- ABA conflict-freeness and defense: `A` is conflict-free iff it does not attack itself; `A` defends `B` iff every assumption set attacking `B` is attacked by `A`. *(p.272)*
- ABA semantics considered: admissible, complete, grounded, preferred, stable, and ideal. The paper uses `sigma`-assumption set for assumption sets satisfying semantics `sigma in {adm, com, grd, stb, prf, ideal}`. *(p.273)*
- Grounded ABA can be equivalently characterized as the least fixpoint of `def_F(A)={a in \mathcal{A} | A defends {a}}`. *(p.274)*
- ABA verification task checks whether a given `S subseteq \mathcal{A}` is a `sigma`-assumption set. Enumeration reports all `sigma`-assumption sets. Credulous acceptance asks whether some `sigma`-assumption set derives a sentence; skeptical acceptance asks whether all `sigma`-assumption sets derive it. *(p.274)*
- ABA+ adds a preorder `<=` over assumptions. The strict preference relation `<` is `a < b` iff `a <= b` and not `b <= a`. *(p.274-p.275)*
- ABA+ `<`-attacks generalize ABA attacks with two cases: normal attacks, where an attacking subset derives a contrary without containing a member strictly less preferred than the target, and reverse attacks, where the target set derives a contrary of the attacker and contains a member strictly less preferred than that attacked assumption. *(p.275)*
- If no preferences are imposed in ABA+, normal `<`-attacks coincide with ABA attacks and reverse `<`-attacks do not arise. With preferences, a non-preference-based attack is either preserved or reversed, but not lost for conflict-freeness purposes. *(p.275)*
- Tree and forward derivability are not generally equivalent for ABA+ reverse attacks because redundant assumptions can weaken an attacker and create reverse attacks under forward derivability that do not exist under tree derivability. *(p.279-p.280)*
- Lemma 8 gives a useful special case: normal `<`-attacks can be checked using forward derivability, and if `A` is conflict-free then reverse `<`-attacking a singleton `{b}` can also be checked by forward derivability. *(p.280)*
- Proposition 9 restates `<`-stable semantics so an assumption `b` not normally `<`-attacked by `E` is acceptable only if either `b in E` or singleton `{b}` is reversely `<`-attacked by `E`. This is used later in the ASP encoding. *(p.280)*
- Proposition 11 identifies three polynomial-time ABA+ checks: whether `A` normally `<`-attacks `B`, whether `A` reversely `<`-attacks `B`, and whether `A` normally `<`-attacks each subset `B' subseteq B` that `<`-attacks `A`. *(p.281-p.282)*

## Figures of Interest
- **Figure 1 (p.270):** Running ABA example with sentences `{a,b,c,d,w,x,y,z}`, assumptions `{a,b,c,d}`, contraries `bar b=x`, `bar c=y`, `bar d=z`, and rules `{w<-a, y<-b,w, x<-c, z<-a,b}`. It also shows a tree derivation and forward derivation for `y`.
- **Table 1 (p.273):** Lists admissible assumption sets in the running example, their deductive closures, which ABA semantics they satisfy, and which ABA+ semantics they satisfy under preference `a<d`.
- **Table 2 (p.277):** Summarizes complexity of sentence acceptance in the LP fragment of ABA: admissible/complete/preferred/stable/grounded/ideal across credulous and skeptical reasoning.
- **Table 3 (p.277):** Summarizes new ABA+ complexity results for verifying assumption-set semantics and credulous/skeptical acceptance.
- **Figure 2 (p.284):** Example of Reduction 1 for formula `(x1 or x2 or not x3) and (not x1 or x2 or x3)`, listing the constructed ABA+ framework and which assumption sets `<`-attack or are `<`-attacked by `{a,b}`.

## Results Summary
The early theoretical results show that ordinary ABA in the LP fragment has polynomial grounded reasoning and complete-semantics verification, while ABA+ preferences create higher complexity through reverse attacks. In ABA+, stable reasoning preserves the same acceptance complexity as stable ABA, but admissibility and grounded/complete verification become harder. *(p.276-p.285)*

## Limitations
The paper intentionally restricts attention to a finite, flat, explicitly given, LP-like ABA fragment. It notes that derivability in more general deductive systems need not be polynomial-time decidable, so the results and encodings are scoped to the chosen fragment. *(p.269)*

For ABA+, some complexity table entries remain open or only partially bounded at this point in the paper: skeptical reasoning for <-admissible and both credulous and skeptical reasoning for <-complete are marked with question marks in Table 3. *(p.277)*

## Arguments Against Prior Work
- Prior ABA approaches either used specialized dispute derivation procedures or translated ABA into AFs before solving. The authors argue that a direct ASP encoding can cover multiple semantics and reasoning modes more uniformly. *(p.267)*
- Complexity of ABA+ had not been fully established, and prior P-ABA results were not directly transferable because P-ABA handles preferences differently from ABA+. *(p.276)*
- A preliminary version of the authors' own work had an erroneous grounded-semantics encoding; this JAIR version provides a new grounded encoding and fuller proofs. *(p.268)*

## Design Rationale
- The chosen flat LP-like ABA fragment matches the assumptions made by existing ABA implementations and makes derivability decidable in polynomial time, which is necessary for the ASP-oriented algorithmic results. *(p.269)*
- The ASP approach is motivated by the empirical success of ASP encodings for abstract argumentation and by the desire to avoid translation to AFs. *(p.267)*
- The paper retains tree derivability in the definition of ABA+ `<`-attacks because replacing it with forward derivability can introduce reverse attacks caused by redundant weaker assumptions. *(p.279-p.280)*
- The attacked-assumptions set `att(E)` is introduced because it gives implementation-friendly polynomial checks for ABA admissibility/completeness and supports the explicit grounded iteration used later in encodings. *(p.278-p.279)*

## Testable Properties
- In the considered ABA fragment, rule heads are never assumptions: `head(r) cap \mathcal{A}=emptyset`. *(p.269)*
- In ABA without preferences, if `X` tree-derives `s`, then `X` forward-derives `s`; if `X` forward-derives `s`, some subset `X'` and rule subset tree-derive `s`. *(p.272)*
- In ABA, set `E` is admissible iff `\mathcal{A}\setminus att(E)` does not attack `E`. *(p.278)*
- In ABA, set `E` is complete iff it is admissible and every `b in \mathcal{A}\setminus E` is attacked by `\mathcal{A}\setminus att(E)`. *(p.278)*
- The ABA grounded assumption set is computable in polynomial time by iterating `S_i=(I_i,D_i,U_i)` for at most `|\mathcal{A}|` steps. *(p.279)*
- Verifying `<`-stability in ABA+ is in P; credulous acceptance under `<`-stable semantics is NP-complete and skeptical acceptance is coNP-complete. *(p.282)*
- Verifying `<`-admissibility in ABA+ is coNP-complete. *(p.285)*
- Verifying `<`-complete or `<`-grounded assumption sets in ABA+ is coNP-hard. *(p.285)*

## Relevance to Project
This is directly relevant to an argumentation backend because it supplies formal semantics, complexity expectations, and ASP-oriented implementation hooks for ABA and ABA+ reasoning. It is especially useful for deciding which ABA+ tasks should be implemented as polynomial checks, NP/coNP calls, or higher-level solver workflows.

## Open Questions
- [ ] Table 3 leaves several ABA+ acceptance complexities open at this stage: skeptical <-admissible, credulous <-complete, and skeptical <-complete. *(p.277)*
- [ ] Later sections must be read for the concrete ASP encodings and empirical benchmark details before implementing the backend from this paper. *(p.267-p.268)*

## Related Work Worth Reading
- Bondarenko et al. (1997) for original ABA and grounded fixpoint characterization. *(p.269-p.274)*
- Dimopoulos et al. (2002), Dunne (2009), and Dvorak & Dunne (2018) for established ABA complexity. *(p.268, p.276-p.277)*
- Cyras and Toni / Bao et al. work on ABA+ preferences. *(p.266, p.274-p.275)*
- Craven and Toni dispute-derivation systems and ABA2AF/ABAPLUS translation-based systems for implementation comparison. *(p.267)*

