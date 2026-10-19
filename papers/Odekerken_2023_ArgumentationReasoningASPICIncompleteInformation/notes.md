---
title: "Argumentation Reasoning in ASPIC+ under Incomplete Information"
authors: "Odekerken, Lehtonen, Borg, Wallner, Jarvisalo"
year: 2023
venue: "KR 2023"
doi_url: ""
---

## One-Sentence Summary

Extends ASPIC+ structured argumentation to handle incomplete information by defining four justification statuses (unsatisfiable, defended, out, blocked) for literals and developing ASP-based algorithms for deciding stability and relevance of queries under grounded semantics.

## Problem Addressed

Standard ASPIC+ assumes complete knowledge bases where all premises are known. In real-world applications (e.g., criminal investigations, police work), information arrives incrementally and the justification status of a conclusion may change as new information is gathered. The paper addresses: (1) how to define meaningful justification statuses when the knowledge base is incomplete, (2) how to determine whether a literal's status is *stable* (will not change with additional information), and (3) how to determine which unresolved queries are *relevant* (could change the status of a conclusion if resolved).

## Key Contributions

1. **Grounded extension under incomplete information**: Formal definitions for reasoning about ASPIC+ with incomplete knowledge bases containing "unsettled" literals whose truth value is unknown.
2. **Four justification statuses**: unsatisfiable, defended, out, blocked -- extending the standard grounded semantics to account for incomplete information.
3. **Stability analysis**: Determining whether the justification status of a literal will remain the same regardless of how unsettled literals are resolved. Includes complexity results (coNP-completeness for stability, Sigma_2^P-completeness for relevance).
4. **Relevance analysis**: Determining which unsettled literals, if resolved, could change the justification status of a query.
5. **ASP-based algorithms**: Practical algorithms for computing justification labels, stability, and relevance using Answer Set Programming encodings.
6. **Empirical evaluation**: Experiments on both synthetic and real-world argumentation benchmarks demonstrating practical feasibility.

## Collection Cross-References
- [[Odekerken_2025_ArgumentativeReasoningASPICIncompleteInformation]] - final JAIR version of this line of work; use this entry as the canonical current paper. The JAIR article adds general complexity bounds, a stronger relevance algorithm, a revised implementation, and a broader empirical study.

## Methodology

### ASPIC+ Background (Definitions 1-5)

**Definition 1 (Argumentation system).** The paper studies the restricted fragment `AS = (L, contradiction, R, <=)` with finite literal set L, a symmetric contradiction function, a finite set R of **defeasible rules only**, and a partial preorder on R. Every literal has at least one contradictory and is not its own contradictory. There are no strict rules or rule-naming function in this fragment. *([printed p.532](pngs/page-001.png))*

**Definition 2 (Knowledge base).** K is a consistent set of literals. All knowledge-base elements are axioms, so there are no attackable ordinary or assumption premises. Consistency means no literal in K contradicts another literal in K. *([printed p.532](pngs/page-001.png))*

For a defeasible rule r: phi_1, ..., phi_n => phi, the antecedents are {phi_1, ..., phi_n} and the consequent is phi (the conclusion of r).

**Definition 3 (AT).** An argumentation theory AT = (AS, K) with argumentation system AS and knowledge base K.

**Definition 4 (Arguments).** The set of arguments Args(AT) that an AT gives rise to contains arguments obtained by applying defeasible/strict rules iteratively:
- If phi in K then phi is an argument A with Prem(A) = {phi}, Conc(A) = phi, Sub(A) = {phi}, Rules(A) = empty, TopRule(A) = undefined, DefRules(A) = empty.
- If A_1, ..., A_n are arguments and there is r in R with those conclusions as antecedents and consequent phi, then `B = A_1,...,A_n ⇒ phi` is a rule-based argument. Only finitely many rule applications are allowed. *([Definition 4, printed p.532](pngs/page-001.png))*

**Definition 5 (Rebuttal attack).** A rebuts B on a rule-based subargument B′ iff `conc(A)` contradicts `conc(B′)`. Rebuttal is the only attack type considered here. **Definition 6 (Defeat)** makes this attack successful iff A is not strictly less preferred than B′. *([printed p.533](pngs/page-002.png))*

