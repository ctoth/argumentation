---
title: "A Comparative Study of Ranking-based Semantics for Abstract Argumentation"
authors: "Elise Bonzon, Jerome Delobelle, Sebastien Konieczny, Nicolas Maudet"
year: 2016
venue: "Proceedings of the 30th AAAI Conference on Artificial Intelligence (AAAI-16)"
doi_url: "https://ojs.aaai.org/index.php/AAAI/article/view/10116"
---

# A Comparative Study of Ranking-based Semantics for Abstract Argumentation

> Scoped audit reread (2026-09-27): verified PDF page 2, page-001.png, for SC/CP/QP/CT/SCT/DP. Corrected definitions below; other sections remain unverified.

## One-Sentence Summary
Compares Cat, SAF, Dbs, Bbs, Tuples* and Matt-Toni ranking semantics through axiomatic properties, also including grounded semantics as a reference in Table 2. *(Table 2, `pngs/page-005.png`)*

## Problem Addressed
Multiple ranking-based semantics for abstract argumentation have been proposed independently, each associated with some desirable properties, but no comparative study existed to take a broader perspective and systematically evaluate all semantics against all proposed properties. *(p.0)*

## Key Contributions
- Defines a comprehensive set of 16 properties (axioms) for ranking-based semantics *(p.1-3)*
- Introduces a formal framework (Social Abstract Argumentation Frameworks) to give precise semantics to some properties *(p.3)*
- Compares six ranking-based semantics: Categoriser, SAF, Discussion-based, Burden-based, Matt & Toni, and Tuples*. *(Table 2, `pngs/page-005.png`)*
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

### Discussion-based Semantics (Amgoud & Ben-Naim 2013)

The discussion count is a sequence $Dis(a)=(Dis_1(a),Dis_2(a),\ldots)$:

$$
Dis_i(a)=\begin{cases}-|R_i^\pm(a)|&i\text{ odd},\\|R_i^\pm(a)|&i\text{ even}.\end{cases}
$$

The counts retain path multiplicities at every depth. Definition 14 compares the complete sequences lexicographically; it is not a scalar count of unattacked leaves. *(Definitions 13-14, `pngs/page-003.png`)*

### Burden-based Semantics (Amgoud & Ben-Naim 2013)

$$
Burden_1(a) = 1 + |Att(a)|
$$

$$
Burden_{i+1}(a) = 1 + \sum_{b \in Att(a)} \frac{1}{Burden_i(b)}
$$

The starting value is $Bur_0(a)=1$. The semantic value is the entire sequence $(Bur_0(a),Bur_1(a),\ldots)$, compared lexicographically with lower burden preferred at the first difference; comparing only its limiting value is not the definition. *(Definitions 15-16, `pngs/page-003.png`, `pngs/page-004.png`)*

### Matt & Toni Semantics

Uses a two-person zero-sum strategic game. Proponent strategies are all argument subsets containing a; opponent strategies are all argument subsets. Non-conflict-free proponent sets receive reward 0, an unchallenged conflict-free set receives 1, and other rewards use normalized attack counts. The strength is the max-min expected reward. *(Definitions 18-20 and preceding strategy sets, `pngs/page-004.png`)*

### Tuples* Semantics (Cayrol & Lagasquie-Schiex 2005)

$$
v(a)=[v_p(a),v_i(a)]
$$

Here $v_p$ is the sorted tuple of even defense-branch lengths and $v_i$ the sorted tuple of odd attack-branch lengths, with multiplicity. Algorithm 1 first compares tuple cardinalities, then uses opposite lexicographic preferences for defense and attack lengths when counts agree. The resulting ranking is partial: arguments may be incomparable. Tuples* restricts the evaluation to acyclic AFs. *(Definition 17 and Algorithm 1, `pngs/page-004.png`)*

### Social Abstract Argumentation Framework (SAF)

$$
M_S(a)=\tau(a)\curlywedge\neg\curlyvee\{M_S(b)\mid b\in R^-_1(a)\}
$$

Definition 11 uses a totally ordered valuation set L and well-behaved operators for combining initial score, aggregated attacker score and negation. For comparison in this paper, arguments receive the same initial social support. The simple product instance uses $L=[0,1]$, $\tau_\epsilon=1/(1+\epsilon)$, product conjunction, probabilistic-sum disjunction and $\neg x=1-x$. *(Definitions 11-12, `pngs/page-003.png`)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Social support | $\nu_S(a)$ | - | 0 | $[-I, I]$ | 3 | Initial social vote on argument |
| Categoriser score | $Cat(a)$ | - | 1 (unattacked) | $(0, 1]$ | 3 | Decreases with more/stronger attackers |
| Discussion count | $Dbs(a)$ | - | 1 (unattacked) | $\mathbb{Z}$ | 3 | Integer; can be negative |
| Burden | $Burden_i(a)$ | - | $1 + |Att(a)|$ | $[1, \infty)$ | 3-4 | Iterative; converges to $Burden_\infty$ |

