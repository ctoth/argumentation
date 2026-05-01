---
title: "A Comparative Study of Ranking-based Semantics for Abstract Argumentation"
authors: "Elise Bonzon, Jerome Delobelle, Sebastien Konieczny, Nicolas Maudet"
year: 2016
venue: "Proceedings of the 30th AAAI Conference on Artificial Intelligence (AAAI-16)"
doi_url: "https://ojs.aaai.org/index.php/AAAI/article/view/10116"
---

# A Comparative Study of Ranking-based Semantics for Abstract Argumentation

## One-Sentence Summary
Provides a systematic axiomatic comparison of five ranking-based semantics for abstract argumentation frameworks, cataloguing 16 desirable properties and determining which semantics satisfy which properties. *(p.0-7)*

## Problem Addressed
Multiple ranking-based semantics for abstract argumentation have been proposed independently, each associated with some desirable properties, but no comparative study existed to take a broader perspective and systematically evaluate all semantics against all proposed properties. *(p.0)*

## Key Contributions
- Defines a comprehensive set of 16 properties (axioms) for ranking-based semantics *(p.1-3)*
- Introduces a formal framework (Social Abstract Argumentation Frameworks) to give precise semantics to some properties *(p.3)*
- Provides complete comparison of five ranking-based semantics (Categoriser, Discussion-based, Burden-based, Matt & Toni, Tuples*) against all 16 properties *(p.4-6)*
- Identifies which properties distinguish between semantics families *(p.5-6)*
- Shows that no single semantics satisfies all properties simultaneously *(p.6)*

## Methodology
The authors collect properties from the literature and introduce new ones, then formally prove or disprove each property for each of five semantics. They use a running example argumentation framework (Figure 1) with 5 arguments to illustrate behavioral differences. They introduce Social Abstract Argumentation Frameworks (SAFs) to formalize properties involving social voting on arguments. *(p.0-3)*

## Key Equations

### Categoriser Function (Besnard & Hunter 2001)

$$
Cat(a) = \frac{1}{1 + \sum_{b \in Att(a)} Cat(b)}
$$

Where: $Cat(a) = 1$ if $Att(a) = \emptyset$ (no attackers); $Att(a)$ is the set of direct attackers of $a$.
*(p.3)*

### Discussion-based Semantics (Cayrol & Lagasquie-Schiex 2005)

The discussion count of $a$ is denoted $Dbs(a)$:

$$
Dbs(a) = P(a) - N(a) + 1
$$

Where: $P(a)$ is the number of non-attacked defenders; $N(a)$ is the number of non-attacked attackers; the ranking is $a \succeq b$ iff $Dbs(a) \geq Dbs(b)$.
*(p.3)*

### Burden-based Semantics (Amgoud & Ben-Naim 2013)

$$
Burden_1(a) = 1 + |Att(a)|
$$

$$
Burden_{i+1}(a) = 1 + \sum_{b \in Att(a)} \frac{1}{Burden_i(b)}
$$

Where: iteration continues until convergence to $Burden_\infty$. The ranking is $a \succeq b$ iff $Burden_\infty(a) \leq Burden_\infty(b)$ (lower burden = more acceptable).
*(p.3-4)*

### Matt & Toni Semantics

Uses a two-person zero-sum strategic game. A proponent and opponent play over argument $a$. The proponent picks a path in the grounded game tree; the opponent plays adversarially. The strength of $a$ is computed from equilibrium strategies. *(p.4)*

### Tuples* Semantics (Cayrol & Lagasquie-Schiex 2005)

$$
v_s(a) = (v_s(a_1), v_s(a_2), \ldots)
$$

Where: $v_s(a)$ is an ordered tuple of sorted values of attackers; comparison is lexicographic. Assigns each argument a tuple representing sorted attacker values; tuples are compared lexicographically to produce a ranking.
*(p.4)*

### Social Abstract Argumentation Framework (SAF)

$$
SAF = (A, R, \nu_S)
$$

Where: $A$ = set of arguments; $R$ = attack relation; $\nu_S : A \to [-I, I]$ is a social support function mapping arguments to initial scores in $[-I, I]$ where $I$ is a totally ordered set with top $\top$ and bottom $\bot$; an argumentation function $\epsilon$ is monotonic; $w_i$ is the pro-argument and $w_\epsilon$ is for the attacked argument.
*(p.3)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Social support | $\nu_S(a)$ | - | 0 | $[-I, I]$ | 3 | Initial social vote on argument |
| Categoriser score | $Cat(a)$ | - | 1 (unattacked) | $(0, 1]$ | 3 | Decreases with more/stronger attackers |
| Discussion count | $Dbs(a)$ | - | 1 (unattacked) | $\mathbb{Z}$ | 3 | Integer; can be negative |
| Burden | $Burden_i(a)$ | - | $1 + |Att(a)|$ | $[1, \infty)$ | 3-4 | Iterative; converges to $Burden_\infty$ |