### Argumentation Frameworks and Semantics

An argumentation system gives rise to arguments as defined above. These arguments with the attack relation form an abstract argumentation framework (AF), which is evaluated using Dung's semantics:
- An AF = (Args, Defeats) where Defeats is derived from attacks plus preference ordering
- Grounded semantics provides a unique fixpoint (grounded extension)

### Observation-Based Arguments and Last-Link (Definitions 4, 6-7)

An observation-based argument is a literal in the consistent axiom base K (Definition 4); there is no separate `(AT,O)` object. Definition 6 concerns defeat, not observation-based theories. Under Definition 7's last-link order, `B <= A` iff A is observation-based or both are rule-based and `top-rule(B) <= top-rule(A)`. *([observation arguments](pngs/page-001.png), [defeat and last-link](pngs/page-002.png))*

### Incomplete Information Extension

**Key distinction**: Not all literals are settled as observed or not. ASPIC+ is extended to handle *incomplete* information where:
- Some observations are definite (settled)
- Others are *unsettled* -- their truth value is not yet known

Definition 7 is the last-link preference principle above. The paper does not introduce the previously transcribed "full-link triples" or a Boolean observation function. Future information is represented by enlarging the consistent axiom base using queryable literals (Definitions 11-12). *([Definition 7](pngs/page-002.png), [queryables and futures](pngs/page-003.png))*

### Justification Statuses under Incomplete Information

The paper defines four justification statuses for literals, extending beyond the standard three:

**Definition 8 (corresponding AF).** The corresponding AF has all arguments of T as its nodes and the defeat relation determined by T as its edges. Definition 9 supplies grounded semantics; the paper writes `G(T)` for this grounded extension. There is no three-argument `AF(AT,O,D)` construction in this definition. *([printed p.533](pngs/page-002.png))*

**Justification statuses** (Definition 10, building on Modgil and Prakken 2013):

For a literal l relative to one current AT T:

1. **Unsatisfiable**: There is no current argument with conclusion l. This alone says nothing about future additions; stable-unsatisfiable is the separate condition ruling out such arguments in every future theory.
2. **Defended**: A literal is *defended* if there is an argument for l in the grounded extension. The literal is justified under grounded semantics.
3. **Out**: There is at least one argument for l, and **every** argument for l is defeated by an argument in G(T).
4. **Blocked**: There is an argument for l, none is in G(T), and at least one argument for l is not defeated by any argument in G(T).

*These quantifiers distinguish out from blocked. [Definition 10, printed p.533](pngs/page-002.png).*

The defended status corresponds to the justified status of conclusions of arguments (Modgil and Prakken 2013, Definition 15). Conclusions that are not justified can be out or blocked: out requires every argument for the literal to be defeated by G(T), whereas blocked leaves at least one such argument undefeated. *([printed p.533](pngs/page-002.png))*

**Example 4 (Justification statuses).** Illustrates the four justification statuses on a concrete AT:
- A literal with no supporting argument is *unsatisfiable*
- A literal in the grounded extension is *defended*
- A literal with a supporting argument that is defeated (and not reinstated) is *out*
- A literal with a supporting argument that is neither in the grounded extension nor definitively defeated is *blocked*

### Section 3: Stability and Relevance

This section introduces the paper's main contributions: formal definitions of stability and relevance for justification statuses under incomplete information.

**Definition 11 (Queryables).** Given an AT = (AS, K), a set Q subset of L is a set of *queryables* if:
- K is a subset of Q, and Q is a subset of L.
- Q is closed under contradictories: for every q in Q, all contradictories of q are also in Q.
- Q restricts the allowable enlarged axiom bases; it includes the existing axioms, rather than only unresolved literals. *([Definition 11, printed p.534](pngs/page-003.png))*

Queryables represent the possible future observations -- the unsettled literals that could be resolved.

