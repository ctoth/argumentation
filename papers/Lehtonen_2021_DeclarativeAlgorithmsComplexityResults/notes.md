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

## Additional Extraction: Complexity, Encodings, and Evaluation

### ABA+ Grounded and Admissible Complexity
- ABA+ frameworks satisfying the FL-property allow the grounded assumption set to be obtained by iterating the defense function from the empty set. The FL-property says that for any <-admissible `A` and any `x in def_F(A)`, `A union {x}` remains <-admissible. *(p.286)*
- Lemma 17: for a finite ABA+ framework satisfying the FL-property, `def_F^i(emptyset)` is the <-grounded assumption set for some `i >= 0`; the iteration reaches a fixpoint after at most `|\mathcal{A}|` applications in the same style as ordinary ABA. *(p.286)*
- Proposition 18: in ABA+ frameworks satisfying the FL-property, the <-grounded assumption set can be computed by a deterministic polynomial-time algorithm with access to an NP oracle; the proof bounds the computation by at most `|\mathcal{A}|^2` NP-oracle calls. *(p.287)*
- WCP, the Axiom of Weak Contraposition, implies the FL-property, but the authors emphasize that WCP does not make the overall ABA+ complexity mild: Proposition 14 and Theorem 15 hardness results still hold under WCP. *(p.287)*
- Theorem 19: credulous acceptance under <-admissible semantics in ABA+ is `Sigma_2^P`-complete, reflecting the need to guess an assumption set and verify <-admissibility, where the latter is coNP-complete. *(p.287)*

### ASP Preliminaries Used by the Encodings
- The implementation target is standard normal ASP with rules of the form `h <- b1,...,bk, not b{k+1},...,not bm`; `h` and all body atoms are atoms. The paper uses no ASP functions, variables are uppercase, and constants are lowercase. *(p.288)*
- A non-ground program is grounded by all substitutions from variables to constants. An interpretation satisfies a positive rule if all positive body atoms being in the interpretation implies the head is also in the interpretation. Answer sets are defined via the Gelfond-Lifschitz reduct. *(p.288)*
- The implementation uses CLINGO for answer-set existence/enumeration and cautious reasoning, and ASPRIN for subset-maximal optimization over a unary predicate, especially to compute preferred assumption sets. *(p.288)*

### ASP Input Representation
- A given ABA framework `F=(\mathcal{L},\mathcal{R},\mathcal{A},bar)` with rules `R={r1,...,rn}` is represented as facts `assumption(a)`, `head(i,b)`, `body(i,b)`, and `contrary(a,b)`. The rule index `i` links heads and bodies. *(p.289)*
- Example 10 maps an ABA framework with sentences `{a,b,x,y}`, assumptions `{a,b}`, contraries `bar a=y`, `bar b=x`, and rules `{x <- a,y; y <- b}` into facts `assumption(a). assumption(b). head(1,x). body(1,a). body(1,y). head(2,y). body(2,b). contrary(a,y). contrary(b,x).` *(p.289)*
- Query sentences are represented by adding `query(s)` to the semantics encoding. Later descriptions identify predicates with the set of constants for which they hold. *(p.289)*

### Common ABA Encoding
- Listing 1 defines `pi_common`, the reusable ASP module for conflict-free assumption sets and forward derivations: `in(X)`/`out(X)` guess assumption membership; `supported(X)` derives assumptions in the set and rule heads whose bodies are supported; `triggered_by_in(R)` checks rule body support; `defeated(X)` marks attacked assumptions; and the final constraint rejects any set containing an assumption it attacks. *(p.290)*
- Credulous acceptance is checked by adding a constraint that rules out answer sets where the query is not supported: `<- not supported(X), query(X).` Skeptical acceptance is checked by searching for a counterexample using `<- supported(X), query(X).`; if the resulting program has no answer set, the query is skeptically accepted. *(p.290)*

