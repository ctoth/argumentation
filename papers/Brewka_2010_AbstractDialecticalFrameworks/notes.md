---
title: "Abstract Dialectical Frameworks"
authors: "Gerhard Brewka, Stefan Woltran"
year: 2010
venue: "Proceedings of the Twelfth International Conference on Principles of Knowledge Representation and Reasoning (KR 2010)"
doi_url: "https://dl.acm.org/doi/10.5555/3031843.3031847"
---

# Abstract Dialectical Frameworks

## One-Sentence Summary
Introduces Abstract Dialectical Frameworks (ADFs), a generalization of Dung argumentation frameworks where each node has an arbitrary acceptance condition over its parents, enabling modeling of support, attack, and complex dependency types within a single framework.

## Problem Addressed
Dung's argumentation frameworks only support a single type of relationship between arguments: attack. Real argumentation often involves support, complex dependencies (e.g., joint attack, evidential support), and different types of nodes. Extensions like bipolar AFs (Cayrol and Lagasquie-Schiex 2005) added support but in limited ways. ADFs provide a uniform generalization where acceptance conditions on nodes can express arbitrary Boolean dependencies. *(p.0)*

## Key Contributions
- Definition of Abstract Dialectical Frameworks (ADFs) with per-node acceptance conditions *(p.0)*
- Generalization of Dung's grounded semantics to ADFs, and preferred and stable semantics to bipolar ADFs; complete semantics is not defined in this paper. *(pp.1, 4-6; [semantics image](pngs/page-006.png))*
- Identification of bipolar ADFs (BADFs) as the subclass where stable and preferred semantics generalize cleanly *(p.1)*
- Representation of acceptance conditions via weights and priorities on links *(p.6)*
- Modeling of five legal proof standards: scintilla of evidence, preponderance of evidence, dialectical validity, beyond reasonable doubt, and beyond doubt. *(p.7; [page image](pngs/page-007.png))*
- Connections to logic programming: ADFs subsume normal logic programs *(p.5)*
- Complexity analysis of ADF reasoning *(p.7)*

## Methodology
The paper defines ADFs as triples D = (S, L, C), then lifts Dung's semantics by defining a consensus operator on three-valued interpretations. It proves that Dung AFs are a special case, shows which properties carry over, identifies the bipolar subclass needed for stable/preferred semantics, and demonstrates practical expressiveness through weighted ADFs and legal proof standard examples. *(p.0-9)*

## Key Equations

### ADF Definition

An ADF is a triple $D = (S, L, C)$ where:
- $S$ is a set of statements (nodes/positions)
- $L \subseteq S \times S$ is a set of links
- $C = \{C_s\}_{s \in S}$ is a set of acceptance conditions, one per statement
Where $C_s$ is a propositional formula over $par(s) = \{b \mid (b,s) \in L\}$
*(p.1)*

### Dung AF as Special Case

For a Dung AF with attackers $a_1, \ldots, a_n$ of node $s$:

$$
C_s = \neg a_1 \wedge \neg a_2 \wedge \cdots \wedge \neg a_n
$$

If $s$ has no attackers: $C_s = \top$
*(p.1)*

### Three-Valued Interpretations

A three-valued interpretation $v: S \to \{t, f, u\}$ partitions $S$ into $(v^t, v^f, v^u)$ — the true, false, and undecided statements. Information ordering: $u <_i t$ and $u <_i f$. *(p.2)*

### Consensus Operator

$$
\Gamma_D(v)(s) = \begin{cases} t & \text{if } C_s[p/v] \text{ is irrefutable (true under all completions of } v \text{)} \\ f & \text{if } C_s[p/v] \text{ is unsatisfiable (false under all completions of } v \text{)} \\ u & \text{otherwise} \end{cases}
$$

Where $C_s[p/v]$ means: replace each parent $p$ of $s$ that has value $t$ by $\top$, value $f$ by $\bot$, and leave undecided parents as propositional variables. Then check if the resulting formula is a tautology (irrefutable), unsatisfiable, or contingent. *(p.2)*

### Grounded Interpretation

$$
\text{grd}(D) = \text{lfp}(\Gamma_D)
$$

The grounded interpretation is the least fixpoint of $\Gamma_D$, starting from the all-undecided interpretation $v_u$ where $v_u(s) = u$ for all $s$. *(p.2-3)*

### Stable Model via Reduced ADF

For a model $M\subseteq S$ of a **bipolar** ADF $D$, the reduced ADF $D^M$ is obtained by:
1. Eliminating all nodes outside $M$ and all incident links.
2. Eliminating **all attacking links**.
3. Restricting each remaining acceptance condition to its remaining parents.

