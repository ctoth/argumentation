---
title: "Reasoning in Assumption-Based Argumentation Using Tree-Decompositions"
authors: "Andrei Popescu and Johannes P. Wallner"
year: 2023
venue: "JELIA 2023, LNCS 14281"
doi_url: "https://doi.org/10.1007/978-3-031-43619-2_14"
pages: "192-208"
---

# Reasoning in Assumption-Based Argumentation Using Tree-Decompositions

## One-Sentence Summary
Popescu and Wallner show that many NP-hard reasoning tasks in flat, finite ABA are fixed-parameter tractable by tree-width and give D-FLAT dynamic-programming algorithms, especially a stable-semantics table algorithm, over tree-decompositions of ABA instances. *(p.192, p.199)*

## Problem Addressed
Computational reasoning in structured argumentation formalisms such as ABA, ASPIC+, DeLP, and deductive argumentation is generally hard, and previous tree-width work mostly targeted abstract argumentation or deductive argumentation rather than rule-based structured formalisms such as ABA, ASPIC+, or DeLP. *(p.193)* The paper asks how to exploit tree-width directly for ABA reasoning, including credulous and skeptical acceptance and counting or enumeration of assumption sets. *(p.193, p.195)*

## Key Contributions
- Shows that deciding credulous or skeptical acceptance of atoms for admissible, complete, stable, or preferred semantics in a given ABA framework is FPT with respect to tree-width, via MSO encodings and Courcelle's theorem. *(p.193, p.198-p.199)*
- Defines tree-decomposition based dynamic-programming algorithms for ABA, with a detailed stable-semantics algorithm and adaptations for admissible and complete semantics. *(p.193, p.199-p.202)*
- Instantiates the algorithms in D-FLAT, using ASP to specify partial solutions at each decomposition node while D-FLAT handles table storage and compatible-solution combination. *(p.193, p.203)*
- Evaluates a prototype on generated low-tree-width ABA frameworks, comparing with a Clingo ASP baseline over counting tasks. *(p.203-p.204)*

## Study Design
Pure algorithmic/theoretical paper with a prototype runtime experiment. The experiment uses generated ABA frameworks on k x n grids, controlled low tree-width, random assumptions, and random query atoms. *(p.203-p.204)*

## Methodology
The paper first represents a flat finite ABA framework as a relational structure over a vocabulary for atoms, assumptions, rules, heads, bodies, contraries, and queries. It then encodes derivability, attacks, conflict-freeness, defense, admissibility, completeness, preferredness, stable semantics, and credulous/skeptical acceptance as MSO formulas. Courcelle's theorem gives FPT tractability over bounded-tree-width structures. *(p.196-p.199)*

For constructive computation, the paper uses bottom-up dynamic programming over a nice tree-decomposition. Tables store partial stable assumption sets as quadruples `(I, R, D, CW)`, where `I` is a witness set of atoms, `R` is the set of satisfied rules, `D` is the set of atoms defeated by `I`, and `CW` is a set of counterwitnesses. The DP combines child tables, updates entries at introduce/remove nodes, and accepts root entries with no counterwitnesses. *(p.199-p.202)*

## Key Equations / Formal Models

ABA rule shape:

$$
a_0 \leftarrow a_1,\ldots,a_n
$$

where each `a_i` is in the atom language `L`; `head(r)=a_0` and `body(r)={a_1,\ldots,a_n}`. *(p.194)*

ABA framework:

$$
F=(L,R,A,\overline{\ })
$$

where `(L,R)` is a deductive system, `A subseteq L` is a non-empty set of assumptions, and the contrary function maps assumptions to atoms. The paper assumes finite flat ABA frameworks and allows the contrary function to be partial. *(p.194)*

Forward derivability:

$$
X \vdash_R a
$$

holds if `a in X` or there is a sequence of rules `(r_1,\ldots,r_n)` ending in head `a`, with every body atom of each rule derived earlier or present in `X`; deductive closure is:

