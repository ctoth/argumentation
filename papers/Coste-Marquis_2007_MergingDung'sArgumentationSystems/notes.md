---
title: "On the Merging of Dung's Argumentation Systems"
authors: "Sylvie Coste-Marquis, Caroline Devred, Sebastien Konieczny, Marie-Christine Lagasquie-Schiex, Pierre Marquis"
year: 2007
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/j.artint.2007.04.012"
pages: "730-753"
produced_by:
  agent: "Claude Opus 4.6 (1M context)"
  skill: "paper-reader"
  timestamp: "2026-03-29T03:04:56Z"
---
# On the Merging of Dung's Argumentation Systems

## One-Sentence Summary
Provides a formal framework for merging multiple Dung argumentation frameworks from different agents using distance-based operators lifted from IC merging, defining partial argumentation frameworks (PAFs) to handle incomplete agent knowledge, and proving properties of the resulting merged systems. *(p.0)*

## Problem Addressed
When multiple agents each have their own argumentation system (AF) over a shared set of arguments, how to derive a single merged argumentation system that is as close as possible to all agents' views. Prior work on merging focused on propositional belief bases; this paper lifts merging to the argumentation level where the objects being merged are attack relations, not formulas. *(p.0-1)*

Two key problems are identified: *(p.4)*
- **Problem 1**: Voting (union/intersection) on extensions does not respect attack structure — accepted sets from different agents may not form valid extensions of any single AF.
- **Problem 2**: Voting only on extensions ignores the attack relations and the information they encode (which extensions are chosen depends on the semantics, and information is lost).

## Key Contributions
- **Partial Argumentation Frameworks (PAFs)**: Extension of Dung AFs where agents can express ignorance about attacks via a three-valued relation (attack/non-attack/ignorance). *(p.5-6)*
- **Consensual expansion**: A way to expand each agent's AF into a PAF that includes all candidate attacks from the group. *(p.6-7)*
- **Distance-based merging operators** for AFs: Using pseudo-distances between PAFs, aggregation functions (sum, max, leximax), to find AFs closest to the profile. *(p.8-9)*
- **Properties** of the merging operators including clash-free part preservation, common part preservation, concordance, compatibility, and majority PAF. *(p.12-18)*
- **Joint acceptability** relations based on voting methods for profiles of AFs. *(p.20-21)*

## Methodology
The paper follows a three-step process: *(p.0-1)*
1. Each agent's AF is expanded into a PAF (partial argumentation framework) capturing what each agent considers attack, non-attack, and unknown.
2. A pseudo-distance between PAFs is defined (the edit distance counts the number of pairs (a,b) where one PAF says attack and the other says non-attack).
3. An aggregation function (sum, max, leximax) combines distances to select the AF(s) closest to the profile.

The approach is analogous to IC merging (Konieczny & Pino Perez) but lifted from propositional bases to argumentation frameworks. *(p.1)*

## Key Definitions

### Dung's Argumentation Framework (recap)
**Definition 1** (p.2): An AF is a pair (A, R) where A is a finite set of arguments and R is a binary relation on A (attack relation). a R b means a attacks b.

**Conflict-free**: S subset of A is conflict-free iff there are no a,b in S such that a R b. *(p.2)*

**Collective defense**: C collectively defends a iff for all b in A, if b R a then there exists c in C such that c R b. *(p.2)*

**Admissible**: S is admissible iff S is conflict-free and defends all its elements. *(p.3)*

**Preferred extension**: Maximal (w.r.t. inclusion) admissible set. *(p.3)*

**Stable extension**: S is stable iff S is conflict-free and for every a not in S, there exists b in S with b R a. *(p.3)*

**Grounded extension**: Least fixed point of the characteristic function F(S) = {a in A : a is defended by S}. *(p.3)*

**Definition 5** (p.3): Self-founded AF: AF = (A, R) is self-founded iff it does not exist an infinite sequence a_0, a_1, ... of arguments from A such that for each i, a_{i+1} R a_i.

**Definition 6** (p.3): Acceptability relation Acc_sigma. For a given AF system, AF = (A, R), a total function from 2^A to {true, false} which associates each subset E of A with true iff E is an acceptable set for AF under semantics sigma.

### Partial Argumentation Frameworks