### ABA Semantics Encodings
- Stable semantics adds the constraint `<- out(X), not defeated(X).`, forcing every assumption to be either selected or attacked by the selected set. *(p.291)*
- Admissibility uses Proposition 4: a conflict-free set is admissible iff undefeated assumptions do not attack it. Listing 2 computes derivability from undefeated assumptions and constrains against selected assumptions attacked by undefeated assumptions. *(p.291)*
- Complete semantics extends admissibility with a constraint excluding any `out` assumption that is not attacked by undefeated assumptions, i.e. assumptions defended by `in` must be included. *(p.291)*
- Preferred semantics uses ASPRIN subset-maximal optimization over `in`: `#preference(p1,superset){in(X): assumption(X)}.` and `#optimize(p1).` over the admissibility encoding. *(p.291)*
- Grounded ABA semantics is encoded in Listing 3 using Lemma 7's explicit iteration. The number of iterations is the number of assumptions; `in(X,I)` represents `I_i`, `defeated(X,I)` represents `D_i`, and `not defeated` represents `U_i`; the final iteration gives the grounded assumption set. *(p.292)*
- The authors explicitly warn that the grounded-semantics encoding in the preliminary 2019 version was erroneous and refer to Appendix B. *(p.292)*
- Ideal semantics adapts Dunne's algorithm: compute assumptions not credulously accepted under admissibility, form `A_in`, remove assumptions attacked by `A_in`, then repeatedly remove assumptions not defended by the current candidate until a fixpoint is reached. The paper notes Dunne's original lines 8-9 were incorrect and are corrected here. *(p.292-p.293)*

### ABA+ ASP Encodings
- ABA+ input extends ABA facts with `preferred(x,y)` whenever `y <= x`, and Listing 4 computes transitive closure plus `strictly_less_preferred` and `no_less_preferred`. *(p.293-p.294)*
- Listing 5 encodes <-stable semantics for ABA+. It combines the common ABA module, the preference module, and a `<-stable` module. Normal attacks are computed with `preferedly_supported` by considering only selected assumptions not less preferred than the target; reverse attacks are computed by checking whether assumptions not normally attacked by `in` can attack a more-preferred selected assumption. *(p.294)*
- The final <-stable constraint rejects any `out` assumption that is neither normally nor reversely `<`-attacked by `in`, matching Proposition 9. *(p.294)*
- Listing 6 is the subroutine used for <-grounded semantics. It guesses suspect attackers, checks normal and reverse attacks between suspects, target, and current defended set, and concludes the target is <-defended exactly when the subroutine program is unsatisfiable. *(p.295-p.297)*
- Algorithm 2 computes the <-grounded assumption set for FL-property ABA+ frameworks by iteratively applying a solver-backed singleton-defense test: for each candidate `a`, if the subroutine with current `grounded` and `target(a)` is unsatisfiable, add `a` to `grounded`, repeating to a fixpoint. *(p.296)*

### Systems Compared
- Existing ABA reasoning systems are grouped into translation-based, specialized, and direct declarative approaches. ABAGRAPH implements dispute derivations in Prolog and supports credulous admissible/grounded, solution enumeration, credulous complete/preferred via admissible, and skeptical complete via grounded. *(p.297)*
- TweetyProject supports enumeration of admissible, complete, stable, preferred, ideal, and grounded assumption sets, but is not optimized for runtime. *(p.297)*
- ABA2AF translates ABA frameworks to AFs and uses AF-level ASP encodings; the authors note that translation can dominate runtime and can produce exponentially larger AFs. *(p.297-p.298)*
- The direct ASP approach in this paper supports credulous, skeptical, and enumeration tasks for ABA admissible, complete, stable, preferred, grounded, and ideal semantics. *(p.298)*
- ABAPLUS is the only ABA+ system identified by the authors. It translates ABA+ to AFs, supports enumeration under <-stable, <-grounded, <-complete, <-preferred, and <-ideal, and answers credulous/skeptical queries through enumeration. It also enforces WCP and may modify the input framework when WCP is not satisfied, meaning it may reason over a modified framework rather than the original instance. *(p.299)*

