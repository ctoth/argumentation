---
title: "AGM Meets Abstract Argumentation: Expansion and Revision for Dung Frameworks"
authors: "Ringo Baumann, Gerhard Brewka"
year: 2015
venue: "IJCAI-15"
doi_url: "https://www.ijcai.org/Abstract/15/387"
produced_by:
  agent: "claude-opus-4-6"
  skill: "paper-reader"
  timestamp: "2026-03-29T03:02:27Z"
---
# AGM Meets Abstract Argumentation: Expansion and Revision for Dung Frameworks

## One-Sentence Summary
Defines AGM-style expansion and revision operators for Dung argumentation frameworks using "Dung logics" — families of logics where ordinary equivalence equals strong equivalence — and reformulates the AGM postulates as properties of monotonic consequence relations over AFs.

## Problem Addressed
Prior work on AF dynamics (expansion, revision, contraction) lacked a systematic connection to the well-established AGM theory of belief change. The classical AGM framework operates on belief sets (deductively closed sets of formulas), but AFs are not propositional theories. The paper bridges this gap by constructing formal logics ("Dung logics") whose models are AFs, enabling the direct application of AGM postulates to argumentation framework change. *(p.1)*

## Key Contributions
- Introduces **Dung logics**: a family of logics called Dung logics where the models are AFs and propositional inference in these logics coincides with strong equivalence of AFs *(p.1)*
- Derives **AGM expansion** for AFs: a concrete expansion operator satisfying all required postulates, based on the notion of a Dung logic *(p.3-4)*
- Derives **AGM revision** for AFs: a concrete revision operator satisfying all required postulates, using a total preorder on models *(p.4-5)*
- Shows that the intersection of models (AFs) is the key operation, and that standard approaches based on distance measures do not work for AFs *(p.4)*
- Establishes **4-equivalence**: a notion of model satisfiability for Dung logics that unifies all standard semantics (stable, preferred, grounded, complete, admissible, conflict-free, stage, semi-stable, ideal, eager) *(p.2)*
- Proves representation theorems for both expansion and revision in terms of AGM postulates *(p.3-5)*

## Methodology
The paper proceeds by:
1. Defining abstract argumentation theory preliminaries (Dung AFs, semantics, equivalence notions) *(p.1-2)*
2. Constructing "Dung logics" — monotonic logics whose models are AFs and whose consequence relation captures strong equivalence *(p.2-3)*
3. Reformulating AGM expansion postulates for AFs and proving a concrete expansion operator satisfies them *(p.3-4)*
4. Reformulating AGM revision postulates for AFs and proving a concrete revision operator satisfies them *(p.4-5)*
5. Discussing the relationship to Cayrol et al.'s revision operators and to enforcement-based approaches *(p.5-6)*

## Key Equations / Statistical Models

### AF Definition
$$
F = (A, R) \text{ where } A \text{ is a set of arguments, } R \subseteq A \times A \text{ is the attack relation}
$$
Where: $A$ = arguments, $R$ = attack relation (binary on $A$)
*(p.1)*

