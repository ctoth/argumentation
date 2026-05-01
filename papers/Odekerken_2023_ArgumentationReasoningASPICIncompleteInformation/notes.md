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

**Definition 1 (Argumentation system).** An argumentation system AS = (L, C, R, n) with:
- L: a logical language closed under negation (complement function)
- C: a set of contraries (if phi in C(psi) then phi attacks psi; asymmetric)
- R = R_s union R_d: strict rules R_s and defeasible rules R_d of form phi_1, ..., phi_n -> phi (strict) or phi_1, ..., phi_n => phi (defeasible)
- n: a naming function for defeasible rules (names are used for undercutting)
- R_s must be closed under contraposition and transitive binary closure

**Contrariness**: phi is a *contrary* of psi if phi in C(psi) but psi not in C(phi). phi is a *contradictory* of psi if phi in C(psi) and psi in C(phi).

**Definition 2 (Knowledge base).** K = (K_n, K_p, K_a) with:
- K_n: axiom premises (not attackable)
- K_p: ordinary premises (attackable)
- K_a: assumption premises (attackable)

For a defeasible rule r: phi_1, ..., phi_n => phi, the antecedents are {phi_1, ..., phi_n} and the consequent is phi (the conclusion of r).

**Definition 3 (AT).** An argumentation theory AT = (AS, K) with argumentation system AS and knowledge base K.

**Definition 4 (Arguments).** The set of arguments Args(AT) that an AT gives rise to contains arguments obtained by applying defeasible/strict rules iteratively:
- If phi in K then phi is an argument A with Prem(A) = {phi}, Conc(A) = phi, Sub(A) = {phi}, Rules(A) = empty, TopRule(A) = undefined, DefRules(A) = empty.
- If A_1, ..., A_n are arguments and there is r in R_s such that Conc(A_1), ..., Conc(A_n) -> phi, then B = A_1, ..., A_n -> phi is an argument.
- If A_1, ..., A_n are arguments and there is r in R_d such that Conc(A_1), ..., Conc(A_n) => phi, then B = A_1, ..., A_n => phi is an argument.

**Definition 5 (Attacks).** Arguments A attacks B if:
- A *undermines* B: Conc(A) in C(phi) for some phi in Prem(B) \ K_n (ordinary premise attack)
- A *rebuts* B at B' (sub-argument): Conc(A) in C(Conc(B')) for some B' in Sub(B) where B' has a defeasible top rule
- A *undercuts* B at B': Conc(A) in C(n(r)) for some B' in Sub(B) with defeasible top rule r

### Argumentation Frameworks and Semantics

An argumentation system gives rise to arguments as defined above. These arguments with the attack relation form an abstract argumentation framework (AF), which is evaluated using Dung's semantics:
- An AF = (Args, Defeats) where Defeats is derived from attacks plus preference ordering
- Grounded semantics provides a unique fixpoint (grounded extension)

### Observation-Based Arguments (Definition 6)

**Definition 6 (Observation-based AT).** An *observation-based AT* is a pair (AT, O) where:
- AT = (AS, K) is an argumentation theory
- O subset of L is a set of *observations*
- Each literal in O is an observation-based argument (no rules needed)
- Both A and the complement of A can be observed

### Incomplete Information Extension

**Key distinction**: Not all literals are settled as observed or not. ASPIC+ is extended to handle *incomplete* information where:
- Some observations are definite (settled)
- Others are *unsettled* -- their truth value is not yet known

**Definition 7 (Full-link triples).** Let A, B in AT. B is two-sided if Conc(A) in C(Conc(B)) and Conc(B) in C(Conc(A)). A full-link triple (A, f, B) exists when:
- f: O -> {t, f} is an observation-based argument
- A and B are both in the AT's arguments
- If A is observation-based, then both A and B are observation-based

### Justification Statuses under Incomplete Information

The paper defines four justification statuses for literals, extending beyond the standard three:

