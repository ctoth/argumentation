---
title: "A General Account of Argumentation with Preferences"
authors: "Sanjay Modgil, Henry Prakken"
year: 2018
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/j.artint.2012.10.008"
---

# A General Account of Argumentation with Preferences

## One-Sentence Summary

Builds on the ASPIC+ framework to provide a general, formally rigorous account of structured argumentation with preferences, revising the conflict-free definition to use attacks rather than defeats, broadening the class of supported instantiations (including classical logic), and proving that key rationality postulates hold under these generalizations. *(p.1)*

## Problem Addressed

Prior work on argumentation with preferences had several gaps: (1) the standard defeat-based definition of conflict-free sets in ASPIC+ did not guarantee rationality postulates without strong additional assumptions *(p.2-3)*; (2) the framework had not been shown to generalize to broad classes of instantiations beyond its original scope, including classical logic and abstract logics *(p.2-3)*; (3) critics (Amgoud & Vesic, Brewka & Woltran) argued that ASPIC+ conflated preference-dependent and preference-independent attacks and could yield inconsistent extensions *(p.3, p.32-34)*. This paper addresses all three issues systematically.

## Key Contributions

1. **Revised conflict-free definition**: Replaces defeat-based conflict-free (Def 13, p.14) with attack-based conflict-free (Def 14, p.14), which is strictly stronger and enables all four rationality postulates to hold without additional assumptions. *(p.14)*

2. **Rationality postulates proven**: Sub-argument closure (Thm 12, p.18), closure under strict rules (Thm 13, p.18), direct consistency (Thm 14, p.18), and indirect consistency (Thm 15, p.19) are all proven for attack-conflict-free extensions under reasonable argument orderings. *(p.18-19)*

3. **Generalized instantiations**: Shows ASPIC+ can be instantiated with:
   - Amgoud & Besnard's abstract logic approach (Section 5.2, p.23-26, Propositions 25-30) *(p.23-26)*
   - Classical logic with preferences (Section 5.3, p.27-29) *(p.27-29)*
   - Brewka's preferred subtheories (Theorem 31, p.29: stable extensions correspond to preferred subtheories) *(p.29)*

4. **Formal preference orderings**: Defines weakest-link and last-link preference principles (Defs 20-21, p.21) with Elitist and Democratic set comparisons (Def 19, p.21), and proves both yield reasonable orderings (Props 19-24, p.22). *(p.21-22)*

5. **Systematic rebuttal of critiques**: Section 6.2 demonstrates that ASPIC+ already distinguishes preference-dependent and preference-independent attacks through argument structure (sub-argument attacks), answering Amgoud & Vesic and Brewka & Woltran. *(p.32-35)*

6. **Correction to Prakken 2010**: The weakest-link definition (Def 21) corrects an anomaly in [40]'s definition where premises and defeasible rules were treated asymmetrically. *(p.21)*

## Methodology

The paper is a formal theoretical contribution. It defines mathematical structures (argumentation systems, knowledge bases, arguments, attacks, defeats, structured argumentation frameworks), states properties, and proves theorems. The methodology is:

1. Define the ASPIC+ argumentation system tuple $\langle \mathcal{L}, \overline{\cdot}, \mathcal{R}, n \rangle$ and knowledge base $\mathcal{K} = \mathcal{K}_n \cup \mathcal{K}_p$. *(Def 2, p.8; Def 4, p.9)*
2. Construct arguments recursively from premises and rules (Def 5, p.9). *(p.9)*
3. Define three attack types: undermining, rebutting, undercutting (Def 8, p.11). *(p.11)*
4. Define defeat via preferences (Def 9, p.12): undercutting always succeeds; rebutting and undermining succeed only when the attacker is not strictly less preferred. *(p.12)*
5. Build structured argumentation frameworks (SAF) and c-consistent SAFs (c-SAF) (Def 11, p.13). *(p.13)*
6. Adopt attack-based conflict-free (Def 14, p.14) instead of defeat-based (Def 13, p.14). *(p.14)*
7. Prove rationality postulates hold under reasonable orderings (Def 18, p.16). *(p.16-19)*
8. Show correspondence with abstract logic and classical logic instantiations. *(p.23-29)*

## Key Equations