### Strong Equivalence
$$
F_1 \equiv_s F_2 \iff \forall F': \sigma(F_1 \cup F') = \sigma(F_2 \cup F')
$$
Where: $F_1, F_2, F'$ are AFs, $\sigma$ is a semantics, $\cup$ denotes AF union (union of arguments and attacks)
*(p.2)*

### Ordinary Equivalence
$$
F_1 \equiv_\sigma F_2 \iff \sigma(F_1) = \sigma(F_2)
$$
*(p.2)*

### 4-Equivalence (Kernel Equivalence)
$$
F_1 \equiv_4 F_2 \iff F_1^k = F_2^k
$$
Where: $F^k$ is the **kernel** of $F$, obtained by removing all self-attacking arguments and their outgoing attacks. Specifically, $F^k = (A^k, R^k)$ where $A^k = A$ and $R^k = R \setminus \{(a,b) \mid (a,a) \in R\}$ — remove all attacks $(a,b)$ where $a$ attacks itself.
*(p.2)*

### Mod Function (Models of a Formula)
$$
\text{Mod}^I(F) = \{G \in \mathcal{F}^I \mid G^k = F^k\}
$$
Where: $\mathcal{F}^I$ is the set of all AFs over argument set $I$, and $G^k = F^k$ means the kernels match. A formula $F$ is satisfiable iff $\text{Mod}^I(F) \neq \emptyset$ for any $I \supseteq A_F$.
*(p.2)*

### Cn (Consequence Operator)
$$
\text{Cn}(X) = \{F \in \mathcal{F} \mid \text{Mod}^I(F') \subseteq \text{Mod}^I(F) \text{ for all } I \supseteq \bigcup_{G \in X} A_G \cup A_F\}
$$
Where: $X$ is a set of AFs, $\mathcal{F}$ is the set of all AFs. This captures the "consequences" of $X$ in the Dung logic — all AFs whose models are supersets of the models of $X$.
*(p.2)*

### Belief Expansion for AFs
$$
F + G = F \cup_k G
$$
Where: $\cup_k$ denotes the **kernel union** — $F \cup_k G$ has arguments $A_F \cup A_G$ and attacks $R_F^k \cup R_G^k \cup \{(a,b) \mid a \in A_F \cup A_G, (a,a) \in R_F \cup R_G\}$. In other words, take the kernel attacks from both and re-add self-loop consequences.
*(p.3-4)*

### AGM Expansion Postulates for AFs (K1-K6)
- **K1**: $\text{Cn}(F) + G$ is a belief set *(closure)*
- **K2**: $G \in \text{Cn}(F) + G$ *(success)*
- **K3**: $\text{Cn}(F) \subseteq \text{Cn}(F) + G$ *(inclusion — expansion only adds)*
- **K4**: If $G \in \text{Cn}(F)$, then $\text{Cn}(F) + G = \text{Cn}(F)$ *(vacuity)*
- **K5**: If $\text{Cn}(F_1) = \text{Cn}(F_2)$, then $\text{Cn}(F_1) + G = \text{Cn}(F_2) + G$ *(extensionality)*
- **K6**: $\text{Cn}(F) + G$ is the smallest belief set satisfying K1-K5 *(minimality)*
*(p.3)*

### Belief Revision for AFs
$$
F * G
$$
Defined via a **faithful assignment**: a function $\leq_F$ mapping each AF $F$ to a total preorder on $\mathcal{F}^I$ such that:
1. If $G_1, G_2 \in \text{Mod}^I(F)$ then $G_1 =_F G_2$ (models of $F$ are minimal)
2. If $G_1 \in \text{Mod}^I(F)$ and $G_2 \notin \text{Mod}^I(F)$ then $G_1 <_F G_2$
3. If $F_1^k = F_2^k$ then $\leq_{F_1} = \leq_{F_2}$
*(p.5)*

### AGM Revision Postulates for AFs (R1-R8)
- **R1**: $F * G$ is a belief set *(closure)*
- **R2**: $G$ is 4-satisfiable by $F * G$ *(success)*
- **R3**: $F * G \subseteq \text{Cn}(F) + G$ *(inclusion)*
- **R4**: If $\lnot G \notin \text{Cn}(F)$ then $\text{Cn}(F) + G \subseteq F * G$ *(vacuity — if G consistent with F, revision = expansion)*
- **R5**: $F * G$ is 4-satisfiable iff $G$ is 4-satisfiable *(consistency)*
- **R6**: If $G_1^k = G_2^k$ then $F * G_1 = F * G_2$ *(extensionality)*
- **R7**: $F * (G_1 \cup_k G_2) \subseteq \text{Cn}(F * G_1) + G_2$ *(superexpansion)*
- **R8**: If $\lnot G_2 \notin F * G_1$ then $\text{Cn}(F * G_1) + G_2 \subseteq F * (G_1 \cup_k G_2)$ *(subexpansion)*
*(p.5)*

### Revision Operator Definition
$$
F * G = \text{Cn}(\min(G, \leq_F))
$$
Where: $\min(G, \leq_F)$ selects the $\leq_F$-minimal models satisfying $G$.
*(p.5)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Semantics family | σ | — | — | stable, preferred, grounded, complete, admissible, conflict-free, stage, semi-stable, ideal, eager | 2 | All unified under 4-equivalence |
| Universe of arguments | I | — | — | any finite/countable set | 2 | Fixed for model comparison |

## Methods & Implementation Details
- **Dung logics construction**: Models are AFs. Satisfiability is defined via kernel equality: $G \models F$ iff $G^k = F^k$. The consequence operator Cn is monotonic (adding formulas only restricts models). *(p.2-3)*
- **Kernel operation**: Remove from the attack relation all attacks $(a,b)$ where $a$ self-attacks. This is the key operation — it makes ordinary equivalence equal strong equivalence for ALL listed semantics simultaneously. *(p.2)*
- **Expansion is kernel union**: The expansion of a belief set by a new AF is the kernel union $F \cup_k G$. This is the unique smallest belief set containing both $F$ and $G$. *(p.3-4)*
- **Revision requires total preorder on models**: Unlike classical AGM where distance measures (Dalal) work, for AFs "standard approaches based on distance measures do not work." The paper proves revision exists but does not provide a concrete distance/preorder — only the representation theorem. *(p.4-5)*
- **4-satisfiability replaces classical consistency**: An AF $G$ is 4-satisfiable iff there exists an AF $F$ such that $\text{Mod}^I(\{F,G\}) \neq \emptyset$, i.e., $F^k = G^k$ restricted to some domain. Actually: $G$ is 4-satisfiable iff for any $I \supseteq A_G$, $\text{Mod}^I(G) \neq \emptyset$. *(p.2)*
- **Inconsistency in Dung logics**: Two AFs $F$ and $G$ are inconsistent (no common model) iff their kernels disagree: there exist $a, b$ such that $(a,b)$ is a kernel attack in one but not the other. *(p.3)*
- **Standard AGM assumptions hold**: Dung logics satisfy compactness, are supra-classical relative to their own language, and satisfy deduction. *(p.3)*
- **Intersection of models**: For a set of AFs $X$, $\text{Mod}^I(X) = \bigcap_{F \in X} \text{Mod}^I(F)$. This intersection is always non-empty for consistent sets. *(p.2)*

## Figures of Interest
- **Example 1 (p.2)**: Three AFs $F$, $G$, $H$ showing 4-equivalence: $F$ has arguments $\{a,b,c\}$ with attacks forming a cycle plus self-loop on $c$; after kernelization all three have the same kernel.
- **Example 2 (p.3)**: Expansion example: $F$ and $G$ with different arguments, their models, and the expansion $F + G$ which is the kernel union.
- **Example 3 (p.4)**: Shows that naive distance-based approaches fail for AF revision — $F$ and $G$ have models where the "closest" model by distance is not unique or sensible.
- **Example 4 (p.5)**: Demonstrates that $\text{Mod}^I_{*G}$ (models of revision result) may indeed contain AFs with more attacks than expected.

## Results Summary
1. **Theorem 1**: The expansion operator $+$ (kernel union) satisfies all AGM expansion postulates K1-K6 for Dung logics. *(p.3)*
2. **Theorem 2**: An operator $*$ satisfies R1-R6 iff it can be represented via a faithful assignment (total preorder on models). *(p.5)*
3. **Lemma 4**: For any AF $F$ and AF $G$, $\text{Mod}^I_{F+G} = \text{Mod}^I_F \cap \text{Mod}^I_G$. *(p.3)*
4. **Lemma 5**: Belief expansion can be generalized to arbitrary finite intersections of models. *(p.4)*
5. **Lemma 6**: The kernel union is a syntactic companion of intersection of models — $\text{Mod}^I(F \cup_k G) = \text{Mod}^I(F) \cap \text{Mod}^I(G)$. *(p.4)*
6. **Key negative result**: Standard distance-based approaches (Dalal-style) do not work for AF revision because AFs have different argument sets and the space is not well-metrized. *(p.4)*

## Limitations
- The paper does **not** provide a concrete revision operator — only representation theorems showing that satisfying the postulates is equivalent to having a faithful assignment. No specific distance metric or preorder is given. *(p.5)*
- Contraction is not addressed (left to companion paper Baumann & Brewka 2019). *(p.1)*
- The approach works only for **finite** AFs (argument sets can be any set, but specific results assume finite). *(p.2)*
- The paper notes that the requirement of 4-satisfiability is "in many cases trivially fulfilled" — vacuous opinions about self-attacking arguments can be freely added, making revision trivial in some cases. *(p.5)*
- Revision results can include "more models" than expected — the paper acknowledges this may seem counter-intuitive (Example 4). *(p.5)*

## Arguments Against Prior Work
- **Cayrol et al. (2010, 2014) revision operators** are criticized as not fully AGM-compliant: "Their definitions are straightforward from a technical point of view since the intersection of models can be simply obtained by taking the conjunction of the given formulas." However, their approach adds new arguments and attacks but doesn't remove existing ones, which limits expressivity. *(p.5-6)*
- **Coste-Marquis et al. (2005, 2007, 2014)** enforcement-based approaches: a revision operator maps an AF $F$ to a set of AFs, selecting which to add and which are not. Then a two-step procedure is performed. These "do not correspond to former extensions of $F$ if $\sigma$ is selected." *(p.6)*
- **Baumann & Brewka (2010)** own earlier expansion work: that paper focused on enforcing acceptance of specific arguments, not on AGM-style expansion of the framework's logical content. *(p.6)*
- **Standard distance measures** (Dalal): "why standard approaches based on distance measures do not work for AFs and present an appropriate satisfying all postulates for a specific Dung logic." *(p.1)*

## Design Rationale
- **Why Dung logics?** The key insight is that for 10 standard argumentation semantics, ordinary equivalence coincides with strong equivalence. This means a single logic captures all these semantics simultaneously, avoiding the need for semantics-specific revision operators. *(p.2)*
- **Why kernel-based?** The kernel operation (removing attacks from self-attacking arguments) is the canonical representative for equivalence classes under 4-equivalence. Two AFs are 4-equivalent iff their kernels are identical. This provides a clean normal form. *(p.2)*
- **Why not distance-based revision?** Example 3 shows that cardinality-based distance between AFs doesn't give sensible results because AFs with different argument sets are incomparable in useful ways. *(p.4)*
- **Why monotonic consequence?** AGM postulates require a consequence operator satisfying Tarskian properties (inclusion, monotonicity, idempotence). The Cn operator defined via model intersection satisfies all these. *(p.2-3)*

## Testable Properties
- **4-equivalence correctness**: Two AFs $F_1, F_2$ with $F_1^k = F_2^k$ must produce identical extensions under all 10 semantics *(p.2)*
- **Expansion postulate K2 (success)**: After expanding $\text{Cn}(F) + G$, the new information $G$ must be entailed *(p.3)*
- **Expansion postulate K3 (inclusion)**: Expansion must be monotonic — $\text{Cn}(F) \subseteq \text{Cn}(F) + G$ *(p.3)*
- **Kernel union is model intersection**: $\text{Mod}^I(F \cup_k G) = \text{Mod}^I(F) \cap \text{Mod}^I(G)$ *(p.4)*
- **Revision postulate R2 (success)**: After revision $F * G$, the AF $G$ must be 4-satisfiable by the result *(p.5)*
- **Revision postulate R4 (vacuity)**: If $G$ is consistent with $F$, revision reduces to expansion *(p.5)*
- **Faithful assignment conditions**: Models of $F$ are $\leq_F$-minimal; kernel-equivalent AFs share the same preorder *(p.5)*

## Relevance to Project
This paper is **highly relevant** to propstore. The project CLAUDE.md lists Dixon 1993 (ATMS context switching = AGM operations) and Alchourron 1985 (AGM postulates) as aspirational, with "no AGM operations implemented." This paper provides the concrete bridge:
- It defines what AGM expansion and revision **mean** for Dung AFs
- The kernel operation maps directly to propstore's existing AF infrastructure
- The expansion operator (kernel union) is immediately implementable
- The revision representation theorem tells us what a valid revision operator must look like (faithful assignment / total preorder)
- The connection to strong equivalence means any revision operator built this way works for ALL standard semantics simultaneously

## Open Questions
- [ ] How does this connect to propstore's ATMS layer? Dixon 1993 says ATMS context switching = AGM operations. This paper says AGM expansion for AFs = kernel union. Can ATMS label sets inform the faithful assignment for revision?
- [ ] The paper leaves the concrete revision preorder unspecified — what distance/ordering over AFs should propstore use?
- [ ] Baumann & Brewka 2019 covers contraction — should that be retrieved too?
- [ ] How does this interact with ASPIC+ structured argumentation? The paper works at the abstract (Dung) level only.

## Related Work Worth Reading
- **Baumann & Brewka 2019**: "AGM Meets Abstract Argumentation: Contraction for Dung Frameworks" (JELIA 2019) — the contraction companion paper
- **Cayrol, de Saint-Cyr, Lagasquie-Schiex 2010**: "Change in abstract argumentation frameworks: Adding an argument" — alternative approach to AF dynamics
- **Coste-Marquis et al. 2014**: Revision via enforcement, different approach
- **Oikarinen & Woltran 2011**: Characterization of strong equivalence for AFs
- **Baumann & Brewka 2010**: Earlier expansion work (already in propstore as Baumann_2010)
- **Diller et al. 2015**: Metalevel approaches to AF revision

## Collection Cross-References

### Already in Collection
- [[Alchourron_1985_TheoryChange]] — the foundational AGM paper whose postulates this paper reformulates for Dung AFs
- [[Dung_1995_AcceptabilityArguments]] — defines the AF = (Args, Defeats) framework that this paper builds AGM operations upon
- [[Baumann_2010_ExpandingArgumentationFrameworksEnforcing]] — the authors' earlier expansion work (enforcement-based, not AGM-based); this paper supersedes the theoretical framing
- [[Gärdenfors_1988_RevisionsKnowledgeSystemsEpistemic]] — epistemic entrenchment for belief revision; this paper's faithful assignment (total preorder on models) is the AF analogue
- [[Coste-Marquis_2005_SymmetricArgumentationFrameworks]] — same authors later do enforcement-based revision (2014); the 2005 symmetry work is a precursor

### New Leads (Not Yet in Collection)
- Oikarinen & Woltran (2011) — "Characterizing Strong Equivalence for Argumentation Frameworks" — foundational for the kernel operation underlying Dung logics
- Baumann & Brewka (2019) — "AGM Meets Abstract Argumentation: Contraction for Dung Frameworks" — companion paper completing the AGM trilogy
- Diller et al. (2015) — extension-based approach to AF belief revision (concurrent IJCAI paper, alternative to model-based approach)

### Supersedes or Recontextualizes
- [[Baumann_2010_ExpandingArgumentationFrameworksEnforcing]] — this 2015 paper provides the full AGM-theoretic foundation for AF expansion, whereas the 2010 paper defined expansion operationally (enforcement). The 2015 kernel union operator is the AGM-compliant generalization.

### Cited By (in Collection)
- (none found)

### Conceptual Links (not citation-based)
**AGM and ATMS:**
- [[Dixon_1993_ATMSandAGM]] — Strong. Dixon proves ATMS context switching is behaviourally equivalent to AGM operations. This paper defines what AGM expansion/revision mean for AFs. Together they suggest ATMS label sets could inform the faithful assignment for AF revision.
- [[Gärdenfors_1988_RevisionsKnowledgeSystemsEpistemic]] — Strong. Epistemic entrenchment provides a concrete ordering mechanism; this paper's faithful assignment is the AF analogue of entrenchment-based revision.

**AF dynamics:**
- [[Cayrol_2014_ChangeAbstractArgumentationFrameworks]] — Strong. Cayrol et al.'s approach to AF change (adding arguments) is directly critiqued in Section 5.4; both address the same problem from different angles.
- [[Boella_2009_DynamicsArgumentationSingleExtensions]] — Strong. Boella et al. study AF dynamics for maintaining single extensions; this paper provides the AGM-theoretic framework for the same problem.
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — Moderate. Survey of constraints and changes in abstract argumentation; contextualizes this paper within the broader AF dynamics literature.
- [[Coste-Marquis_2007_MergingDung'sArgumentationSystems]] — Strong. Merging AFs is closely related to revision; the merging operators could potentially be connected to the faithful assignment mechanism.

**Belief revision foundations:**
- [[Rotstein_2008_ArgumentTheoryChangeRevision]] — Strong. Addresses argument theory change and revision from a different angle (structured arguments rather than abstract AFs).