### Empirical Setup and Results
- For ABA comparisons with ABAGRAPH and ABA2AF, the authors used 680 ABA frameworks with up to 90 sentences from earlier experiments. For acceptance problems they chose ten query sentences per framework and filtered trivial instances, leaving 1728 instances for credulous admissible/grounded and 4613 for skeptical stable; all 680 base frameworks were used for preferred enumeration. *(p.299)*
- Additional ABA+ comparison benchmarks were generated from modified parameter family 4 of Craven and Toni: each framework has 37% of sentences as assumptions, rule counts and body sizes chosen from bounded intervals dependent on sentence count, all sentences derivable by at least one rule, and rule/body bounds capped at 20. Complete and ideal benchmarks used 20 frameworks at each of 10,14,18,22,26,30 sentences, for 120 frameworks. ABA+ preferences used random assumption permutations with density 15% or 40%. *(p.300)*
- Computing setup: CLINGO 5.2.2 for ASP and ABA2AF; ASPRIN 3 for preferred semantics; SICStus Prolog 4.5 for ABAGRAPH; 2.83 GHz Intel Xeon E5440 quad-core machine with 32 GB RAM; 600-second timeout per instance. *(p.300)*
- Table 6 shows the ASP approach had zero timeouts and small cumulative runtimes across all listed comparisons, while ABAGRAPH, ABA2AF, and ABAPLUS generally had many timeouts and much higher runtimes. Examples: ABA admissible enumeration with query has ASP cumulative 53s versus ABAGRAPH 20131s and ABA2AF 24897s; ABA+ <-stable enumeration without query has ASP cumulative 2s versus ABAPLUS 1729s; ABA+ <-grounded has ASP cumulative 46s versus ABAPLUS 1732s. *(p.301)*
- The authors conclude the ASP-based approach clearly outperforms state-of-the-art systems on every tested ABA and ABA+ problem variant. Even the smallest average performance gap was ABA preferred, where ASP median runtime was about three quarters of ABA2AF on commonly solved instances and ASP cumulative runtime was under one tenth of ABA2AF's. *(p.302)*
- Scalability benchmarks used larger frameworks with sentence counts `{50,250,500,1000,1500,2000,2500,3000,3500,4000}`; for ABA they tested 10 arbitrary query sentences per framework for admissible, complete, and stable, extension enumeration for preferred, and no queries for unique ideal semantics; for ABA+ they generated six frameworks per sentence count, three preference orderings at density 15% and three at 40%, then queried ten arbitrary sentences per framework. *(p.302)*
- The ASP approach routinely solved instances up to 3000 sentences for ABA and up to 1000 for ABA+, while earlier comparison benchmarks had only up to 90 sentences. In the larger ABA benchmark, ABAGRAPH only solved 50-sentence instances within the timeout. *(p.302-p.303)*
- For ABA+ <-stable scalability, preference density had little effect: densities 15% and 40% showed the same timeout behavior and mean runtimes within five seconds for each sentence count. *(p.303)*

### Related Work and Interpretation of Preferences
- ABA complexity has been studied by Dimopoulos et al., Dunne, Karamlou et al., Cyras et al., and summarized by Dvorak and Dunne. Results corresponding to Corollaries 5 and 6 were independently shown by Cyras et al. *(p.304)*
- ASPIC+ can capture the commonly studied ABA fragment without preferences; extending the ASP approach to ASPIC+ variants is identified as a promising direction, with first steps already made by Lehtonen et al. (2020). *(p.304)*
- Preferences can be used to modify the attack relation, as in ABA+, or to select among extensions without modifying attacks. The paper argues that this distinction matters for applications because modifying attacks can change results compared to the same framework without preferences. *(p.305)*
- The authors cite Wakaki's legal reasoning example where careless ABA+ preference use violates the principle that an accused is innocent until proven guilty, illustrating that different preference-handling schemes may fit different application settings. *(p.305)*
- p_ABA uses preferences to select most preferred extensions without modifying the attack relation; ABA+ uses reverse attacks; and ASPIC+ permits preferences over arguments or over premises/defeasible rules, with several ways to lift preferences to the argument level. *(p.305)*