## Implementation Details
- Categoriser: recursive computation, base case Cat(a)=1 when no attackers. Handle cycles via iterative fixed-point. *(p.3)*
- Burden-based: iterative computation starting from Burden_1, converging. When cycles exist in AF, some tuples can be infinite; the method requires a topological sort approach or iterative approximation. *(p.4)*
- Tuples*: construct sorted tuples of attacker values, compare lexicographically. The method returns multiple solutions for acyclic graphs only; cycles require special handling. *(p.4)*
- Algorithm 1 (p.4): For Tuples* — input is initial values of arguments and a set S; output is a ranking between a and b via lexicographic comparison of sorted tuples.
- SAF evaluation: use the simple product semantics where $\epsilon_P(v_i, w_i, w_\epsilon) = v_i \cdot w_i / (v_i \cdot w_\epsilon)$ to compute argument scores. *(p.3)*

## Figures of Interest
- **Fig 1 (p.3):** Running example argumentation framework with 5 arguments (a,b,c,d,e). Categories: Cat(a)=0.28, Cat(b)=1, Cat(c)=0.5, Cat(d)=0.65, Cat(e)=0.53. Used throughout to compare all semantics.
- **Table 1 (p.5):** Orders obtained on Example 1 by each semantics — shows Cat and Dbs agree on this example, but Bbs, M&T, and Tup* differ.
- **Table 2 (p.5-6):** Complete property satisfaction matrix for all five semantics. The central result of the paper.

## Results Summary
- **Categoriser (Cat):** Satisfies Abs, VP+, DP, CT, SCT, CP, DDP, TAB, TDB, +AB, Ext, and Null. Does not satisfy QP or Non-attacked Equivalence. *(p.5)*
- **Discussion-based (Dbs):** Satisfies Abs, VP+, CT, SCT, CP, DDP, TAB, TDB, +AB, Ext, Ind, Null. Does not satisfy DP or QP. *(p.5)*
- **Burden-based (Bbs):** Satisfies Abs, VP, DP, CT, DDP, TAB, +DB, +AB, Ext, Ind, Null. Does not satisfy VP+, SCT, CP, QP, TDB. *(p.5)*
- **Matt & Toni (M&T):** Satisfies Abs, VP+, DP, SCT, TAB, TDB, +AB, Ext, Ind, Null. Does not satisfy CT, CP, DDP, QP. *(p.5)*
- **Tuples* (Tup*):** Very recently proposed; most properties satisfied. *(p.5-6)*
- No semantics satisfies all 16 properties. *(p.6)*
- Properties form clusters that distinguish semantics families. *(p.6)*

## Limitations
- Only considers five ranking-based semantics available at time of writing. *(p.6)*
- Some properties may conflict (cannot all be satisfied simultaneously), but the paper does not prove incompatibility results. *(p.6)*
- Does not address computational complexity of the different semantics. *(p.6)*
- Cycle handling is only briefly discussed; Tuples* explicitly restricted to acyclic graphs for full analysis. *(p.4)*
- The paper notes that the distinction between Void Precedence (VP) and its stronger form (VP+) deserves further study. *(p.6)*

## Arguments Against Prior Work
- Extension-based semantics (grounded, preferred, stable, complete) produce only a binary classification (accepted/rejected) or a limited number of levels, while ranking-based semantics provide a finer-grained total preorder. *(p.0)*
- Prior proposals of ranking-based semantics were made independently without systematic comparison, making it impossible to understand their relative merits. *(p.0)*
- The discussion-based semantics can produce counterintuitive results in some cases: it does not satisfy Distributed Precedence (DP), meaning it cannot always distinguish arguments based on how their defense is distributed. *(p.5)*

## Design Rationale
- Properties are chosen to capture intuitive requirements: an unattacked argument should rank higher (Void Precedence), self-attacking arguments should rank lowest (Self-Contradiction), more attackers should mean lower rank (Cardinality Precedence). *(p.1-2)*
- Social Abstract Argumentation Frameworks are introduced specifically to formalize properties like Copy, Non-attacked Equivalence, and related notions that require reasoning about argument similarity in context. *(p.3)*
- The axiomatic approach (defining properties independently of any specific semantics) allows principled comparison and guides design of future semantics. *(p.0)*