### Contrariness function
$$\overline{\cdot}: \mathcal{L} \to 2^\mathcal{L}$$
- If $\varphi \in \overline{\psi}$ and $\psi \in \overline{\varphi}$: contradictories
- If $\varphi \in \overline{\psi}$ and $\psi \notin \overline{\varphi}$: $\varphi$ is a contrary of $\psi$
*(Def 2, p.8)*

### Strict closure
$$Cl_{\mathcal{R}_s}(S) = \text{closure of } S \text{ under strict rules}$$
*(Def 3, p.8)*

### c-consistency
A set $S \subseteq \mathcal{L}$ is c-consistent iff for no $\varphi$: $S \vdash \varphi$ and $S \vdash \overline{\varphi}$.
*(Def 3, p.8)*

### Set comparison $\lhd_s$ (Def 19)
For finite sets $\Gamma, \Gamma'$:
- $\Gamma = \emptyset \Rightarrow \Gamma \not\lhd_s \Gamma'$
- $\Gamma' = \emptyset, \Gamma \neq \emptyset \Rightarrow \Gamma \lhd_s \Gamma'$
- **Elitist**: $\Gamma \lhd_{\text{Eli}} \Gamma'$ iff $\exists X \in \Gamma$ s.t. $\forall Y \in \Gamma', X < Y$
- **Democratic**: $\Gamma \lhd_{\text{Dem}} \Gamma'$ iff $\forall X \in \Gamma, \exists Y \in \Gamma', X < Y$
*(Def 19, p.21)*

### Last-link principle (Def 20)
$B \prec A$ iff:
1. $\text{LastDefRules}(B) \lhd_s \text{LastDefRules}(A)$; or
2. Both have no last defeasible rules and $\text{Prem}_p(B) \lhd_s \text{Prem}_p(A)$
*(Def 20, p.21)*

### Weakest-link principle (Def 21)
$B \prec A$ iff:
1. If both strict: $\text{Prem}_p(B) \lhd_s \text{Prem}_p(A)$
2. If both firm: $\text{DefRules}(B) \lhd_s \text{DefRules}(A)$
3. Otherwise: both $\text{Prem}_p(B) \lhd_s \text{Prem}_p(A)$ AND $\text{DefRules}(B) \lhd_s \text{DefRules}(A)$
*(Def 21, p.21)*

### Abstract logic consequence operator (Def 23)
$cn: 2^\mathcal{L} \to 2^\mathcal{L}$ satisfying: inclusion, idempotency, compactness, non-triviality ($cn(\{p\}) \neq \mathcal{L}$), and $cn(\emptyset) \neq \mathcal{L}$.
*(Def 23, p.23)*

### Reasonable argument orderings (Def 18)
An argument ordering $\preceq$ is reasonable iff:
1. i) $\forall A, B$, if $A$ is strict and firm and $B$ is plausible or defeasible, then $B \prec A$; ii) $\forall A, B$, if $B$ is strict and firm then $B \not\prec A$; iii) $\forall A, A', B$ such that $A'$ is a strict continuation of $\{A\}$, if $A \not\preceq B$ then $A' \not\preceq B$, and if $B \not\prec A$ then $B \not\prec A'$
2. Let $\{C_1, \ldots, C_n\}$ be a finite subset of $\mathcal{A}$, and for $i = 1 \ldots n$, let $C^{+\backslash i}$ be some strict continuation of $\{C_1, \ldots, C_{i-1}, C_{i+1}, \ldots, C_n\}$. Then it is not the case that $\forall i, C^{+\backslash i} \prec C_i$.
*(Def 18, p.16-17)*

### Reasonable inducing ordering (Def 22)
An ordering $\leq$ is reasonable inducing if it is a strict partial ordering (irreflexive and transitive) and for any $c \in \mathcal{R}_d \cup \mathcal{K}_p$, if $c$ is a defeasible rule or ordinary premise, and for $\text{LastDefRules}$, $\text{Prem}_p$, $\text{DefRules}$ as needed, the last-link and weakest-link principles yield reasonable argument orderings.
*(Def 22, p.22)*

## Parameters