$$
Th_R(X)=\{a \in L \mid X \vdash_R a\}
$$

*(p.194)*

Attack between assumption sets:

$$
A \text{ attacks } B \text{ iff } A' \vdash_R \overline{b} \text{ for some } A' \subseteq A \text{ and } b \in B
$$

*(p.194-p.195)*

Tree-decomposition width:

$$
\max\{|D_t| \mid t \in T\}-1
$$

Tree-width is the minimum width over all tree-decompositions of the structure. *(p.195-p.196)*

Courcelle-style runtime:

$$
O(f(|\varphi|,w)\cdot |I|)
$$

for evaluating MSO formula `phi` over a structure `I` of tree-width `w`. *(p.196)*

ABA vocabulary:

$$
\tau_{ABA}=\{atom/1, asm/1, rule/1, head/2, body/2, contrary/2, query/1\}
$$

The associated structure `I_F` has facts for atoms, assumptions, rules, rule heads/bodies, contraries, and query atoms. *(p.196)*

Rule satisfaction by a set variable `E`:

$$
\forall r \left(rule(r) \rightarrow \exists s((head(r,s) \wedge s \in E) \vee (body(r,s) \wedge s \notin E))\right)
$$

This is named `phi_sat(E)` and means each rule is classically satisfied by `E`: either the head is in `E` or some body element is missing. *(p.198)*

Derivability / least-model formula:

$$
\varphi_{Th}(E)=\varphi_{sat}(E)\wedge \forall E'((E' \subseteq E \wedge E' =_A E)\rightarrow \neg\varphi_{sat}(E'))
$$

`E` satisfies the rules and no proper subset with the same assumptions satisfies the rules, so `E` corresponds to the least model of the Horn theory with assumptions as facts. *(p.198)*

Attack:

$$
\varphi_{att}(E,S)=\exists x,a(x \in E \wedge a \in S \wedge contrary(a,x))
$$

`E` attacks `S` if the contrary of an assumption in `S` is contained in `E`. *(p.198)*

Conflict-free:

$$
\varphi_{cf}(E)=\varphi_{Th}(E)\wedge \neg\varphi_{att}(E,E)
$$

*(p.198)*

Defense:

$$
\varphi_{def}(E,A)=\forall S((S\subseteq L \wedge \varphi_{Th}(S)\wedge \varphi_{att}(S,A))\rightarrow \varphi_{att}(E,S))
$$

`E` defends `A` if every derivably closed `S` attacking `A` is attacked by `E`. *(p.198)*

Semantics:

$$
\varphi_{adm}(E)=\varphi_{cf}(E)\wedge \varphi_{def}(E,E)
$$

$$
\varphi_{com}(E)=\varphi_{adm}(E)\wedge \forall S((\varphi_{def}(E,S)\wedge \varphi_{Th}(S))\rightarrow S\subseteq E)
$$

$$
\varphi_{prf}(E)=\varphi_{adm}(E)\wedge \neg\exists E'((E'\subseteq L \wedge E\subset E' \wedge \varphi_{adm}(E')))
$$

Stable semantics is expressed as conflict-freeness plus every assumption outside `E` being attacked by `E`. *(p.198)*

Credulous and skeptical reasoning:

$$
\varphi_\sigma^{Cred}=\exists E(E\subseteq L \wedge \varphi_{query}(E)\wedge \varphi_\sigma(E))
$$

$$
\varphi_\sigma^{Skept}=\forall E((E\subseteq L \wedge \varphi_\sigma(E))\rightarrow \varphi_{query}(E))
$$

