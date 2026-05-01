---
title: "Advancing Algorithmic Approaches to Probabilistic Argumentation under the Constellation Approach"
authors: "Andrei Popescu, Johannes P. Wallner"
year: 2024
venue: "KR 2024 — 21st International Conference on Principles of Knowledge Representation and Reasoning"
doi_url: "https://proceedings.kr.org/2024/55/"
---

# Advancing Algorithmic Approaches to Probabilistic Argumentation under the Constellation Approach

## One-Sentence Summary
Provides exact dynamic-programming algorithms for computing extension and acceptability probabilities in probabilistic argumentation frameworks (PrAFs) under the constellation approach, parameterized by treewidth of the primal graph.

## Problem Addressed
Reasoning with defaulting and conflicting knowledge in argumentation is computationally hard under the constellation approach. Prior work established #P-completeness and #P^NP-completeness results but lacked practical exact algorithms. The paper fills this gap with tree-decomposition-based dynamic programming algorithms that are fixed-parameter tractable (FPT) w.r.t. treewidth. *(p.0)*

## Key Contributions
- First exact tree-decomposition-based DP algorithm for computing extension and acceptability probabilities in PrAFs under the constellation approach *(p.0)*
- Existing complexity results restated: extension probability is #P-complete for admissible, stable, and complete semantics; acceptability is #P-complete for admissible/stable and #P^NP-complete for complete *(p.1)*
- Preprocessing via connected-component decomposition before tree-decomposition *(p.4)*
- Proof that the DP approach is fixed-parameter tractable w.r.t. treewidth *(p.4)*
- Experimental evaluation comparing DP vs. brute-force and ASP-based approaches *(p.7-8)*

## Methodology
The paper first decomposes PrAFs by connected components, then applies nice tree-decomposition to each component's primal graph. A bottom-up DP algorithm processes the tree-decomposition in post-order, maintaining tables of partial solutions at each bag (node). The algorithm handles four node types: leaf, introduce (argument or attack), forget, and join. Probabilities are computed by summing over all subframeworks consistent with each partial solution. *(p.4-7)*

## Key Equations / Statistical Models

### PrAF Definition
$$
F = (A, R, P)
$$
Where: $(A, R)$ is an AF with arguments $A$ and attacks $R \subseteq A \times A$; $P: A \cup R \to (0,1]$ assigns independent probabilities to arguments and attacks.
*(p.2)*