| Symbol | Meaning | Page |
|--------|---------|------|
| $\mathcal{L}$ | Logical language | p.8 |
| $\overline{\cdot}$ | Contrariness function mapping formulas to sets of contraries/contradictories | p.8 |
| $\mathcal{R} = \mathcal{R}_s \cup \mathcal{R}_d$ | All inference rules (strict + defeasible) | p.8 |
| $\mathcal{R}_s$ | Strict inference rules (cannot be attacked) | p.8 |
| $\mathcal{R}_d$ | Defeasible inference rules (can be undercut) | p.8 |
| $n$ | Naming convention for defeasible rules | p.8 |
| $\mathcal{K} = \mathcal{K}_n \cup \mathcal{K}_p$ | Knowledge base | p.9 |
| $\mathcal{K}_n$ | Axiom/certain premises (cannot be attacked) | p.9 |
| $\mathcal{K}_p$ | Ordinary premises (can be undermined) | p.9 |
| $\mathcal{A}$ | Set of arguments | p.9 |
| $\mathcal{C}$ | Attack/conflict relation | p.13 |
| $\mathcal{D}$ | Defeat relation | p.13 |
| $\preceq$ | Preference ordering over arguments | p.12 |
| $\prec$ | Strict part of $\preceq$ | p.12 |
| $\lhd_s$ | Set comparison (Elitist or Democratic) | p.21 |
| $\leq_{\text{Eli}}$ | Elitist set comparison | p.21 |
| $\leq_{\text{Dem}}$ | Democratic set comparison | p.21 |
| $Prem(A)$ | All premises of argument $A$ | p.9 |
| $Conc(A)$ | Conclusion of argument $A$ | p.9 |
| $Sub(A)$ | All sub-arguments of $A$ | p.9 |
| $DefRules(A)$ | All defeasible rules in $A$ | p.9 |
| $Rules(A)$ | All rules in $A$ | p.9 |
| $TopRule(A)$ | Last rule applied in $A$ | p.9 |
| $DirectSub(A)$ | Direct sub-arguments of $A$ | p.9 |
| $LastDefRules(A)$ | Last defeasible rules in $A$ | p.10 |
| $Prem_p(A)$ | Ordinary premises of $A$ | p.10 |
| $\nu(A)$ | Maximal fallible sub-arguments of $A$ | p.14 |
| $cn$ | Consequence operator (abstract logic) | p.23 |
| $\Sigma$ | Theory / premise set (abstract logic) | p.23 |
| SAF | Structured Argumentation Framework $\langle \mathcal{A}, \mathcal{C}, \preceq \rangle$ | p.13 |
| c-SAF | SAF restricted to c-consistent arguments | p.13 |
| AT | Argumentation Theory $\langle \mathcal{AS}, \mathcal{K} \rangle$ | p.13 |

## Implementation Details