**Definition 9** (p.5-6): A *partial argumentation framework* (PAF) over A is a quadruple PAF = (A, R, I, N) where:
- A is a finite set of arguments
- R, I, N are binary relations on A
- R is the attack relation
- I is the ignorance relation
- N = (A x A) \ (R union I) is the non-attack relation
- R, I, N partition A x A

Each PAF can be viewed as a compact representation of a set of AFs over A. *(p.6)*

**Definition 10** (Completion of a PAF): Let PAF = (A, R, I, N). Let AF = (A, R'). AF is a completion of PAF iff R subset R' and R' subset (R union I). *(p.6)*

The set of all completions of PAF is denoted C(PAF). *(p.6)*

### Expansion

**Definition 11** (Expansion of an AF): Let P = {AF_1, ..., AF_n}. Let e_i be a profile of n AFs such that AF_i = (A_i, R_i). Let A = union of all A_i, N_i = {(a,b) in A x A : (a,b) not in R_i and a in A_i and b in A_i}, I_i = (A x A) \ (R_i union N_i). The consensual expansion of AF_i is the PAF exp(AF_i, P) = (A, R_i, I_i, N_i). *(p.6-7)*

Key insight: An AF is expanded by treating known non-attacks as non-attacks, known attacks as attacks, and all pairs involving arguments not in the agent's original set as ignorance. *(p.7)*

**Proposition 13** (p.7): The consensual expansion exp_GP of AF over P is an expansion of AF over P in the sense of Definition 12.

### Pseudo-distance and Aggregation

**Definition 15** (p.8): A *pseudo-distance* d between PAFs over A is a mapping that:
- d(x, y) = d(y, x) (symmetry)
- d(x, y) = 0 iff x = y (minimality)
- d is a distance if additionally d(x, z) <= d(x, y) + d(y, z) (triangle inequality)

**Definition 16** (p.8): An *aggregation function* is a mapping tensor from (R+)^n to (R+) satisfying:
- Non-decreasingness: if x_i >= x_i', then tensor(x_1,...,x_i,...,x_n) >= tensor(x_1,...,x_i',...,x_n)
- Minimality: tensor(x_1,...,x_n) = 0 iff for all i, x_i = 0
- Identity: tensor(x) = x

**Definition 17** (Merging of n AFs) (p.8-9): Let P = <AF_1,...,AF_n> be a profile of n AFs. Let d be a pseudo-distance between PAFs, tensor an aggregation function, exp_1,...,exp_n be n expansion functions. The *merging* of P is:

$$
\Delta^{\otimes}_{d}(\langle AF_1, \ldots, AF_n \rangle) = \{AF \text{ over } \bigcup A_i \mid AF \text{ minimizes } \otimes_{i=1}^{n} d(\text{exp}_i(AF_i, \mathcal{P}), AF)\}
$$
*(p.9)*

### Edit Distance

**Definition 18** (Edit distance) (p.9): Let PAF_1 = (A, R_1, I_1, N_1) and PAF_2 = (A, R_2, I_2, N_2) be two PAFs over A. The *edit distance* between PAF_1 and PAF_2 is the mapping d_e such that:
- d_e(PAF_1, PAF_2) = 0 if R_1 = R_2 and N_1 = N_2 (and hence I_1 = I_2)
- d_e(PAF_1, PAF_2) = |{(a,b) in A x A : (a,b) in R_1 intersect N_2 or (a,b) in N_1 intersect R_2}| otherwise

The edit distance counts pairs where one PAF says "attack" and the other says "non-attack." Ignorance is treated as halfway between attack and non-attack. *(p.9-10)*

**Proposition 19** (p.10): The edit distance d_e between PAFs is a distance (satisfies triangle inequality).

### Specific Aggregation Functions

Three aggregation functions are used: *(p.9)*
- **Sum** (Sigma): tensor(x_1,...,x_n) = x_1 + ... + x_n
- **Max**: tensor(x_1,...,x_n) = max(x_1,...,x_n)
- **Leximax**: sorts distances in decreasing order then compares lexicographically

The resulting merging operators are denoted Delta^Sigma_de, Delta^Max_de, Delta^Leximax_de. *(p.9-11)*

## Key Equations / Statistical Models

