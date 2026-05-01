---
title: "Value-Based Reasoning in ASPIC+"
authors: "Johannes P. Wallner, Adam Wyner, Tomasz Zurek"
year: 2024
venue: "Computational Models of Argument (COMMA 2024)"
doi_url: "https://doi.org/10.3233/FAIA240332"
pages: "325-336"
---

# Value-Based Reasoning in ASPIC+

## One-Sentence Summary
Introduces a way to inject values into ASPIC+ before argument construction by filtering each agent's premise and defeasible-rule base through an agent-specific value profile, then computing one grounded extension per agent and intersecting them for a collective result. *(p.1-6)*

## Problem Addressed
Value-based argumentation frameworks usually treat values as a way to order already-constructed arguments. The authors argue that this is too late in the pipeline for many realistic multi-agent settings, because agents who differ in values should often differ earlier: in which propositions they accept, which defeasible rules they are willing to use, and therefore which arguments they can even construct. *(p.1-2, p.5-6)*

The target problem is therefore not merely "which argument wins under a value ordering?", but "how should values reshape the argumentation theory itself so different agents can build different arguments from the same shared background?" *(p.1, p.5-6)*

## Key Contributions
- Defines a **value-based framework (VBF)** with agents, propositions, values, a totally ordered scale, and two agent-specific functions: a threshold/limit for each value and a score for each proposition relative to that value. *(p.2-3)*
- Integrates the VBF into ASPIC+ by defining an **agent-specific subjective knowledge base** that keeps propositions passing the agent's value filter and introduces complementary literals for rejected propositions. *(p.4-5)*
- Defines an **agent-specific subjective defeasible-rule set** by filtering rules whose body or head uses filtered-out propositions, yielding one subjective ASPIC+ theory and one associated AF per agent. *(p.5-6)*
- Defines a **collective grounded extension** `G*` as the intersection of all agents' grounded extensions and proves that it is conflict-free while showing by example and proposition that it need not be admissible. *(p.5-6)*

## Methodology
The paper starts from two inputs: a standard ASPIC+ argumentation theory `T` and a value-based framework `V`. It first defines which propositions survive an agent's value profile, then converts filtered-out propositions into complementary literals so that the agent's subjective knowledge base can explicitly express rejection of those propositions. It next filters defeasible rules so that only rules whose body and head survive the filter remain available. This produces one subjective argumentation theory `T_a` per agent. Each `T_a` is turned into an AF in the ordinary ASPIC+ way, grounded semantics is applied separately to each AF, and the collective result is taken as the intersection of those grounded extensions. *(p.2-6)*

## Formal Background Reused from ASPIC+
The paper works with a simplified ASPIC+ setup. A knowledge base is split into axioms `K_n` and ordinary premises `K_p`; a language `L` is closed under negation; rules are partitioned into strict and defeasible rules; and arguments are finite derivation trees built from the knowledge base and rules. *(p.3-4)*

Attacks are the standard ASPIC+ attacks: rebut, undermine, and undercut. From an argumentation theory one obtains an AF `(A, D)` whose nodes are arguments and whose attack relation is induced from the ASPIC+ attacks. Grounded, complete, and preferred semantics are then applied in the usual Dung-style way. *(p.4)*

## Core Definitions

### Value-Based Framework
The value layer is not an ordering over arguments. Instead it is an upstream structure over agents and propositions:

$$
V = (Agents, Prop, Values, Scale)
$$

where `Scale` is a totally ordered set of weights, each agent `a` has a threshold `ValLimit(a,v)` for each value `v`, and each proposition `p` receives an agent- and value-specific score `ValProp(a,v,p)`. Intuitively, a proposition survives for agent `a` only if it passes every relevant value filter for that agent. *(p.2-3)*

### ASPIC+ Argumentation Theory
The paper uses an argumentation theory

$$
T = (L, C, R_s, R_d, n, K)
$$

with language `L`, contrary function `C`, strict rules `R_s`, defeasible rules `R_d`, naming function `n` for defeasible rules, and knowledge base `K = K_n ∪ K_p`. Arguments are finite derivations rooted in elements of `K`, with the usual `Prem(A)`, `Conc(A)`, `Sub(A)`, `DefRules(A)`, and `TopRule(A)` functions. *(p.3-4)*

### Subjective Proposition Base
For each agent `a`, the VBF induces a filtered set of positive literals that are acceptable under that agent's value profile. The paper then introduces the complementary set `CompaProps_a`, containing `¬p` for each filtered-out positive literal `p`. These complementary literals are important: they let the agent not merely ignore a proposition, but actively carry its rejection inside the subjective theory. *(p.5)*

### Subjective Knowledge Base
The subjective knowledge base for an agent is obtained by taking the original knowledge base, removing filtered-out ordinary premises, and adding the complementary literals for those rejected propositions as ordinary premises. The paper explicitly keeps strict rules untouched. *(p.5)*

### Subjective Defeasible Rules
Defeasible rules are filtered more aggressively than premises. A rule survives for agent `a` only when every literal in its body and its head survives the agent's proposition filter. Thus the rule layer is also personalized, not merely the premise layer. *(p.5)*