- **ASPIC+ is a framework, not a system**: it specifies how to build argumentation systems by choosing a logical language, contrariness function, rules, knowledge base, and preference ordering. *(p.7)*
- **Argument construction is recursive**: base case is a premise from $\mathcal{K}$; inductive case applies a strict or defeasible rule to the conclusions of existing arguments. *(Def 5, p.9)*
- **Three attack types**: undermining (on ordinary premises), rebutting (on conclusions of defeasible inferences), undercutting (on defeasible inference steps via naming convention). Undercutting is always preference-independent. *(Def 8, p.11)*
- **Defeat filters attacks through preferences**: rebutting and undermining succeed only when the attacker is not strictly weaker ($A \not\prec B'$). Undercutting always succeeds regardless of preferences. *(Def 9, p.12)*
- **Attack-based conflict-free is the recommended definition**: stricter than defeat-based, ensures all rationality postulates hold with fewer auxiliary assumptions. *(Def 14, p.14; discussed p.14-15)*
- **Reasonable argument orderings (Def 18)**: the sufficient condition for all results; requires (i) strict+firm arguments dominate plausible/defeasible ones, (ii) strict+firm arguments are never dominated, (iii) strict continuation preserves preference status. *(Def 18, p.16-17)*
- **Classical logic instantiation**: strict rules = classical consequence; without preferences, preferred/stable extensions = maximal consistent subsets; with preferences, = Brewka's preferred subtheories (Theorem 31). *(p.27-29)*
- **Transposition closure**: required for well-definedness of (c-)SAFs; if $\phi_1, \ldots, \phi_n \to \psi$ is a strict rule, then for each $i$, $\phi_1, \ldots, \overline{\psi}, \ldots \to \overline{\phi_i}$ must also be a strict rule. *(Def 12, p.13; Example 7, p.15)*
- **Attacks on sub-arguments are critical**: A requirement for attacks is that they should only be targeted at fallible elements of an argument, i.e., only on uncertain premises or defeasible inferences. In particular, conclusions of deductive inferences in an argument cannot be attacked. *(p.5)*
- **Two roles of attacks**: (1) encoding mutual incompatibility of information (declarative), and (2) determining which arguments prevail (procedural). *(p.5-6)*
- **Preference-dependent vs preference-independent attacks**: undermining and rebutting are preference-dependent (may be overridden by stronger arguments); undercutting is preference-independent (always succeeds). This distinction is structural in ASPIC+, not requiring separate attack types. *(p.5-6, p.12)*
- **The naming convention $n$**: maps each defeasible rule to a well-formed formula that names it, enabling undercutting attacks that target specific inference steps. *(Def 2, p.8)*
- **Well-definedness conditions (Def 12)**: a (c-)SAF is well-defined iff it is axiom consistent, well-formed and closed under contraposition or closed under transposition. *(p.13)*
- **Fundamental lemma holds for c-SAFs**: under reasonable orderings, Dung's fundamental lemma (Props 9-11, p.17) holds, ensuring admissible extensions form a complete partial order. *(p.17)*

## Figures of Interest

- **Figure 1** (p.11): ASPIC+ argument trees with dashed lines for defeasible rules and solid lines for strict rules, showing how arguments chain from premises through inference steps.
- **Figure 2** (p.13): Attack graph for Example 5, illustrating undermining, rebutting, and undercutting attacks with preference-dependent and preference-independent distinctions.
- **Figure 3** (p.16): Arguments built from transpositions of strict rules, showing how transposition generates additional arguments and attacks. Part a) shows argument trees, b) shows the ASPIC+ attack graph, c) shows a possible defeat graph.
- **Figure 4** (p.28): Classical logic argumentation: attack graph (a) vs defeat graph (b), showing how preferences filter symmetric attacks into asymmetric defeats.
- **Figure 5** (p.33): Counter-examples to critiques of PAFs, showing that ASPIC+'s sub-argument structure prevents the inconsistent extensions that flat approaches produce.

## Results Summary

1. **Fundamental lemma holds** (Props 9-11, p.17): Under reasonable orderings, Dung's fundamental lemma holds for c-SAFs, ensuring admissible extensions form a complete partial order. *(p.17)*
2. **All four rationality postulates satisfied** (Thms 12-15, p.18-19): Sub-argument closure, closure under strict rules, direct consistency, indirect consistency all hold for attack-conflict-free complete extensions of well-defined c-SAFs with reasonable orderings. *(p.18-19)*
3. **Attack = defeat for conflict-free** (Prop 16, p.19): Under the paper's assumptions, attack-based and defeat-based conflict-free definitions yield the same extensions for all standard Dung semantics. *(p.19)*
4. **Last-link and weakest-link are reasonable** (Props 19-24, p.22): Both preference principles, under both Elitist and Democratic set comparisons, produce reasonable argument orderings. *(p.22)*
5. **Abstract logic correspondence** (Props 25-27, p.25-26): ASPIC+ c-SAFs based on abstract logics satisfy all postulates; extensions coincide; premise-minimal ASPIC+ arguments correspond to abstract logic arguments. *(p.25-26)*
6. **Classical logic / preferred subtheories correspondence** (Thm 31, p.29): Stable extensions of classical-logic c-SAFs correspond exactly to Brewka's preferred subtheories. *(p.29)*
7. **Corollary 29** (p.26): Abstract logic argumentation theory is closed under contraposition, axiom consistent, c-classical, and well-formed. *(p.26)*
8. **Proposition 28** (p.25): For any complete extension, the conclusions of arguments form a fixed point of the abstract logic consequence operator. *(p.25)*
9. **Proposition 30** (p.26): For last-link and weakest-link orderings under the elitist set comparison, all results hold for abstract logic c-SAFs with preferences. *(p.26)*
10. **Proposition 32** (p.29): For classical logic c-SAFs, rationality postulates hold under both attack and defeat definitions of conflict-free. *(p.29)*