$$
\Delta^{\otimes}_{de}(\mathcal{P}) = \{AF \text{ over } A \mid AF \text{ minimizes } \bigotimes_{i=1}^{n} de(\text{exp}_i(AF_i, \mathcal{P}), AF)\}
$$
Where: P is a profile of AFs, de is the edit distance, tensor is an aggregation function, exp_i is the expansion function for agent i.
*(p.9)*

$$
de(\text{PAF}_1, \text{PAF}_2) = |R_1 \cap N_2| + |N_1 \cap R_2|
$$
Where: R_i is the attack relation, N_i is the non-attack relation of PAF_i.
*(p.9-10)*

$$
\text{Acc}_{\sigma}(\text{PAF}) = \{E \subseteq A \mid \exists AF \in C(\text{PAF}), \text{Acc}_{\sigma}(AF) = \text{true for } E\}
$$
Where: C(PAF) is the set of completions of PAF, sigma is a Dung semantics.
*(p.6)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Number of agents | n | - | - | >= 1 | p.8 | Size of the profile |
| Edit distance | d_e | - | - | [0, |A|^2] | p.9 | Integer-valued for AFs |
| Aggregation function | tensor | - | Sum | {Sum, Max, Leximax} | p.8-9 | Three studied in detail |

## Methods & Implementation Details

- **Three-step merging process**: (1) Expand each AF_i to PAF_i, (2) compute edit distances from each PAF_i to every candidate AF over the shared argument set A, (3) aggregate distances and select minimizers. *(p.0-1)*
- **Expansion policy**: Each agent expands their AF by adding ignorance for all pairs involving arguments they don't know about. The expansion is consensual — it respects each agent's known attacks and non-attacks. *(p.6-7)*
- **Computational note**: The paper notes that computing the merging can be done by considering all AFs over A (which is exponential in |A|^2), but the edit distance only depends on the attack relation, so it suffices to enumerate all possible attack relations. *(p.9)*
- **Sufficiency many agents**: The concept of "sufficiently many" refers to different voting thresholds — simple majority can be used for instance. *(p.7)*

## Figures of Interest
- **Fig (p.4)**: Example 7 — Two agents AF_1 and AF_2 where naive union/intersection of extensions fails. Shows that voting on extensions ignores attack structure.
- **Fig (p.8)**: Example 14 — Four AFs (AF_1 through AF_4) over arguments {a,b,c,d} with their PAF expansions illustrated, showing how different aggregation functions (Sum, Max, Leximax) produce different merged AFs.
- **Fig (p.11-12)**: Example 18 continued — Illustrates discrepancies between Sum, Max, and Leximax merging operators. AF'_1 is the most consensual (equidistant from all PAFs).
- **Fig (p.12)**: Example 20 — Two agents with different argument sets showing how attacks from unknown-to-known arguments are handled.
- **Fig (p.16)**: Example 30 — Concordance vs discordance: three AFs where AF_1 and AF_3 are concordant but AF_1 and AF_2 are discordant.
- **Fig (p.19)**: Example 38 — Majority PAF construction and correspondence with merging result.

## Results Summary

### Properties of Consensual Expansion and PAFs

**Proposition 13** (p.7): Consensual expansion is indeed an expansion in the formal sense.

**Proposition 23** (p.13): If P = <PAF_1, ..., PAF_n> is a profile of PAFs with common part CP(P), the common part is pointwise included in the clash-free part. *(p.13-14)*

**Proposition 25** (p.14): If all PAFs are over the same set of arguments and the common part of P is P-dominated by CP(P), then the clash-free part of the profile and its common part are identical. *(p.14)*

### Properties of Merging Operators

**Proposition 29** (p.15-16): The profile P is concordant iff and only if exp_GP(P) = {Delta^Sigma_de(P)}. When concordant, all aggregation functions produce the same result. *(p.15-16)*

**Proposition 33** (p.17): P is compatible iff P is concordant and every exp_GP(AF_i, P) is compatible with every other. *(p.17)*

**Proposition 35** (p.17): If P is concordant, then for any aggregation function, the clash-free part of any profile P is included in each AF in the merging. *(p.17)*