**Definition 12 (Future argumentation theories).** Given an AT = (AS, K) and a set of queryables Q, an AT' = (AS, K') is a *future* of AT w.r.t. Q if:
- `K ⊆ K′ ⊆ Q`; the argumentation system remains the same.
- K′ is consistent, as required of every AT by Definition 2. There are no ordinary/assumption partitions to preserve. *([Definition 12, printed p.534](pngs/page-003.png))*

A future AT represents a possible state of knowledge after resolving some or all queryables.

**Definition 13 (j-stability).** Given an AT = (AS, K), a set of queryables Q, and a justification status j in {unsatisfiable, defended, out, blocked}:
- A literal l is *stable-j* (or *j-stable*) w.r.t. Q iff l has justification status j in T' for every future AT' of T w.r.t. Q
- Intuitively, l is j-stable if its status will not change regardless of how the queryables are resolved

**Example 5 (Stability statuses).** Demonstrates j-stability: a literal that is defended in the current AT and remains defended in all future ATs is stable-defended. A literal whose status could flip from defended to out (or vice versa) when a queryable is resolved is not stable.

**Definition 14 (Minimal stable-j future theory).** Given an AT = (AS, K), a set of queryables Q, a justification status j, and a literal l:
- A future AT' of AT w.r.t. Q is a *minimal stable-j future theory* for l if:
  1. l is stable-j in AT′ with respect to the **same Q**.
  2. There is no AT″ with `T ⊑_Q T″ ⊏_Q T′` in which l is stable-j. Minimality includes the original T as a possible smaller future. *([Definition 14, printed p.534](pngs/page-003.png))*
- In other words, the knowledge base is minimally expanded to achieve stability of l at status j

**Example 6 (Minimal stable-j future theory).** Shows that a literal may require resolving only a subset of queryables to become stable, and the minimal stable-j future theory identifies the smallest such subset.

**Definition 15 (j-relevance).** Given an AT = (AS, K), a set of queryables Q, a justification status j, and a literal l:
- For `q ∈ Q` with `q ∉ K` and no contradictory of q already in K, q is *j-relevant* for l iff q itself belongs to K′ for some minimal stable-j future theory `(AS,K′)` for l.
- Relevance is literal-specific: q and a contradictory of q are considered separately, and both can be relevant via different minimal futures. *([Definition 15 and Example 8, printed p.534](pngs/page-003.png))*

**Example 7 (j-relevance).** Shows a case where a queryable q is defended-relevant for a literal l because adding q to the axioms changes l's status.

**Example 8 (Both q and q_bar relevant).** Demonstrates that both a queryable q and its contradictory q_bar can be j-relevant for the same literal l -- resolving q either way could contribute to stabilizing l, but through different minimal future theories.

### Complexity Results (Section 4)

Justification status (Definition 10) is decidable in **polynomial time** for the paper's fragment (Theorem 1). The proof works over rule sets rather than first enumerating every argument, which can be exponential in theory size. The least fixpoint C of the rule defence operator yields `G(T)=Arg_T(C)` (Proposition 4). *([rule reformulation](pngs/page-004.png), [Theorem 1](pngs/page-005.png))*

### Stability (Section 4.3)

**Definitions 16-19 (rule-set reformulation).** A rule r is applicable by D iff an argument using r can be constructed from `D ∪ {r}` and K. D defeats r iff an applicable rule in D has a contradictory consequent and is not strictly less preferred than r, or an axiom contradicts r's consequent. D defends r iff the set of rules not defeated by D does not defeat r. The characteristic function collects rules both applicable and defended by D. These are not Definition 10, which defines literal justification statuses. *([printed p.535](pngs/page-004.png))*

**Stability** means a literal's justification status will not change regardless of how the unsettled observations are resolved.

**Proposition 7.** Deciding j-stability with respect to the allowed future theories is coNP-complete for each of {unsatisfiable, defended, out, blocked}; hardness holds even without rule preferences. *([printed p.536](pngs/page-005.png))*

### Relevance (Section 4.4)

A query (unsettled observation) is *relevant* for a given literal if resolving that query could change the literal's justification status.