### Subjective Argumentation Theory
For each agent `a`, the paper defines a subjective AT `T_a` by pairing the original language/contrary function/strict rules with the agent's subjective knowledge base and subjective defeasible-rule set. The corresponding AF `F_a` is constructed in the ordinary ASPIC+ manner from `T_a`. *(p.5)*

### Collective Grounded Extension
If `G_a` is the grounded extension of agent `a`'s subjective AF, then the collective grounded extension is:

$$
G^* = \bigcap_{a \in Agents} G_a
$$

This captures arguments that all agents accept under their own value-filtered reasoning. *(p.5)*

## Key Equations and Constructions

$$
V = (Agents, Prop, Values, Scale)
$$

Where:
- `Agents` = audience/agent set
- `Prop` = positive literals to which value profiles are attached
- `Values` = values used for filtering
- `Scale` = totally ordered weights or priorities used to compare proposition scores with agent thresholds
*(p.2-3)*

$$
T = (L, C, R_s, R_d, n, K)
$$

Where:
- `L` = language closed under negation
- `C` = contrary function
- `R_s` = strict rules
- `R_d` = defeasible rules
- `n` = naming function for defeasible rules
- `K = K_n \cup K_p` = axioms plus ordinary premises
*(p.3-4)*

$$
G^* = \bigcap_{a \in Agents} G_a
$$

Where:
- `G_a` = grounded extension of the AF generated by the subjective AT of agent `a`
- `G^*` = collectively acceptable arguments under grounded semantics
*(p.5)*

## Worked Examples

### Example 1: Passing and Failing Value Filters
The first example shows two agents `α` and `β`, two values, and a three-level scale. Proposition `p_1` survives for `α` because it passes both value filters, but fails for `β` because one value score falls below the threshold. This illustrates that the same proposition can be admissible for one agent and filtered out for another. *(p.3)*

### Example 2: Base ASPIC+ Theory
Before introducing values, the paper builds a small ASPIC+ theory with literals `a,b,c,d,f` and their complements, several defeasible rules, one ordinary-premise base, and empty axioms. The corresponding AF has seven arguments and a small set of attacks; the example is used as the template that later gets personalized per agent. *(p.4)*

### Example 3: Subjective Knowledge Bases
This example shows how two agents starting from the same original knowledge base end up with different subjective knowledge bases after filtering. One agent retains `a` while another does not; rejected propositions show up as complementary literals such as `¬d` in the subjective base. *(p.5)*

### Example 4: Subjective AFs and Cross-Agent Disagreement
The paper then derives separate AFs for `α` and `β`. The two AFs contain different arguments because their rule and premise bases differ. Their complete extensions also differ: for one agent, a grounded extension includes arguments built from `a`; for the other it includes arguments built from `b`. This is the central concrete demonstration that values are changing argument construction, not merely post hoc preference resolution. *(p.5)*

### Example 5: Collective Acceptance Without Admissibility
The most important example constructs a case where the intersection of the agents' grounded extensions is `{d}`. The collective set is conflict-free, but `d` is not admissible in the original AT or in the subjective ATs because it is attacked by arguments not counterattacked inside the intersection. This example is the paper's main warning against assuming that "accepted by everyone individually" implies collective admissibility. *(p.5-6)*

## Formal Results

### Proposition 1
If `A` is an argument in a subjective AT `T_a`, then the premises and defeasible rules used by `A` do not contain elements filtered out by the agent's value profile. This formalizes that the construction really is upstream: filtered-out material is not merely defeated later; it is absent from the agent's argument construction basis. *(p.6)*

### Proposition 2
If a proposition `p` is in `CompaProps_a`, then `¬p` belongs to the grounded extension `G_a`. In effect, when a proposition is ruled out by values, the subjective theory does not simply stay silent; it contains an undefeated ordinary premise expressing rejection of `p`. *(p.6)*

### Proposition 3
The collective grounded extension `G*` is conflict-free in the original AT and in all subjective ATs, but it is not admissible in general. This is the paper's headline metatheoretic result: intersection is safe from outright internal conflict, but it does not preserve the stronger defense condition. *(p.6)*

## Implementation Details
- Represent values as **agent-local filtering metadata** on propositions, not as a single public ordering over arguments. *(p.2-3, p.6)*
- Run value filtering **before** argument construction, not after the AF already exists. *(p.1, p.5-6)*
- Maintain one subjective theory per agent:
  - filtered ordinary premises
  - added complementary literals for rejected propositions
  - unchanged strict rules
  - filtered defeasible rules
  *(p.5)*
- Build one AF per agent from the corresponding subjective theory, then compute grounded semantics independently per agent. *(p.5)*
- If a system needs collective agreement, intersect the grounded extensions rather than trying to force a single shared premise base. *(p.5)*
- Do not assume the collective result is admissible just because it is conflict-free. Any implementation that treats `G*` as a full extension object will be too strong. *(p.5-6)*
- The construction is especially appropriate when agents privately weight values and do not expose those value profiles directly to others. *(p.6)*