**Corollary 37** (p.18): When sum is used and all AFs are over the same arguments, the merging is the PAF obtained by applying strict majority rule to decide each attack. *(p.18)*

**Definition 38** (Majority PAF) (p.18): The majority PAF MP(P) of a profile of AFs over the same set A is defined by: (a,b) in R iff more than |P|/2 AFs have the attack; (a,b) in N iff more than |P|/2 AFs don't have the attack; otherwise (a,b) in I. *(p.18-19)*

**Proposition 39** (p.19): MP(P) is a PAF. *(p.19)*

**Proposition 40** (p.19): Every AF over A which minimizes Sum of d_e(AF, AF_i) is a completion of MP(P). *(p.19)*

### Joint Acceptability

**Definition 42** (p.20): Joint acceptability — a joint acceptability relation for a profile P = <AF_1,...,AF_n> of AFs, denoted Acc_sigma, is a total function from 2^A to {true, false} which associates each subset E of A with true iff E is jointly acceptable set for <AF_1,...,AF_n> and with false otherwise. *(p.20)*

**Definition 43** (p.20): Instances of joint acceptability:
- S is **skeptically jointly acceptable** for P iff for all i, S is included in at least one acceptable set for each AF_i.
- S is **credulously jointly acceptable** for P iff S is included in at least one acceptable set for at least one AF_i.
- S is **justly acceptable** by majority for P iff it is included in at least one acceptable set for at least a weak majority of AFs. *(p.20)*

**Proposition 44** (p.21): The set of jointly acceptable sets equals the set of all acceptable sets of the merging when only considering the merging. *(p.21)*

## Limitations
- The framework only considers the attack relation; support is not modeled. *(p.22)*
- Computational complexity is not analyzed — enumerating all AFs over A is exponential in |A|^2. *(p.9, implicit)*
- The expansion policy assumes agents agree on which arguments exist; only the attack relation differs. *(p.5)*
- The paper acknowledges that PAFs could be extended to weighted AFs where agents assign strengths to attacks. *(p.22)*
- Joint acceptability (Section 7) is explored but the connection to the merging operators is shown to not always hold cleanly — the merged AFs' extensions don't always correspond to what voting on extensions would give. *(p.21-22)*

## Arguments Against Prior Work
- **Naive union/intersection of extensions fails**: Example 7 (p.4) shows that taking the union or intersection of preferred extensions from different agents' AFs can produce sets that are not valid extensions of any single AF. The attack structure is violated. *(p.4)*
- **Voting on extensions ignores attack information**: Even when extensions coincide, the underlying attack relations carry information that purely extensional approaches discard. *(p.4-5)*
- **Simple union/intersection of AFs is too crude**: Taking the union of attack relations (AF_1 union AF_2) or intersection doesn't respect the agents' intended semantics. Union adds attacks from Agent 1 that Agent 2 explicitly disagrees with. *(p.4-5)*

## Design Rationale
- **Why PAFs?**: Standard AFs force binary decisions (attack or not). PAFs add a third option (ignorance) that is essential when agents have different argument sets — an agent shouldn't be forced to commit on attacks involving arguments they don't know about. *(p.5)*
- **Why edit distance?**: It counts minimal changes needed to reconcile two PAFs, treating each (a,b) pair independently. This gives a natural metric on the space of attack relations. *(p.9)*
- **Why multiple aggregation functions?**: Sum favors the majority, Max is more egalitarian (minimizes worst-case disagreement), Leximax is between the two. Different social choice principles. *(p.11)*
- **Why not merge at the extension level?**: Because extensions are derived objects — merging the generating structure (attack relation) is more informative and avoids the voting paradoxes shown in Problem 1. *(p.4-5)*

## Testable Properties
- **Edit distance is a metric**: d_e satisfies symmetry, minimality, and triangle inequality. *(p.10)*
- **Concordant profiles produce unique merging**: If P is concordant, Delta^tensor_de(P) is a singleton for any aggregation function. *(p.15-16)*
- **Common part preservation**: The common part of a concordant profile is preserved in the merging result. *(p.13-14)*
- **Clash-free part inclusion**: For concordant profiles, the clash-free part is included in every AF in the merging. *(p.17)*
- **Majority PAF correspondence**: With sum aggregation over same-argument AFs, every merged AF is a completion of the majority PAF. *(p.19)*
- **Sum merging = majority graph**: With sum and same arguments, the merging is the PAF obtained by strict majority on each pair. *(p.18)*