**Lemma 1.** Let T=(AS,K), let Q be its queryables, and let q be an unobserved queryable with no contradictory already in K. Then q is j-relevant for l iff there is a future `T′=(AS,K′)` such that l is **not stable-j** in T′ but **is stable-j** in `(AS,K′ ∪ {q})`. The test concerns stability across all remaining futures, rather than a single current-label change; q need not differ from l. *([printed p.536](pngs/page-005.png))*

**Theorem 2.** Deciding whether a queryable is j-relevant for a literal in an AT w.r.t. a set of queryables is Sigma_2^P-complete for each j in {unsatisfiable, defended, out, blocked}. Hardness holds even without preferences.

## Key Equations

1. **Grounded extension computation**: The grounded extension is the least fixpoint of a characteristic function F applied iteratively:
   - `F(S) = {A in Args | every defeater B of A is defeated by some C in S}`.
   - Grounded extension = lfp(F) = F^0 subset F^1 subset ... (iterated until fixpoint)

2. **Stability condition**: A literal l with status j is *j-stable* iff for all possible completions C of unsettled observations, the status of l remains j in the resulting grounded extension.

3. **Relevance condition**: A queryable q is *j-relevant* for l iff some future `(AS,K′)` is not stable-j for l, while `(AS,K′ ∪ {q})` is stable-j (Lemma 1). Equivalently, q occurs in some minimal stable-j future theory (Definition 15). A marginal change between two current labels is not the definition. *([Definition 15](pngs/page-003.png), [Lemma 1](pngs/page-005.png))*

## Parameters

- **Argumentation system parameters**: finite literal set L, symmetric contradiction function, finite defeasible-rule set R, and partial preorder on R.
- **Knowledge base**: consistent axiom-only set K; its members yield observation-based arguments.
- **Queryables**: `K ⊆ Q ⊆ L`, closed under contradictories; future bases K′ are consistent sets between K and Q. *([fragment](pngs/page-001.png), [queryables](pngs/page-003.png))*
- **Preferences**: Ordering over defeasible rules or arguments (optional; used to convert attacks to defeats)

## Implementation Details

### ASP Encoding (Section 5)

The algorithms are implemented as Answer Set Programming (ASP) encodings using the Clingo solver.

**Listing 1: Common Module**
- Lines 1-3 collect literals and rules from the input theory, and line 4 makes contradiction symmetric.
- Lines 5-7 compute derivable literals and applicable rules; line 8 marks nonderivable literals `unsat`.
- Line 7 uses an ASP conditional literal over rule-body members. It does not invoke Clingo's Python scripting.
- The common module is combined with Listing 2 for the no-preference justification encoding or Listing 3 for the preference-aware encoding. *([printed p.537](pngs/page-006.png))*

The encoding assigns justification labels (defended, out, blocked, unsatisfiable) for each literal in the program by:
1. Collecting all rules from D_AT
2. Determining applicable and defeated rules
3. Computing the grounded extension via iterative fixpoint
4. Assigning labels based on membership in the extension

**Key ASP constructs used**:
- `literal`, `xrule`, `head`, `body`, `axiom`, and `ctr` describe the compact theory.
- `derivable`, `applicable_rule`, and `unsat` are provided by the common module.
- `defended`, `out`, and `blocked` are obtained by the justification modules, with rule-level `defended_rule`, `defeated`, and undefeated-rule predicates.
- The encodings reason over literals and rules rather than building `vertex`/`att` facts for an explicit argument graph. *([Listings 1-2](pngs/page-006.png), [Listing 3](pngs/page-007.png))*

**Stability Encoding (Section 5.2; Listing 2 itself is the no-preference justification module)**
- Uses counterexample-based checking
- A literal's status is stable if no completion of unsettled observations changes its status
- The ASP solver searches for a counterexample (a completion where the status differs)
- If no counterexample exists, the literal is stable

The stability check uses the brave/cautious reasoning modes of Clingo:
- For each literal and its current status, attempt to find a completion that yields a different status
- If the solver returns UNSAT, the status is stable