$M$ is stable iff it is the **least model** of $D^M$. The reduct has only supporting links, so Proposition 5 guarantees its least model. This is the original 2010 definition, which differs from the false-atom substitution/grounded reduct introduced in 2013. *(Definition 6, p.4; [page image](pngs/page-004.png))*

### Weighted ADF Acceptance

One numerical acceptance condition proposed for weighted ADFs is:

$$
C_s(R)=\mathit{in}\ \text{iff}\ \sum_{r\in R}w(r,s)>0
$$

The paper also proposes comparing the strongest positive and negative weights, or requiring their magnitude difference to exceed a threshold. Numerical sum thresholds are examples, not the definition of every weighted ADF. Qualitative weights distinguish valid, strong, credible, and weak pro/con links. *(pp.6-7; [page image](pngs/page-007.png))*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Acceptance condition | $C_s$ | - | - | Any propositional formula over par(s) | 1 | One per node |
| Link weight | $w_i$ | - | - | $\mathbb{R}$ (positive=support, negative=attack) | 6 | For weighted ADFs |
| Qualitative link strengths | $v,s,c,w$ | - | - | valid, strong, credible, weak | 7 | Positive and negative versions encode pro/con links |
| Numerical margin threshold | - | - | - | application-specific | 7 | Optional comparison of strongest positive and negative magnitudes |
| Preponderance of evidence | - | - | - | qualitative condition | 7 | Some pro link, no valid con link, and every remaining con strength strictly outweighed |
| Beyond reasonable doubt | - | - | - | qualitative condition | 7 | Some valid/strong pro link and no accepted con link |

## Implementation Details

### Data Structures
- ADF: triple (S, L, C) where S is set of nodes, L is set of directed edges, C maps each node to a propositional formula over its parents *(p.1)*
- Three-valued interpretation: mapping from S to {t, f, u} *(p.2)*
- Can represent acceptance conditions as: (a) explicit propositional formulas, (b) truth tables (completely defined Boolean functions), or (c) weighted sums with thresholds *(p.1, 6)*

### Grounded Model Computation
1. Start with $v_0 = v_u$ (all undecided)
2. Apply $\Gamma_D$ iteratively: $v_{i+1} = \Gamma_D(v_i)$
3. Stop when $v_{i+1} = v_i$ (fixpoint reached)
4. The fixpoint is the grounded interpretation
*(p.2-3)*

### Stable Model Check
1. Given candidate model $M$ of a bipolar ADF, remove nodes outside $M$ and their incident links.
2. Remove all attacking links and restrict remaining acceptance conditions to remaining parents.
3. Compute the least model of this supporting-only reduct by iterating its monotone immediate-consequence operator from $\emptyset$.
4. $M$ is stable iff it equals that least model.
*(Definitions 5-6 and Proposition 5, p.4; [page image](pngs/page-004.png))*

### Bipolar ADF Classification
- A link $(a,b)$ is **supporting** iff there is no $R\subseteq par(b)$ with $C_b(R)=\mathit{in}$ and $C_b(R\cup\{a\})=\mathit{out}$: adding $a$ cannot turn acceptance into rejection. *(Definition 5, p.4; [page image](pngs/page-004.png))*
- A link $(a,b)$ is **attacking** if: flipping $a$ from false to true can only hurt acceptance *(p.4)*
- An ADF is **bipolar** (BADF) if every link is supporting or attacking; a redundant link may satisfy both definitions and has no influence. *(p.4)*
- Dung AFs are bipolar (all links are attacking) *(p.4)*

### Reduction from ADF to Bipolar ADF
- Every ADF $D=(S,L,C)$ can be transformed into a BADF $D'$ by adding nodes representing subsets of $S$.
- A subset node accepts exactly its represented assignment, using supporting links from members and attacking links from nonmembers; ordinary nodes are supported by subset nodes satisfying their original conditions.
- Each model of $D$ is contained in a model of $D'$, and each model of $D'$ projects to a model of $D$ by intersection with $S$. This is a model-preserving ADF-to-BADF construction, not a translation to a Dung AF, and can be exponential. *(p.5; [page image](pngs/page-005.png))*