## Implementation Details
- Categoriser: recursive computation, base case Cat(a)=1 when no attackers. Handle cycles via iterative fixed-point. *(p.3)*
- Burden-based: construct burden-number sequences from Bur_0=1 and compare lexicographically, retaining the earliest differing step. *(Definitions 15-16, `pngs/page-003.png`, `pngs/page-004.png`)*
- Tuples*: construct sorted defense/attack branch-length tuples and apply Algorithm 1's cautious partial comparison; cycles are excluded from Tuples* in this study. *(`pngs/page-004.png`)*
- Algorithm 1 (p.4): For Tuples* — input is initial values of arguments and a set S; output is a ranking between a and b via lexicographic comparison of sorted tuples.
- SAF evaluation: in the simple product semantics, multiply the common initial support $1/(1+\epsilon)$ by the complement of the probabilistic-sum aggregate of attacker scores. *(Definition 11 and following simple-product instance, `pngs/page-003.png`)*

## Figures of Interest
- **Fig 1 (p.3):** Running example argumentation framework with 5 arguments (a,b,c,d,e). Categories: Cat(a)=0.28, Cat(b)=1, Cat(c)=0.5, Cat(d)=0.65, Cat(e)=0.53. Used throughout to compare all semantics.
- **Table 1 (p.5):** Orders obtained on Example 1 by each semantics — shows Cat and Dbs agree on this example, but Bbs, M&T, and Tup* differ.
- **Table 2 (p.5-6):** Complete property satisfaction matrix for all five semantics. The central result of the paper.

## Results Summary
- **Categoriser and SAF:** satisfy Abs, In, VP, DP, CT, SCT, ↑AB, ↑DB, +AB, Tot and NaE; other listed properties are not satisfied. *(Propositions 2-3, `pngs/page-003.png`)*
- **Discussion-based:** satisfies Abs, In, VP, DP, CT, SCT, CP, ↑AB, ↑DB, +AB, Tot and NaE; notably not DDP. *(Proposition 4, `pngs/page-003.png`)*
- **Burden-based:** satisfies Abs, In, VP, DP, CT, SCT, CP, DDP, ↑AB, ↑DB, +AB, Tot and NaE. *(Proposition 5, `pngs/page-004.png`)*
- **Matt & Toni:** satisfies Abs, In, VP, +AB, SC, Tot, NaE and AvsFD; notably not DP, CT or SCT. *(Proposition 7, `pngs/page-004.png`)*
- **Tuples*:** satisfies Abs, In, VP, +DB, ↑AB, ↑DB, +AB, NaE and AvsFD; it fails totality, and SC is marked inapplicable because Tuples* excludes cycles. *(Proposition 6 and Table 2, `pngs/page-004.png`, `pngs/page-005.png`)*
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
- Discussion-based semantics satisfies Defense Precedence (DP) but not Distributed Defense Precedence (DDP); Burden-based satisfies both. *(Propositions 4-5, `pngs/page-003.png`, `pngs/page-004.png`)*

## Design Rationale
- Properties are chosen to capture intuitive requirements: an unattacked argument should rank higher (Void Precedence), self-attacking arguments should rank lowest (Self-Contradiction), more attackers should mean lower rank (Cardinality Precedence). *(p.1-2)*
- Social Abstract Argumentation Frameworks are introduced specifically to formalize properties like Copy, Non-attacked Equivalence, and related notions that require reasoning about argument similarity in context. *(p.3)*
- The axiomatic approach (defining properties independently of any specific semantics) allows principled comparison and guides design of future semantics. *(p.0)*

## Testable Properties
- Void Precedence: A non-attacked argument must be strictly higher than any attacked argument. *(p.1)*
- Self-Contradiction: A self-attacking argument is ranked strictly lower than every non-self-attacking argument; a tie violates SC. *(p.1)*
- Cardinality Precedence: If a has strictly fewer direct attackers than b, a ranks strictly higher, regardless of whether those attackers are themselves attacked and including zero attackers. *(p.1)*
- Quality Precedence: If some direct attacker of b strictly outranks every direct attacker of a, then a strictly outranks b; attacker sets need not be singletons. *(p.1)*
- Counter-Transitivity (CT): If the direct attackers of b are at least as numerous and acceptable as those of a under the injective group comparison in Definition 6, then a is at least as acceptable as b. *(p.2)*
- Strict Counter-Transitivity (SCT): If the direct attackers of b strictly dominate those of a under the strict group comparison in Definition 6, then a strictly outranks b. *(p.2)*
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
