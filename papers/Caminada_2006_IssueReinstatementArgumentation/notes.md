---
title: "On the Issue of Reinstatement in Argumentation"
authors: "Martin Caminada"
year: 2006
venue: "JELIA 2006, Lecture Notes in Artificial Intelligence 4160, pp. 111-123"
doi_url: "https://doi.org/10.1007/11853886_11"
---

# On the Issue of Reinstatement in Argumentation

## One-Sentence Summary
Provides a labelling-based characterization of Dung's argumentation semantics through reinstatement postulates, establishing exact correspondences between labelling restrictions (on in/out/undec) and standard semantics (complete, preferred, grounded, stable), and introduces semi-stable semantics as a new alternative.

## Problem Addressed
Dung's theory provides several semantics (grounded, preferred, stable, complete) for argumentation frameworks, but the question of *why* these particular semantics make sense from the perspective of reinstatement postulates has received little attention. The paper asks: what minimal requirements must any principle for handling reinstatement satisfy, and how do these relate to Dung's standard semantics? *(p.1)*

## Key Contributions
- Introduces a formal definition of **reinstatement labelling** using three labels (in, out, undec) with precise conditions linking argument status to attacker status *(p.3)*
- Defines **Ext2Lab** and **Lab2Ext** conversion functions establishing a bijection between complete extensions and reinstatement labellings *(p.3-4)*
- Shows that each of Dung's semantics corresponds to a specific restriction on reinstatement labellings (Table 1) *(p.7)*
- Introduces **semi-stable semantics** as the semantics corresponding to labellings with minimal undec, offering a new middle ground between preferred and stable semantics *(p.6-7)*
- Establishes a partial ordering of semantics: stable > semi-stable > preferred > complete, and grounded > complete *(p.7)*
- Argues for preferred semantics over complete semantics on pragmatic grounds (floating conclusions) *(p.8-9)*
- Discusses the principle of excluded middle in argumentation and its relationship to condensed labellings *(p.10-11)*

## Methodology
The paper takes a postulate-based approach: define minimal conditions for reinstatement, formalize them as labelling constraints, then systematically vary those constraints to recover all of Dung's standard semantics plus a new one (semi-stable). *(p.1-2)*

## Key Definitions

### Definition 1: Argumentation Framework *(p.2)*
A pair $(Ar, def)$ where $Ar$ is a set of arguments and $def \subseteq Ar \times Ar$.

### Definition 2: Defense / Conflict-free *(p.2)*
- $A^+ = \{B \mid A \text{ def } B\}$ (arguments attacked by A)
- $A^- = \{B \mid B \text{ def } A\}$ (arguments attacking A)
- $\mathcal{A}rgs^+ = \{B \mid A \text{ def } B \text{ for some } A \in \mathcal{A}rgs\}$
- $\mathcal{A}rgs^- = \{B \mid B \text{ def } A \text{ for some } A \in \mathcal{A}rgs\}$
- $\mathcal{A}rgs$ defends $A$ iff $A^- \subseteq \mathcal{A}rgs^+$
- $\mathcal{A}rgs$ is conflict-free iff $\mathcal{A}rgs \cap \mathcal{A}rgs^+ = \emptyset$

### Definition 3: Acceptability Semantics *(p.2)*
Let $\mathcal{A}rgs$ be conflict-free with $F(\mathcal{A}rgs) = \{A \mid A \text{ is defended by } \mathcal{A}rgs\}$:
- **Admissible** iff $\mathcal{A}rgs \subseteq F(\mathcal{A}rgs)$
- **Complete extension** iff $\mathcal{A}rgs = F(\mathcal{A}rgs)$
- **Grounded extension** iff minimal (w.r.t. set-inclusion) complete extension
- **Preferred extension** iff maximal (w.r.t. set-inclusion) complete extension
- **Stable extension** iff preferred extension that defeats every argument in $Ar \setminus \mathcal{A}rgs$

### Definition 4: AF-labelling *(p.2)*
A total function $\mathcal{L}: Ar \rightarrow \{\texttt{in}, \texttt{out}, \texttt{undec}\}$, partitioning arguments into three sets:
- $\texttt{in}(\mathcal{L}) = \{A \in Ar \mid \mathcal{L}(A) = \texttt{in}\}$
- $\texttt{out}(\mathcal{L}) = \{A \in Ar \mid \mathcal{L}(A) = \texttt{out}\}$
- $\texttt{undec}(\mathcal{L}) = \{A \in Ar \mid \mathcal{L}(A) = \texttt{undec}\}$