## Figures of Interest
- **Example 1 (p.2):** Six-node legal ADF $\{l,w,s,k,m,i\}$: witness/liar evidence supports self-defense, killer and self-defense determine murderer, and innocence holds unless murder holds. *([page image](pngs/page-002.png))*
- **Example 4 (p.4):** Exclusive-or acceptance of $c$ from $a,b$ makes both links neither supporting nor attacking. *([page image](pngs/page-004.png))*
- **Example 5 (p.5):** $a$ and $b$ support each other and $b$ attacks $c$; the models are $\{a,b\}$ and $\{c\}$, but only $\{c\}$ is stable. *([page image](pngs/page-005.png))*
- **Weighted version of Example 1 (p.6):** The same six-node graph is annotated with positive/negative link types. The five proof-standard definitions appear as text on p.7. *([graph image](pngs/page-006.png), [standards image](pngs/page-007.png))*

## Results Summary
- Dung AFs are a special case of ADFs where all acceptance conditions are conjunctions of negated attackers *(p.1)*
- Grounded (called well-founded) semantics generalizes to all ADFs. This paper does not define complete semantics. *(pp.2-3)*
- Preferred and stable semantics require restriction to bipolar ADFs (BADFs) for clean generalization *(p.3-5)*
- Every finite BADF has a preferred model (Proposition 10); stable models need not exist. Example 2's mixed attack/support cycle has no model at all. Well-founded is the paper's terminology for its generalization of grounded semantics. *([Example 2](pngs/page-002.png), [Proposition 10](pngs/page-006.png))*
- Normal logic programs have a bipolar representation with extra rule-name nodes $N$: a program stable model $M$ maps to $M\cup N[M]$, and an ADF stable model projects back by removing $N$. The direct atom-only representation need not be bipolar. *(Proposition 8, p.5; [page image](pngs/page-005.png))*
- Weighted ADFs provide a practical representation of acceptance conditions using numerical weights *(p.6-7)*
- For BADFs with known supporting/attacking links: well-founded model checking is polynomial; stable credulous/skeptical acceptance is NP-complete/coNP-complete; preferred credulous/skeptical acceptance is NP-complete/$\Pi_2^P$-complete. For arbitrary ADFs, well-founded model checking and bipolarity recognition are coNP-hard. *(Propositions 13-17, pp.7-8; [page 7](pngs/page-007.png), [page 8](pngs/page-008.png))*

## Limitations
- Stable and preferred semantics do not generalize cleanly beyond bipolar ADFs — the paper acknowledges this restriction is needed but limits expressiveness *(p.3-4)*
- With link types known, the listed BADF acceptance tasks retain their Dung complexity. Arbitrary ADF well-founded checking is already coNP-hard. *(pp.7-8)*
- The paper is an initial proposal; many details (algorithms, implementations) are left to future work *(p.8)*
- Weight-based standards include qualitative comparisons and several numerical policies; they can be compiled to Boolean acceptance conditions and do not enlarge the ADF formalism. *(p.7)*
- The general ADF-to-BADF model-preserving translation may introduce exponentially many subset nodes. *(p.5)*

## Arguments Against Prior Work
- Dung AFs are too restrictive: only one link type (attack), so support, joint attack, and other dependencies cannot be directly modeled *(p.0)*
- Bipolar AFs (Cayrol & Lagasquie-Schiex 2005) add support but in a limited, ad-hoc way — they don't allow arbitrary acceptance conditions *(p.0, 8)*
- Oren and Norman (2008) require evidential support ultimately grounded in an environment argument; ADF acceptance conditions allow a wider range of support and weight policies. *(p.9)*
- Dunne et al. (2009) use attack weights for inconsistency handling, whereas this paper uses link weights to determine acceptance conditions. *(p.9)*

## Design Rationale
- Acceptance conditions are placed on nodes rather than links because the same link may be supporting in some contexts and attacking in others — the node's condition determines the aggregate effect *(p.1)*
- Three-valued semantics (t/f/u) chosen because undecided status is essential for grounded semantics and cautious reasoning *(p.2)*
- Bipolar restriction for stable/preferred semantics is motivated by the observation that without it, the reduced ADF construction doesn't preserve the intended relationship between models *(p.3-4)*
- Weighted ADFs bridge theory and practice: weights are intuitive for users (especially in legal domains) while acceptance conditions provide formal precision *(p.6-7)*

## Testable Properties
- For any Dung AF translated to ADF, the grounded extension of the Dung AF must equal the grounded interpretation of the ADF *(p.2)*
- For a BADF, every stable model must also be a preferred model *(p.4)*
- Every finite BADF has at least one preferred model. *(Proposition 10, p.6)*
- The well-founded accepted set is contained in every two-valued model. *(Proposition 2, p.3)*
- A weighted acceptance condition must follow its selected proof standard; a sum threshold alone does not define all weighted ADFs. *(p.7)*
- For Dung AFs viewed as ADFs: stable extensions of the Dung AF = stable models of the corresponding ADF *(p.2)*
- If an ADF has no links (all conditions are $\top$ or $\bot$), grounded model assigns t to nodes with $C_s = \top$ and f to nodes with $C_s = \bot$ *(p.2)*
- A constant-$\top$ node belongs to every model (and therefore every stable model). This paper does not establish the corresponding assertion for every preferred model; its original admissibility is defined through deletion. *(Definition 2 and Definition 7)*
- In the rule-node translation, stable models correspond after adding applicable rule names in the forward direction and projecting them away in the reverse direction. *(Proposition 8, p.5)*