**Relevance Algorithm (Algorithm 1; Listing 3 itself is the preference-aware justification module)**
- The input includes one queryable q, target literal l, and desired justification status j.
- Guess a consistent candidate axiom set containing q and the original K.
- Check that l is stable-j under that candidate, and that it is not stable-j after removing q.
- If both checks succeed, return YES. Otherwise refine the candidate space using the counterexample: exclude subsets when the first stability check fails, or supersets when the candidate without q is already stable-j.
- Exhausting the candidate space returns NO. This is a CEGAR search over future theories, not two current-status evaluations with q true/false. *([Algorithm 1 and Proposition 9, printed p.538](pngs/page-007.png))*

**ASP-Based Counterexample Generation (Section 5.3)**
- Uses CEGAR (Counterexample-Guided Abstraction Refinement) approach
- Based on Clarke, Gupta, and Strichman (2004) SAT-based counterexample generation
- Treats NP-abstraction as overapproximation of the solution space
- Iteratively refines by drawing candidates from the abstract space and verifying in the concrete semantics
- Candidate solutions are compared with an ASP solver; if valid, it's a solution; if there's a counterexample, the candidate is refined

**Proposition 5.** The least fixpoint of the rule-set defence operator is reached in at most `ceil(|R|/2)` iterations. Proposition 6 then characterizes the four justification labels from that fixpoint; Proposition 8 supplies the simpler no-preference characterization used by Listing 2. *([Propositions 5-6](pngs/page-004.png), [Proposition 6 continued](pngs/page-005.png), [Proposition 8](pngs/page-006.png))*

The implementation is available as open source at https://bitbucket.org/odekerken/...

### Performance

**Table 1**: Number of solved instances and mean runtimes for both real-world and synthetic benchmarks.

For real-world data:
- Justification status (without preferences): 0.26 seconds average, fraction of 3.5 seconds max
- Algorithm for relevance can scale well to reasonable-sized instances (up to 100 literals)
- Higher variance for instances with up to 100 literals

For synthetic data:
- Generated tree-like structures with configurable parameters
- Randomly sampling 1/3 of subtrees of each size between 1 and 10 from K and the empty knowledge base
- Stability instances are harder; relevance computation depends on the instance structure

**Table 2**: Shows results for deciding relevance both with and without preferences. For real-world data without preferences, the approach can decide relevance of a query in 0.26 seconds on average, with a maximum of 3.5 seconds. The algorithm for relevance can scale well to reasonable-sized instances, solving all instances with up to 100 literals. Higher variance at larger instances (up to 100 literals, or larger), with some instances not solvable in 600 seconds.

## Figures of Interest

- **Figure 1 (printed p.532)**: Each square is a literal; rounded squares are queryable literals, and shading identifies current knowledge-base members. Double-lined arrows are rules and single-lined arrows are negations. It is a theory diagram, not an argument attack graph with fixed/unfixed edges. *([page image](pngs/page-001.png))*
- **Table 1 (page 8)**: Number of solved instances and mean runtimes over solved instances for different configurations (with/without preferences, stability/relevance).
- **Table 2 (page 8)**: Detailed results for relevance with and without preferences across different instance sizes.

## Results Summary

1. **Complexity results**: Stability checking is coNP-complete; relevance checking is Sigma_2^P-complete for all four justification statuses.
2. **ASP algorithms work in practice**: The ASP-based approach handles real-world benchmarks efficiently (sub-second for justification, seconds for stability/relevance on moderate-sized instances).
3. **CEGAR approach effective**: The counterexample-guided refinement approach for relevance is practical.
4. **Scalability**: Handles instances with up to ~100 literals and rules effectively; larger instances (100+) show higher variance and occasional timeouts at 600s.
5. **Real-world applicability**: Tested on online trade fraud investigation data from the Netherlands Police, demonstrating practical use in criminal investigation scenarios.

## Limitations

