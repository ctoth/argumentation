---
title: "On bipolarity in argumentation frameworks"
authors:
  - Leila Amgoud
  - Claudette Cayrol
  - Marie-Christine Lagasquie-Schiex
  - Pierre Livet
year: 2008
venue: "International Journal of Intelligent Systems, 23(10):1062-1093"
doi_url: "https://doi.org/10.1002/int.20307"
---

## One-Sentence Summary

A comprehensive survey showing that bipolarity (the coexistence of positive and negative entities) pervades all five steps of the argumentation process, culminating in a formal abstract bipolar argumentation framework extending Dung's AF with a support relation.

## Problem Addressed

Standard argumentation frameworks (Dung 1995) model only one kind of interaction between arguments: attack/defeat. In practice, arguments also *support* each other, creating a bipolar structure. This paper systematically studies where and how bipolarity appears across the entire argumentation pipeline, using the Dubois-Prade nomenclature of three types of bipolarity. *(p.3)*

## Key Contributions

1. **Taxonomy of bipolarity in argumentation**: Identifies bipolarity at every level of the argumentation process (argument construction, interaction, valuation, selection, conclusion), classifying each by Dubois-Prade type *(p.3-4)*
2. **Abstract bipolar argumentation framework**: Formal definition of BAF = (A, R_def, R_sup) extending Dung's AF with a support relation *(p.10-11)*
3. **Gradual valuation for BAFs**: Local and global valuation functions that combine positive (support) and negative (defeat) information into a single value per argument *(p.15-17)*
4. **Acceptability semantics for BAFs**: Definitions of conflict-free, admissible, stable, and preferred extensions that account for the support relation, including the concept of "closure for R_sup" *(p.22-23)*
5. **Supported defeat**: A new notion of defeat that arises through support paths, enabling indirect attacks *(p.22)*

## Methodology

The paper uses a survey + formal framework approach:
- Reviews how bipolarity appears in existing argumentation literature across all process steps *(p.4)*
- Uses the Dubois-Prade taxonomy of bipolarity: Type 1 (uni-variate: single scale [-1,1]), Type 2 (bi-variate: two independent scales), Type 3 (heterogeneous: both features from different sources with consistency requirement) *(p.3)*
- Introduces formal definitions building on Dung's framework *(p.5)*
- Provides worked examples at each level *(p.6-8, 12-14)*

## Key Equations

**Local gradual valuation** (Definition 9, p.15-16):

$$v(A) = g(h_{def}(v(B_1), \ldots, v(B_n)), h_{sup}(v(C_1), \ldots, v(C_m)))$$

where $B_i$ are direct defeaters, $C_j$ are direct supporters, $h$ is an aggregation function, $g$ combines defeat and support values.

Instance 1: $\mathcal{H}_{def} = \mathcal{H}_{sup} = V = [-1,1]$, $h_{def} = h_{sup} = \max$, $g(x,y) = \frac{x-y}{2}$ *(p.16)*