## Relevance to Project
This paper is highly relevant to propstore's multi-agent argumentation framework. Key applications:
1. **Merging AFs from different sources**: When different papers or knowledge sources produce different attack relations over shared arguments, this framework provides principled merging operators.
2. **PAFs for incomplete knowledge**: The PAF formalism (attack/non-attack/ignorance) maps directly to propstore's non-commitment discipline — agents can express uncertainty about attacks without being forced to commit.
3. **Distance-based operators**: The edit distance and aggregation functions provide concrete algorithms for computing merged AFs, complementing the existing Dung AF implementation.
4. **Connection to IC merging**: The framework bridges argumentation merging with the well-studied IC merging literature, providing rationality postulates.

## Open Questions
- [ ] How does this relate to Yun et al. 2023 merging paper already in the collection?
- [ ] Can the edit distance be computed efficiently for large argument sets?
- [ ] How to extend to ASPIC+ where attacks are derived from rules/premises?
- [ ] Connection to ATMS: could PAF ignorance be mapped to ATMS assumption labels?

## Collection Cross-References

### Already in Collection (cited by this paper)
- [[Dung_1995_AcceptabilityArguments]] — The foundational AF theory this paper extends. All definitions (conflict-free, admissible, preferred, stable, grounded) are from Dung 1995.
- [[Brewka_1989_PreferredSubtheoriesExtendedLogical]] — Cited as precursor to argumentation-based belief revision.
- [[Pollock_1987_DefeasibleReasoning]] — Cited for defeasible reasoning foundations.
- [[Simari_1992_MathematicalTreatmentDefeasibleReasoning]] — Cited for mathematical treatment of defeasible reasoning.
- [[Coste-Marquis_2005_SymmetricArgumentationFrameworks]] — Earlier work by the same lead author on symmetric AFs; the merging paper builds on this group's earlier contributions.

### Cited By (in Collection)
- [[Baumann_2015_AGMMeetsAbstractArgumentation]] — Cites this paper; connects merging operators to AGM-style revision of AFs. Merging AFs is closely related to revision via faithful assignment mechanism.
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — Survey on argumentation dynamics that covers this paper's merging framework.
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — Cites this paper in context of probabilistic argumentation.

### Now in Collection (previously listed as leads)
- [[Konieczny_2002_MergingInformationUnderConstraints]] — Defines the IC merging framework (postulates IC0-IC8) for combining multiple belief bases under integrity constraints, with representation theorems via syncretic assignments and distance-based operator families (Sigma, Max, GMax). This is the foundational propositional-level framework that Coste-Marquis 2007 lifts to argumentation frameworks.

### New Leads (Not Yet in Collection)
- Cayrol, Devred, Lagasquie-Schiex 2003 — Collective argumentation and disjunctive programming.

### Conceptual Links (not citation-based)
- [[Baumann_2010_ExpandingArgumentationFrameworksEnforcing]] — Expansion/enforcement of AFs relates directly to the expansion step in the merging process here.
- [[Boella_2009_DynamicsArgumentationSingleExtensions]] — Dynamics of argumentation, including single-extension enforcement, overlaps with the merging framework's goal of producing merged extensions.
- [[Alchourron_1985_TheoryChange]] — AGM theory of change; Coste-Marquis's merging lifts IC merging (which operationalizes AGM-like postulates) to argumentation.

## Related Work Worth Reading
- Konieczny & Pino Perez 2002: IC merging postulates for propositional belief bases — the foundation this paper lifts to AF level. *(p.1)* -> NOW IN COLLECTION: [[Konieczny_2002_MergingInformationUnderConstraints]]
- Cayrol, Devred, Lagasquie-Schiex 2003: Collective argumentation and dynamic programming. *(p.23)*
- Brewka 1989: Preferred subtheories, a precursor to argumentation-based belief revision. *(p.23)*
- Prakken, Vreeswijk 2002: Logics for defeasible argumentation — Handbook chapter. *(p.23)*
- Elvang-Goransson et al.: Acceptability of arguments as logical uncertainty. *(p.3)*