## Limitations

- The framework is purely theoretical; no implementation or empirical evaluation is provided. *(p.35)*
- Computational complexity of computing extensions under ASPIC+ is not addressed (inherits from Dung's framework, which is generally intractable). *(p.35)*
- The preference ordering must be specified externally; the paper provides last-link and weakest-link as standard options but does not prescribe how to choose between them for a given domain. *(p.20-21)*
- Transposition closure is required for well-definedness, which may generate a large number of additional strict rules in practice. *(p.13, p.15)*
- The contrariness function maps formulas to sets of contraries, but for classical logic the paper restricts to symmetric contradictories. *(p.8, p.27)*
- The paper focuses on Dung semantics (complete, preferred, grounded, stable); other semantics (e.g., semi-stable, ideal) are not considered. *(p.4)*
- Defeasible rules are essential for non-trivial results: if all rules are strict and monotonic, the framework reduces to classical logic with maximal consistent subsets. *(p.29-30)*
- The paper acknowledges that implementations and "human" models of argumentation practice need to be established as future work. *(p.35-36)*

## Arguments Against Prior Work

- **Dung's abstract framework ignores internal argument structure.** Dung's argumentation frameworks [23] treat arguments as atomic entities with no internal structure, making it "difficult to understand and even test the behaviour of an intelligent system." The abstract approach has "a mathematical nature that is remote from how people actually reason." *(p.1)*
- **Prior ASPIC+ lacked revised conflict-free definition.** The original ASPIC+ framework [35] used Dung's standard conflict-free notion. This paper introduces a revised definition of conflict-free that accounts for the structure of attacks and defeats, resolving issues identified in [34] about consistency guarantees. *(pp.2--3)*
- **Existing nonmonotonic formalisms lack argumentation structure.** In logical models of nonmonotonic reasoning, "the argumentation metaphor has proved to oversimplify some drawbacks of other formalisms," but these formalisms do not make the argumentative structure explicit, making it "difficult to understand and even test the behaviour." *(p.1)*
- **Classical logic approaches are too limited.** Systems that restrict to classical logic and deductive inference (Besnard and Hunter [12]) "need to be mixed: deductive and defeasible argumentation," because restricting to deductive inference misses the essential defeasible character of real argumentation. *(p.3)*
- **Attacks should target only fallible elements.** A key requirement is that "attacks should only be targeted at fallible elements of an argument, i.e., on ordinary premises or defeasible inferences." Attacks on conclusions of deductive inference steps from axiom premises are pointless since these cannot be wrong. *(p.5)*
- **"Abstract logic" approaches lack defeasible rules.** Some approaches to argumentation (e.g., Amgoud and Besnard [9]) use abstract logics without distinguishing strict from defeasible rules, losing "the essential role of defeasible inference rules in models of argumentation" needed "to bridge the gap between formalisms and human reasoning." *(p.3)*
- **Prior systems conflated preference-dependent and preference-independent attacks.** The distinction between preference-dependent attacks (undermining, rebutting) and preference-independent attacks (undercutting) was not properly formalized in earlier frameworks, leading to confusion about when preferences should determine defeat. *(pp.5--6)*
- **Recent critiques of Dung's approach are addressed.** The paper examines "some counter-recent criticisms of Dung's abstract approach, as well as critiques of Dung's approach extended with preferences" [25], arguing that "a proper modelling of the use of preferences requires making the structure of arguments explicit." *(p.3)*

## Design Rationale

- **Structured argumentation bridges abstract and concrete.** ASPIC+ serves as "an intermediate level of abstraction between Dung's fully abstract level and concrete instantiating logics," providing enough structure to prove rationality postulates while remaining general enough to instantiate with different logics. *(pp.1--2)*
- **Attacks encode mutual incompatibility.** "Attacks encode the mutual incompatibility of the information contained in the attacking and attacked arguments, in a way that accounts for their dialectical use." This unifies different attack types under a single semantic principle. *(p.6)*
- **Three attack types with different preference behavior.** Undermining (attacks on ordinary premises), rebutting (attacks on defeasible inference conclusions), and undercutting (attacks on defeasible inference applicability) are distinguished because they have fundamentally different relationships to preferences: undercutting always succeeds regardless of preferences. *(pp.5--6)*
- **Revised conflict-free notion.** The paper revises the standard conflict-free definition to account for structured arguments: conflict-free is defined in terms of attacks rather than defeats, ensuring that no extension contains arguments that attack each other even before preference filtering. *(pp.2--3)*
- **Axiom premises cannot be attacked.** Axiom premises ($\mathcal{K}_n$) are distinguished from ordinary premises ($\mathcal{K}_p}$): axioms "are certain knowledge and thus cannot be attacked," while ordinary premises are uncertain and thus attackable. This models the distinction between established facts and defeasible assumptions. *(p.8)*
- **Naming convention for defeasible rules.** Each defeasible rule $r$ is associated with a formula $n(r)$ representing the applicability of that rule. Undercutting attacks target this name, providing a clean mechanism for "blocking the inference" without denying either premise or conclusion. *(p.8)*
- **Transposition closure ensures consistency.** Requiring transposition closure of strict rules (if $p_1, \ldots, p_n \rightarrow q$ then $p_1, \ldots, p_{i-1}, \overline{q}, p_{i+1}, \ldots, p_n \rightarrow \overline{p_i}$) ensures that the framework satisfies direct and indirect consistency rationality postulates. *(pp.13, 15)*
- **Reasonable orderings guarantee rationality.** The "reasonable" ordering requirement (an argument cannot be strictly weaker than its proper sub-arguments) is a minimal condition sufficient to guarantee that all four rationality postulates hold. *(p.18)*
- **Instantiation demonstrates generality.** The paper instantiates the framework with Tarskian classical logic, demonstrating that stable extensions correspond to Brewka's preferred subtheories --- showing ASPIC+ can capture well-known nonmonotonic reasoning systems as special cases. *(pp.27--30)*