## Testable Properties
- Void Precedence: A non-attacked argument must be strictly higher than any attacked argument. *(p.1)*
- Self-Contradiction: A self-attacking argument is ranked no higher than any non-self-attacking argument. *(p.1)*
- Cardinality Precedence: If a has strictly fewer direct attackers than b (all non-attacked), a ranks strictly higher. *(p.1)*
- Quality Precedence: For arguments attacked by one direct attacker each, the one with the weaker attacker ranks higher. *(p.1)*
- Counter-Transitivity (CT): If a is at least as acceptable as b, then an argument attacked only by b should be at least as acceptable as one attacked only by a. *(p.2)*
- Strict Counter-Transitivity (SCT): If a is strictly more acceptable than b, then an argument attacked only by b is strictly more acceptable than one attacked only by a. *(p.2)*
- Distributed Defense Precedence (DDP): An argument with distributed defense (multiple independent defenders) should be preferred over one with concentrated defense (same number of defenders through one path). *(p.2)*

## Relevance to Project
Directly relevant to the argumentation layer. The propstore needs to compute argument acceptability rankings, not just extension membership. This paper provides the axiomatic framework for choosing which ranking semantics to implement, and the property satisfaction table guides implementation choices. The Categoriser function is particularly relevant as a simple, well-behaved baseline that satisfies many properties.

## Open Questions
- [ ] Which properties are most important for the propstore's use case?
- [ ] Can incompatibility between properties be formally proven?
- [ ] How do these semantics scale computationally on large AFs?
- [ ] How to handle cycles in Tuples* and Burden-based semantics?

## Collection Cross-References

### This paper cites (in collection)
- **Dung_1995_AcceptabilityArguments** — AF = (A, R) definition, grounded/preferred/stable/complete extensions. The formal foundation on which all ranking-based semantics operate.
- **Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation** — Principle-based evaluation of extension-based semantics. This paper is the ranking-based counterpart to Baroni 2007's extension-based analysis.
- **Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation** — Discussion-based and Tuples semantics originate from Cayrol & Lagasquie-Schiex 2005. (Note: the collection paper is on bipolar argumentation, a different 2005 paper by same authors.)
- **Gabbay_2012_EquationalApproachArgumentationNetworks** — Equational semantics for argumentation. Gabbay's Eq_inverse family is related to the Categoriser function studied here.

### This paper is cited by (in collection)
- **Hunter_2017_ProbabilisticReasoningAbstractArgumentation** — Cites a related 2016 COMMA paper by same authors on propagation-based ranking semantics.
- **Järvisalo_2025_ICCMA20235thInternational** — Cites this paper directly as [9].

### Now in Collection (previously listed as leads)
- [[Besnard_2001_Logic-basedTheoryDeductiveArguments]] — Origin of the Categoriser function, one of the five ranking semantics compared in this paper. Defines deductive arguments from classical logic with undercut-based defeat.
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — Proposes the axiomatic postulate framework (8 postulates) for ranking-based semantics and constructs Discussion-based and Burden-based semantics. Many of the 16 properties in Bonzon 2016 originate here.
- [[Matt_2008_Game-TheoreticMeasureArgumentStrength]] — Defines argument strength as the value of a two-person zero-sum game between proponent and opponent, computed via LP/simplex. One of the five ranking semantics compared; satisfies Abs, VP+, DP, SCT, TAB, TDB, +AB, Ext, Ind, Null but not CT, CP, DDP, QP.
- [[Leite_2011_SocialAbstractArgumentation]] — Defines Social Abstract Argumentation Frameworks (SAFs), where arguments receive positive and negative social votes and semantics compute graded strengths from those vote counts plus attack structure. This is the socially grounded ranking/gradual baseline in Bonzon's comparison.

### New leads (not in collection)
- **Pu, Luo, et al. 2014** — Argument ranking with categoriser function (KSEM'14).
- **Leite and Martins 2011** — Social abstract argumentation. Defines SAFs used in this paper. → NOW IN COLLECTION: [[Leite_2011_SocialAbstractArgumentation]]

## Related Work Worth Reading
- Besnard and Hunter 2001 — Categoriser function origin → NOW IN COLLECTION: [[Besnard_2001_Logic-basedTheoryDeductiveArguments]]
- Amgoud and Ben-Naim 2013 — Burden-based semantics with axiomatic properties → NOW IN COLLECTION: [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]]
- Cayrol and Lagasquie-Schiex 2005 — Discussion-based and Tuples semantics
- Matt and Toni 2008 — Game-theoretic argument strength → NOW IN COLLECTION: [[Matt_2008_Game-TheoreticMeasureArgumentStrength]]
- Pu, Luo, et al. 2014 — Argument ranking with categoriser function (KSEM'14)
- Leite and Martins 2011 — Social abstract argumentation → NOW IN COLLECTION: [[Leite_2011_SocialAbstractArgumentation]]
- Baroni 2007 — Principle-based evaluation (extension-based counterpart to this work)
