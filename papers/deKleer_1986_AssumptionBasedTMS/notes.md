---
title: "An Assumption-based TMS"
authors: "Johan de Kleer"
year: 1986
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/0004-3702(86)90080-9"
---

# An Assumption-based TMS

## One-Sentence Summary
Defines the Assumption-based Truth Maintenance System (ATMS), a new TMS architecture that labels every datum with the sets of assumptions under which it holds, enabling simultaneous exploration of multiple problem-solving contexts without backtracking or retraction. *(p.127)*

## Problem Addressed
Conventional justification-based TMSs (Doyle's TMS) maintain a single consistent database state, requiring expensive context switching, suffering from overzealous contradiction avoidance, experiencing the unouting problem, and being unable to compare multiple solutions simultaneously. *(pp.138-140)* These limitations make them poorly suited for tasks like differential diagnosis, qualitative reasoning, and constraint satisfaction where multiple hypothetical worlds must coexist. *(p.133)*

## Key Contributions
- Introduces the **ATMS** as a fundamentally new kind of TMS that manipulates **assumption sets** rather than justifications alone *(p.127)*
- Defines the core data structures: **nodes**, **assumptions**, **justifications**, **environments**, **labels**, **nogoods**, and **contexts** *(pp.143-147)*
- Establishes four key label properties: **consistency**, **soundness**, **completeness**, and **minimality** *(pp.144-145)*
- Shows how the ATMS eliminates context switching, backtracking, retraction, and the unouting problem *(pp.154-156)*
- Introduces **classes** as a mechanism for grouping nodes and encoding constraint-language variables *(pp.153-154)*
- Provides detailed **implementation guidance** using bit-vectors for environments, hash tables for subset tests, and three-cache optimization for environment unions *(pp.157-160)*
- Presents a complete comparison showing how the ATMS overcomes all seven limitations of conventional TMSs *(pp.154-156)*

## Methodology
The paper proceeds through:
1. **Motivation via search analysis** (Section 2): Shows four defects of chronological backtracking (futile backtracking, rediscovering contradictions, rediscovering inferences, incorrect ordering) and how dependency-directed backtracking partially addresses them *(pp.134-137)*
2. **Limitations of conventional TMSs** (Section 3): Catalogs seven specific problems (single-state, overzealous contradiction avoidance, switching states, dominance of justifications, cumbersome machinery, unouting, circular support) *(pp.138-140)*
3. **ATMS definition** (Section 4): Formal definitions of all data structures and algorithms *(pp.141-153)*
4. **Limitations removed** (Section 5): Shows how the ATMS resolves each limitation *(pp.154-156)*
5. **Implementation** (Section 6): Practical data structure and algorithm choices *(pp.157-160)*
6. **Summary** (Section 7): Four key ATMS properties *(pp.160-161)*

## Key Equations

Justification form (propositional Horn clause): *(p.143)*

$$
x_1, x_2, \ldots \Rightarrow n
$$

Material implication interpretation: *(p.143)*

$$
x_1 \wedge x_2 \wedge \cdots \rightarrow n
$$

Derivability condition (node n holds in environment E given justifications J): *(p.143)*

$$
E, J \vdash n
$$

Inconsistency condition: *(p.143)*

$$
E, J \vdash \perp
$$

Label soundness (for every environment E in n's label): *(p.144)*

$$
J \vdash E \rightarrow n
$$

Label completeness (every consistent E for which J entails E->n is a superset of some label environment E'): *(p.144)*

$$
E' \subseteq E
$$

Label update algorithm (complete label for consequent node n given justification k with antecedent labels j_ik): *(p.151)*

$$
\bigcup_k \left\{ x \mid x = \bigcup_i x_i \text{ where } x_i \in j_{ik} \right\}
$$

In propositional form, a complete label is computed by converting the conjunction of disjunctions: *(p.151)*

$$
\bigvee_k \bigwedge_i j_{ik}
$$

into disjunctive normal form, then removing inconsistent and subsumed environments. *(p.151)*

## Parameters

| Name | Symbol | Units | Default | Range | Notes | Page |
|------|--------|-------|---------|-------|-------|------|
| Number of assumptions | n | - | - | 1-1000+ | Practical ATMS handles n=1000 (2^1000 space) | p.152 |
| Garbage collection threshold | - | % | 30 | - | ~30% of assumptions can typically be garbage collected | p.158 |
| Nogood cache size threshold | - | assumptions | 3 | - | Nogoods of length 3+ cached per assumption | p.158 |

## Implementation Details

### Core Data Structures

**ATMS Node** has five slots: *(p.152)*
1. **Datum**: Problem solver's representation of the fact
2. **Label**: Set of environments (computed by ATMS, never modified by problem solver)
3. **Justifications**: List of derivations of the datum
4. **Consequents**: List of justifications where node is antecedent
5. **Contradictory**: Single bit indicating whether datum is contradictory

**Environment** has three additional slots beyond basic: *(p.152)*
1. **Assumptions**: Set of assumptions defining it
2. **Nodes**: Set of nodes whose label mentions it
3. **Contradictory**: Single bit for inconsistency

**Justification** has three slots: *(p.152)*
1. **Informant**: Problem-solver-supplied description of inference
2. **Consequent**: The node justified
3. **Antecedents**: List of nodes the inference depends on

**Assumption** has three additional slots (beyond node slots): *(p.160)*
1. **Position**: Bit-vector position corresponding to this assumption
2. **Contras**: Bit-vector of other assumptions it is inconsistent with
3. **Nogoods**: Minimal nogoods of length three or greater in which it appears

**Environment** has three additional implementation slots: *(p.160)*
1. **Contras**: Bit-vector of other assumptions inconsistent with it
2. **Cache**: A cache of the results of adding assumptions to this environment
3. **Count**: Number of assumptions

### Four Node Types
1. **Premises**: Justification with no antecedents; label = {empty environment}; hold universally *(p.146)*
2. **Assumptions**: Label contains singleton environment mentioning itself; notation: gamma_x for assumption associated with datum x *(p.146)*
3. **Assumed nodes**: Neither premise nor assumption; justified under an assumption *(p.147)*
4. **Derived nodes**: All other nodes; derived from justifications *(p.147)*

### Four Node Categories
Each context implicitly separates nodes into three categories, and combined with non-context information yields four: *(p.145)*
1. **True**: Nodes which hold in the empty environment; must hold in every consistent context; this set grows monotonically *(p.145)*
2. **In**: Nodes whose label has at least one nonempty environment; hold in at least one nonuniversal consistent context; this set grows nonmonotonically *(p.145)*
3. **Out**: Nodes whose label is empty; hold in no known consistent context; this set grows nonmonotonically *(pp.145-146)*
4. **False**: Nodes which do not hold in any context which has or will be found; this set grows monotonically *(p.146)*

### Bit-Vector Representation *(p.157)*
- Each assumption assigned a unique bit position
- Environment = bit-vector of assumptions
- Union of environments = bitwise OR
- Subset test = (set1 AND NOT set2) == 0
- Hash table keyed by bit-vectors for O(1) environment lookup
- Nogood test via hash table of nogood bit-vectors

### Three-Cache Optimization for Environment Unions *(p.158)*
When adding a single assumption to an environment:
1. **First cache**: Set of minimal nogoods of size >= 3 containing this assumption
2. **Second cache**: Bit-vector of assumptions inconsistent with this environment
3. **Third cache**: Each added assumption paired with resulting consistent environment
These three caches combined with the hash table make assumption addition very fast.

### Label Update Algorithm *(pp.151-152)*
1. For each new justification, compute cross-product of antecedent labels (union of one environment from each antecedent)
2. Remove inconsistent environments (check against nogood database)
3. Remove subsumed environments (any environment that is a superset of another in the label)
4. If new label differs from old, propagate to all consequent nodes
5. If node is gamma_perp, add new environments to nogood database and remove from all labels

### Retraction of Justifications *(p.153)*
- Direct retraction is inefficient (isomorphic to LISP garbage collection)
- Preferred approach: conjoin extra "defeasability" assumption with justification
- To retract: contradict the conjoined assumption
- This avoids recursive label invalidation

### Assumption Garbage Collection *(pp.158-159)*
- An assumption can be garbage collected if all consequent nodes are true (hold universally) or false (contradictory)
- Or if the singleton environment containing the assumption is contradictory
- Typically ~30% of assumptions qualify
- Must integrate into justifications before collecting; problem solver must signal when collectible
- Garbage collection removes the assumption from the environment hash table and nogood database, and the bit-vector position is recycled

### Lazy Label Updates *(p.159)*
- Labels for contradictory nodes must always be updated (otherwise contradictions will be missed)
- For non-contradictory nodes, label updates can be deferred until the node is examined
- A second propagator sends "update" messages backwards along justification links

### Complexity *(pp.152-153)*
- Efficiency is proportional to number of environments actually considered, not total space size
- Most environments are inconsistent in practice, so label sizes remain manageable
- Worst case requires constructing the full environment lattice (2^n), but this requires cleverly constructed pathological justifications
- In practice, inconsistencies are identifiable in small subsets of assumptions, so large parts of the lattice need never be checked

## Figures of Interest
- **Fig. 1 (p.141):** Reasoning system architecture -- Problem Solver sends justifications to TMS, TMS returns beliefs. Shows the two-component architecture with problem solver containing domain knowledge (P(a), forall x P(x)->Q(x), Q(a)) and TMS containing propositional justifications.
- **Fig. 2 (p.149):** Environment lattice for assumptions {A, B, C, D, E} -- shows how environments form a lattice with subset relationships, circled nodes = contexts of a particular datum (gamma_{x+y=1}), squared nodes = contexts of another datum (gamma_{x=1}), crossed-out nodes = nogoods and their supersets. The single nogood is {A, B, E}.

## Results Summary
The ATMS: *(pp.152-153, 160-161)*
- Handles n=1000 assumptions (2^1000 potential contexts) efficiently because only minimal environments are stored in labels *(p.152)*
- Efficiency is proportional to number of environments actually considered, not total space size *(p.153)*
- Most environments are inconsistent in practice, so label sizes remain manageable *(p.153)*
- Three primitive operations: create node, create assumption, add justification *(p.150)*
- Order-independent: results insensitive to order of assumption/justification introduction *(p.150)*

## Seven Limitations of Conventional TMSs *(pp.138-140)*

1. **Single-state problem**: Only one solution can be considered at a time; impossible to compare two equally plausible solutions *(p.138)*
2. **Overzealous contradiction avoidance**: If A and B are contradictory, the TMS guarantees either A or B will be worked on, but not both; only assertions directly affected by the contradiction should be retracted *(pp.138-139)*
3. **Switching states is difficult**: No efficient mechanism to temporarily change an assumption outside of contradiction response; once a contradiction is introduced it cannot be removed *(p.139)*
4. **Dominance of justifications**: Assumptions are context-dependent (any node whose current supporting justification depends on some other node being out); the set of considered assumptions changes as problem solving proceeds *(p.139)*
5. **Machinery is cumbersome**: Determining well-founded support requires global constraint satisfaction; detecting loops of odd numbers of nonmonotonic justifications is expensive *(p.139)*
6. **Unouting**: When a datum is derived, retracted when a contradiction occurs, and then reasserted when a second contradiction causes context switch, previously discovered data can be rederived -- the process of determining which retracted data should be reasserted is called unouting *(pp.139-140)*
7. **Circular support**: Although it is simple to construct circular justifications (a => b and b => a), the basic ATMS mechanism will never mistakenly use them as a basis for support *(p.155)*

## Four ATMS Properties (Summary) *(pp.160-161)*

1. **Label consistency**: All inconsistent environments are identified and defined not to have contexts; they do not appear in node labels *(p.160)*
2. **Label soundness**: No context will contain a datum it should not; nodes which hold in no context will have empty labels, ensuring the problem solver will not mistakenly work on irrelevant nodes *(p.160)*
3. **Label completeness**: Every context will contain every datum it should; all nodes which hold in any context have nonempty labels, enabling the problem solver to identify all relevant nodes *(pp.160-161)*
4. **Label minimality**: Each node label has the fewest disjuncts and each disjunct has the fewest assumptions; changing any label assumption affects the node's status *(p.161)*

## Additional Findings

### TMS as Cache and Learning Scheme *(p.129)*
The TMS serves three roles: (1) cache for all inferences ever made so they need not be repeated; (2) enables nonmonotonic inferences ("Unless there is evidence to the contrary infer A"); (3) constraint satisfaction procedure to determine what data is believed. The ATMS can be viewed as an intelligent cache, or a very primitive learning scheme.

### Spatial Metaphor *(pp.129-130)*
The actions of the ATMS are best understood in terms of a spatial metaphor. Assumptions are the dimensions of the search space. A solution corresponds to a point in the space, and a context (characterized by a set of assumptions) defines a point, line, plane, volume, etc. depending on its generality. When a derivation is made, the ATMS records it in the most general way so that it covers as large a region of the space as possible. Conversely, when a contradiction is recorded, the ATMS finds its most general form to rule out as much of the search space as possible.

### Problem-Solver-TMS Interface Protocol *(pp.130, 157)*
De Kleer in [8] presents a problem-solver-TMS protocol which, if followed, allows the TMS to control the problem solver so that no inference is ever done twice. *(p.141)* The problem solver compiles rules, the TMS runs them to determine solutions. A rule examined by the problem solver (i.e., compiled) need never be examined again on the same data because it is already compiled within the TMS as a justification. *(p.130)*

### Distinction Between Assumption and Assumed Datum *(p.142)*
An *assumption* is restricted to designate a decision to assume without any commitment as to what is assumed. An *assumed datum* is the problem-solver datum that has been assumed to hold. Assumptions are connected to assumed data via justifications.

### ATMS Permits Derived Assumptions *(p.142)*
The ATMS permits assumptions to be derived if need be, although this paper avoids utilizing this feature. This has provoked considerable controversy.

### Classes as Variables *(pp.153-154)*
In many applications a node can be a member of at most one class. In such cases, the class is viewed as a variable and its nodes as values. Each pair of nodes in a closed class are marked inconsistent. Classes are also used to represent patterns in assertional languages, where every assertion is a node and every rule antecedent pattern is a class.

### Binary Nogoods Are Efficiently Represented *(p.158)*
As a side-effect of the representation of binary nogoods, oneof disjunctions are represented at no cost. Without this efficient representation, n^2 nogoods would have been required to represent a oneof disjunction of size n.

### Contradiction Handling by Length *(p.157)*
Contradictions involving less than three assumptions are common and best handled with special case mechanisms: a contradiction of the empty environment indicates an error; a contradiction of length one indicates an individual assumption has become inconsistent; every ATMS operation on assumptions first checks whether any supplied assumptions are inconsistent.

## Limitations
- The ATMS is oriented toward finding ALL solutions; extra cost is incurred to find fewer solutions (opposite of conventional TMS tradeoff) *(p.137)*
- Worst-case exponential in number of assumptions (2^n environments) *(pp.152-153)*
- Pathological cases exist where every possible environment is a minimal nogood or minimal label environment for some node *(p.153)*
- Direct justification retraction is expensive; the defeasability-assumption workaround adds complexity *(p.153)*
- Node-class framework, while convenient, is not logically necessary *(p.153)*
- The ATMS does not guarantee that irrelevant nodes will ultimately be irrelevant; conversely, although label completeness enables identifying all relevant nodes, this does not guarantee they will ultimately be relevant *(p.161)*

## Testable Properties
- Label consistency: No environment in any node's label should be a superset of any nogood *(p.144)*
- Label soundness: Every environment in a node's label must entail the node given the justifications *(p.144)*
- Label completeness: Every consistent environment from which the node is derivable must be a superset of some label environment *(p.144)*
- Label minimality: No environment in a label is a superset of another environment in the same label *(p.145)*
- Nogoods are closed under subset: if {A,B} is nogood, {A,B,C} need not be stored (it's implied) *(p.148)*
- Order independence: The same set of assumptions and justifications must produce the same labels regardless of introduction order *(p.150)*
- Node categories partition: Every node is in exactly one of {true, in, out, false} sets; these are non-overlapping *(p.145)*
- Bit-vector subset: For environments E1, E2 represented as bit-vectors, E1 subset of E2 iff (E1 AND NOT E2) == 0 *(p.157)*
- Assumption garbage: An assumption is collectible iff its singleton environment is nogood OR all its consequent nodes are true or false *(p.158)*
- Circular justifications are harmless: a => b and b => a produces no label propagation because both start with empty labels; any environment added by the loop would be a superset of one already present *(p.155)*
- Label update termination: the simple label update process must terminate because there are a finite number of assumptions *(p.152)*

## Relevance to Project
This is the foundational paper for the ATMS, which is the core inference substrate for the propstore's assumption-tracking, environment management, and hypothetical reasoning. Every concept introduced here (environments, labels, nogoods, contexts, label properties) is directly used in the propstore world model. The companion paper [8] (already in collection as deKleer_1986_ProblemSolvingATMS) builds the problem-solving architecture on top of this foundation.

## Open Questions
- [ ] How does the ATMS interact with probabilistic or graded assumptions (not addressed in this paper)?
- [ ] What are practical limits on number of assumptions before bit-vector operations become impractical?
- [ ] How does the three-cache optimization perform with very dense nogood sets?

## Collection Cross-References

### Already in Collection
- [[deKleer_1986_ProblemSolvingATMS]] -- companion paper in same journal issue; builds the problem-solving architecture (consumers, scheduling, constraint language, control disjunctions) on top of the ATMS substrate defined here

### Now in Collection (previously listed as leads)
- [[Doyle_1979_TruthMaintenanceSystem]] -- The original justification-based TMS that the ATMS replaces. Introduces support-list and conditional-proof justifications, the truth maintenance process, dependency-directed backtracking with nogoods, and control patterns for defaults and alternatives. The ATMS addresses all seven limitations cataloged in Section 3 of this paper.
- [[Reiter_1980_DefaultReasoning]] -- Cited as [18]; provides the formal framework for default reasoning (assumptions held in absence of contrary information) that the ATMS supports computationally. Reiter's extensions (fixed-point belief sets under defaults) correspond to ATMS environments.

### New Leads (Not Yet in Collection)
- de Kleer (1986) -- "Extending the ATMS" -- extends the basic ATMS with default reasoning, disjunction axioms, propositional expressions *(cited as [7], p.128)*
- Stallman and Sussman (1977) -- "Forward reasoning and dependency-directed backtracking" -- early dependency tracking that the ATMS builds upon *(cited as [20], p.137)*
- McAllester (1978) -- "A three-valued truth maintenance system" -- cited as [14], one of the TMS mechanisms analyzed for limitations *(p.137)*
- Williams (1984, 1985) -- "ART the advanced reasoning tool" -- alternative architecture that handles unouting via multiple datum copies *(cited as [22,23], pp.156-157)*

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[deKleer_1986_ProblemSolvingATMS]] -- references this as [8] throughout for ATMS definitions, label properties, and the problem-solver-TMS protocol
- [[Dixon_1993_ATMSandAGM]] -- proves the ATMS functional specification is behaviourally equivalent to AGM belief revision under appropriate entrenchment encoding
- [[Shapiro_1998_BeliefRevisionTMS]] -- surveys the ATMS as one of four TMS architectures, describing its assumption-set-based label tracking
- [[Martins_1988_BeliefRevision]] -- cites as [6]; the main alternative approach to assumption-based reasoning that MBR/SWM compares against
- [[Falkenhainer_1987_BeliefMaintenanceSystem]] -- the BMS extends Doyle's TMS in a different dimension (continuous beliefs) than the ATMS (multiple contexts); complementary extensions

### Conceptual Links (not citation-based)
- [[deKleer_1986_ProblemSolvingATMS]] -- direct companion; this paper defines the ATMS substrate, that paper defines the problem-solving architecture that runs on top of it
- [[Martins_1983_MultipleBeliefSpaces]] -- **Strong.** Both systems maintain multiple hypothetical contexts simultaneously. MBR's restriction sets are functionally analogous to ATMS nogoods; MBR's contexts map to ATMS environments. Key difference: MBR operates within a relevance logic while the ATMS is logic-independent.
- [[deKleer_1984_QualitativePhysicsConfluences]] -- **Strong.** The qualitative physics framework is the application domain that motivated the ATMS. Multiple interpretations from qualitative constraint satisfaction correspond directly to ATMS environments.
- [[Alchourron_1985_TheoryChange]] -- **Strong.** The AGM postulates define rational belief revision; Dixon (1993) proved the ATMS satisfies them. The ATMS's context switching implements AGM contraction/expansion.
- [[Ginsberg_1985_Counterfactuals]] -- **Moderate.** Ginsberg's counterfactual evaluation (set proposition to unknown, recompute closure) maps directly to ATMS assumption retraction and label recomputation.
- [[Gärdenfors_1988_RevisionsKnowledgeSystemsEpistemic]] — **Strong.** Defines the epistemic entrenchment postulates that formalize retraction priority — the ATMS's assumption labels provide the computational substrate from which entrenchment orderings can be extracted (Dixon 1993 proves this correspondence).
- [[Popescu_2024_ProbabilisticArgumentationConstellation]] — **Strong.** Popescu's DP table rows (partial I/O/U labellings with probability weights) are structurally analogous to ATMS labels (minimal assumption sets). Each row represents a context (possible world configuration) with its probability. The constellation approach's enumeration of subframeworks maps to the ATMS's management of multiple simultaneous consistent contexts. For propstore, the ATMS label structure could serve as the data structure for Popescu's probability-weighted DP entries.

## Related Work Worth Reading
- Doyle [12]: Original justification-based TMS (the system the ATMS improves upon) *(p.161)*
- de Kleer [7]: Extending the ATMS with propositional expressions (disjunction axioms) *(p.161)*
- de Kleer [8]: Problem solving with the ATMS (companion paper, already in collection) *(p.161)*
- Martins [13]: Reasoning in multiple belief spaces (related multi-context approach) *(p.161)*
- Williams [22]: ART advanced reasoning tool (alternative architecture compared in paper) *(p.162)*
- Stallman and Sussman [20]: Forward reasoning and dependency-directed backtracking (early dependency tracking) *(p.162)*
- Reiter [18]: Default logic (formal framework for the kind of reasoning the ATMS supports) *(p.162)*
