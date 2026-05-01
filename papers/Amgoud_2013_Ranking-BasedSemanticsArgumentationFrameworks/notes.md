---
title: "Ranking-Based Semantics for Argumentation Frameworks"
authors: "Leila Amgoud, Jonathan Ben-Naim"
year: 2013
venue: "7th International Conference on Scalable Uncertainty Management (SUM 2013), Lecture Notes in Computer Science vol 8078"
doi_url: "https://doi.org/10.1007/978-3-642-40381-1_11"
---

# Ranking-Based Semantics for Argumentation Frameworks

## One-Sentence Summary
Proposes an axiomatic framework of postulates for ranking-based (gradual) argumentation semantics that rank-order arguments from most acceptable to weakest, and constructs two concrete semantics (Discussion-based and Burden-based) satisfying those postulates.

## Problem Addressed
Extension-based semantics (grounded, preferred, stable, complete from Dung 1995) partition arguments into only two or three classes (accepted/rejected, or accepted/rejected/undecided). This is too coarse for applications like decision-making where one needs a fine-grained ranking of all arguments by acceptability. Additionally, existing extension-based semantics rest on the killing principle (an attack is sufficient to kill an argument), absoluteness (arguments are either accepted or not), and fairness (all accepted arguments have the same level of acceptability) --- all of which are debatable in many application contexts. *(p.1-2)*

## Key Contributions
- Defines **ranking-based semantics** as a new family that outputs a total preorder (ranking) over arguments, providing gradual acceptability rather than binary in/out *(p.2)*
- Proposes **eight postulates** (axioms) that any reasonable ranking-based semantics should satisfy, grounded in four considerations: weakening, counting, quality, and cardinality of attackers *(p.2)*
- Proves **compatibility and incompatibility** results between postulates *(p.9)*
- Constructs two concrete ranking-based semantics: **Discussion-based (Dbs)** and **Burden-based (Bbs)** *(p.9-11)*
- Proves which postulates each semantics satisfies and which it violates *(p.10-11)*
- Shows that Bbs refines Dung's extension-based semantics (ranking within extensions) while Dbs may return different results *(p.12)*

## Methodology
The paper follows an axiomatic methodology: first define formal postulates capturing desirable properties, then construct semantics and verify which postulates they satisfy. This mirrors the approach of Baroni & Giacomin (2007) for extension-based semantics but adapted to ranking-based outputs. *(p.2-3)*

## Formal Definitions

### Argumentation Framework (Definition 1)
An argumentation framework is an ordered pair $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$ where $\mathcal{A}$ is a finite set of arguments and $\mathcal{R}$ is a binary relation on $\mathcal{A}$ (i.e., $\mathcal{R} \subseteq \mathcal{A} \times \mathcal{A}$). $(a, b) \in \mathcal{R}$ means $a$ attacks $b$. *(p.3)*

### Key Notation
- $\text{Att}(\mathcal{A}) = \{a \in \mathcal{A} \mid \exists b, (b, a) \in \mathcal{R}\}$: set of attacked arguments *(p.3)*
- $\text{Arg}(a) = \{b \mid (b, a) \in \mathcal{R}\}$: direct attackers of $a$ *(p.3)*
- $\text{Def}_i(a)$: defenders of $a$ at depth $i$ --- all defenders of $a$ in $\mathcal{A}$ *(p.5)*

### Ranking (Definition 2)
A ranking on $\mathcal{A}$ is a binary relation $\succeq$ on $\mathcal{A}$ such that:
- $\forall a, b \in \mathcal{A}$: $a \succeq b$ or $b \succeq a$ (totality)
- $\forall a, b, c \in \mathcal{A}$: if $a \succeq b$ and $b \succeq c$ then $a \succeq c$ (transitivity)

Where $a \succeq b$ means $a$ is at least as acceptable as $b$. Strict part: $a \succ b$ iff $a \succeq b$ and $b \not\succeq a$. Equal part: $a \simeq b$ iff $a \succeq b$ and $b \succeq a$. *(p.3)*

