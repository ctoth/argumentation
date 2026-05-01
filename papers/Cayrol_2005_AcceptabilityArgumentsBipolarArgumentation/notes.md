---
title: "On the Acceptability of Arguments in Bipolar Argumentation Frameworks"
authors: "C. Cayrol, M.C. Lagasquie-Schiex"
year: 2005
venue: "ECSQARU 2005, LNAI 3571"
doi_url: "https://doi.org/10.1007/11518655_33"
---

# On the Acceptability of Arguments in Bipolar Argumentation Frameworks

## One-Sentence Summary
Extends Dung's abstract argumentation framework with an independent support relation alongside defeat, defining bipolar argumentation frameworks (BAFs) with new acceptability semantics (d-admissible, s-admissible, c-admissible extensions) that enforce coherence between support and defeat. *(p.378)*

## Problem Addressed
Classical argumentation frameworks (Dung 1995) model only one kind of interaction between arguments: defeat/attack. However, arguments can also support each other (e.g., confirming a premise used by another argument). This paper addresses how to handle both defeat and support as independent, first-class relations, and how to redefine acceptability semantics accordingly. *(pp.378-379)*

Both relations, defeat and support, are assumed to be independent (i.e., the support relation is not defined in terms of the defeat relation, and vice-versa). *(p.378)*

## Key Contributions
- Formal definition of bipolar argumentation frameworks (BAFs) with independent defeat and support relations *(p.382)*
- New interaction types: supported defeat, indirect defeat, direct defeat *(p.383)*
- Two notions of coherence for sets of arguments: internal coherence (conflict-free) and external coherence (safe sets) *(pp.384-385)*
- Three new admissibility-based semantics: d-admissible, s-admissible, c-admissible *(p.386)*
- Generalized stable and preferred extensions for BAFs *(pp.385-386)*
- Structural properties of extensions in acyclic BAFs (Property 4) *(p.387)*

## Methodology
Extends Dung's abstract approach by adding a support relation to the framework tuple. Derives new types of defeat by combining support sequences with direct defeats. Defines set-level operations (set-defeat, set-support) and builds coherence and admissibility notions on top. Restricts main results to acyclic bipolar interaction graphs. *(pp.382-387)*

The approach instantiates Dung's basic framework with the relation set-defeats; the obtained graph is still acyclic. *(p.385, footnote 8)*

## Background: Dung's Framework (Recap)

An abstract argumentation framework is a pair $\langle \mathcal{A}, \mathcal{R} \rangle$ where $\mathcal{A}$ is a set of arguments and $\mathcal{R}$ is a binary relation called defeat. *(p.380)*

Dung's key definitions recalled: *(p.380)*
- **Conflict-free**: $S$ is conflict-free iff there exist no $A, B \in S$ such that $A \mathcal{R} B$
- **Acceptable**: an argument $A$ is acceptable w.r.t. $S$ iff for each $B$ that defeats $A$, there exists $C \in S$ that defeats $B$
- **Admissible**: $S$ is admissible iff $S$ is conflict-free and each argument in $S$ is acceptable w.r.t. $S$
- **Preferred extension**: maximal (for set-inclusion) admissible set
- **Stable extension**: $S$ is conflict-free and $\forall A \notin S$, $\exists B \in S$ such that $B \mathcal{R} A$
- **Grounded extension**: least fixed point of the characteristic function $F(S) = \{A \mid A \text{ is acceptable w.r.t. } S\}$

For acyclic defeat graphs: unique stable extension = unique preferred extension = grounded extension. *(p.380)*

## Argumentation Process (Three Steps)

The argumentation process is based on three steps: *(p.378)*
1. The exchange of arguments
2. The valuation of interacting arguments
3. The definition of the most acceptable of these arguments

The acceptability of an argument depends on its membership of some sets, called acceptable sets or extensions, characterised by particular properties. It is a collective acceptability. *(p.384)*

## Key Definitions

### Definition 1 (Abstract Bipolar Argumentation Framework)
A BAF is a tuple $\langle \mathcal{A}, \mathcal{R}_{def}, \mathcal{R}_{sup} \rangle$ where:
- $\mathcal{A}$ is a finite set of arguments
- $\mathcal{R}_{def} \subseteq \mathcal{A} \times \mathcal{A}$ is a defeat relation
- $\mathcal{R}_{sup} \subseteq \mathcal{A} \times \mathcal{A}$ is a support relation