### Definition 5: Reinstatement Labelling *(p.3)*
An AF-labelling $\mathcal{L}$ is a reinstatement labelling iff:
- $\forall A \in Ar: (\mathcal{L}(A) = \texttt{out} \equiv \exists B \in Ar: (B \text{ def } A \wedge \mathcal{L}(B) = \texttt{in}))$
- $\forall A \in Ar: (\mathcal{L}(A) = \texttt{in} \equiv \forall B \in Ar: (B \text{ def } A \supset \mathcal{L}(B) = \texttt{out}))$

This is the central definition: an argument is **in** iff all its defeaters are **out**; an argument is **out** iff it has at least one defeater that is **in**.

### Definition 6: Ext2Lab and Lab2Ext *(p.3-4)*
- $\texttt{Ext2Lab}_{(Ar,def)}(\mathcal{A}rgs)$: converts extension to labelling where $\texttt{in} = \mathcal{A}rgs$, $\texttt{out} = \mathcal{A}rgs^+$, $\texttt{undec} = Ar \setminus (\mathcal{A}rgs \cup \mathcal{A}rgs^+)$
- $\texttt{Lab2Ext}_{(Ar,def)}(\mathcal{L})$: converts labelling to extension, returning $\texttt{in}(\mathcal{L})$

### Definition 8: Admissible Stage Extension (Verheij) *(p.7)*
A pair $(\mathcal{A}rgs, \mathcal{A}rgs^+)$ where $\mathcal{A}rgs$ is an admissible set and $\mathcal{A}rgs \cup \mathcal{A}rgs^+$ is maximal.

### Definition 9: Condensed Labelling *(p.10-11)*
A labelling $\mathcal{C}$ is a condensed labelling iff:
- $\forall A \in Ar: (\mathcal{C}(A) = \texttt{out} \equiv \exists B \in Ar: (B \text{ def } A \wedge \mathcal{C}(B) = \texttt{in}))$
- $\forall A \in Ar: (\mathcal{C}(A) = \texttt{in} \supset \forall B \in Ar: (B \text{ def } A \supset \mathcal{C}(B) = \texttt{out}))$

The difference from reinstatement labellings: the second condition uses implication ($\supset$) instead of equivalence ($\equiv$), so an argument with all defeated attackers need not be labelled in.

## Key Theorems

### Theorem 1: Reinstatement Labellings = Complete Extensions *(p.4)*
$\mathcal{L}$ is a reinstatement labelling of $(Ar, def)$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is a complete extension. Conversely, if $\mathcal{A}rgs$ is a complete extension then $\texttt{Ext2Lab}(\mathcal{A}rgs)$ is a reinstatement labelling.

### Theorem 3: Stable Semantics *(p.4)*
$\mathcal{L}$ is a reinstatement labelling with empty undec iff $\texttt{Lab2Ext}(\mathcal{L})$ is a stable extension.

### Theorem 4: Preferred Semantics (maximal in) *(p.5)*
$\mathcal{L}$ is a reinstatement labelling with maximal $\texttt{in}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is a preferred extension.

### Theorem 5: Preferred Semantics (maximal out) *(p.5)*
$\mathcal{L}$ is a reinstatement labelling with maximal $\texttt{out}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is a preferred extension.

### Theorem 6: Grounded Semantics (maximal undec) *(p.5)*
$\mathcal{L}$ is a reinstatement labelling with maximal $\texttt{undec}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is the grounded extension.

### Theorem 7: Grounded Semantics (minimal in) *(p.5)*
$\mathcal{L}$ is a reinstatement labelling with minimal $\texttt{in}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is the grounded extension.

### Theorem 8: Grounded Semantics (minimal out) *(p.5)*
$\mathcal{L}$ is a reinstatement labelling with minimal $\texttt{out}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is the grounded extension.

### Theorem 9: Preferred Extension Subsumption *(p.6)*
If $\mathcal{A}rgs$ is a preferred extension, there is not necessarily a reinstatement labelling where $\texttt{undec}$ is minimal. A preferred extension does not necessarily imply semi-stable.