1. **Grounded semantics only**: The paper focuses exclusively on grounded semantics. Extension to preferred, stable, or other Dung semantics is left as future work.
2. **Preference scope**: The fragment includes rule preferences. Separate simpler justification encodings are given without preferences, but the coNP/Sigma_2^P hardness results already hold without preferences; the paper does not establish a higher complexity class from adding them. *([complexity](pngs/page-005.png), [encodings](pngs/page-006.png))*
3. **Scalability ceiling**: For larger instances (100+ literals/rules), the ASP approach can time out (600s limit), suggesting limitations for very large knowledge bases.
4. **Binary observations only**: Observations are binary (true/false); no support for graded or probabilistic observations.
5. **Research-note provenance**: The earlier note recorded reconstruction from extracted text. The formal corrections above were checked against the original page images, including the original rendered page 003; reconstructed prose is not used as paper evidence. *([original page 003](pngs/page-003.png))*

## Testable Properties

1. **Justification label correctness**: For any complete AT (no unsettled observations), the four justification labels should partition all literals in L.
2. **Stability monotonicity**: If a literal is j-stable, adding more observations (resolving queryables) should not change its status.
3. **Relevance soundness**: For an eligible unobserved q, non-j-relevance means no future theory changes from not stable-j to stable-j for l when q is added. This does not equate q with its contradictories or reduce relevance to current-label changes. *(Lemma 1; [page image](pngs/page-005.png))*
4. **Grounded extension uniqueness**: For any given complete AT, there is exactly one grounded extension.
5. **Complexity bounds**: A witness to **non-stability** is a future theory with a different justification status, checkable in polynomial time. Relevance is in Sigma_2^P by guessing the future from Lemma 1 and using two stability-oracle checks. *([complexity proofs, printed p.536](pngs/page-005.png))*

## Relevance to Project

1. **Incomplete information in propstore**: The propstore deals with claims from scientific literature where information is inherently incomplete. This paper's framework for reasoning under incomplete information directly applies.
2. **Stability for claim status**: The stability concept maps to determining whether a claim's acceptance status is robust -- will gathering more evidence change the conclusion?
3. **Relevance for information gathering**: The relevance concept can guide which additional papers or evidence to seek -- which unresolved questions would actually matter for a given claim's status?
4. **ASPIC+ integration**: The paper builds on ASPIC+ (Modgil & Prakken 2014, 2018), both already in the collection, providing computational methods for the formal framework.
5. **ASP implementation**: The ASP-based approach offers a concrete implementation path using existing solvers (Clingo).
6. **Criminal investigation parallel**: The paper's motivating domain (police investigations with incrementally arriving evidence) parallels the propstore's scenario of incrementally processing scientific papers.

## Open Questions

1. How do the complexity results change for semantics other than grounded (preferred, stable)?
2. Can the ASP encodings be adapted for online/incremental computation as new observations arrive?
3. How does this framework interact with the bipolar argumentation (support + attack) from Cayrol 2005?
4. What is the relationship between stability here and the epistemic entrenchment ordering in AGM (Dixon 1993)?
5. Can the relevance algorithm be used to prioritize which papers to read next in the propstore?

## Related Work Worth Reading

- Odekerken, Borg, and Bex (2020): "Estimating stability for efficient argument-based inquiry" (COMMA 2020) -- predecessor on stability estimation
- Odekerken, Borg, and Bex (2022): "Stability and relevance in incomplete argumentation frameworks" (COMMA 2022) -- companion paper on abstract frameworks
- Rapberger and Ulbricht (2022): "On dynamics in structured argumentation formalisms" (KR 2022) -- dynamics in structured argumentation
- Testerink, Odekerken, and Bex (2019): "A method for efficient argument-based inquiry" (FQAS) -- efficient inquiry methods
- Niskanen, and Jarvisalo (2020): "Algorithms for dynamic argumentation frameworks: An incremental SAT-based approach" -- incremental algorithms
- Baroni, Caminada, and Giacomin (2011): Handbook chapter on argumentation semantics
- Besnard, Garcia, Hunter, Modgil, Prakken, Simari, and Toni (2014): "Introduction to structured argumentation" -- survey of structured argumentation approaches

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as ref 11; this paper builds directly on Dung's grounded semantics, using the grounded extension as the basis for defining the four justification statuses (unsatisfiable, defended, out, blocked) under incomplete information.
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — cited as ref 21; this is the ASPIC+ tutorial that defines the base framework (argumentation systems, knowledge bases, arguments, three attack types) that Odekerken et al. extend to handle incomplete information.
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — cited as ref 20 (as "Modgil and Prakken 2013"); the full technical ASPIC+ paper providing the preference-based defeat mechanism and rationality postulates that this paper's incomplete-information extension builds upon.
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — cited as ref 27; the original ASPIC framework paper defining arguments as inference trees from strict/defeasible rules with three attack types, which this paper's incomplete-information extension builds upon.