The support relation is assumed to be totally independent of the defeat relation (i.e., it is not defined using the defeat relation). *(p.382)*

### Definition 2 (Bipolar Interaction Graph)
The graph associated with a BAF has two kinds of edges: one for the defeat relation and another one for the support relation. *(p.382)*

A **leaf** is an argument $A$ such that no argument defeats $A$ and no argument supports $A$ (i.e., $A$ has no predecessors in the bipolar interaction graph). *(p.382)*

### Definition 3 (Supported and Indirect Defeat)

A **supported defeat** for argument $B$ is a sequence:

$$
A_1 \mathcal{R}_1 \ldots \mathcal{R}_{n-1} A_n, \quad n \geq 3
$$

where $A_n = B$, $\forall i = 1 \ldots n-2$, $\mathcal{R}_i = \mathcal{R}_{sup}$ and $\mathcal{R}_{n-1} = \mathcal{R}_{def}$.

An **indirect defeat** for argument $B$ is a sequence:

$$
A_1 \mathcal{R}_1 \ldots \mathcal{R}_{n-1} A_n, \quad n \geq 3
$$

where $A_n = B$, $\forall i = 2 \ldots n-1$, $\mathcal{R}_i = \mathcal{R}_{sup}$ and $\mathcal{R}_1 = \mathcal{R}_{def}$.

A **direct defeat** is a simple $(A, B) \in \mathcal{R}_{def}$ (also called a supported defeat of length 2 by extension, footnote 3). *(p.383)*

### Definition 4 (Set-Defeat and Set-Support)
Let $S \subseteq \mathcal{A}$, $A \in \mathcal{A}$:
- $S$ **set-defeats** $A$ iff there exists a supported defeat or indirect defeat for $A$ from an element of $S$
- $S$ **set-supports** $A$ iff there exists a sequence $A_1 \mathcal{R}_1 \ldots \mathcal{R}_{n-1} A_n$, $n \geq 2$, with $\forall i = 1 \ldots n-1$, $\mathcal{R}_i = \mathcal{R}_{sup}$, $A_n = A$, and $A_1 \in S$

*(p.383)*

### Definition 5 (Defence by a Set)
$S \subseteq \mathcal{A}$ defends collectively $A \in \mathcal{A}$ iff $\forall B \in \mathcal{A}$, if $\{B\}$ set-defeats $A$ then $\exists C \in S$ such that $\{C\}$ set-defeats $B$.

Note: Uses set-defeat instead of Dung's original defeat (footnote 4). *(p.383)*

### Definition 6 (Conflict-Free Set)
$S \subseteq \mathcal{A}$ is conflict-free iff $\nexists A, B \in S$ such that $\{A\}$ set-defeats $B$.

Note: This generalizes Dung's conflict-free using set-defeats (in the sense of Definition 4) rather than just direct defeat (footnote 5). *(p.384)*

### Definition 7 (Safe Set)
$S \subseteq \mathcal{A}$ is safe iff $\nexists B \in \mathcal{A}$ such that $S$ set-defeats $B$ and either $S$ set-supports $B$, or $B \in S$.

Safe = no argument is both set-defeated and set-supported (or member) of $S$. This definition is inspired by the definition of a controversial argument proposed in [1] (Dung) and the notion in [7] (footnote 6). *(p.385)*

### Property 1
- If $S$ is safe, then $S$ is conflict-free *(p.385)*
- If $S$ is conflict-free and closed for $\mathcal{R}_{sup}$, then $S$ is safe *(p.385)*

### Definition 8 (Stable Extension)
$S \subseteq \mathcal{A}$ is a stable extension of $\langle \mathcal{A}, \mathcal{R}_{def}, \mathcal{R}_{sup} \rangle$ iff $S$ is conflict-free and $\forall A \notin S$, $S$ set-defeats $A$. *(p.385)*