### Theorem 10: Semi-stable = Minimal Undec *(p.6)*
$\mathcal{L}$ is a reinstatement labelling with minimal $\texttt{undec}$ iff $\texttt{Lab2Ext}(\mathcal{L})$ is a semi-stable extension.

### Theorem 11: Semi-stable and Stable Coincidence *(p.7)*
If there exists a stable extension, then the semi-stable extensions coincide with the stable extensions.

### Theorem 12: Semi-stable = Admissible Stage Extension *(p.7)*
$(\mathcal{A}rgs, \mathcal{A}rgs^+)$ is an admissible stage extension iff $\mathcal{A}rgs$ is a semi-stable extension.

### Theorem 13: Complete Semantics and Excluded Middle *(p.10)*
The set of complete extensions $CE_1, \ldots, CE_n$ is the set of complete extensions iff for every complete extension, for each argument $A$, $A \in CE_i$ or $A$ has an attacker in $CE_i$.

### Theorem 14: Conditions for Excluded Middle *(p.10)*
Complete semantics coincides with condensed complete semantics when the principle of excluded middle holds (no undec arguments). Credulous and sceptical complete semantics coincide with credulous and sceptical preferred semantics in the excluded-middle case.

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Labels | {in, out, undec} | - | - | 3 values | 2 | Tri-valued labelling |
| Labelling restriction | varies | - | none | see Table 1 | 7 | Determines semantics |

## Table 1: Reinstatement Labellings vs Dung-style Semantics *(p.7)*

| Restriction on Reinstatement Labelling | Dung-style Semantics | Linked by Theorem |
|----------------------------------------|---------------------|-------------------|
| no restrictions | complete semantics | 1 |
| empty undec | stable semantics | 3 |
| maximal in | preferred semantics | 4 |
| maximal out | preferred semantics | 5 |
| maximal undec | grounded semantics | 6 |
| minimal in | grounded semantics | 7 |
| minimal out | grounded semantics | 8 |
| minimal undec | semi-stable semantics | 10 |

## Implementation Details
- **Ext2Lab algorithm**: Given a complete extension $\mathcal{A}rgs$, compute $\texttt{in} = \mathcal{A}rgs$, $\texttt{out} = \mathcal{A}rgs^+$ (all arguments attacked by extension members), $\texttt{undec} = Ar \setminus (\mathcal{A}rgs \cup \mathcal{A}rgs^+)$ *(p.3)*
- **Lab2Ext algorithm**: Given a reinstatement labelling $\mathcal{L}$, return $\texttt{in}(\mathcal{L})$ *(p.3)*
- **Semi-stable computation**: Enumerate all preferred extensions, convert to labellings, select those with minimal $\texttt{undec}(\mathcal{L})$ *(p.6-7)*
- **Condensed labelling computation**: Weaker than reinstatement -- allows in-labelled arguments not to have all attackers defeated, useful for modelling the excluded middle principle *(p.10-11)*

## Figures of Interest
- **Fig 1 (p.3):** Three argumentation frameworks illustrating reinstatement labellings: linear chain (A defeats B defeats C), diamond with mutual defeat, isolated self-defeating node F
- **Fig 2 (p.6):** Preferred extension does not necessarily imply minimal undec: AF with arguments A, B, C, D where {A} is preferred but labelling has C, D as undec, while a non-preferred complete extension {} has everything undec
- **Fig 3 (p.7):** Hierarchy diagram: stable > semi-stable > preferred and grounded, both > complete
- **Fig 4 (p.8):** Floating argument example: A-B mutual defeat, both attack C, C attacks D
- **Fig 5 (p.8):** Three reinstatement labellings for Fig 4: L1 (A:in, B:out, C:out, D:in), L2 (A:undec, B:undec, C:undec, D:undec), L3 (A:out, B:in, C:out, D:in)
- **Fig 6 (p.8):** Preferred semantics rules out L2 (where all are undec), keeping only L1 and L3

## Results Summary
The paper establishes a complete taxonomy of Dung's semantics through labelling restrictions, proving that each standard semantics corresponds to exactly one type of restriction on reinstatement labellings. Semi-stable semantics emerges naturally as the "minimal undec" case, filling a gap between preferred (maximal in) and stable (empty undec). The hierarchy stable > semi-stable > preferred > complete is proven, with grounded as a separate branch below complete. *(p.7)*