## Testable Properties

1. **Rationality postulates**: Any implementation of ASPIC+ with attack-based conflict-free, reasonable orderings, and well-defined c-SAFs MUST produce extensions that satisfy sub-argument closure, closure under strict rules, direct consistency, and indirect consistency. *(Thms 12-15, p.18-19)*
2. **Preference filtering**: Undercutting attacks must always succeed regardless of preferences. Rebutting and undermining must succeed only when the attacker is not strictly weaker. *(Def 9, p.12)*
3. **Last-link vs weakest-link**: Given the same knowledge base and rules, last-link and weakest-link orderings may produce different defeat relations and different extensions. Both must be reasonable per Definition 18. *(Defs 20-21, p.21; Def 18, p.16)*
4. **Classical logic correspondence**: For a classical-logic c-SAF without preferences, preferred/stable extensions must correspond to maximal consistent subsets. With preferences, they must correspond to Brewka's preferred subtheories. *(Thm 31, p.29; Section 5.3, p.27-29)*
5. **Abstract logic embedding**: For any abstract logic $\langle \mathcal{L}, cn \rangle$ satisfying the five conditions of Def 23, the ASPIC+ c-SAF construction must yield the same extensions as the direct abstract logic construction. *(Props 25-27, p.25-26; Def 23, p.23)*
6. **Attack on sub-arguments only**: Attacks should only target fallible elements (ordinary premises and defeasible inference steps), not conclusions derived by strict rules alone. *(p.5, Def 8 p.11)*
7. **Transposition generates additional arguments**: When strict rules have transpositions, new arguments and attacks must be generated; the resulting SAF must still be well-defined. *(Def 12, p.13; Example 7, p.15)*
8. **Strict+firm arguments dominate**: Under reasonable orderings, any argument that is strict and firm must be strictly preferred to any plausible or defeasible argument, and must never be strictly less preferred than any argument. *(Def 18 conditions 1.i and 1.ii, p.16)*

## Relevance to Project

This paper is directly foundational for the propstore's argumentation architecture. Key connections:

- **Claim conflict resolution**: ASPIC+'s three attack types (undermining, rebutting, undercutting) map directly to ways claims can conflict in the propstore. Undermining challenges a premise/source; rebutting challenges a conclusion; undercutting challenges the inference method. *(Def 8, p.11)*
- **Preference-based defeat**: The propstore needs to resolve conflicts between claims from sources of varying reliability. ASPIC+'s preference orderings (last-link, weakest-link, Elitist, Democratic) provide formal options for encoding source credibility and claim strength. *(Defs 19-21, p.21)*
- **Rationality guarantees**: The four postulates ensure that the propstore's justified claims are logically consistent, closed under strict inference, and include all sub-arguments of accepted arguments. *(Thms 12-15, p.18-19)*
- **Bridge to existing work**: Theorem 31 connects ASPIC+ to Brewka's preferred subtheories, and the abstract logic correspondence connects to Amgoud & Besnard's work, both of which may be relevant for the propstore's belief revision architecture. *(p.29, p.23-26)*
- **Complements Dung 1995 and Modgil & Prakken 2014**: This paper extends and revises both, providing the most mature version of the ASPIC+ framework in the collection. *(p.1-3)*
- **Sub-argument structure prevents inconsistency**: The key insight from Section 6.2 is that flat PAF approaches can yield inconsistent extensions, but ASPIC+'s sub-argument structure with attacks on sub-arguments prevents this. This is directly relevant to propstore's architecture: claim graphs must preserve sub-argument structure. *(p.32-34, Figure 5 p.33)*

## Open Questions

1. How should the propstore choose between last-link and weakest-link orderings for different types of claim conflicts? *(Defs 20-21, p.21)*
2. Can the Elitist vs Democratic set comparison choice be made domain-dependent (e.g., Elitist for safety-critical domains, Democratic for aggregating opinions)? *(Def 19, p.21)*
3. How does the computational cost of computing ASPIC+ extensions scale with the size of the propstore's claim graph? *(not addressed in paper, p.35)*
4. Can the naming convention for defeasible rules ($n$) be used to encode argument scheme types from Walton's taxonomy (already in the collection)? *(Def 2, p.8)*
5. How does the attack-based conflict-free definition interact with the bipolar argumentation of Cayrol 2005 (also in the collection), which adds support relations? *(Def 14, p.14)*

## Related Work Worth Reading

- **Amgoud & Vesic 2011** [9]: Alternative preference-based argumentation framework; key critique target of this paper. *(p.32-35)*
- **Bench-Capon 2003** [10]: Value-based argumentation frameworks; extends Dung with audiences and values. *(p.30)*
- **Caminada & Amgoud 2007** [18]: Original rationality postulates paper that this work builds on and extends. *(p.4, p.18)*
- **Brewka 1989** [16]: Preferred subtheories; formally connected to ASPIC+ via Theorem 31. *(p.28-29)*
- **Prakken 2010** [40]: The original ASPIC+ paper; this paper revises and extends it. *(p.7, p.21)*

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [23]; all of ASPIC+'s semantics (complete, preferred, grounded, stable extensions) are defined in terms of Dung's abstract argumentation framework. Dung 1995 is the foundational layer this paper builds on. *(p.4)*
- [[Pollock_1987_DefeasibleReasoning]] — cited as [37]; Pollock's rebutting/undercutting defeater distinction is formalized as two of ASPIC+'s three attack types. Pollock's defeasible reasoning is a special case of the ASPIC+ framework. *(p.9)*
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — same authors' tutorial introduction to ASPIC+. This 2018 paper is the full technical version with complete proofs, general contrariness function, revised conflict-free definition, and broader instantiation results. The 2014 tutorial references this paper as "Modgil & Prakken (2013)." *(p.3)*
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — co-authored by Prakken; cites this paper (as "Modgil and Prakken 2011") as the modern ASPIC+ framework integrating Pollock's ideas with structured argumentation.

### New Leads (Not Yet in Collection)
- Caminada & Amgoud (2007) [18] — "On the evaluation of argumentation formalisms" — introduced the rationality postulates that this paper proves for revised ASPIC+ *(p.18)*
- Amgoud & Vesic (2011) [9] — "A new approach for preference-based argumentation frameworks" — key critique target; Section 6.2 systematically rebuts their arguments *(p.32-35)*
- Bench-Capon (2003) [10] — "Persuasion in practical argument using value-based argumentation frameworks" — extends Dung with audiences and values *(p.30)*
- Simari & Loui (1992) [46] — "A mathematical treatment of defeasible argumentation and its implementation" — early structured argumentation system *(p.51)*
- Vreeswijk (1997) [48] — "Abstract argumentation systems" — abstract framework for structured argumentation *(p.51)*