**Definition 8 (corresponding AFs).** As, corresponding AFs are used. For an AT = (AS, K), an observation-based AT (AT, O), and a set of defeasible rules D subset of R_d, define:
- AF(AT, O, D): the AF over the full argumentation theory with observations O and rules D
- This allows computing the grounded extension for different possible completions

**Justification statuses** (Definition 9, building on Modgil and Prakken 2013):

For a literal l relative to an AT with a set of possible completions:

1. **Unsatisfiable**: A literal is *unsatisfiable* if there is no argument A in Args with Conc(A) = l. The literal cannot be concluded regardless of what information arrives.
2. **Defended**: A literal is *defended* if there is an argument for l in the grounded extension. The literal is justified under grounded semantics.
3. **Out**: A literal is *out* if it is not unsatisfiable but not defended -- there exists an argument for it, but it is not in the grounded extension (it is defeated).
4. **Blocked**: A literal is *blocked* if there is an argument for l in an observation-based argument A, but it is not in the grounded extension and not definitively out.

These four statuses correspond to the justified status of conclusions of arguments (Modgil and Prakken 2013, Definition 13). Conclusions of arguments that are justified (in the grounded extension) are *defended*. A literal that is *out* is not justifiable (every argument for the literal is defeated based on the grounded extension). A literal that is *blocked* is not justified under the grounded semantics but might be justifiable for semantics other than grounded (Baroni, Caminada, and Giacomin 2011).

**Example 4 (Justification statuses).** Illustrates the four justification statuses on a concrete AT:
- A literal with no supporting argument is *unsatisfiable*
- A literal in the grounded extension is *defended*
- A literal with a supporting argument that is defeated (and not reinstated) is *out*
- A literal with a supporting argument that is neither in the grounded extension nor definitively defeated is *blocked*

### Section 3: Stability and Relevance

This section introduces the paper's main contributions: formal definitions of stability and relevance for justification statuses under incomplete information.

**Definition 11 (Queryables).** Given an AT = (AS, K), a set Q subset of L is a set of *queryables* if:
- Q is closed under contradictories: for every q in Q, the contradictory q_bar is also in Q
- Q represents the literals whose truth value is not yet known but could potentially be added to the axioms K_n

Queryables represent the possible future observations -- the unsettled literals that could be resolved.

**Definition 12 (Future argumentation theories).** Given an AT = (AS, K) and a set of queryables Q, an AT' = (AS, K') is a *future* of AT w.r.t. Q if:
- K_n subset of K'_n subset of K_n union Q (the axioms can only grow by adding queryables)
- K'_p = K_p and K'_a = K_a (ordinary and assumption premises remain unchanged)
- K'_n is consistent (no contradictory pair from Q is added simultaneously)

A future AT represents a possible state of knowledge after resolving some or all queryables.

**Definition 13 (j-stability).** Given an AT = (AS, K), a set of queryables Q, and a justification status j in {unsatisfiable, defended, out, blocked}:
- A literal l is *stable-j* (or *j-stable*) w.r.t. Q iff l has justification status j in T' for every future AT' of T w.r.t. Q
- Intuitively, l is j-stable if its status will not change regardless of how the queryables are resolved

**Example 5 (Stability statuses).** Demonstrates j-stability: a literal that is defended in the current AT and remains defended in all future ATs is stable-defended. A literal whose status could flip from defended to out (or vice versa) when a queryable is resolved is not stable.

**Definition 14 (Minimal stable-j future theory).** Given an AT = (AS, K), a set of queryables Q, a justification status j, and a literal l:
- A future AT' of AT w.r.t. Q is a *minimal stable-j future theory* for l if:
  1. l is stable-j in AT' w.r.t. Q' = Q \ (K'_n \ K_n) (the remaining queryables after resolving those added to K'_n)
  2. There is no future AT'' of AT with K_n subset K''_n subset K'_n such that l is stable-j in AT'' w.r.t. the corresponding remaining queryables