## Limitations
- Proofs are omitted from the paper (available in separate technical report [10]) *(p.1)*
- The discussion of which semantics is "most appropriate" remains partially open *(p.10-11)*
- The paper focuses on abstract argumentation only, not structured argumentation *(p.1)*
- Semi-stable semantics computation requires enumerating preferred extensions first *(implicit)*

## Arguments Against Prior Work
- Complete semantics alone is insufficient because it includes "unreasonable" labellings like the all-undec labelling for floating arguments *(p.8)*
- Preferred semantics, while pragmatically useful (resolves floating conclusions), rules out valid reinstatement labellings without strong justification -- the maximality of in-labelled arguments is not a compelling criterion *(p.8-9)*
- The approach of using extension-based definitions alone obscures the underlying labelling structure and the relationships between semantics *(p.1)*

## Design Rationale
- Three-valued labelling (in/out/undec) is chosen over two-valued because undecided status is needed for arguments whose attackers are themselves undecided *(p.2-3)*
- Reinstatement labelling uses biconditional (iff) rather than one-directional implication to ensure both directions: being in requires all attackers out, AND having all attackers out requires being in *(p.3)*
- Semi-stable semantics is introduced because it is the closest to stable semantics without the existence problem: semi-stable extensions always exist, stable extensions may not *(p.7)*
- Condensed labellings (Definition 9) use weaker conditions to capture the excluded middle principle, allowing some arguments to remain out even when their attackers are all defeated *(p.10-11)*

## Testable Properties
- For any AF, Ext2Lab(Lab2Ext(L)) = L for any reinstatement labelling L *(p.4)*
- For any AF, Lab2Ext(Ext2Lab(Args)) = Args for any complete extension Args *(p.4)*
- Every stable extension is a semi-stable extension *(p.7)*
- Every semi-stable extension is a preferred extension *(p.7)*
- Every preferred extension is a complete extension *(p.2)*
- Every grounded extension is a complete extension *(p.2)*
- If a stable extension exists, semi-stable extensions coincide with stable extensions (Theorem 11) *(p.7)*
- The grounded extension is the unique reinstatement labelling with maximal undec *(p.5)*
- Reinstatement labellings are in bijection with complete extensions (Theorem 1) *(p.4)*

## Relevance to Project
This paper is foundational for propstore's argumentation layer. The labelling-based view of semantics provides:
1. A concrete data structure (three-valued labellings) for representing argument status
2. A principled way to convert between extension-based and labelling-based representations
3. The theoretical basis for semi-stable semantics, which is useful when stable extensions don't exist
4. A taxonomy connecting labelling restrictions to semantics, which can guide the choice of resolution strategy in the render layer
5. The reinstatement postulate itself serves as a correctness criterion for any argumentation semantics implementation

## Open Questions
- [ ] How does semi-stable semantics perform computationally compared to preferred?
- [ ] Can the labelling approach be extended to structured argumentation (ASPIC+)?
- [ ] How do condensed labellings relate to the graded/weighted argumentation in propstore?
- [ ] What is the relationship between Caminada's labellings and the ATMS labels in propstore?

## Related Work Worth Reading
- [1] Dung 1995: The acceptability of arguments (foundational AF paper)
- [9] Caminada 2006: Coherence and flexibility in dialogue games (postulates)
- [10] Caminada 2006: Technical report with full proofs for this paper
- [12] Verheij 2003: Admissible stage extensions (predecessor to semi-stable concept)
- [15] Prakken: Relating protocols and arguments (floating conclusions discussion)
- [2] Vreeswijk & Prakken 2000: Credulous vs sceptical reasoning
- [13] Jakobovits & Vermeir 1999: Robust semantics

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [1]; the foundational AF paper defining the semantics that this paper re-characterizes via labellings
- [[Pollock_1987_DefeasibleReasoning]] — cited as [7]; Pollock's defeasible reasoning with rebutting/undercutting defeat relates to the reinstatement principle formalized here
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — cites this paper as [7/9]; evaluates semi-stable semantics (introduced here) against formal principles, finding it satisfies skepticism adequacy but not resolution adequacy
- [[Verheij_2002_ExistenceMultiplicityExtensionsDialectical]] — related via Verheij 1996/2003 citations [12/21]; Verheij's admissible stage extensions are proven equivalent to semi-stable extensions (Theorem 12)
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - cited as [4]; defines a different response to indirect attack, where odd-length attack paths block co-acceptance inside prudent extensions.