In acyclic BAFs, Definition 8 ensures the existence of a unique stable extension (by instantiating Dung's framework with set-defeats, footnote 8). However, the unique stable extension is not always safe. *(p.385)*

### Example 3
The set $\{A, H\}$ is the unique stable extension, and it is safe. An acyclic bipolar argumentation framework may have no safe stable extension. *(pp.385-386)*

### Consequence 1
If $S$ is a stable extension of $\langle \mathcal{A}, \mathcal{R}_{def}, \mathcal{R}_{sup} \rangle$, then $S$ is not safe iff $S$ set-supports an element of $\mathcal{A} \setminus S$. *(p.386)*

### Definition 9 (d-Admissible Set)
$S \subseteq \mathcal{A}$ is d-admissible iff $S$ is conflict-free and $S$ defends all its elements. *(p.386)*

### Definition 10 (s-Admissible Set)
$S \subseteq \mathcal{A}$ is s-admissible iff $S$ is safe and $S$ defends all its elements. *(p.386)*

### Definition 11 (c-Admissible Set)
$S \subseteq \mathcal{A}$ is c-admissible iff $S$ is conflict-free, $S$ is closed for $\mathcal{R}_{sup}$, and $S$ defends all its elements.

Note: c-admissible implies s-admissible (by Property 1). From all the previous results, it follows that each c-admissible set is s-admissible, and each s-admissible set is d-admissible. *(p.386)*

### Definition 12 (Preferred Extensions)
- A **d-preferred** extension is a maximal (for set-inclusion) d-admissible set *(p.386)*
- A **s-preferred** extension is a maximal s-admissible set *(p.386)*
- A **c-preferred** extension is a maximal c-admissible set *(p.386)*

### Example 3 (continued)
The set $\{G, H, E\}$ is d-admissible, but not s-admissible. The set $\{G, H, I, E, D\}$ is the unique d-preferred extension. *(p.387)*

### Property 2
There exists a d-preferred (resp. s-preferred, c-preferred) extension. *(p.386)*

### Property 3
A d-preferred (resp. s-preferred) extension of $\langle \mathcal{A}, \mathcal{R}_{def}, \mathcal{R}_{sup} \rangle$ is a d-preferred extension of $\langle \mathcal{A}, \mathcal{R}_{def} \cup \mathcal{R}_{sup}, \emptyset \rangle$. *(p.386, implied from text; need to verify)*

### Property 4 (Acyclic BAFs)
Let $S$ be the unique stable extension of an acyclic BAF: *(p.387)*
1. The s-preferred extensions and c-preferred extensions are subsets of $S$ *(p.387)*
2. If $S$ is safe, there is a unique s-preferred extension which equals $S$, which is also a d-preferred extension *(p.387)*
3. If $S$ is not safe, each s-preferred extension is included in a s-preferred extension. The s-preferred extensions are the subsets of $S$ which are maximal for set-inclusion and safe *(p.387)*
4. If $S$ is safe, $\emptyset$ is safe, there is only one c-preferred extension *(p.387)*
5. If $S$ is not safe and $\emptyset$ is safe, there is only one c-preferred extension *(p.387)*

### Example 4
Consider the argumentation system on p.387:
- $\{A_1, A_2, B\}$ is the only d-preferred extension *(p.387)*
- $\{A_1, A_3\}$ and $\{M\}$ are the only two s-preferred extensions. None of them is closed for $\mathcal{R}_{sup}$. *(p.387)*
- $\{A_1\}$ is the unique c-preferred extension *(p.387)*
- $\{A_1, A_2, B\}$ is the unique stable extension *(p.387)*

## Parameters

| Name | Symbol | Units | Default | Range | Notes | Page |
|------|--------|-------|---------|-------|-------|------|
| Arguments | $\mathcal{A}$ | - | - | finite set | Set of abstract arguments | p.382 |
| Defeat relation | $\mathcal{R}_{def}$ | - | - | $\subseteq \mathcal{A} \times \mathcal{A}$ | Binary relation on arguments | p.382 |
| Support relation | $\mathcal{R}_{sup}$ | - | - | $\subseteq \mathcal{A} \times \mathcal{A}$ | Binary relation on arguments, independent of defeat | p.382 |

## Implementation Details

### Data Structures
- BAF: directed graph with two edge types (defeat edges, support edges) *(p.382)*
- Can be represented as two adjacency lists or a single graph with labeled edges *(p.382)*
- Bipolar interaction graph: single directed graph merging both relations with edge labels *(p.382)*

### Key Algorithms (Implicit)
1. **Compute supported defeats**: Find all paths where support edges lead to a final defeat edge *(p.383)*
2. **Compute indirect defeats**: Find all paths where a defeat edge is followed by support edges *(p.383)*
3. **Compute set-defeat**: Check if any element of S has a supported or indirect defeat path to target *(p.383)*
4. **Compute set-support**: Check if any element of S has a pure support path to target *(p.383)*
5. **Check conflict-free**: For all pairs in S, verify no set-defeat exists *(p.384)*
6. **Check safe**: Verify S does not simultaneously set-defeat and set-support (or contain) any argument *(p.385)*
7. **Check closed for R_sup**: For all A in S, if A R_sup B then B in S *(p.386)*
8. **Compute extensions**: Enumerate maximal admissible sets under chosen semantics *(p.386)*

### Edge Cases
- Acyclic vs. cyclic: Main results (Property 4) only hold for acyclic bipolar interaction graphs *(p.387)*
- Empty set is always d-admissible and s-admissible (when safe), but not necessarily c-admissible *(p.386)*
- A stable extension may not be safe (Example 3: {A, H} is unique stable extension but not s-admissible in the second sub-example) *(pp.385-386)*
- Unique stable extension always exists for acyclic BAFs (by instantiating Dung with set-defeats) *(p.385)*
- An acyclic bipolar argumentation framework may have no safe stable extension *(p.386)*

## Figures of Interest
- **Fig (p.381, Example 1):** Argumentation graph for murder trial example with 5 arguments ($A_1$ through $A_5$), showing defeat edges. A leaf is an argument with no defeaters and no supporters.
- **Fig (p.383, Example 2):** Bipolar interaction graph with nodes A-K showing supported defeats (A-B-C-D, E-C) and indirect defeat (G-A-B-C). Support edges shown with double-line arrows, defeat edges with single arrows.
- **Fig (p.384):** Diagrams illustrating internal vs external coherence violations. Top row: three cases of internal incoherence (set-defeat within Set S). Bottom row: two cases of external incoherence (Set S simultaneously set-defeats and set-supports same argument).
- **Fig (p.387, Example 4):** Argumentation system showing distinct d-preferred, s-preferred, and c-preferred extensions.

## Example 1 (Murder Trial)
Arguments in a murder trial scenario: *(p.381)*
- $A_1$: in favour of *w* (the butler did it), with premises [*r*: witness saw him]
- $A_2$: in favour of *w*, with premises [*s*: the butler had a motive]
- $A_3$: in favour of $\neg w$, with premises [*t*: the butler has an alibi]
- $A_4$: in favour of *w*, with premises [*r'*: if the alibi is short-sighted, reliable witness]
- $A_5$: in favour of *w* confirming the witness is reliable

Defeat edges: $A_3$ defeats $A_1$, $A_4$ defeats $A_3$. Support edges: $A_2$ supports $A_1$ (same conclusion), $A_5$ supports $A_4$ (confirms premise). *(p.381)*

Note: a defeat edge is represented by a crossed arrow on the interaction graph. *(p.381)*

## Section 3: Bipolarity and Interaction

Conflicts captured by the defeat relation in argumentation systems, and used for contradiction-based negative interactions. The concept of defence has been introduced in order to reinstate some of the defeated arguments, especially those whose defeaters are in turn defeated. *(p.381)*

Most logical theories of argumentation assume that if an argument $A_1$ defends an argument $A_2$ (i.e., $A_1$ defeats the defeater of $A_2$), then $A_1$ is a kind of support for $A_2$. But support can exist independently: an argument can support another without defeating its defeaters. *(p.381)*

Three types of positive interaction identified in the literature: *(p.381)*
1. An argument $A_1$ confirms the premises of $A_2$
2. $A_1$ confirms the conclusion of $A_2$ (same conclusion, different premises)
3. $A_1$ is brought by $A_2$ (on one side, $A_1$ gets a support and on the other side, $A_1$ gives a confirmation)

## Arguments Against Prior Work

1. **Dung's framework models only one kind of interaction.** In most existing argumentation frameworks, only one kind of interaction between arguments is considered: the defeat (attack) relation. However, recent studies have shown that another kind of interaction may exist -- an argument can support another argument. *(p.378)*
2. **Defence is not the same as support.** In Dung's framework, the concept of defence (A defeats the defeater of B) provides an implicit, indirect form of positive interaction. But direct support -- where an argument confirms the premises or conclusion of another, or is brought forward by another -- is a fundamentally different relationship that exists independently of any defeat chain. *(p.381)*
3. **Cognitive psychology motivates bipolarity.** Studies in cognitive psychology have shown that positive and negative evaluations are assessed by independent systems, suggesting that argumentation frameworks should model support and defeat as independent relations rather than deriving one from the other. *(p.379)*
4. **Conflict-free is insufficient for bipolar coherence.** Dung's notion of conflict-free (no direct defeat within a set) is too weak when support relations exist. A set can be conflict-free in Dung's sense yet still be incoherent because it simultaneously defeats and supports the same argument (external incoherence). *(p.384-385)*
5. **Stable extensions can be unsafe.** In bipolar frameworks, the unique stable extension (which always exists for acyclic BAFs) may not be safe -- it may set-support an argument outside the extension while also set-defeating it. This means Dung's stable semantics alone does not guarantee coherent behavior when support relations are present. *(p.385-386)*
6. **Classical frameworks cannot model supported and indirect defeat.** When support sequences combine with defeat, new types of conflict emerge: supported defeat (support chain ending in defeat) and indirect defeat (defeat followed by support chain). These cannot be represented in a framework with only a single defeat relation. *(p.383)*

## Design Rationale

1. **Support and defeat as independent, first-class relations.** The central design choice: the support relation is not defined in terms of the defeat relation, and vice-versa. Both are primitive binary relations on the set of arguments. This independence is motivated by cognitive psychology research on bipolar preferences. *(p.378, p.382)*
2. **Abstract approach following Dung's methodology.** Like Dung, the paper abstracts from the internal structure of arguments and focuses on the relations between them. Arguments are treated as atomic entities whose role is determined entirely by the defeat and support relations. *(p.382, p.388)*
3. **Derived interaction types from primitive relations.** Supported defeat (support chain + final defeat) and indirect defeat (initial defeat + support chain) are defined as composite interaction types derived from sequences of primitive defeat and support edges. This allows the framework to capture transitive effects of support on conflict. *(p.383)*
4. **Two-level coherence: internal and external.** Internal coherence requires conflict-free (no set-defeat within the set). External coherence requires safety (no argument is simultaneously set-defeated and set-supported or contained by the set). This two-level design captures the distinct problems of self-contradiction (internal) and ambivalence (external). *(p.384-385)*
5. **Three-tier admissibility hierarchy.** d-admissible (conflict-free + defence), s-admissible (safe + defence), and c-admissible (conflict-free + closed for R_sup + defence) form an increasing strength hierarchy. This gives users three levels of commitment to bipolar coherence, with c-admissible being the strongest (and most conservative). *(p.386)*
6. **Restriction to acyclic frameworks for clean results.** The paper deliberately restricts its main structural results (Property 4) to acyclic bipolar interaction graphs, where unique stable extensions exist and the relationships between d-preferred, s-preferred, and c-preferred extensions can be precisely characterized. Cyclic frameworks are left for future work. *(p.385, p.387)*
7. **Instantiation of Dung via set-defeats.** The framework generates a standard Dung-style AF by using set-defeats (which incorporate both supported and indirect defeats) as the attack relation. This ensures all of Dung's results about extension existence carry over to the bipolar setting. *(p.385, footnote 8)*

## Results Summary
- Three levels of admissibility semantics of increasing strength: d-admissible (weakest), s-admissible, c-admissible (strongest) *(p.386)*
- For acyclic BAFs: unique stable extension always exists; s-preferred and c-preferred are subsets of it *(pp.385, 387)*
- When the unique stable extension is safe, it equals the unique s-preferred extension *(p.387)*
- c-admissible sets are always s-admissible (Property 1 consequence) *(p.386)*
- The paper focuses on acyclic frameworks; cyclic case left for future work *(p.387)*
- The hierarchy: c-admissible $\Rightarrow$ s-admissible $\Rightarrow$ d-admissible *(p.386)*
- Each d-preferred (resp. c-preferred) extension is included in a d-preferred extension *(p.387)*
- There is only one d-preferred extension in an acyclic BAF and it is the unique stable extension (implied by Property 4 and instantiation of Dung) *(p.387)*

## Limitations
- Results restricted to acyclic bipolar argumentation frameworks *(p.387)*
- No computational complexity analysis provided *(p.388, mentioned as future work)*
- No algorithms given explicitly (only definitions and properties) *(throughout)*
- Support relation semantics not fully explored (what exactly constitutes support is application-dependent) *(p.381)*
- Cyclic frameworks and their properties left entirely to future work *(p.388)*
- No comparison with other approaches to handling support (e.g., evidential support) *(throughout)*

## Future Work (Stated by Authors)
- A thorough study of the new semantics, including computational issues *(p.388)*
- Investigation of new characteristic properties, such as a generalization of "being closed for $\mathcal{R}_{sup}$" — interested in sets $S$ which are closed for $\mathcal{R}_{sup}$ and which contain any argument supporting an argument of $S$. Their idea is to define a meta argumentation system over such sets of arguments. *(p.388)*

## Testable Properties
- Safe implies conflict-free (Property 1, first part) *(p.385)*
- Conflict-free + closed for R_sup implies safe (Property 1, second part) *(p.385)*
- c-admissible implies s-admissible *(p.386)*
- s-admissible implies d-admissible *(p.386)*
- Every c-preferred extension is s-admissible *(p.386)*
- In acyclic BAFs, a unique stable extension always exists *(p.385)*
- The s-preferred and c-preferred extensions are subsets of the unique stable extension (acyclic case) *(p.387)*
- Empty set is always d-admissible *(p.386)*
- If stable extension S is safe, then S is the unique s-preferred extension *(p.387)*
- Stable extension S is not safe iff S set-supports an element of $\mathcal{A} \setminus S$ (Consequence 1) *(p.386)*
- {A,H} and {B,F} are conflict-free in Example 2 *(p.385)*
- {H,B} is not conflict-free in Example 2 (in the sense of Dung) *(p.385)*
- {H,C} is not conflict-free because C suffers indirect defeat from H *(p.385)*
- {B,D} is not conflict-free because D suffers supported defeat from B *(p.385)*
- {A,H} is not safe since A supports B and H defeats B *(p.385)*
- {B,F} is not safe since D suffers supported defeat from B, and F supports D *(p.385)*
- {G,I,H} is safe *(p.385)*
- {G,H,I,E} is conflict-free and closed for $\mathcal{R}_{sup}$, so it is safe *(p.385)*

## Relevance to Project
Foundational paper for bipolar argumentation. Provides the formal definitions needed to implement argumentation frameworks that handle both attack and support between arguments/claims, which is essential for modeling evidential relationships in a propositional store where claims can both conflict with and reinforce each other.

## Open Questions
- [ ] How do these semantics extend to cyclic BAFs? *(p.388, listed as future work)*
- [ ] What is the computational complexity of computing the various extensions? *(p.388, listed as future work)*
- [ ] How does this relate to later work on evidential support vs. deductive support?
- [ ] Connection to ASPIC+ structured argumentation with bipolar relations?
- [ ] How does the meta argumentation system over closed-for-support sets work? *(p.388, mentioned as future direction)*

## Related Work Worth Reading
- Dung, P.M. (1995). On the acceptability of arguments. Artificial Intelligence 77, 321-357 — foundational framework this extends *(p.389, ref [1])*
- Karacapilidis, N., Papadias, D. (2001). Computer supported argumentation and collaborative decision making — support relation in argumentation *(p.389, ref [5])*
- Amgoud, L., Cayrol, C., Lagasquie-Schiex, M.C. (2004). On the bipolarity in argumentation frameworks — companion/prior work on BAFs *(p.389, ref [2])*
- Boella, G., et al. (2004). Handbook of Philosophical Logic, Volume 4 — coalitions of arguments *(p.389, ref [4])*
- Verheij, B. (2003). Artificial argument assistants — support in argumentation *(p.389, ref [11])*
- Bondarenko, A., Dung, P.M., Kowalski, R.A., Toni, F. (1997). An abstract, argumentation-theoretic approach to default reasoning *(p.389, ref [3])*
- Prakken, H., Sartor, G. (1997). Argument-based extended logic programming with defeasible priorities *(p.389, ref [8])*
- Simari, G., Loui, R. (1992). A mathematical treatment of defeasible reasoning and its applications *(p.389, ref [10])*

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [1]; this paper directly extends Dung's abstract argumentation framework by adding an independent support relation. All of Cayrol's definitions (conflict-free, admissible, stable, preferred) generalize Dung's originals using set-defeat in place of direct defeat.

### New Leads (Not Yet in Collection)
- Amgoud, Cayrol, Lagasquie-Schiex (2004) — "On the bipolarity in argumentation frameworks" — companion/prior work developing the bipolar argumentation concept *(p.389, ref [2])* — **Related paper now in collection** as `Amgoud_2008_BipolarityArgumentationFrameworks` (same authors' 2008 comprehensive survey)
- Karacapilidis, N. and Papadias, D. (2001) — "Computer supported argumentation and collaborative decision making" — practical system (Hermes) with support relations *(p.389, ref [5])* — **Now in Collection** as `Karacapilidis_2001_ComputerSupportedArgumentationCollaborative`
- Verheij, B. (2002) — "On the existence and multiplicity of extensions in dialectical argumentation" — relevant to extension computation *(p.389, ref [11])* — **Now in Collection** as `Verheij_2002_ExistenceMultiplicityExtensionsDialectical`

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[Amgoud_2008_BipolarityArgumentationFrameworks]] — cites Cayrol & Lagasquie-Schiex via [CLS04/CLS05/CLS06]; comprehensively reviews and extends the BAF semantics from this paper within a broader bipolarity taxonomy.

### Conceptual Links (not citation-based)
- [[Dung_1995_AcceptabilityArguments]] — **Strong.** Cayrol directly extends Dung's framework. Where Dung defines admissible/preferred/stable/grounded extensions over a single attack relation, Cayrol adds a support relation and derives three new admissibility levels (d-admissible, s-admissible, c-admissible) that collapse to Dung's originals when the support relation is empty. The paper instantiates Dung's framework using set-defeats to prove existence of stable extensions in acyclic BAFs.
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — **Strong.** ASPIC+ and BAFs represent two different approaches to enriching Dung's abstract framework. ASPIC+ adds internal structure to arguments (premises, rules, conclusions) while keeping Dung's single attack relation. Cayrol adds a second relation (support) while keeping arguments abstract. Both generate Dung-style frameworks at the abstract level. A full argumentation system could combine both: structured arguments (ASPIC+) with bipolar relations (Cayrol).
- [[Clark_2014_Micropublications]] — **Moderate.** Clark's micropublication model includes both support and challenge relations between scientific claims, and explicitly references Toulmin-Verheij defeasible argumentation with bipolar networks (Use Case 8). Cayrol's BAF formalization provides the abstract semantics for determining which claims are jointly acceptable in such bipolar claim-evidence networks.
- [[Mayer_2020_Transformer-BasedArgumentMiningHealthcare]] — **Strong.** Mayer's pipeline extracts exactly the structures Cayrol formalizes: bipolar argumentation frameworks with both support and attack relations between arguments. The evidence-claim-support/attack graphs mined from RCT abstracts are concrete instances of Cayrol's BAFs, and Cayrol's acceptability semantics (d-admissible, s-admissible, c-admissible) could be applied to determine which of the extracted clinical arguments are jointly acceptable.
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — **Strong.** Modgil & Prakken's ASPIC+ and Cayrol's BAFs enrich Dung's framework in complementary directions: ASPIC+ adds internal argument structure and preference-based defeat while keeping a single attack relation; BAFs add a support relation while keeping arguments abstract. Modgil 2018's open question 5 explicitly asks how ASPIC+'s attack-based conflict-free definition interacts with bipolar support relations. Combining both extensions (structured bipolar argumentation with preferences) remains an open research direction.
- [[Brewka_2010_AbstractDialecticalFrameworks]] — **Strong.** ADFs strictly generalize Cayrol's bipolar argumentation frameworks. Where Cayrol adds a separate support relation alongside Dung's attack relation, Brewka & Woltran unify both into per-node acceptance conditions — any propositional formula over parents. Bipolar ADFs (BADFs), where each link is purely supporting or attacking, correspond to BAFs. ADFs also handle non-bipolar links (neither purely supporting nor attacking), which BAFs cannot express.
- [Developing the Abstract Dialectical Framework](../Polberg_2017_DevelopingAbstractDialecticalFramework/notes.md) — **Strong.** Polberg's PhD thesis builds on this BAF foundation in Chapter 4 §4.6 and §4.7, developing translations BAF↔{AFN, EAFC, EAS, AF, SETAF, ADF, AFRA} (Translations 51-66 plus Table 4.8). The thesis cites later Cayrol & Lagasquie-Schiex BAF papers ([CLS09]/[CLS10]/[CLS13]/[CLS15]) but engages directly with the d-/s-/c-admissibility hierarchy this 2005 paper introduces. Polberg's "BAF Fundamental-Lemma failure" criticism (which restricts BAF to `d-`complete and `d-`grounded only) is a direct pushback on the admissibility extensions defined here.