## Relevance to Project
ADFs are directly relevant to propstore's argumentation layer. Where Dung AFs only model attack between arguments, ADFs allow modeling support relationships, evidential dependencies, and complex acceptance conditions. This is critical for:
- Modeling claims that support other claims (not just attack)
- Representing complex defeat conditions (e.g., a claim is defeated only if BOTH of two counterarguments hold)
- Weighted acceptance conditions map to confidence/strength-based reasoning
- Legal proof standards can be represented as explicit acceptance policies; the paper's five qualitative standards are not all numerical threshold parameters
- The bipolar subclass (BADFs) may be sufficient for most propstore use cases while keeping computational properties manageable

## Open Questions
- [ ] Can the BADF restriction be relaxed for propstore's use cases, or are all relevant links bipolar?
- [ ] How do ADFs interact with ASPIC+ structured argumentation?
- [ ] What is the practical algorithm for computing preferred extensions of BADFs?
- [ ] How do weighted ADFs relate to probabilistic argumentation frameworks (Hunter 2017, Li 2011)?
- [ ] Later work (Brewka et al. 2013) extended ADFs significantly — should that be read next?

## Cross-References (in this repo)

### Cites
- [[Dung_1995_AcceptabilityArguments]] — The foundational AF paper that ADFs generalize
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — Bipolar AFs, the most direct predecessor; ADFs subsume BAFs
- [[Bench-Capon_2003_PersuasionPracticalArgumentValue-based]] — Value-based AFs; cited for preference-based extensions
- [[Caminada_2006_IssueReinstatementArgumentation]] — Semi-stable semantics; cited for alternative semantics
- [[Simari_1992_MathematicalTreatmentDefeasibleReasoning]] — Defeasible reasoning; cited for specificity-based preferences
- [[Vreeswijk_1997_AbstractArgumentationSystems]] — Abstract argumentation systems; cited as prior generalization attempt
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — ASPIC+; cited for structured argumentation

### Cited by
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — Discusses how ADFs with Boolean conditions relate to equational approach (Section 2.2)
- [[Thimm_2012_ProbabilisticSemanticsAbstractArgumentation]] — Cites the 2013 revisited version in context of probabilistic semantics
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — References probabilistic ADFs (Polberg & Doder 2014)
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — Mentions ADFs as a generalization
- [[Čyras_2021_ArgumentativeXAISurvey]] — Directly cites Brewka & Woltran 2010
- [[Charwat_2015_MethodsSolvingReasoningProblems]] — Cites the 2013 revisited version for solving methods
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — Cites ADF semantics work
- [[Tang_2025_EncodingArgumentationFrameworksPropositional]] — Cites ADF encoding work
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — References ADF revision work

## Related Work Worth Reading
- Brewka, Ellmauthaler, Strass, Wallner, Woltran (2013) — "Abstract Dialectical Frameworks Revisited" — IJCAI conference follow-up correcting and generalizing the semantics → NOW IN COLLECTION: [[Brewka_2013_AbstractDialecticalFrameworksRevisited]]
- Strass (2013) — Approximating operators and semantics for ADFs
- Cayrol and Lagasquie-Schiex (2005) — On the acceptability of arguments in bipolar argumentation frameworks (the bipolar AF paper ADFs generalize)
- Pollock (2005) — Followed ADF-like approach with multiple link types before ADFs formalized it
- Dung (1995) — The foundational AF paper that ADFs generalize
- Prakken (2005) — On relating Dung frameworks to rule-based argumentation
- Fazzinga, Flesca, and Furfaro (2016) — Probabilistic extension of ADFs
- Later complexity work can be consulted separately; a 2011 paper cannot be a citation in this 2010 paper.

## Collection Cross-References

### Now in Collection (previously listed as leads)
- [[Brewka_2013_AbstractDialecticalFrameworksRevisited]] — Repairs the original paper's restricted preferred/stable semantics by defining three-valued semantics for arbitrary ADFs, adds static and dynamic preference handling, and sketches the DIAMOND ASP implementation.