### New Leads (Not Yet in Collection)
- Jakobovits, Vermeir (1999) — "Robust semantics for argumentation frameworks" — alternative approach to handling the same problematic cases (odd cycles, floating arguments)

### Now in Collection (previously listed as leads)
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - Defines prudent semantics by forbidding indirect conflicts inside accepted sets. It complements Caminada's semi-stable semantics: both handle problematic standard-Dung behavior, but prudent semantics filters co-acceptance by odd-path reachability while semi-stable minimizes undecided arguments through labelling structure.

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — cites this for semi-stable semantics definition and reinstatement analysis
- [[Caminada_2007_EvaluationArgumentationFormalisms]] — cites this in its reference list (same first author's follow-up work on rationality postulates)
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — cites this in its reference list
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — lists this as a New Lead for labelling-based semantics relevant to Pollock's defeat status assignments *(p.7)*
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — cites this in its reference list; Hunter's epistemic labellings generalize the in/out/undec labellings introduced here to probability distributions
- [[Charwat_2015_MethodsSolvingReasoningProblems]] — cites this in its reference list as part of the semi-stable semantics definition
- [[Järvisalo_2025_ICCMA20235thInternational]] — ICCMA competition includes semi-stable semantics (introduced here) as one of the evaluated semantics tracks

### Conceptual Links (not citation-based)
**Labelling-based semantics:**
- [[Caminada_2007_EvaluationArgumentationFormalisms]] — **Strong.** Same first author's follow-up work applying labelling-based semantics to evaluate ASPIC-style argumentation formalisms against rationality postulates. The reinstatement labellings defined here provide the formal foundation for the evaluation criteria in that paper.
- [[Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation]] — **Strong.** Baroni's SCC-recursive schema decomposes AF computation by graph structure; Caminada's labelling approach provides an alternative characterization of the same semantics. Semi-stable semantics (introduced here) satisfies directionality (proven in Baroni 2007), connecting the two frameworks.

**Extension existence and semantics comparison:**
- [[Verheij_2002_ExistenceMultiplicityExtensionsDialectical]] — **Strong.** Verheij characterizes when stable extensions exist; semi-stable semantics (introduced here) provides a fallback when they don't, with Theorem 11 proving the two coincide when stable extensions exist.
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - **Moderate.** Both papers introduce conservative variants of Dung semantics for unintuitive cases. Caminada does so through labellings and semi-stable extensions; Coste-Marquis et al. do so by rejecting extension members connected by odd-length indirect attack paths.

**Structured argumentation:**
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — **Moderate.** ASPIC+ generates Dung-style AFs from structured arguments; the labelling-based semantics defined here can be applied to those generated AFs, providing an alternative to extension-based computation.
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — **Moderate.** Odekerken extends ASPIC+ with incomplete information using four justification statuses (unsatisfiable, defended, out, blocked) that parallel the in/out/undec labelling scheme introduced here.
- [[Brewka_2010_AbstractDialecticalFrameworks]] — **Moderate.** Brewka & Woltran cite Caminada's semi-stable semantics as one of the alternative semantics for Dung AFs. ADFs generalize the in/out/undec three-valued interpretation that Caminada's labellings formalize, using it as the basis for the consensus operator that defines ADF grounded and complete semantics.
- [Developing the Abstract Dialectical Framework](../Polberg_2017_DevelopingAbstractDialecticalFramework/notes.md) — **Strong.** Polberg's EAFC labelling chapter §3.4 extends Caminada's three-valued reinstatement labelling (in/out/und) directly to extended argumentation frameworks with collective attacks. Polberg's "Eq family" (standard / preferred / grounded / stable / complete / semi-stable / stage / ideal / eager EAFC labellings) lifts the Caminada labelling apparatus into the EAFC setting and proves correspondence with extension-based semantics on argument labels. Polberg's §3.6 then evaluates 16 EAFC semantics × 24 Caminada-style postulates — a direct application of this paper's principle-based methodology at thesis scale.