### Now in Collection (previously listed as leads)
- [[Brewka_1989_PreferredSubtheoriesExtendedLogical]] — Defines preferred subtheories as principled maximal consistent subsets selected by reliability orderings (level-based and partial-order-based). Theorem 31 of this paper establishes that stable extensions of classical-logic ASPIC+ c-SAFs correspond exactly to Brewka's preferred subtheories, providing the semantic bridge between flat and structured approaches to prioritized nonmonotonic reasoning. *(p.28-29)*

### Now in Collection (previously listed as leads)
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — The original ASPIC framework paper that this 2018 work revises and extends. Prakken 2010 defines the core framework (arguments as inference trees, three attack types, defeat with preferences) and proves rationality postulates under closure conditions. This 2018 paper revises the conflict-free definition (attack-based rather than defeat-based), broadens supported instantiations, and provides complete proofs for the generalized framework. *(p.7)*

### Supersedes or Recontextualizes
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — this 2018 paper is the full technical version; the 2014 tutorial is an accessible introduction that omits proofs and uses simplified "ordinary negation" instead of the general contrariness function. The 2018 paper also revises the conflict-free definition (attack-based rather than defeat-based) which the 2014 tutorial does not incorporate. *(p.3)*

### Cited By (in Collection)
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — cites this paper as "Modgil & Prakken (2013)" (the Artificial Intelligence journal publication); references it as the full technical version with complete proofs
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — cites as "Modgil and Prakken (2011)"; positions it as the modern integration of Pollock's ideas with structured argumentation
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — cited as ref 20 (as "Modgil and Prakken 2013"); extends the full ASPIC+ framework with incomplete information handling, building on the preference-based defeat mechanism and rationality postulates proved here

### Conceptual Links (not citation-based)
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — **Strong.** Cayrol extends Dung's framework with support relations (bipolar argumentation); Modgil & Prakken extend it with structured arguments and preferences. Both enrich the same abstract foundation in complementary directions. Open question 5 in this paper explicitly asks how ASPIC+'s attack-based conflict-free definition interacts with Cayrol's support relations.
- [[Clark_2014_Micropublications]] — **Strong.** Clark's micropublication model uses Toulmin-Verheij defeasible argumentation with support/challenge relations. ASPIC+'s three attack types (undermining, rebutting, undercutting) provide formal semantics for Clark's challenge relations, and ASPIC+'s preference orderings can encode source credibility for Clark's attributed claims.
- [[Walton_2015_ClassificationSystemArgumentationSchemes]] — **Strong.** Walton & Macagno classify argumentation schemes; ASPIC+ instantiates them as defeasible inference rules. Open question 4 in this paper asks whether the naming convention for defeasible rules can encode Walton's argument scheme types.
- [[deKleer_1986_AssumptionBasedTMS]] — **Moderate.** ATMS environments (consistent assumption sets) correspond structurally to conflict-free sets in Dung's framework. Both address consistency maintenance under contradictory information, from different traditions.
- [[Dixon_1993_ATMSandAGM]] — **Moderate.** Dixon bridges ATMS and AGM belief revision; this paper bridges structured and abstract argumentation. Both connect different formalisms for managing beliefs under contradiction.
- [[Reiter_1980_DefaultReasoning]] — **Moderate.** Default logic is cited via Dung's correspondence results. ASPIC+ can model default reasoning by treating default rules as defeasible inference rules. *(p.29-30)*
- [[Shapiro_1998_BeliefRevisionTMS]] — **Moderate.** Shapiro surveys TMS architectures as belief revision mechanisms; ASPIC+ provides an argumentation-theoretic alternative with explicit preference-based conflict resolution.
- [[Gärdenfors_1988_RevisionsKnowledgeSystemsEpistemic]] — **Strong.** ASPIC+ preference orderings over rules/premises serve the same structural role as epistemic entrenchment orderings — both determine which beliefs survive conflict. The entrenchment postulates (EE1-EE5) provide rationality criteria that ASPIC+ preference-based defeat implicitly satisfies.