where `phi_query(E)` states that all atoms tagged by `query` are in `E`. *(p.198)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Tree-decomposition width | `w` | - | - | `max |D_t| - 1` | 196 | Parameter for Courcelle theorem and FPT result. |
| Tree-decomposition bag | `D_t` | set elements | - | subset of domain `D` | 195 | Bags cover elements, cover relation tuples, and satisfy connectedness. |
| Grid height/width parameter | `k` | atoms per side component | - | `{2,3,5}` | 204 | Generated `k x n` grids for experiments. |
| Grid length parameter | `n` | atoms per side component | - | `{10,20,100,200,400,500,700}` | 204 | Four instances per `k,n`, excluding three D-FLAT errors. |
| Rules per non-assumption head | `rph` | rules | random | `0-3` | 203 | Number of rules per head in generated instances. |
| Runtime timeout | - | seconds | 600 | 600 per run | 204 | Applied to each experimental run. |
| Memory limit | - | MB | 8192 | 8192 | 204 | Applied to experiments. |
| CPU architecture | - | cores | 8 | Intel i5, 8 cores | 204 | Linux 64-bit machine. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| `count-adm` Clingo median | runtime seconds | 600.0 | - | - | generated ABA instances | 204 |
| `count-adm` D-FLAT median | runtime seconds | 287.179 | - | - | generated ABA instances | 204 |
| `count-co` Clingo median | runtime seconds | 0.039 | - | - | generated ABA instances | 204 |
| `count-co` D-FLAT median | runtime seconds | 254.624 | - | - | generated ABA instances | 204 |
| `count-st` Clingo median | runtime seconds | 0.034 | - | - | generated ABA instances | 204 |
| `count-st` D-FLAT median | runtime seconds | 5.97 | - | - | generated ABA instances | 204 |
| `count-adm-q` D-FLAT median | runtime seconds | 98.24 | - | - | query-constrained counting | 204 |
| `count-co-q` D-FLAT median | runtime seconds | 98.39 | - | - | query-constrained counting | 204 |
| `count-st-q` D-FLAT median | runtime seconds | 5.30 | - | - | query-constrained counting | 204 |
| Timeout reduction for `count-adm` | timeouts | 29 vs 55 | - | - | D-FLAT vs Clingo | 204 |
| Stable counting timeouts | timeouts | 0 for `count-st`; 2 D-FLAT vs 0 Clingo for `count-st-q` | - | - | generated ABA instances | 204 |

## Methods & Implementation Details
- The running ABA example has assumptions `{a,b}`, atoms `{a,b,x,y,z}`, rules `r1=(x<-a)`, `r2=(y<-x)`, `r3=(z<-b)`, and contraries `bar(a)=z`, `bar(b)=y`; its stable assumption sets are `{a}` and `{b}`. *(p.194-p.195)*
- Nice tree-decomposition node types used by the algorithm are leaf, root, introduction, removal, and join. Leaves and the root have empty bags; introduction nodes add one object; removal nodes remove one object; join nodes have two children with the same bag. *(p.199)*
- Partial stable assumption sets are quadruples `(I,R,D,CW)`: `I subseteq L` is the witness, `R subseteq R` the satisfied rules, `D subseteq A` defeated atoms, and `CW` counterwitness pairs `(C,R_C)`. *(p.199-p.200)*
- Counterwitnesses share the same assumptions as `I` but have strictly fewer atoms and proper subsets of associated satisfied rules, testing whether atoms in `I` are derivable from the assumptions in `I`. *(p.200)*
- Algorithm 1 iterates over tree-decomposition nodes in post-order and calls Algorithm 2 to fill `Tab(t)` from child tables. *(p.200)*
- Algorithm 2 returns empty tables for leaves, merges compatible child tables at joins, accepts root entries with empty counterwitnesses, branches at introduced atoms by either not adding or adding the atom, updates defeated atoms and satisfied rules, removes atoms only when stable conditions are met, and removes rules only when satisfied. *(p.201-p.202)*
- For admissibility, the adaptation tracks derivability for undefeated atoms, checks undefeated atoms are not attacked by the supported assumptions, tracks defeated atoms, requires assumptions to be either undefeated or defeated, and adds an admissibility check rejecting assumption sets attacked by some undefeated atom. *(p.202)*
- For complete semantics, the adaptation tracks an additional set `AU` of assumptions attacked by undefeated atoms and rejects assumption sets missing undefeated assumptions that are not attacked by an undefeated assumption set. *(p.202)*
- D-FLAT invokes an ASP solver at each decomposition node, computes partial solutions, stores them, and combines compatible partial solutions by extension pointers. *(p.203)*
- The prototype supports enumeration and counting for `adm`, `com`, and `st`, plus skeptical and credulous acceptance checks for those semantics. *(p.203)*