### Ranking-Based Semantics (Definition 3)
A ranking-based semantics is a function $\mathbf{S}$ that transforms any argumentation framework $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$ into a ranking on $\mathcal{A}$. *(p.3)*

## Key Equations

### Discussion Count (Definition 10)

$$
\text{Dis}_{\mathbf{A}i}(a) = \begin{cases} -N & \text{if } i \text{ is odd} \\ N & \text{if } i \text{ is even} \end{cases}
$$

Where $N$ is the number of linear discussions for $a$ in $\mathbf{A}$ of length $i$.
*(p.10)*

### Discussion-Based Semantics (Definition 11)
Dbs transforms any $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$ into ranking $\text{Dbs}(\mathbf{A})$ on $\mathcal{A}$ such that $\forall a, b \in \mathcal{A}$, $\langle a, b \rangle \in \text{Dbs}(\mathbf{A})$ iff one of:
- $\forall i \in \{1, 2, \ldots\}$, $\text{Dis}_i(a) = \text{Dis}_i(b)$
- $\exists i \in \{1, 2, \ldots\}$, $\text{Dis}_i(a) < \text{Dis}_i(b)$ and $\forall j \in \{1, 2, \ldots, i-1\}$, $\text{Dis}_j(a) = \text{Dis}_j(b)$

Lexicographic comparison of won and lost linear discussions. *(p.10)*

### Linear Discussion (Definition 9)
A linear discussion for $a$ in $\mathbf{A}$ is a sequence $a_0, \ldots, a_n$ of elements of $\mathcal{A}$ where $n$ is a positive integer such that $a_0 = a$ and $\forall i \in \{1, \ldots, n\}$, $a_i \mathcal{R} a_{i-1}$. The length of a linear discussion is $n$. A linear discussion is won if $n$ is odd (ends with defender), lost if $n$ is even (ends with attacker). *(p.9)*

### Burden Number (Definition 12)

$$
\text{Bur}_{\mathbf{A}i}(a) = \begin{cases} 1 & \text{if } i = 0 \\ 1 + \sum_{b \in \text{Arg}(a)} \text{Bur}_{\mathbf{A}(i-1)}(b) & \text{if } i > 0 \end{cases}
$$

By convention, if $\text{Att}(a) = \emptyset$ then $\sum_{b \in \text{Arg}(a)} \text{Bur}_{\mathbf{A}(i-1)}(b) = 0$.
*(p.11)*

### Burden-Based Semantics (Definition 13)
Bbs transforms any $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$ into ranking $\text{Bbs}(\mathbf{A})$ on $\mathcal{A}$ such that $\forall a, b \in \mathcal{A}$, $\langle a, b \rangle \in \text{Bbs}(\mathbf{A})$ iff one of:
- $\forall i \in \{0, 1, \ldots\}$, $\text{Bur}_i(a) = \text{Bur}_i(b)$
- $\exists i \in \{0, 1, \ldots\}$, $\text{Bur}_i(a) = \text{Bur}_i(b)$ and $\forall j \in \{0, 1, \ldots, i-1\}$, $\text{Bur}_j(a) = \text{Bur}_j(b)$

Lexicographic comparison of burden numbers at each step. *(p.11)*

## Postulates