### New Leads (Not Yet in Collection)
- Odekerken, Borg, and Bex (2022) ref 24 — "Stability and relevance in incomplete argumentation frameworks" (COMMA 2022) — companion paper performing the same stability/relevance analysis at Dung's abstract level rather than ASPIC+'s structured level
- Rapberger and Ulbricht (2022) ref 28 — "On dynamics in structured argumentation formalisms" — complementary work on how structured argumentation frameworks change over time
- Baroni, Caminada, and Giacomin (2011) ref 4 — handbook chapter on argumentation semantics; comprehensive reference for the semantics taxonomy underlying the justification statuses

### Now in Collection (previously listed as leads)
- [[Lehtonen_2020_AnswerSetProgrammingApproach]] — Provides the base ASP encodings for computing ASPIC+ semantics (without preferences) that this paper extends with incomplete-information reasoning. Lehtonen et al. reformulate extensions as σ-assumptions (pairs of ordinary premises and defeasible rules), proving these biject with AF extensions (Theorem 5) and providing correct ASP encodings for conflict-free, admissible, complete, stable, and preferred semantics that scale to N=3000 atoms.
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - ABA direct-ASP and complexity predecessor for the same broader solver line that this ASPIC+ incomplete-information paper extends.

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- (none — this is the newest paper in the collection)

### Conceptual Links (not citation-based)
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — **Moderate.** Prakken & Horty's survey contextualizes Pollock's defeat statuses within ASPIC+; Odekerken et al. extend these statuses to handle incomplete information, directly building on the framework Prakken helped develop.
- [[Pollock_1987_DefeasibleReasoning]] — **Moderate.** Pollock's four-valued defeat status (defeated, undefeated, provisionally defeated, provisionally undefeated) for arguments in inference graphs is a precursor to Odekerken's four justification statuses (unsatisfiable, defended, out, blocked) for literals under incomplete information. Both address the question of how argument/literal status can be provisional pending further information.
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — **Weak.** Both extend Dung's framework in different directions: Cayrol adds support relations (bipolar argumentation), Odekerken adds incomplete information handling. Open question whether bipolar argumentation under incomplete information could combine both extensions.
- [[Dixon_1993_ATMSandAGM]] — **Moderate.** Both address reasoning under incomplete/changing information. Dixon's ATMS context switching manages multiple simultaneous assumption sets; Odekerken's stability analysis determines whether a conclusion is robust across all possible completions of unsettled observations. The ATMS's enumeration of consistent environments is structurally related to Odekerken's enumeration of future argumentation theories.
- [[deKleer_1986_AssumptionBasedTMS]] — **Moderate.** The ATMS maintains labels recording which assumption sets support each datum; Odekerken's framework determines which unsettled observations (analogous to assumptions) are relevant to a query's justification status. Both systems reason about conclusions under multiple possible worlds defined by unresolved choices.
- [[Fang_2025_LLM-ASPICNeuro-SymbolicFrameworkDefeasible]] — **Strong.** Both extend ASPIC+ for real-world settings. Fang uses LLMs to extract structured beliefs from natural language and feeds contradiction pairs into ASPIC+ for resolution via grounded extensions. Odekerken handles incomplete KBs with four justification statuses. They are complementary: Fang's LLM extraction will inevitably produce incomplete KBs, and Odekerken's framework provides the formal semantics for reasoning with whatever the LLM manages to extract.
