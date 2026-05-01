---
title: "Advancing Algorithmic Approaches to Probabilistic Argumentation under the Constellation Approach"
authors: "Andrei Popescu, Johannes P. Wallner"
year: 2024
venue: "IJCAI 2024 (Workshop / Conference paper)"
doi_url: ""
---

# Advancing Algorithmic Approaches to Probabilistic Argumentation under the Constellation Approach

## One-Sentence Summary
Provides exact tree-decomposition-based dynamic programming algorithms for computing probabilities of extensions and argument acceptability in Probabilistic Argumentation Frameworks (PAFs) under the constellation approach, with new counting complexity results distinguishing set-extension from argument-acceptability problems.

## Problem Addressed
Computing probabilities in PAFs under the constellation approach is computationally hard (FP^{#P}-complete for complete/preferred/stable semantics). Prior work relied on Monte Carlo approximation. This paper provides the first exact DP algorithms exploiting tree-decomposition structure, making exact computation tractable for low-treewidth instances. *(p.1)*

## Key Contributions
- New counting complexity results: counting subframeworks where a set is an extension is #·P-complete (but NOT #P-hard under parsimonious reductions); counting subframeworks where an argument is accepted is #·NP-complete *(p.1, p.4)*
- First dynamic programming algorithm on tree-decompositions for exact probabilistic AF computation under the constellation approach *(p.1, p.5)*
- The DP algorithm handles admissible, complete, stable, and preferred semantics *(p.5)*
- Experimental evaluation showing the approach is competitive with Monte Carlo methods on structured (low-treewidth) instances *(p.8)*
- Extensions: incorporating dependencies between arguments (e.g., mutual exclusion), relaxing independence assumptions *(p.8)*

## Methodology

### Probabilistic Argumentation Framework (PAF)
A PAF is a triple F = (A, R, P) where A is a set of arguments, R is a set of attacks, and P : A ∪ R → (0,1] assigns probabilities to arguments and attacks. *(p.2)*

Under the constellation approach, a subframework F' = (A', R') is a possible world where each argument a ∈ A appears with probability P(a) and each attack (a,b) ∈ R appears with probability P(a,b), independently. *(p.2)*

### Key Probability Formulas

$$
P(F') = \prod_{a \in A'} P(a) \cdot \prod_{a \in A \setminus A'} (1 - P(a)) \cdot \prod_{(a,b) \in R'} P((a,b)) \cdot \prod_{(a,b) \in R \setminus R'} (1 - P((a,b)))
$$
Where: F' = (A', R') is a subframework (possible world), P(a) is probability of argument a existing, P((a,b)) is probability of attack (a,b) existing.
*(p.3)*

$$
P_\sigma^{ext}(F, S) = \sum_{F' \in \mathcal{F}_P(F) : S \in \sigma(F')} P(F')
$$
Where: σ is a semantics (admissible, complete, stable, preferred), S ⊆ A is a set of arguments, F_P(F) is the set of all subframeworks.
*(p.3)*

$$
P_\sigma^{acc}(F, a) = \sum_{F' \in \mathcal{F}_P(F) : \exists S \in \sigma(F'), a \in S} P(F')
$$
Where: a ∈ A is an argument, this computes the probability that a is credulously accepted.
*(p.3)*

### Labeling-Based Approach
The algorithm uses complete labellings L = (I, O, U) where:
- I (in): argument is accepted
- O (out): argument is rejected (attacked by an accepted argument)
- U (undecided): argument is neither in nor out
*(p.3)*

Conditions for complete labelling: *(p.3)*
- a ∈ I iff all its attackers are in O
- a ∈ O iff at least one attacker is in I
- a ∈ U iff not all attackers are in O and no attacker is in I

### Relationship Between Semantics and Labellings
- Admissible: I ⊆ {correctly labelled in}
- Complete: all three sets satisfy the conditions
- Stable: U = ∅
- Preferred: I is maximal (no complete labelling with strictly larger I)
*(p.5)*

## Complexity Results

### Counting Subframeworks for Set-Extension

**Theorem 5.** For σ ∈ {complete, preferred, stable}: counting the number of subframeworks where S is a σ-extension is #·P-complete under Turing reductions. *(p.4)*

**Proposition 2.** Unless P = NP, there is no parsimonious reduction from #SAT to counting subframeworks where a given set is an extension for complete semantics. *(p.4)*

This is because checking whether a subframework has a queried set as a complete extension can be done in polynomial time (a result from Fazzinga, Flesca, Furfaro 2020). *(p.4)*

### Counting Subframeworks for Argument Acceptability

**Theorem 6.** For σ ∈ {complete, under the parameter tree-width}: counting subframeworks where an argument is accepted is #·NP-complete. *(p.5)*

Key insight: computing acceptability is harder than computing set-extension probability because checking whether an argument is in SOME extension of a given subframework requires solving an NP problem (finding the extension), whereas checking if a GIVEN set is an extension is polynomial. *(p.4-5)*

**Theorem 7.** There is a fixed-parameter algorithm w.r.t. treewidth for computing the probability of a set of arguments being a complete extension. *(p.5)*

## Tree-Decomposition-Based DP Algorithm

### Core Data Structure
A tree-decomposition of the PAF's undirected primal graph, where:
- Each node t has a bag B_t ⊆ A (subset of arguments)
- Bags satisfy: every argument in some bag, every attack's endpoints co-occur in some bag, connectedness (bags containing same argument form subtree)
- Width = max bag size - 1
- Treewidth = minimum width over all tree-decompositions
*(p.4)*

### Nice Tree-Decomposition
The algorithm uses "nice" tree-decompositions with four node types: *(p.5)*
1. **Leaf node**: empty bag, no children
2. **Join node**: two children with identical bags
3. **Introduce node**: one child, adds exactly one argument (B_t = B_{t'} ∪ {a})
4. **Forget node**: one child, removes exactly one argument (B_t = B_{t'} \ {a})

Important boundary from the paper text and figures: Popescu & Wallner assume a valid
tree decomposition / nice tree decomposition is available and illustrate one in Fig. 3,
but they do **not** present a concrete algorithm for constructing the underlying tree
decomposition from an elimination ordering. The local bug in our bag-parent selection is
therefore not something the paper directly specifies; the paper starts from a valid TD.

### Algorithm Structure (Algorithm 1 — main)

For a given input PAF F = (A, R, P): *(p.5-6)*
1. Compute nice tree-decomposition (T, (B_t)) of the associated undirected graph
2. Initialize empty table for each node
3. Process nodes in **post-order** traversal
4. For each node type (leaf, introduce, forget, join), apply the corresponding sub-algorithm
5. Return the probability from the root node's table

The paper also states that root and leaf nodes can be assumed to have empty bags, and
that one can transform a rooted decomposition so that each node has at most two children
and each introduce / forget node changes exactly one argument. *(p.5-6)*

### Table Structure
Each row in a table represents a partial labelling of the arguments in the current bag. For a bag with arguments {a, b, c}, a row might be (I, O, U) indicating a is in, b is out, c is undecided. *(p.6)*

The table stores:
- A (partial) labelling ℓ of arguments in the bag
- A probability value p — the sum of P(F') over all subframeworks consistent with this partial labelling for the subtree below this node
*(p.6)*

### Sub-Algorithms

**Leaf nodes:** Table has single row with empty labelling, probability 1. *(p.6)*

**Introduce nodes** (Algorithm 2, adding argument a): *(p.6-7)*
- For each existing row with labelling ℓ' and probability p:
  - Try labelling a as "in" (I): check that no argument in current bag attacks a and is labelled I (i.e., no conflict). Multiply p by P(a).
  - Try labelling a as "out" (O): there must be an attacker in I. Check attacks from I-labelled arguments to a. Multiply by P(a) and attack probabilities.
  - Try labelling a as "undecided" (U): no attacker in I, but not all attackers settled as out yet. Multiply by P(a).
- Witness tracking: for "out" labelling, need at least one attacking argument labelled "in" AND the attack must exist. This is handled via a witness mechanism.
*(p.6-7)*

**Forget nodes** (Algorithm 3, removing argument a): *(p.7)*
- Main concern: finalize conditions that couldn't be checked while a was in the bag
- For "in" arguments: ensure all attackers were out (attacks either didn't exist or were from out-labelled arguments)
- For "out" arguments: ensure at least one witnessed attack from an in-labelled argument
- For "undecided" arguments: conditions checked on removal
- Rows with same labelling (minus the forgotten argument) are merged by summing probabilities
*(p.7)*

**Join nodes** (Algorithm not shown in detail): *(p.6)*
- Combine tables from two children that share the same bag
- Rows with compatible labellings are combined; probabilities are multiplied (since subtrees are independent)

### Probability Updates

When adding argument a, probability is updated by multiplying P(a) and considering the factors for each added attack in the structure. *(p.6)*

$$
p' = p \cdot P(a) \cdot \prod_{(b,a) \in R, \ell(b)=\text{in}} P((b,a)) \cdot \prod_{(a,b) \in R, \ell(b) \neq \text{in}} [\text{factor}]
$$
*(p.6)*

The witnesses are updated as follows: *(p.6)*
- ψ(a) = 1 if some attacker labelled "in" has a certain attack to a
- ψ(a) tracks whether the "out" condition for a has been conclusively witnessed

### Handling Different Semantics

The core algorithm handles **complete** semantics. Other semantics are obtained by: *(p.5)*
- **Admissible**: relax conditions — allow undecided arguments that could be forced out
- **Stable**: at forget time, reject any row with U-labelled arguments (U = ∅ requirement)
- **Preferred**: post-process — a complete extension is preferred iff no strictly larger complete extension exists. Track maximality via inclusion checks.

### Fixed-Parameter Tractability

**Theorem 7:** The algorithm runs in time O(f(k) · n) where k is treewidth and n is number of arguments. The table size per bag is bounded by 3^k (three possible labels per argument in bag). *(p.5)*

This means: for bounded treewidth, the algorithm runs in polynomial time (linear in n, exponential only in treewidth k).

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Treewidth | k (tw) | - | - | 0 to \|A\|-1 | p.4 | Width of tree-decomposition; algorithm is FPT in this |
| Number of arguments | n = \|A\| | - | - | 1+ | p.8 | Problem size |
| Argument probability | P(a) | - | - | (0,1] | p.2 | Probability argument exists in subframework |
| Attack probability | P((a,b)) | - | - | (0,1] | p.2 | Probability attack exists in subframework |
| Number of subframeworks | \|F_P(F)\| | - | - | up to 2^{\|A\|+\|R\|} | p.2 | Exponential in args+attacks |
| Table rows per bag | - | - | - | up to 3^k | p.5 | Three labels (I,O,U) per argument in bag |

## Implementation Details
- Tree-decomposition computed using htd library (Abseher, Musliu, and Woltran 2017) *(p.7)*
- Two implementations: one using rational numbers (exact), one using natural numbers (counting subframeworks) *(p.7)*
- For computing a nice tree-decomposition, used htd library *(p.7)*
- Implemented in Python 3 (ASP/clingo prototype) and as standalone Python *(p.7)*
- For baseline comparison: Monte Carlo sampling and ASP-based exact computation *(p.7)*
- Database-style tree expansion operations (Gottlob et al. 2001) *(p.1)*
- The algorithm computes probabilities for admissible sets and stable semantics as well, under complete semantics conditions *(p.5)*

Implementation consequence for our repo: Popescu 2024 is the authority for the DP over
a valid nice TD, but not for the exact decomposition-construction routine in
`compute_tree_decomposition()`. If our local constructor violates running intersection
or returns a disconnected forest, that is our auxiliary TD-builder bug, not a conflict
with the DP described in the paper.

### Data Structures Needed *(p.5-6)*
- Tree-decomposition: tree T with bags B_t for each node t
- Table per node: rows are (labelling, probability) pairs
- Labelling: mapping from bag arguments to {I, O, U}
- Witness function ψ: tracks whether "out" arguments have confirmed attacking "in" arguments
- Nice tree-decomposition converter

### Initialization *(p.6)*
- Leaf nodes: single row, empty labelling, probability = 1
- Process bottom-up (post-order traversal)

### Edge Cases *(p.6-7)*
- Argument with no attackers: can only be labelled I or U, never O
- Self-attacking arguments: special handling needed
- Uncertain attacks: probability factors for attack existence must be tracked through introduce/forget
- "Forget" of an "undecided" argument: must verify no in-labelled attacker exists (otherwise it should have been out)

## Figures of Interest
- **Fig 1 (p.3):** PAF with certain attacks/uncertain arguments — running example throughout paper
- **Fig 2 (p.5):** Nice tree-decomposition of the PAF from Example 1, with corresponding table contents for the computation
- **Fig 3 (p.5):** Another PAF (Example 6) used to illustrate the DP algorithm

## Results Summary
- Experiments on grids (|A| = n) with possible attacks (bidirectional, one-directional, or no attack per edge) *(p.8)*
- Attack and argument probabilities chosen uniformly at random from (0,1] with probability 0.01 *(p.8)*
- Linux machine, 4-core, 8GB RAM, 900s timeout *(p.8)*
- Clingo (ASP) solver for complete semantics baseline *(p.8)*
- DP approach competitive with Monte Carlo on low-treewidth instances *(p.8)*
- Results show median runtime; DP scales better than ASP on structured instances *(p.8)*
- For higher treewidth (>10-15), the exponential blowup in table size dominates *(p.8)*
- The percentage of the format approach being faster is roughly one third on many instances, but the median runtime is close *(p.8)*

## Limitations
- Algorithm is exponential in treewidth (3^k factor) — impractical for high-treewidth graphs *(p.5, p.8)*
- Current implementation only handles independent probabilities (arguments and attacks independent) *(p.2)*
- Preferred semantics requires additional post-processing for maximality checking *(p.5)*
- Only credulous acceptance considered (not skeptical) *(p.3)*
- Grid instances used in experiments may not reflect real-world AF structure *(p.8)*
- No standard benchmark set exists for probabilistic AFs *(p.8)*

## Arguments Against Prior Work
- Monte Carlo approaches (Fazzinga, Flesca, Furfaro 2013, 2015) can only approximate, never give exact results. For applications requiring exact probabilities, MC is insufficient. *(p.1)*
- Prior exact approaches enumerate all possible worlds explicitly — exponential without exploiting structure. *(p.1)*
- ASP-based approaches (clingo) do not exploit tree-decomposition structure and scale worse on low-treewidth instances. *(p.7-8)*
- Weighting-based approaches (Fichte et al. 2018) for abstract argumentation don't directly handle probabilistic AFs under constellation semantics. *(p.1)*

## Design Rationale
- Tree-decomposition chosen because it is the standard technique for exploiting bounded treewidth in combinatorial problems. The PAF's primal graph (undirected version) admits tree-decomposition. *(p.4-5)*
- Nice tree-decomposition used to simplify case analysis: only four node types instead of arbitrary bag overlaps. *(p.5)*
- Complete labellings (I/O/U) chosen over extension-based representation because they allow local verification: each argument's label can be checked against its neighbors in the current bag. *(p.5-6)*
- Witness mechanism for "out" arguments is necessary because the attacking "in" argument may not be in the same bag — the witness tracks whether the attack has been confirmed. *(p.6)*

## Testable Properties
- For any PAF, the sum of P(F') over all subframeworks F' must equal 1 *(p.2)*
- P_σ^{ext}(F, S) must be in [0, 1] for any semantics σ and set S *(p.3)*
- P_σ^{acc}(F, a) must be in [0, 1] for any argument a *(p.3)*
- For a PAF with all probabilities = 1 (classical AF), the algorithm must return 1.0 for every σ-extension and accepted argument, 0.0 for non-extensions *(p.2-3)*
- Stable extensions are complete extensions with U = ∅: P_stable^{ext} ≤ P_complete^{ext} *(p.5)*
- Preferred extensions are subset-maximal complete extensions *(p.5)*
- Every stable extension is preferred; every preferred is complete; every complete is admissible *(p.2)*
- The number of table rows per node is at most 3^{|B_t|} *(p.5)*
- For a leaf node, the table has exactly one row with probability 1 *(p.6)*
- After a forget node, rows with identical remaining labellings must be merged (summed) *(p.7)*
- The DP result at the root must equal the brute-force enumeration result for small instances *(p.5)*

## Relevance to Project
This paper provides the algorithmic foundation for exact probabilistic argumentation in propstore's PrAF implementation. Key takeaways:
1. **When to use exact vs MC:** Use tree-decomposition DP when treewidth is low (say ≤ 10-15). Use Monte Carlo when treewidth is high or unknown.
2. **Complexity guidance:** Computing P^{ext}(F, S) is #·P-complete; computing P^{acc}(F, a) is #·NP-complete. The acceptability problem is strictly harder (counting-wise).
3. **Implementation blueprint:** The nice tree-decomposition + table-based DP with I/O/U labellings is directly implementable. The witness mechanism for tracking "out" justification is the key non-obvious detail.
4. **Integration with ATMS:** The labelling approach (I/O/U) maps naturally to ATMS assumption labels — each labelling row is essentially an assumption context.

## Open Questions
- [ ] How to extend the DP algorithm to handle dependent argument/attack probabilities (mentioned as future work, p.8)?
- [ ] Can the witness mechanism be simplified for the case of certain attacks (all attack probabilities = 1)?
- [ ] What is the practical treewidth of propstore's argumentation graphs? This determines whether exact DP is feasible.
- [ ] How to handle preferred semantics efficiently in the DP framework (maximality checking)?
- [ ] Can the algorithm be extended to bipolar argumentation (support + attack)?

## Related Work Worth Reading
- Fazzinga, Flesca, Furfaro 2013, 2015, 2019, 2020 — foundational complexity and MC algorithms for probabilistic AFs *(p.1, p.3, p.4)*
- Fichte, Hecher, Meier, Woltran 2018, 2021, 2022 — weighted model counting for abstract argumentation, tree-decomposition DP *(p.1)*
- Dung 1995 — foundational AF semantics *(p.2)*
- Li, Oren, Norman 2011 — probabilistic argumentation semantics *(p.2-3)*
- Hunter, Thimm 2017 — probabilistic reasoning with abstract argumentation *(p.1)*
- Gottlob, Greco, Scarcello 2001 — tree-decomposition for database queries *(p.1)*
- Abseher, Musliu, Woltran 2017 — htd library for tree-decompositions *(p.7)*
- Hemaspaandra, Vollmer 1995 — counting complexity hierarchy (#·P, #·NP classes) *(p.4)*
- Dvořák, Woltran 2012 — complexity of abstract argumentation *(p.2)*

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as foundational AF semantics; all semantics computed by this paper's DP algorithm (admissible, complete, stable, preferred) are Dung's standard semantics *(p.2)*
- [[Li_2011_ProbabilisticArgumentationFrameworks]] — cited as the source of PAF semantics under the constellation approach; this paper's algorithms compute Li et al.'s probability definitions exactly *(p.2-3)*
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — cited as prior work on probabilistic reasoning with AFs; Hunter & Thimm's epistemic approach is an alternative to the constellation approach that this paper targets *(p.1)*
- [[Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth]] — cited as Fichte et al. 2021; predecessor work on tree-decomposition-guided reductions for argumentation. Fichte reduces to SAT/QBF while preserving treewidth; Popescu applies tree-decomposition DP directly to probabilistic AFs

### New Leads (Not Yet in Collection)
- Fazzinga, Flesca, Furfaro (2019, 2020) — foundational complexity results for probabilistic AFs; FP^{#P}-completeness proofs that this paper refines with counting classes
- Gottlob, Greco, Scarcello (2001) — tree-decomposition for database queries; the DP table approach originates here
- Abseher, Musliu, Woltran (2017) — htd library for computing tree-decompositions; implementation dependency
- Hemaspaandra, Vollmer (1995) — counting complexity hierarchy (#·P, #·NP classes); needed to understand the complexity separation results

### Supersedes or Recontextualizes
- (none — this paper extends rather than supersedes existing work)

### Cited By (in Collection)
- (none found)

### Conceptual Links (not citation-based)
- **Tree-decomposition DP for argumentation:**
  - [[Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth]] — **Strong.** Both papers exploit bounded treewidth for tractable argumentation computation, but with complementary approaches: Fichte compiles to SAT/QBF preserving O(k) treewidth, while Popescu runs DP directly on the tree-decomposition with I/O/U labelling tables. Popescu's approach avoids the SAT solver overhead but is specific to probabilistic extension computation. For propstore, both approaches are relevant: Fichte for non-probabilistic semantics computation, Popescu for probabilistic queries.
- **ATMS and multiple-context reasoning:**
  - [[deKleer_1986_AssumptionBasedTMS]] — **Strong.** Popescu's DP table rows (partial labellings with probability weights) are structurally analogous to ATMS labels (minimal assumption sets). Each row represents a context (possible world configuration) with its probability. The ATMS's management of multiple simultaneous consistent contexts maps directly to the constellation approach's enumeration of subframeworks. For propstore, the ATMS label structure could serve as the data structure for storing Popescu's DP table entries.
  - [[Dixon_1993_ATMSandAGM]] — **Moderate.** Dixon proves ATMS context switching equals AGM belief revision. Popescu's probability-weighted contexts add a quantitative dimension: each ATMS context gets a probability, and extension membership becomes a weighted sum over contexts rather than a binary membership test.
- **Probabilistic argumentation semantics:**
  - [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — **Strong.** Hunter & Thimm define epistemic probabilities over arguments (degree of belief), while Popescu computes constellation probabilities (likelihood of structural configurations). For propstore, these are complementary: Hunter's approach assigns beliefs to arguments within a fixed AF; Popescu's approach assigns probabilities to the AF structure itself. Both probability types may be needed.
  - [[Li_2011_ProbabilisticArgumentationFrameworks]] — **Strong.** Li et al. define the PAF semantics; Popescu provides the first exact algorithms. Together they form the complete specification+implementation pair for probabilistic argumentation under the constellation approach.
- **Extension computation:**
  - [[Dung_1995_AcceptabilityArguments]] — **Strong.** Popescu's algorithms compute probabilities over Dung's extension semantics. The I/O/U labelling used in the DP is a direct encoding of Caminada's labelling characterization of Dung's semantics.