## Figures and Tables of Interest
- **Table 1 (p.5):** Side-by-side argument sets for the two agents, showing how the subjective theories produce different arguments and grounded/preferred results.
- **Figure 1 (p.6):** Visualizes Example 5. It shows the grounded extensions for the two agents and the resulting intersection `{d}`, making the non-admissibility of the collective result concrete.

## Results Summary
This is a theoretical paper rather than an empirical one. Its main "results" are constructional and semantic:
- values can be pushed into ASPIC+ at the level of theory formation, not only defeat comparison *(p.1-5)*
- the resulting agent-specific theories can disagree both on which arguments exist and on which arguments are accepted *(p.5)*
- the intersection of grounded extensions provides a natural notion of collective acceptance, but only with the guarantee of conflict-freeness, not admissibility *(p.5-6)*

## Limitations
- The paper develops the collective notion only for **grounded semantics**; it does not work out analogous collective constructions for preferred, complete, or stable semantics. *(p.5-6)*
- The collective operator is intentionally weak: conflict-free but not admissible in general. Any stronger collective guarantee is left to future work. *(p.5-6)*
- The paper leaves the **internal structure of values** largely abstract. The scale and threshold functions are specified, but a richer formal theory of values is deferred. *(p.6)*
- The ASPIC+ setting is somewhat simplified in the preliminaries; the authors note assumptions that could be relaxed later. *(p.3, p.6)*

## Arguments Against Prior Work
- Classic VAF/VBF approaches treat values mainly as a way to **order abstract arguments** or successful attacks. The authors argue this is too coarse for settings where values should alter which premises, rules, and arguments are available in the first place. *(p.1-2, p.6)*
- In VAF/VBF, values are embedded in abstract structures rather than in individual agents' private profiles. The paper explicitly wants private, agent-indexed value profiles. *(p.1-3, p.6)*
- Context-based/value-ordering approaches can differentiate parties, but the authors argue that their model is more direct for proposition-level filtering and clearer about the role of values in shaping knowledge bases. *(p.6)*
- Preference-based structured argumentation increases computational cost; the paper presents its filter-first approach as a conceptually different route that may also avoid some of that burden. *(p.6)*

## Design Rationale
- **Why filter propositions first?** Because the authors want values to determine what an agent is even willing to entertain or use, not merely which finished argument it prefers. *(p.1-2, p.5)*
- **Why add complementary literals for rejected propositions?** So the agent's theory can represent active rejection and generate attacks, rather than merely omitting content. *(p.5-6)*
- **Why leave strict rules intact?** The point is to personalize defeasible, value-sensitive reasoning while preserving the common deductive backbone. *(p.5)*
- **Why grounded semantics?** It gives one unique extension per agent, making the collective intersection well-defined and easy to interpret. *(p.4-6)*
- **Why intersection for collective reasoning?** It captures arguments accepted by all agents while preserving a minimal safety guarantee of conflict-freeness. *(p.5-6)*

## Relevance to Propstore
This paper is a direct design option for any propstore feature that wants agent-relative reasoning without cloning the entire world model manually. It suggests a concrete architecture:
1. annotate propositions with value scores per agent and per value dimension
2. store agent-specific thresholds over those value dimensions
3. derive one subjective proposition/rule base per agent
4. build one argumentation layer per agent from those filtered inputs
5. intersect grounded acceptability when a "shared minimum agreement" view is required

It is especially relevant if propstore needs:
- personalized evidence admissibility
- value-sensitive disagreement between agents over the same corpus
- collective reasoning that records only what all agents would currently endorse

Its main warning for implementation is equally important: the collective intersection should not be mistaken for a full admissible extension. *(p.5-6)*

## Open Questions
- Can the collective construction be generalized beyond grounded semantics while preserving useful guarantees? *(p.6)*
- What stronger collective operators, if any, preserve admissibility or other Dung-style semantic properties? *(p.5-6)*
- How should the internal structure of values themselves be represented if the system needs richer value reasoning than threshold filtering? *(p.6)*
- What are the computational consequences of this filter-first approach compared with preference-based ASPIC+ implementations? *(p.6)*

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — the AF semantics used once each subjective AT is turned into an argumentation framework. *(p.4-5)*
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — the structured-argumentation basis this paper extends with agent-relative value filtering. *(p.3-5)*
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — a contrasting way to handle value/preference sensitivity at the argument-comparison level rather than at theory construction. *(p.6)*
- [[Bench-Capon_2003_PersuasionPracticalArgumentValue-based]] — earlier value-based argumentation at the abstract level; this paper's main foil. *(p.1-2, p.6)*

### New Leads (Not Yet in Collection)
- Zurek and Wyner (2022), *Towards a Formal Framework for Motivated Argumentation and the Roots of Conflict*. *(ref.1)*
- Wyner and Zurek (2023), *On Legal Teleological Reasoning*. *(ref.2)*
- Perelman (1969), *The New Rhetoric*. *(ref.6)*
- Schwartz (2012), *An Overview of the Schwartz Theory of Basic Values*. *(ref.7)*

### Cited By (in Collection)
- (none found)