### Subframework Probability
$$
P(F') = \prod_{x \in A' \cup R'} P(x) \cdot \prod_{x \in (A \cup R) \setminus (A' \cup R')} (1 - P(x))
$$
Where: $F' = (A', R')$ is a subframework of $F$; each element present with probability $P(x)$, absent with $1 - P(x)$; independence assumed.
*(p.2)*

### Extension Probability
$$
P_{ext}^{\sigma}(F)(S) = \sum_{F' \in sub(F), S \in \sigma(F')} P(F')
$$
Where: $\sigma$ is a semantics (admissible, complete, stable, grounded, preferred); $sub(F)$ is the set of all subframeworks; $S$ is a candidate extension.
*(p.2)*

### Acceptability Probability
$$
P_{acc}^{\sigma}(F)(a) = \sum_{F' \in sub(F), \exists S \in \sigma(F') : a \in S} P(F')
$$
Where: $a$ is an argument whose probability of being accepted (appearing in some $\sigma$-extension) is computed.
*(p.2-3)*

### Extension-Based vs. Labelling-Based Views
$$
P_{ext}^{\sigma}(F)(S) = \sum_{F' \in sub(F)} P(F') \cdot [S \in \sigma(F')]
$$
The paper proves a direct correspondence between the extension-based and labelling-based views for computing these probabilities. *(p.3)*

### Labelling Completeness
A complete labelling $\ell$ of $F = (A, R)$ satisfies:
- $\ell(a) = \text{in}$ iff all attackers of $a$ are labelled $\text{out}$
- $\ell(a) = \text{out}$ iff some attacker of $a$ is labelled $\text{in}$
- $\ell(a) = \text{undec}$ otherwise (not forced in or out)
*(p.2)*

### Connected Component Multiplication
$$
P_{ext}^{\sigma}(F)(S) = \prod_{i} P_{ext}^{\sigma}(C_i)(S \cap A_i)
$$
Where: $C_1, \ldots, C_k$ are the connected components of $F$; probabilities of components are independent and can be multiplied.
*(p.4)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument probability | P(a) | — | — | (0,1] | 2 | Independent per-argument |
| Attack probability | P(r) | — | — | (0,1] | 2 | Independent per-attack |
| Treewidth | tw | — | — | varies | 4 | Key tractability parameter |
| Grid width (experiments) | k | — | — | 1-7 | 7 | Controls treewidth in grid PAFs |
| Grid height (experiments) | — | — | — | up to 150 | 7 | Number of argument rows |
| Number of arguments | |A| | — | — | up to 150 | 7 | In experimental instances |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| DP vs brute-force | Runtime ratio | orders of magnitude faster | — | — | Low treewidth grids | 8 |
| DP feasibility ceiling | Max treewidth | ~6-7 | — | — | Grid PAFs, exact computation | 8 |
| ASP (clingo) comparison | Competitive with DP | Similar for small instances | — | — | clingo encoding | 8 |
| Scalability | Arguments handled | 150 | — | — | Grid PAFs with bounded tw | 7-8 |

## Methods & Implementation Details

### Preprocessing: Connected Component Decomposition *(p.4)*
- Before tree-decomposition, decompose the PrAF into connected components
- Process each component independently
- Combine results by multiplying probabilities (independence)
- Reduces problem size significantly for sparse PAFs

### Nice Tree-Decomposition *(p.5)*
- Input: primal graph of the PrAF (arguments as vertices, edges between arguments that attack each other or share an attack relation)
- A tree-decomposition is a tree where each node is a "bag" of vertices
- **Nice** tree-decomposition restricts to four node types:
  1. **Leaf node**: empty bag
  2. **Introduce node**: adds exactly one element (argument or attack) to parent bag
  3. **Forget node**: removes exactly one argument from parent bag
  4. **Join node**: two children with identical bags, merges their tables

### DP Table Structure *(p.5-6)*
Each bag maintains a table of rows, each row is a tuple:
- $E_i$: partial subframework description (which arguments/attacks are present)
- $att_i$: attacks within current context
- $c_i$: complete labelling candidate (in/out/undec for each argument in bag)
- $p_i$: accumulated probability
- $w_i$: witness — a partial labelling used to verify completeness conditions

### Algorithm 1: Main DP *(p.5)*
1. Compute nice tree-decomposition of primal PAF graph
2. Initialize empty table for each bag
3. Process bottom-up (post-order traversal)
4. At root, sum probabilities of all valid complete extensions

### Algorithm 2: Introduce Argument Node *(p.6)*
- When introducing argument $a$:
  - For each existing row, create up to 3 new rows (a labelled in/out/undec)
  - Check labelling consistency with existing attacks
  - Update witness for completeness verification
  - Multiply probability by $P(a)$ if present, $(1 - P(a))$ if absent

### Algorithm 3: Forget Argument Node *(p.6-7)*
- When forgetting argument $a$:
  - Project out $a$ from all rows
  - Merge rows that become identical after projection
  - Sum probabilities of merged rows
  - Check completeness conditions before forgetting

### Introduce Attack Node *(p.6)*
- When introducing attack $(a, b)$:
  - For each existing row, check if attack is consistent with current labelling
  - If $a$ is labelled "in" and $b$ is labelled "in", the row is invalid (conflict)
  - Update attack set and probabilities accordingly

### Join Node *(p.6)*
- Two children with identical bags
  - For compatible rows (same labelling), multiply probabilities
  - Combine subframework descriptions
  - Merge attack sets

### Completeness Checking via Witnesses *(p.5-6)*
- A witness is a partial labelling used to check that "undecided" labels are justified
- An argument labelled "undec" must have: not all attackers out (otherwise should be "in"), not some attacker in (otherwise should be "out")
- Witnesses track whether these conditions can be met for arguments that have been forgotten

### Theorem 6: Fixed-Parameter Tractability *(p.4)*
- There is a fixed-parameter algorithm w.r.t. treewidth for computing:
  - The probability of a set of arguments being a complete extension
  - Parameters: treewidth $k$, algorithm runs in time $f(k) \cdot n$ for some function $f$

## Figures of Interest
- **Fig 1 (p.2):** A PrAF with certain (solid) and uncertain (dashed) arguments and attacks. Example with 6 arguments showing subframework enumeration.
- **Fig 2 (p.5):** Nice tree-decomposition of the PrAF from Example 6, showing bag structure with introduce/forget/join nodes.
- **Fig 3 (p.5):** Tree decomposition of the primal graph with introduce nodes for arguments and attacks.
- **Table 1 (p.8):** Median running times in seconds (timeouts) for complete semantics across different grid sizes and widths.

## Results Summary
The DP algorithm significantly outperforms brute-force enumeration for PrAFs with low treewidth (tw <= 6-7). For grid-based PAFs, the algorithm scales to 150 arguments when treewidth is bounded. The ASP/clingo-based comparison shows competitive performance for small instances but the DP approach has better theoretical guarantees. For high treewidth (>15-20), neither exact approach is feasible, confirming the need for sampling-based approaches (e.g., Li et al. 2012 Monte Carlo). *(p.7-8)*

## Limitations
- Algorithm complexity is exponential in treewidth — for dense graphs with high treewidth, the approach is infeasible *(p.8)*
- Currently limited to complete semantics in the full algorithm; admissible and stable require adaptations *(p.8)*
- The approach does not solve the same problem for preferred semantics (requires different techniques) *(p.8)*
- Only handles independent probabilities (no correlations between argument/attack existence) *(p.8)*
- Witness mechanism adds overhead to table sizes *(p.5-6)*

## Arguments Against Prior Work
- Brute-force enumeration of all $2^{|A|+|R|}$ subframeworks is clearly infeasible for practical sizes *(p.1)*
- ASP-based encodings (Fazzinga, Flesca, Furfaro 2013, 2015) provide alternative exact approaches but lack the FPT guarantees of tree-decomposition *(p.8)*
- Li et al. 2012 Monte Carlo approach provides approximate answers but no exactness guarantees *(p.0, p.8)*
- Previous work on PrAF acceptability (Dung 2010; Hunter and Thimm 2017) focused on the epistemic approach rather than the constellation approach, which has different semantics *(p.0)*

## Design Rationale
- Tree-decomposition chosen because it exploits graph structure (bounded treewidth) to achieve FPT complexity *(p.4)*
- Nice tree-decomposition preferred over arbitrary decomposition for algorithmic simplicity — each step handles exactly one element *(p.5)*
- Connected component preprocessing reduces problem size without changing semantics *(p.4)*
- Witness mechanism chosen to handle completeness checking without backtracking — tracks conditions that need to be verified when arguments are forgotten from bags *(p.5-6)*
- Labelling-based view (in/out/undec) preferred over extension-based view for the DP because it naturally captures complete semantics conditions *(p.2-3)*

## Testable Properties
- For any PrAF, $\sum_{S} P_{ext}^{\sigma}(F)(S) \leq 1$ (probabilities of extensions sum to at most 1, can be less because some subframeworks may have no $\sigma$-extension) *(p.2)*
- $P_{acc}^{\sigma}(F)(a) \geq P_{ext}^{\sigma}(F)(S)$ for any $S$ containing $a$ (acceptability probability is at least as large as any single extension probability containing $a$) *(p.2-3)*
- Connected component decomposition: $P_{ext}^{\sigma}(F)(S) = \prod_i P_{ext}^{\sigma}(C_i)(S \cap A_i)$ — multiplication of independent components *(p.4)*
- For a PAF with all probabilities = 1, the result must equal the deterministic AF extensions *(p.2)*
- For stable semantics, the sum of all extension probabilities equals the probability that a stable extension exists *(p.2)*
- The DP algorithm and brute-force enumeration must produce identical results for any PrAF *(p.7)*

## Relevance to Project
This paper is directly relevant to propstore's probabilistic argumentation layer. The project already implements Li et al. 2012 Monte Carlo sampling for PrAFs. This paper provides:
1. **Exact computation alternative** — for PrAFs with low treewidth, exact probabilities can be computed instead of MC approximation
2. **Complexity bounds** — confirms #P/#P^NP hardness, justifying MC as default with exact computation as optimization for structured instances
3. **Connected component optimization** — already partially implemented in propstore's component decomposition for MC dispatch (Hunter & Thimm 2017)
4. **Tree-decomposition algorithms** — could be implemented as an exact-mode solver alongside the existing MC sampler
5. **Treewidth as decision criterion** — compute treewidth to decide whether exact DP or MC sampling is appropriate

## Open Questions
- [ ] What is the practical treewidth of argumentation frameworks generated by propstore's ASPIC+ bridge?
- [ ] Could the tree-decomposition approach be combined with MC for a hybrid strategy (exact for low-tw components, MC for high-tw)?
- [ ] How does the witness mechanism interact with propstore's existing ATMS labelling?
- [ ] The paper's "constellation approach" treats argument/attack existence as independent — does this match propstore's PrAF model?

## Related Work Worth Reading
- Fazzinga, Flesca, and Furfaro 2013, 2015, 2018: ASP-based approaches to probabilistic argumentation complexity
- Popescu and Wallner 2023: Reasoning in assumption-based argumentation using tree-decompositions (JELIA 2023) — predecessor to this work
- Wallner 2020: Structural constraints for dynamic operators in abstract argumentation
- Dvořák, Woltran et al. 2012: Tractable abstract argumentation via backdoor sets (structural parameters)
- Samer and Szeider 2010: Algorithms for propositional model counting (foundational for #P DP)