## Figures of Interest
- **Fig. 1 (p.197):** Part of the running example's nice tree-decomposition with table rows for selected nodes. Blue entries are witnesses and red entries are counterwitnesses. It illustrates node 13 introducing atom `x` and table `tau_12` introducing rule `r2`. *(p.197, p.200-p.202)*
- **Table 1 (p.204):** Median runtimes and timeout counts for Clingo and D-FLAT on six counting tasks. D-FLAT reduces timeouts on admissible counting but is slower than Clingo on complete and stable median runtimes. *(p.204)*

## Results Summary
The theoretical result is that credulous or skeptical acceptance of atoms under admissible, complete, stable, or preferred semantics is FPT with respect to the tree-width of the ABA structure. *(p.199)* Experimentally, D-FLAT showed promise for complex counting tasks with many solutions, especially reducing admissible-counting timeouts, while Clingo was faster for complete counting and stable counting was roughly on par or favored Clingo in median runtime. *(p.204)*

## Limitations
- The detailed DP algorithm is presented for stable semantics because of page limits; admissible and complete variants are described as modifications, not full algorithms. *(p.199, p.202)*
- The implementation in D-FLAT does not require nice tree-decompositions, but the paper presents the algorithm over nice decompositions for clarity. *(p.199)*
- Prototype performance depends on D-FLAT performance. The discussion identifies DBMS-based DP and decomposition-guided QBF reductions as natural future comparison points. *(p.205)*
- Previous random ABA generation often produced high tree-width instances, so the experiment uses a controlled low-tree-width grid generator; this limits representativeness of the benchmark distribution. *(p.203-p.204)*

## Arguments Against Prior Work
- Prior tree-width work in argumentation focused mostly on abstract argumentation and deductive argumentation, leaving rule-based structured formalisms such as ABA, ASPIC+, and DeLP without a direct tree-width account. *(p.193)*
- Recent work shows that lifting abstract-argumentation computation to structured argumentation is not immediate and requires dedicated formalism-specific work. *(p.193)*
- MSO encodings give wide applicability but may not yield tight runtime bounds; QBF/decomposition-guided reductions can provide tighter runtime bounds and lower bounds under constraints. *(p.205)*

## Design Rationale
- ABA is represented as a relational structure so MSO can capture semantics and Courcelle's theorem can be applied directly. *(p.196-p.199)*
- The DP algorithm stores witnesses and counterwitnesses because derivability in ABA must be checked against the least model induced by assumptions and rules, not merely by local bag membership. *(p.198-p.200)*
- D-FLAT is used because it was developed specifically for declarative specification of DP algorithms over tree-decompositions, allowing the ABA algorithm to be stated in ASP while D-FLAT handles decomposition and table combination. *(p.199, p.203)*

## Testable Properties
- An implementation of the MSO route should answer credulous/skeptical acceptance under `adm`, `com`, `st`, and `prf` in FPT time parameterized by tree-width, subject to Courcelle's theorem constants. *(p.199)*
- In the stable DP, a root table entry is a full stable assumption set only when its counterwitness set is empty. *(p.200-p.201)*
- At atom removal nodes, if the removed atom is an assumption, Algorithm 2 preserves only entries where the assumption is either in the witness or defeated. *(p.202)*
- At rule removal nodes, Algorithm 2 preserves only entries where the removed rule has already been satisfied. *(p.202)*
- For complete semantics, any supported assumption set that omits undefeated assumptions not attacked by undefeated assumptions should be rejected. *(p.202)*