### Postulate 1: Abstraction (Ab)
A ranking-based semantics $\mathbf{S}$ satisfies **abstraction** iff for any two argumentation frameworks $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$ and $\mathbf{A}' = \langle \mathcal{A}', \mathcal{R}' \rangle$, for any isomorphism $f$ from $\mathbf{A}$ to $\mathbf{A}'$, then $\forall a, b \in \mathcal{A}$: $\langle a, b \rangle \in \mathbf{S}(\mathbf{A})$ iff $\langle f(a), f(b) \rangle \in \mathbf{S}(\mathbf{A}')$. The ranking should not depend on the identity of arguments. *(p.3-4)*

### Postulate 2: Independence (In)
For every argumentation framework $\mathbf{A}$: $\forall a, b \in \text{Con}(\mathcal{A})$, $\forall a, b \in \text{Arg}(\mathcal{B})$, $\langle a, b \rangle \in \mathbf{S}(\mathbf{A})$ iff $\langle a, b \rangle \in \mathbf{S}(\mathbf{B})$.
Ranking within a weakly connected component is independent of arguments in other components. *(p.4)*

### Postulate 3: Void Precedence (VP)
For every argumentation framework $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$: $\forall a \in \mathcal{A}$, if $a \notin \text{Att}(\mathcal{A})$ then $\forall b \in \text{Att}(\mathcal{A})$, $a \succ b$. A non-attacked argument is strictly more acceptable than any attacked argument. *(p.4-5)*

### Postulate 4: Defense Precedence (DP)
For every argumentation framework: if the defense of $a$ is in $\mathcal{A}$ (i.e., $\forall b, (b,a) \in \mathcal{R} \Rightarrow \exists c, (c,b) \in \mathcal{R}$), then $\forall b \in \mathcal{A}$ s.t. $\text{Def}_1(b) = \emptyset$ and $|\text{Def}_0(a)| = |\text{Def}_0(b)|$, it holds that $a \succ b$. An argument whose attackers are themselves attacked (defended) should be ranked higher than one whose attackers are not attacked, given the same number of direct attackers. *(p.5)*

### Postulate 5: Counter-Transitivity (CT)
For every argumentation framework $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$: $\forall a, b \in \mathcal{A}$, if $\exists f: \text{Arg}(b) \to \text{Arg}(a)$ injective such that $\forall x \in \text{Arg}(b)$, $f(x) \succeq x$, then $a \succeq b$. If $a$'s attackers are at least as numerous and each mapped attacker is at least as acceptable, then $a$ is at least as acceptable as $b$. *(p.6)*

### Definition 7: Strict Group Comparisons (SGC)
For all $a, b \in \mathcal{A}$: $\langle \mathcal{A}, \mathcal{D} \rangle \models \text{Sgc}(z)$ if there exists an injective function $f$ from $B$ to $A$ that meets two conditions:
- $\forall x \in B$, $f(x) \succeq x$
- $|B| < |A|$ or $\exists x \in B, f(x) \succ x$

Essentially, $A$'s elements are strictly better than $B$'s from a global point of view based on both cardinality and acceptability. *(p.6)*

### Postulate 6: Strict Counter-Transitivity (SCT)
$\forall a, b \in \mathcal{A}$: if $\text{Sgc}(\text{Arg}(b), \text{Arg}(a))$, then $a \succ b$. *(p.6)*

### Postulate 7: Cardinality Precedence (CP)
For every argumentation framework $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$: $\forall a, b \in \mathcal{A}$ such that $\forall c \in \text{Att}(\mathcal{A})$, then $\langle a, b \rangle \in \mathbf{S}(\mathcal{A})$ iff $|\text{Arg}(a)| \leq |\text{Arg}(b)|$. When all attackers are non-attacked, cardinality alone determines ranking. *(p.8)*

### Postulate 8: Quality Precedence (QP)
For every argumentation framework $\mathbf{A} = \langle \mathcal{A}, \mathcal{R} \rangle$: $\forall a, b \in \mathcal{A}$ such that $\exists c \in \text{Att}(\mathcal{A})$ with $|\text{Att}(a)| = |\text{Att}(b)|$ and the defense conditions differ, then quality of defense matters. *(p.8)*

### Postulate 9: Distributed Defense Precedence (DDP)
If the defense of $a$ is simple and distributed and the defense of $b$ is simple but not distributed, then $a \succ b$. Distributed defense (each attacker attacked by exactly one distinct defender) is preferable to concentrated defense. *(p.8)*

### Simple and Distributed Defense (Definition 8)
- The defense of $a$ is **simple** if every defender of $a$ attacks exactly one attacker of $a$
- The defense of $a$ is **distributed** if every attacker of $a$ is attacked by at most one defender

*(p.8)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Discussion length threshold | $t$ | - | longest elementary cycle | $\geq$ longest cycle | p.10 | Conjecture: equality threshold dependent on longest elementary cycle in framework |
| Burden step | $i$ | - | - | $\{0, 1, 2, \ldots\}$ | p.11 | Iteration step for burden number computation |

## Implementation Details
- **Data structures**: Argumentation framework as directed graph $(\mathcal{A}, \mathcal{R})$. For Dbs: enumerate all linear discussions (paths in the attack graph). For Bbs: iterative computation of burden numbers at each step. *(p.9-11)*
- **Dbs computation**: For each argument, count linear discussions of each length. Discussions of odd length are "won" (count negatively), even length are "lost" (count positively). Rank arguments by lexicographic comparison of these counts starting from length 1. *(p.9-10)*
- **Bbs computation**: Initialize all burden numbers to 1. At each step $i$, each argument's burden = $1 + \sum$ (burden of attackers at step $i-1$). Rank by lexicographic comparison of burden sequences. *(p.11)*
- **Convergence for Dbs**: In acyclic frameworks, linear discussions are finite and the semantics is well-defined. With cycles, $\text{Dis}_i(a)$ may never stop evolving. Authors conjecture a threshold $t$ (dependent on longest elementary cycle) beyond which counts stabilize. Computation can be truncated at step $t$; the greater $t$, the closer to the true ranking. *(p.10)*
- **Convergence for Bbs**: Similarly, an equality-ensuring threshold probably exists, making exact computation possible despite the infinite sequence $\{0, 1, \ldots\}$. *(p.11)*
- **Cycle handling**: Both Dbs and Bbs treat odd and even length cycles similarly. They "unroll" cycles --- the semantics do not distinguish between a loop ($a\mathcal{R}a$) and a cycle ($a\mathcal{R}b, b\mathcal{R}a$). *(p.12)*

## Figures of Interest
- **Fig p.4**: Two isomorphic argumentation frameworks illustrating the Abstraction postulate (Postulate 1)
- **Fig p.5**: Argumentation framework for Example 2 (grounded extension) showing Independence postulate
- **Fig p.5**: Framework showing Defense Precedence with defenders
- **Fig p.8**: Framework for Example 5 illustrating Distributed Defense Precedence
- **Fig p.13**: Weighted attack framework from related work comparison

## Postulate Satisfaction Results

| Postulate | Dbs | Bbs |
|-----------|-----|-----|
| Ab (Abstraction) | Yes | Yes |
| In (Independence) | Yes | Yes |
| CT (Counter-Transitivity) | Yes | Yes |
| SCT (Strict Counter-Transitivity) | Yes | Yes |
| CP (Cardinality Precedence) | Yes | Yes |
| VP (Void Precedence) | Yes (corollary) | Yes (corollary) |
| DP (Defense Precedence) | Yes (corollary) | Yes (corollary) |
| DDP (Distributed Defense Precedence) | No | Yes |

*(p.10-12)*

**Key difference**: Bbs satisfies DDP while Dbs does not. This means the two semantics can return very different rankings on the same framework. *(p.12)*

## Compatibility Results

**Proposition 2**: If $\mathbf{S}$ satisfies SCT, then it satisfies CT. If $\mathbf{S}$ satisfies CT and SCT, then it satisfies VP and DP. *(p.6, 9)*

**Proposition 3**: No ranking-based semantics can satisfy both DP' (a strengthened version) and QP' (a strengthened quality precedence). *(p.9)*

**Proposition 4**: The postulates Ab, In, CT, SCT, CP, and DDP are compatible. *(p.9)*

## Results Summary
- Dbs gives precedence to the number/quality of discussions (argument chains), comparing lexicographically by discussion length *(p.10)*
- Bbs gives precedence to cardinality of attackers over their quality, following a burden-accumulation model *(p.11-12)*
- Bbs refines Dung's extension-based semantics: accepted arguments rank above undecided, which rank above rejected. Dbs may differ. *(p.12)*
- Both semantics treat the structure obtained by "unrolling" cycles, not distinguishing loops from mutual attacks *(p.12)*

## Limitations
- Neither Dbs nor Bbs takes into account possible dependencies between an argument and its attackers, nor dependencies between two attackers *(p.11)*
- Cycle handling is simplistic: both semantics do not distinguish between a self-attacking argument and a mutual attack cycle *(p.12)*
- Convergence thresholds for cyclic frameworks are only conjectured, not proven *(p.10-11)*
- The approach does not handle weighted attacks (though authors note it could be extended) *(p.13)*
- Only 8 references cited; the related work discussion is brief *(p.13)*

## Arguments Against Prior Work
- Extension-based semantics (Dung 1995) are criticized for coarseness: only two or three equivalence classes of arguments, which is insufficient for decision-making *(p.1-2)*
- The killing principle (one successful attack kills an argument) is argued to be too strong for applications like decision-making where an attack only weakens *(p.1-2)*
- Absoluteness (all accepted arguments have equal acceptability) is identified as debatable *(p.1)*
- Fairness (equal treatment of all accepted arguments) is questioned *(p.1)*
- Cayrol & Lagasquie-Schiex (2005) graduality approach is contrasted: their approach extends existing extension-based semantics by considering weighted attacks, while Amgoud & Ben-Naim introduce a fundamentally new kind of semantics *(p.13)*
- Dunne et al. (2011) weighted argument systems are noted as different because weights are inputs from the argumentation system, not derived from the attack structure *(p.13)*

## Design Rationale
- Ranking-based semantics chosen over extension-based because they provide a total preorder rather than a partition, enabling finer-grained comparison *(p.2)*
- Axiomatic approach chosen to enable principled comparison between different semantics *(p.2)*
- Postulates are designed to be individually meaningful yet compatible, allowing semantics to be evaluated against a menu of desirable properties *(p.2-3)*
- Discussion-based semantics motivated by the idea that argument strength is determined by the full chain of attackers and defenders ("unrolling" the attack graph) *(p.9)*
- Burden-based semantics motivated by iterative accumulation where burden grows with each step based on attackers' burdens *(p.11)*

## Testable Properties
- Non-attacked arguments must be ranked strictly above all attacked arguments (VP) *(p.4-5)*
- Arguments in different weakly connected components must be ranked independently (In) *(p.4)*
- If there is an injective mapping from $b$'s attackers to $a$'s attackers where each mapped attacker is at least as acceptable, then $a \succeq b$ (CT) *(p.6)*
- Strict version: if the mapping is strict (either fewer attackers or at least one strictly more acceptable), then $a \succ b$ (SCT) *(p.6)*
- When all attackers are non-attacked, the argument with fewer attackers must be ranked higher (CP) *(p.8)*
- Dbs satisfies Ab, In, CT, SCT, CP but not DDP *(p.10)*
- Bbs satisfies Ab, In, CT, SCT, CP, and DDP *(p.11-12)*
- For Bbs: accepted arguments in Dung's grounded/preferred/stable extensions rank above undecided, which rank above rejected *(p.12)*
- Burden numbers at step 0 are always 1 for all arguments *(p.11)*
- For non-attacked arguments, burden remains 1 at all steps *(p.11)*

## Relevance to Project
This paper is directly relevant to propstore's argumentation layer. Where Dung 1995 provides binary accept/reject semantics and extension computation, this paper provides the theoretical basis for **gradual/ranking-based semantics** --- computing a total ordering over arguments by acceptability. This is essential for:
1. The render layer's resolution strategies that need to compare argument strength rather than just accept/reject
2. Decision-making scenarios where the "strongest" argument matters, not just whether it's in an extension
3. Bridging between the argumentation layer and heuristic analysis layer, where embedding similarities produce graded confidence

The postulate framework provides testable correctness criteria for any ranking implementation, analogous to how AGM postulates constrain belief revision.

## Open Questions
- [ ] What is the exact convergence threshold for Dbs and Bbs in cyclic frameworks?
- [ ] Can the approach be extended to weighted attacks (authors suggest yes)?
- [ ] How do Dbs and Bbs compare to Gabbay 2012's equational semantics?
- [ ] What is the relationship between these postulates and Baroni & Giacomin 2007's principle-based evaluation?
- [ ] Can defense precedence be strengthened without losing compatibility with other postulates?

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — foundational AF definition; Amgoud & Ben-Naim propose ranking-based semantics as a finer-grained alternative to Dung's extension-based semantics
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — methodological inspiration; Baroni & Giacomin's principle-based evaluation of extension semantics is mirrored here for ranking-based semantics
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — cited for the Discussion-based semantics origin (note: the collection paper is on bipolar argumentation, a different 2005 paper by same authors)
- [[Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation]] — cited as [3] for SCC-recursiveness
- [[Amgoud_2011_NewApproachPreference-basedArgumentation]] — same first author's prior work on preference-based argumentation (cited as [1])

### New Leads (Not Yet in Collection)
- Dunne, Hunter, McBurney, Parsons & Wooldridge 2011 — "Weighted argument systems" (AIJ) — weighted argumentation where weights are externally provided rather than derived from structure → NOW IN COLLECTION: [[Dunne_2011_WeightedArgumentSystemsBasic]]
- Garcia & Simari 2004 — "Defeasible logic programming" — argumentative approach to logic programming
- Dung, Mancarella & Toni 2007 — "Computing ideal skeptical argumentation" — ideal semantics computation → NOW IN COLLECTION: [[Dung_2007_ComputingIdealScepticalArgumentation]]

### Now in Collection (previously listed as leads)
- [[Dunne_2011_WeightedArgumentSystemsBasic]] — Defines weighted argument systems where positive weights live on attacks and an inconsistency budget `β` determines which attacks may be ignored. This is the main externally weighted contrast case for Amgoud and Ben-Naim's ranking semantics, which derive orderings from graph structure rather than taking weights as input.
- [[Dung_2007_ComputingIdealScepticalArgumentation]] — Defines proof procedures for ideal sceptical semantics in abstract argumentation and ABA. It provides the ideal-semantics comparison point for ranking-based approaches that want to be more discriminating than grounded semantics while staying on the sceptical side of preferred semantics.

### Cited By (in Collection)
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — directly compares Burden-based semantics (from this paper) against 16 axiomatic properties alongside four other ranking semantics; many of the properties originate from this paper's postulates
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — cites this paper in its reference list as part of the ranking-based semantics literature
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — cites this paper; identifies dynamics in ranking-based semantics as an open area
- [[Matt_2008_Game-TheoreticMeasureArgumentStrength]] — conceptual competitor; game-theoretic argument strength is an alternative to the axiomatic ranking approach

### Conceptual Links (not citation-based)
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — **Strong.** Both papers assign graded acceptability values to arguments in Dung AFs, but via fundamentally different methods: Gabbay uses fixed-point equations over [0,1] values (continuous numerical), while Amgoud & Ben-Naim use lexicographic comparison of discussion/burden sequences (discrete ordinal). Gabbay's Eq_max corresponds to Caminada complete labellings; Amgoud's Bbs refines Dung's extensions. The two approaches represent the numerical vs. ordinal branches of gradual argumentation semantics.
- [[Matt_2008_Game-TheoreticMeasureArgumentStrength]] — **Strong.** Matt & Toni's game-theoretic semantics and Amgoud & Ben-Naim's axiomatic semantics solve the same problem (gradual argument ranking) from different foundations. Bonzon 2016 later compares both directly, finding they satisfy different subsets of properties. Matt & Toni fails CT and CP which Amgoud's semantics satisfy; Amgoud's Dbs fails DDP which Bbs satisfies.
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — **Strong.** Bonzon et al. provide the definitive comparative evaluation of five ranking semantics including both Dbs and Bbs from this paper, testing them against 16 properties (many originating here). The comparison paper is the empirical validation of this paper's axiomatic framework.

## Related Work Worth Reading
- Cayrol & Lagasquie-Schiex 2005 "Graduality in Argumentation" (JAIR) --- gradual acceptability via weighted attacks
- Baroni & Giacomin 2007 "On principle-based evaluation of extension-based argumentation semantics" (AIJ) --- principle-based evaluation framework (already in collection)
- Dunne et al. 2011 "Weighted argument systems" (AIJ) --- weighted argumentation
- Amgoud & Vesic 2011 "A new approach for preference-based argumentation frameworks" (already in collection)
- Dung, Mancarella & Toni 2007 "Computing ideal skeptical argumentation"