- In other words, the knowledge base is minimally expanded to achieve stability of l at status j

**Example 6 (Minimal stable-j future theory).** Shows that a literal may require resolving only a subset of queryables to become stable, and the minimal stable-j future theory identifies the smallest such subset.

**Definition 15 (j-relevance).** Given an AT = (AS, K), a set of queryables Q, a justification status j, and a literal l:
- A queryable q in Q is *j-relevant* for l if q or q_bar appears in K'_n \ K_n for some minimal stable-j future theory AT' for l
- Intuitively, q is j-relevant if resolving q could be part of the minimal information needed to stabilize l's status at j

**Example 7 (j-relevance).** Shows a case where a queryable q is defended-relevant for a literal l because adding q to the axioms changes l's status.

**Example 8 (Both q and q_bar relevant).** Demonstrates that both a queryable q and its contradictory q_bar can be j-relevant for the same literal l -- resolving q either way could contribute to stabilizing l, but through different minimal future theories.

### Complexity Results (Section 4)

Justification status (Definition 9) is decidable in **polynomial time**: given a complete AT, the grounded extension can be computed in polynomial time via the characteristic function's least fixpoint, and each literal's justification status is determined by its membership (or non-membership) in the extension.

### Stability (Section 4.3)

**Definition 10.** For deciding stability by rule:
- Given an AT = (AS, K), the corresponding AF, a set of defeasible rules D subset of R_d, and a rule r in R_d:
  - r is *applicable* if its antecedents are all in K or derivable
  - r is *defeated* if there exists a defeating argument against it

**Stability** means a literal's justification status will not change regardless of how the unsettled observations are resolved.

**Proposition 7.** Deciding whether a literal is j-stable in an AT w.r.t. a set of defeasible rules is coNP-complete for {unsatisfiable, defended, out, blocked}. Hardness holds for each status.

### Relevance (Section 4.4)

A query (unsettled observation) is *relevant* for a given literal if resolving that query could change the literal's justification status.

**Lemma 1.** Let AT = (AS, K), let AF be a set of queryables and let j be a justification status. Given a literal l in L and queryable q in Q where q != l and q_bar != l:
- if l is not in AF's arguments then l is not q-relevant
- otherwise relevance can be checked by examining whether resolving q (positively or negatively) would change l's status

**Theorem 2.** Deciding whether a queryable is j-relevant for a literal in an AT w.r.t. a set of queryables is Sigma_2^P-complete for each j in {unsatisfiable, defended, out, blocked}. Hardness holds even without preferences.

## Key Equations

1. **Grounded extension computation**: The grounded extension is the least fixpoint of a characteristic function F applied iteratively:
   - F(S) = {A in Args | A is not attacked by any B in Args \ S, or every attacker of A is attacked by some C in S}
   - Grounded extension = lfp(F) = F^0 subset F^1 subset ... (iterated until fixpoint)

2. **Stability condition**: A literal l with status j is *j-stable* iff for all possible completions C of unsettled observations, the status of l remains j in the resulting grounded extension.

3. **Relevance condition**: A queryable q is *j-relevant* for literal l iff there exists a completion C and a completion C' that differ only on q such that l has status j in one but not the other.

## Parameters

- **Argumentation system parameters**: L (language), C (contrariness function), R_s (strict rules), R_d (defeasible rules), n (naming function)
- **Knowledge base partitions**: K_n (axioms), K_p (ordinary premises), K_a (assumptions)
- **Observations**: O (set of observed literals)
- **Queryables**: Q (set of unsettled literals whose truth value is unknown)
- **Preferences**: Ordering over defeasible rules or arguments (optional; used to convert attacks to defeats)

## Implementation Details

### ASP Encoding (Section 5)

The algorithms are implemented as Answer Set Programming (ASP) encodings using the Clingo solver.