### Conclusions and Appendices
- The conclusion restates the paper's two central results: direct non-trivial ASP encodings for ABA/ABA+ reasoning, and complexity results showing that ABA+ preferences via reverse attacks can increase complexity. Stable-semantics credulous/skeptical acceptance has the same complexity in ABA and ABA+, while <-admissible credulous acceptance rises to `Sigma_2^P`-complete. *(p.306-p.307)*
- Future work directions include extending the ASP approach beyond flat LP-like ABA(+) to general non-flat frameworks, developing algorithms for second-level polynomial-hierarchy tasks, investigating labeling-based encodings, and applying the direct ASP route to related structured formalisms such as ASPIC+. *(p.306-p.307)*
- Acknowledgements identify Academy of Finland grants 276412, 312662, 322869, University of Helsinki DoCS, and Austrian Science Fund grants P30168-N31 and I2854. *(p.307)*
- Appendix A proves Lemma 20, used in Proposition 11 Item 2 and the <-grounded ASP encoding. It characterizes tree derivability from a subset intersecting `A'` via reachability in a graph whose vertices are `Th_R(A)` and whose edges connect rule heads to rule-body atoms. *(p.307-p.308)*
- Appendix A defines WCP: if `A` derives the contrary of `b` and has some `a'` strictly less preferred than `b`, then there is a <=-minimal `a` in `A` with `a < b` such that replacing `a` by `b` lets the adjusted assumption set derive the contrary of `a`. *(p.308)*
- Proposition 21 shows coNP-hardness for deciding whether a given assumption set in an ABA+ framework satisfying WCP reversely counterattacks all sets that <-attack it. The proof modifies Reduction 1 with additional rules while preserving relevant conflict-free attacks. *(p.309)*
- Theorem 22 strengthens Theorem 15 under WCP: verifying whether a set is <-admissible in an ABA+ framework satisfying WCP is still coNP-complete. *(p.309)*
- Appendix A gives the full proof of Theorem 19: membership guesses an assumption set, checks derivability of the query in polynomial time, and checks <-admissibility in coNP; hardness reduces from true quantified Boolean formulas of form `exists X forall Y phi`. *(p.309-p.311)*
- Appendix B explains a counterexample to the preliminary 2019 grounded encoding: in an ABA framework with assumptions `{a,b,c}`, `a` should enter the grounded set and then defend `c`, but the old encoding does not determine a needed rule to be out, so it fails to add `c`. *(p.311-p.312)*
- Appendix C explains why Dunne's original ideal-semantics algorithm lines 8-9 are wrong: they consider only attacks from `A_out union A_CA` when checking whether the current candidate defends itself, missing attacks from sets containing both outside assumptions and the candidate. In the concrete example, the original algorithm incorrectly returns `{d}` instead of the empty ideal assumption set. *(p.311-p.313)*

## Open Questions
- [ ] Table 3 leaves several ABA+ acceptance complexities open at this stage: skeptical <-admissible, credulous <-complete, and skeptical <-complete. *(p.277)*
- [ ] Later sections must be read for the concrete ASP encodings and empirical benchmark details before implementing the backend from this paper. *(p.267-p.268)*

## Related Work Worth Reading
- Bondarenko et al. (1997) for original ABA and grounded fixpoint characterization. *(p.269-p.274)*
- Dimopoulos et al. (2002), Dunne (2009), and Dvorak & Dunne (2018) for established ABA complexity. *(p.268, p.276-p.277)*
- Cyras and Toni / Bao et al. work on ABA+ preferences. *(p.266, p.274-p.275)*
- Craven and Toni dispute-derivation systems and ABA2AF/ABAPLUS translation-based systems for implementation comparison. *(p.267)*