## Relevance to Project
This is directly relevant to implementation work on structured argumentation because it gives an ABA-specific bridge from formal semantics to bounded-tree-width dynamic programming, including enough table-state structure to guide solver design. It is also a useful comparison point for propstore-style argument reasoning where rule-based derivability, attacks, contraries, and acceptance modes need explicit computational provenance rather than just abstract AF semantics.

## Open Questions
- [ ] Can the D-FLAT algorithm be reimplemented in a propstore-native or Datalog-like engine while preserving the witness/counterwitness invariants? *(p.199-p.203)*
- [ ] Which ABA instance graph representation should define tree-width for practical systems: the full `tau_ABA` structure, a primal/incidence graph, or a normalized rule hypergraph? *(p.196-p.199)*
- [ ] How does the D-FLAT approach compare empirically against decomposition-guided QBF reductions and DBMS-based DP on non-synthetic ABA instances? *(p.205)*
- [ ] Can the same table-state design be adapted cleanly to ASPIC+ or DeLP without collapsing their structured-rule details into abstract AFs? *(p.193, p.205)*

## Related Work Worth Reading
- Lehtonen, Wallner, and Jarvisalo 2021 on declarative algorithms and complexity results for ABA, the direct ASP-style comparison target. *(p.208)*
- Cerutti, Gaggl, Thimm, and Wallner 2018 on foundations of implementations for formal argumentation. *(p.206)*
- Fichte et al. 2021 on decomposition-guided reductions for argumentation and treewidth, relevant for QBF/SAT-style alternatives. *(p.207)*
- Lampis, Mengel, Mitsou, and Ordyniak 2018 on QBF as an alternative to Courcelle's theorem. *(p.208)*
- Dewoprabowo et al. 2022 on practical counting of Dung extensions by dynamic programming. *(p.206)*

## Collection Cross-References

### Already in Collection
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - the direct ASP-based ABA baseline and comparison target for this paper's tree-decomposition route.
- [On the Computational Complexity of Assumption-Based Argumentation for Default Reasoning](../Dimopoulos_2002_ComputationalComplexityAssumption-basedArgumentation/notes.md) - older complexity boundary paper for ABA/default-reasoning semantics.
- [An abstract, argumentation-theoretic approach to default reasoning](../Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/notes.md) - foundational ABA formalism used by the tree-decomposition encoding.

### New Leads (Not Yet in Collection)
- Samer and Szeider (2010) on propositional model counting via tree-decompositions - the model-counting DP substrate behind several bounded-width argumentation algorithms.
- D-FLAT and htd implementation papers - needed if we want a production-quality tree-decomposition backend rather than only a structural heuristic.
- Fichte et al. on decomposition-guided reductions for argumentation and treewidth - present in the sibling `../propstore/papers` collection, but not yet processed in this collection.

### Cited By (in Collection)
- [Algorithmic Approaches to Probabilistic Argumentation under the Constellation Approach](../Popescu_2024_AlgorithmicProbabilisticArgumentationConstellation/notes.md) - cites this paper as the ABA tree-decomposition predecessor to later probabilistic AF algorithms.
- [Advancing Algorithmic Approaches to Probabilistic Argumentation](../Popescu_2024_ProbabilisticArgumentationConstellation/notes.md) - cites this line as part of the bounded-treewidth dynamic-programming toolkit for argumentation.

### Conceptual Links (not citation-based)
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - complementary routing class: Lehtonen's direct ASP route is a strong general default, while Popescu and Wallner create a shape-sensitive route when low treewidth makes DP attractive.
- [Advancing Algorithmic Approaches to Probabilistic Argumentation](../Popescu_2024_ProbabilisticArgumentationConstellation/notes.md) - same authors and same decomposition idea, but applied to probabilistic abstract argumentation rather than flat finite ABA.
- Fichte et al.'s decomposition-guided SAT/QBF reductions - strong conceptual neighbor present in `../propstore/papers`: both exploit bounded treewidth; Fichte preserves treewidth through reductions, while this paper executes dynamic programming directly over ABA structure.