Instance 2: $V = [-1,1]$, $\mathcal{H}_{def} = \mathcal{H}_{sup} = [0,\infty[$, $h(x_1,\ldots,x_n) = \sum \frac{x_i+1}{2}$, $g(x,y) = \frac{1}{1+y} - \frac{1}{1+x}$ *(p.16)*

**Supported defeat** (Definition 23, p.22):

A supported defeat is a path $A_1, \ldots, A_{n-1}, A_n$ ($n \geq 2$) such that $A_1, \ldots, A_{n-1}$ is in $R_{sup}$ and $A_{n-1}, A_n$ is in $R_{def}$. A homogeneous defeat path of length 1 is also a supported defeat.

**Conflict-free in bipolar AF** (Definition 25, p.23):

$S$ is conflict-free iff $\nexists A, B \in S$ such that $\{A\}$ defeats $B$ (where defeat includes supported defeat).

**Admissible in bipolar AF** (Definition 28, p.23):

$S$ is admissible iff $S$ is conflict-free, closed for $R_{sup}$, and defends all its elements.

## Parameters

| Parameter | Description | Source |
|-----------|-------------|--------|
| $\alpha$ | Minimal value for defeat/support (no defeat/support = $\alpha$) | p.16 |
| $\beta$ | Maximal value for defeat/support (infinity of defeaters/supporters = $\beta$) | p.16 |
| $V$ | Valuation scale (interval of reals) | p.15 |
| $h_{def}, h_{sup}$ | Aggregation functions for defeat/support branch values | p.15 |
| $g$ | Combination function merging defeat and support scores | p.15 |

## Implementation Details

- The BAF is a triple $(A, R_{def}, R_{sup})$ where $R_{def}$ and $R_{sup}$ are binary relations on arguments *(p.10)*
- Support relation is independent of the defeat relation; both are built separately *(p.14)*
- The notion of "closure for $R_{sup}$" is critical for admissibility: if an argument $A$ is in an admissible set and $B$ supports $A$, then $B$ must also be in the set *(p.23)*
- Supported defeat creates new attack paths: a support chain ending in a defeat counts as a defeat *(p.22)*
- For desire-handling systems, a desire $d$ is unachievable if every complete plan is conflict-free but not supported *(p.22)*
- Three classes of arguments in selection: acceptable, rejected, in abeyance *(p.19, 24)*

## Figures of Interest

- **Figure 1** (p.4): Five-step argumentation process diagram (knowledge base -> arguments -> interactions -> weights -> acceptable/rejected/abeyance -> conclusion)
- **Figure p.11**: Bipolar graph with direct/indirect defenders and supporters
- **Example 6 graph** (p.13): Reporter discussion showing defeat + support interactions
- **Example 7 graph** (p.13): Medical prosthesis discussion with bipolar structure
- **Table** (p.26): Summary of bipolarity types across all argumentation process steps

## Results Summary

The paper demonstrates that bipolarity:
- At the **argument level** (Section 3): is Type 2 (bi-variate) with exclusivity *(p.8)*
- At the **interaction level** (Section 4): is at least Type 3 (heterogeneous), sometimes Type 2 when both relations computed from same data *(p.14)*
- At the **valuation level** (Section 5): local = Type 2, global = Type 3 *(p.18-19)*
- At the **selection level** (Section 6): is Type 2 with exclusivity *(p.24)*

The summary table *(p.26)* shows exclusivity always holds, duality sometimes holds, exhaustivity generally does not hold, and the two kinds of information are not always computed from the same data or with the same process.

## Limitations

- The support relation defined here ("explanation support" or "conclusion support") is only one possible notion; other notions like deductive support or necessary support are not covered *(p.12)*
- The framework assumes the bipolar graph is acyclic for the valuation step *(p.15)*
- The paper is primarily a survey and framework definition; no computational complexity analysis is provided
- No algorithmic implementations are discussed for computing extensions in BAFs
- The connection between the gradual valuation approach and the extension-based approach is not fully developed *(p.25)*

## Arguments Against Prior Work

- Standard Dung frameworks only consider defeat, missing the support dimension that exists in real argumentation *(p.3)*
- Previous work on bipolar argumentation (Cayrol & Lagasquie-Schiex 2005) focused on specific semantics; this paper provides the comprehensive survey *(p.4)*
- Verheij's approach [Ver02] defines conflict differently (two arguments in conflict about a third); this paper notes it as an alternative *(p.23, footnote 22)*

## Design Rationale

- Bipolarity is not optional decoration but a fundamental feature of argumentation that appears at every level *(p.25)*
- The Dubois-Prade taxonomy provides a principled classification rather than ad hoc categories *(p.3)*
- Exclusivity constraint (cannot simultaneously support and defeat the same argument) is essential for rational reasoning *(p.14, footnote 8)*
- Closure for support in admissibility ensures that accepted arguments have their support base also accepted *(p.23)*

## Testable Properties

1. **Exclusivity**: In a BAF, if $A R_{sup} B$ then $\neg(A R_{def} B)$ and vice versa *(p.14)*
2. **Supported defeat transitivity**: If A supports B and B defeats C, then A "supported-defeats" C *(p.22)*
3. **Admissible sets must be closed for R_sup**: If $A \in S$ (admissible) and $B R_{sup} A$, check $B \in S$ *(p.23)*
4. **Local valuation monotonicity**: Adding a defeater decreases value; adding a supporter increases value *(p.15-16)*
5. **Conflict-free with supported defeat**: A set containing both an argument and its supported-defeater is not conflict-free *(p.23)*

## Relevance to Project

**High relevance.** This paper directly extends the bipolar argumentation support already partially implemented in propstore (per Cayrol 2005). Key implications:

- **Support relation formalization**: The BAF = (A, R_def, R_sup) triple maps directly to the existing AF construction in propstore, which already separates attacks and supports *(architecture layer 4)*
- **Supported defeat**: The notion that support chains create new defeat paths must be implemented in extension computation — a support path ending in a defeat counts as a defeat for conflict-free checking
- **Closure for R_sup in admissibility**: When computing admissible/preferred extensions in a BAF, the support closure requirement adds a constraint beyond standard Dung semantics
- **Gradual valuation**: The local/global valuation framework provides a principled way to compute argument strength in bipolar settings, complementing the existing Z3-based approach
- **Three types of bipolarity**: The Dubois-Prade taxonomy could inform how propstore classifies different kinds of bipolar relationships between claims

## Open Questions

1. How should the gradual valuation approach interact with the extension-based approach already implemented?
2. Should propstore implement supported defeat as a derived relation, or compute it on-the-fly during extension computation?
3. The paper mentions other notions of support (deductive, necessary) — which are most relevant for propstore's use case?
4. How does closure for R_sup interact with the ASPIC+ preference ordering already in the system?

## New Leads

- **[CLS04]** Cayrol and Lagasquie-Schiex (2004) — "Bipolar abstract argumentation systems" — the foundational BAF paper with detailed semantics
- **[MCLS05]** Mailly, Cayrol, Lagasquie-Schiex (2005) — Further semantics for bipolar AF (referenced for acceptability semantics)
- **[DP06]** Dubois and Prade (2006) — "On the qualitative comparison of sets of positive and negative affects" — the bipolarity taxonomy used throughout
- **[Amg99]** Amgoud (1999) — "A formal framework for handling conflicting desires" — desire-based argumentation with bipolarity
- **[Ver02]** Verheij (2002) — "On the existence and multiplicity of extension in dialectical argumentation" — alternative conflict notion for bipolar AFs — **Now in Collection** as `Verheij_2002_ExistenceMultiplicityExtensionsDialectical`

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [Dun95]; the foundational AF paper that BAFs extend. All BAF definitions generalize Dung's originals by adding a support relation alongside defeat.
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — cited via [CLS04/CLS05/CLS06]; Cayrol and Lagasquie-Schiex's earlier BAF work that this survey comprehensively reviews and extends. The three admissibility levels (d-admissible, s-admissible, c-admissible) from Cayrol 2005 are discussed and contextualized within the broader bipolarity taxonomy.
- [[Verheij_2002_ExistenceMultiplicityExtensionsDialectical]] — cited as [Ver02]; proposes an alternative conflict notion for bipolar settings where two arguments conflict about a third, noted as an alternative to supported defeat.
- [[Karacapilidis_2001_ComputerSupportedArgumentationCollaborative]] — cited as [KP02]; HERMES system referenced as an example of bipolarity in decision-making argumentation, where positions can both support and attack alternatives.
- [[Pollock_1987_DefeasibleReasoning]] — related via [Pol01] (Pollock 2001); Pollock's defeasible reasoning with variable degrees of justification connects to the gradual valuation approach.
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] / [[Modgil_2018_GeneralAccountArgumentationPreferences]] — related via Prakken & Sartor [PS97]; ASPIC+ lineage papers in the collection.

### New Leads (Not Yet in Collection)
- **[CLS04]** Cayrol and Lagasquie-Schiex (2004) — "Bipolar abstract argumentation systems" — foundational BAF paper with detailed semantics
- **[MCLS05]** Mailly, Cayrol, Lagasquie-Schiex (2005) — Further semantics for bipolar AF
- **[DP06]** Dubois and Prade (2006) — "On the qualitative comparison of sets of positive and negative affects" — bipolarity taxonomy (Type 1/2/3)
- **[BH93]** Besnard and Hunter (2001) — "A logic-based theory of deductive arguments"

### Cited By (in Collection)
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — lists Amgoud, Cayrol, Lagasquie-Schiex (2004) as related work (prior companion paper by same authors)
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — references Amgoud in multiple contexts: abstract logic approach (Section 5.2), rebuttal of Amgoud & Vesic critique (Section 6.2)

### Conceptual Links (not citation-based)
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — **Strong.** Same research program. Cayrol 2005 defines the core BAF semantics (d/s/c-admissibility); Amgoud 2008 provides the comprehensive survey placing BAFs within the Dubois-Prade bipolarity taxonomy and adding gradual valuation.
- [[Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation]] — **Moderate.** Baroni's SCC-recursive schema works on standard AFs; an open question (noted in Baroni's paper) is whether it extends to BAFs with support. Amgoud's BAF formalization is what such an extension would need to handle.
- [[Mayer_2020_Transformer-BasedArgumentMiningHealthcare]] — **Moderate.** Mayer extracts bipolar argumentation structures (support/attack between evidence and claims) from clinical text. Amgoud's BAF formalization and gradual valuation could provide the formal semantics for reasoning over these extracted structures.
- [[Clark_2014_Micropublications]] — **Moderate.** Clark's micropublication model includes both support and challenge relations grounded in Toulmin-Verheij argumentation. Amgoud's bipolarity taxonomy and BAF semantics formalize the abstract structure underlying Clark's bipolar claim-evidence networks.
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — **Moderate.** Odekerken extends ASPIC+ for incomplete information; combining this with Amgoud's bipolar support relation is an open integration question for propstore.
- [Developing the Abstract Dialectical Framework](../Polberg_2017_DevelopingAbstractDialecticalFramework/notes.md) — **Strong.** Polberg's Chapter 4 §4.6 BAF translation chapter sits in the same problem space as this Amgoud-Cayrol bipolarity survey: when does support combine with attack, what does "supported defeat" formally mean, and which semantics are stable across translations to and from BAFs. Polberg uses a different formal toolkit (per-node acceptance conditions over ADFs as the unifying substrate, plus a basic / coalition / attack-propagation / defender pattern catalogue for translations) and arrives at sharp impossibility results that complement Amgoud-Cayrol's gradual-valuation approach.