**Listing 1: Justification Status Algorithm**
- The ASP program has 5 modules:
  1. Lines 1-3: Collect literals from the AT and AF, enumerate observations
  2. Lines 3-5: Determine which literals are derivable and not derivable
  3. Lines 5-7: Determine which literals' conclusions are defeatable
  4. Lines 7-8: Use Clingo's Python scripting for conflict detection
  5. Lines 8-set: Compute the justification labels

The encoding assigns justification labels (defended, out, blocked, unsatisfiable) for each literal in the program by:
1. Collecting all rules from D_AT
2. Determining applicable and defeated rules
3. Computing the grounded extension via iterative fixpoint
4. Assigning labels based on membership in the extension

**Key ASP constructs used**:
- `vertex(X)` for arguments
- `att(X,Y)` for attacks
- `defended(X)` for literals in the grounded extension
- `not_defended(X)` for literals not in the extension
- `unsatisfiable(X)` for literals with no supporting argument

**Listing 2: Stability Algorithm**
- Uses counterexample-based checking
- A literal's status is stable if no completion of unsettled observations changes its status
- The ASP solver searches for a counterexample (a completion where the status differs)
- If no counterexample exists, the literal is stable

The stability check uses the brave/cautious reasoning modes of Clingo:
- For each literal and its current status, attempt to find a completion that yields a different status
- If the solver returns UNSAT, the status is stable

**Listing 3: Relevance Algorithm (Algorithm 1)**
- A candidate q is a queryable; tests whether resolving q could change the status of a target literal
- The algorithm:
  1. For each candidate queryable q:
     a. Set q to true, compute grounded extension, check if target's status changes
     b. Set q to false, compute grounded extension, check if target's status changes
  2. If either resolution changes the target's status, q is relevant
- Uses ASP with multi-shot solving (Clingo's incremental interface)

**ASP-Based Counterexample Generation (Section 5.3)**
- Uses CEGAR (Counterexample-Guided Abstraction Refinement) approach
- Based on Clarke, Gupta, and Strichman (2004) SAT-based counterexample generation
- Treats NP-abstraction as overapproximation of the solution space
- Iteratively refines by drawing candidates from the abstract space and verifying in the concrete semantics
- Candidate solutions are compared with an ASP solver; if valid, it's a solution; if there's a counterexample, the candidate is refined

**Proposition 5.** Given an AT = (AS, K) where |O| = 0, delta is labeled:
- *defended* if there is an argument A for l such that ext(A) subset of K_n ∪ K_a, where del ⊆ L, there is no argument for ext(l) based on l, and
- *out* if l is not unsatisfiable and there is no argument A for l with ext(A) subset of Args(AT, O)

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

- **Figure 1 (page 1)**: Example AT (ASPIC+ argumentation theory). Each square is a literal in the knowledge base. Rounded rectangles are rules. Arrows represent attack relations. Shows a concrete example with fixed arrows (solid) and unfixed arrows (dashed) to illustrate the difference between complete and incomplete information settings.
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
2. **No preferences in some results**: Some complexity results and algorithms are presented without preferences; adding preferences increases computational difficulty.
3. **Scalability ceiling**: For larger instances (100+ literals/rules), the ASP approach can time out (600s limit), suggesting limitations for very large knowledge bases.
4. **Binary observations only**: Observations are binary (true/false); no support for graded or probabilistic observations.
5. **Single page rendering issue**: Page 003 originally rendered as black but has been reconstructed from pdftotext extraction.

## Testable Properties

1. **Justification label correctness**: For any complete AT (no unsettled observations), the four justification labels should partition all literals in L.
2. **Stability monotonicity**: If a literal is j-stable, adding more observations (resolving queryables) should not change its status.
3. **Relevance soundness**: If queryable q is not j-relevant for literal l, then resolving q in any direction should not change l's justification status.
4. **Grounded extension uniqueness**: For any given complete AT, there is exactly one grounded extension.
5. **Complexity bounds**: Stability decisions should be verifiable in polynomial time given a witness (coNP membership). Relevance decisions should be verifiable with a Sigma_2^P oracle.

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
