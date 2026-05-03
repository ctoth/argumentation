---
title: "On the bipolarity in argumentation frameworks"
authors: "Leila Amgoud, Claudette Cayrol, Marie-Christine Lagasquie-Schiex"
year: 2004
venue: "10th International Workshop on Non-Monotonic Reasoning (NMR 2004), Uncertainty Frameworks subworkshop, Whistler, Canada"
doi_url: "https://hal.science/hal-03198386"
pages: 9
affiliation: "IRIT-UPS, Toulouse, France"
note: "PDF page numbering: HAL cover banner is PDF page 0; paper text begins at PDF page 1 (cited below as paper page 1)."
---

# On the bipolarity in argumentation frameworks

## One-Sentence Summary
A position-and-survey paper that introduces *bipolarity* — explicit positive (support) and negative (attack/defeat) interactions between arguments — into Dung-style abstract argumentation, sketching three layers where bipolarity matters: (1) the abstract framework structure itself (adding a support relation R_sup alongside R_def), (2) gradual valuation of arguments combining defeat-branch and support-branch contributions, and (3) selection of acceptable sets of arguments / complete plans built from desires and sub-desires. *(p.1)*

## Problem Addressed
Dung's argumentation framework uses a single binary defeat relation R that encodes only negative interactions between arguments. In real-world reasoning (knowledge-base argumentation, decision-making, multi-agent dialogue), arguments often *support* one another (positive interaction) as well as attack one another. The authors observe that bipolarity (i.e. the coexistence of positive and negative preferences/interactions, treated separately) has been useful in cognitive psychology and in decision theory and is implicit in several argumentation works, but no abstract framework captures it cleanly. The paper surveys how bipolarity surfaces at three levels of an argumentation process and proposes new abstract definitions and valuation/selection schemes that respect it. *(p.1)*

## Key Contributions
- A position paper that names *bipolarity* in argumentation frameworks and identifies three levels at which it appears: the abstract framework, the valuation of arguments, and the selection of acceptable sets. *(p.1)*
- A new **abstract bipolar argumentation framework** as a triple `<A, R_def, R_sup>` extending Dung's pair `<A, R>` with an explicit support relation. *(p.2)*
- A **graphical / branch structure** over a bipolar AF: defeat branches and support branches, with direct/indirect classifications of defeaters, defenders, supporters, and direct/indirect attackers. *(p.3, Def.4 and Def.5)*
- A **gradual (numeric) valuation** that combines defeat-branch and support-branch valuations via a compensation function and obeys local principles (P1–P3) and global principles (Pg1–Pg4). *(p.5)*
- A **selection layer** built on a desire / sub-desire / partial plan / complete plan vocabulary, with conflict and attack relations among complete plans and an axiom-based notion of acceptable set of complete plans. *(p.6–7, Def.9–Def.19)*

## Study Design (empirical papers)

*Not applicable — this is a position paper / theoretical survey with new abstract definitions, no empirical study.*

## Methodology
The paper proceeds in three layers:

1. **Recap of Dung 1995.** An argumentation framework is `<A, R>` where R ⊆ A × A is a binary defeat relation. Acceptability semantics (admissible, preferred, stable, grounded) and characteristic function F_<A,R>(S) are recalled. *(p.1–2)*

2. **Abstract bipolar AF.** Add a second binary support relation R_sup independent of R_def: `<A, R_def, R_sup>`. The support relation is *not* assumed to be reducible to defeat-of-defeaters; it is taken to be an autonomous primitive. Branches and indirect interactions are read off the bipartite graph G_b. *(p.2–3)*

3. **Bipolar valuation.** Each argument α gets a local valuation v(α) computed from a function h_R that aggregates defeat-branch valuations and a function h_R_sup that aggregates support-branch valuations, then combined by a function g (compensation between negative and positive contributions). Local principles P1–P3 fix the qualitative behavior; global principles Pg1–Pg4 fix monotonicity in numbers and quality of attackers/supporters. *(p.4–5)*

4. **Bipolar selection.** Three categories of acceptable arguments: *in favor*, *against*, *in abeyance*. Concrete scheme for desire-driven decision making: from a knowledge base K, a set of desires D, and a defeasible base D_def, build *partial plans* (h, U) and *complete plans* (h, U_1 ∪ … ∪ U_n) per Defs 9–14, define attack/conflict between plans (Defs 15–16), and propose Def.19 acceptable set of complete plans subject to three axioms. *(p.6–7)*

## Key Equations / Statistical Models

The paper is mostly definitional. The substantive numeric machinery is the local/global valuation in §"Gradual valuation":

Local valuation of an argument α with defeat-branch attackers C_1,…,C_n and support-branch supporters B_1,…,B_p:

$$
v(\alpha) \;=\; g\!\big(\, h_{R_{def}}(v(C_1),\dots,v(C_n)),\ h_{R_{sup}}(v(B_1),\dots,v(B_p)) \,\big)
$$

Where:
- v: A → V (V is a finite set of valuations, e.g. an interval [0,1] or {⊕,…,⊖}) *(p.5)*
- h_R aggregates defeat-branch values, h_R_sup aggregates support-branch values *(p.5)*
- g compensates between negative and positive contributions *(p.5)*

Concrete numeric instances suggested in footnotes for V = [-1, 1] or V = [0, 1]:

$$
\alpha = 0,\ \beta = \infty,\ g(\alpha, \alpha) = 0
$$

with the example aggregator defined elementwise:

$$
h_{def}(x_1,\dots,x_n) \;=\; \tfrac{1}{1 + \sum_i x_i^{-1}} \quad (\text{example 6 form})
$$

i.e. an "1/(1+Σ 1/x_i)" style aggregator that is monotone non-increasing in the number and strength of attackers. The compensation g and exact closed forms are sketched only by example. *(p.5–6)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument set | A | — | — | finite | 1 | All bipolar AFs are over a finite A |
| Defeat relation | R_def | — | — | ⊆ A×A | 2 | Same role as Dung's R |
| Support relation | R_sup | — | — | ⊆ A×A | 2 | New primitive in bipolar AF; independent of R_def |
| Valuation codomain | V | — | — | totally ordered finite or [0,1] or [-1,1] | 5 | Numeric or qualitative scale |
| Compensation neutral element | α | — | 0 | depends on V | 5 | g(α,α) returns the neutral |
| Compensation maximum | β | — | ∞ or 1 | depends on V | 5 | "best" valuation |
| Maximum-attack value | v_min | — | 0 | depends on V | 5 | Identifies the worst element |
| Maximum-support value | v_max | — | 1 | depends on V | 5 | Identifies the best element |

The paper does not attach concrete numeric defaults beyond the worked examples; symbol values vary by chosen scale. The above table records the named quantities.

## Effect Sizes / Key Quantitative Results

*Not applicable — no empirical results.*

## Methods & Implementation Details

- A bipolar AF is **<A, R_def, R_sup>** with R_def, R_sup ⊆ A × A independent. *(p.2, abstract bipolar AF definition)*
- The bipartite graph G_b uses two distinct edge types ("→" for defeat, dashed "⤳" for support). *(p.3, Def.4)*
- **Branch structure (Def.4):**
  - A *leaf* of the bipolar graph is a node with no incoming edges.
  - A *path* from a leaf A_t to A is a sequence A_t, A_{t-1}, …, A_0 = A in which each consecutive pair is connected by either a defeat or support edge.
  - A *defeat branch for A* is a path of length n ≥ 1 (number of edges = n) such that the **last edge** (A_1 → A_0) is a defeat edge.
  - A *support branch for A* is a path whose last edge is a support edge.
  - A branch from A is *direct* if A has only one predecessor in the bipolar graph; otherwise the branch is *indirect*. *(p.3)*
- **Defeaters/Defenders/Supporters (Def.5):**
  - Direct defeaters of A = elements of R_def^{-1}(A).
  - Direct defenders of A = elements of R_def^{-1}(R_def^{-1}(A)) (i.e. attackers of A's attackers).
  - Indirect defeaters of A = elements at odd distance ≥ 3 along an alternating attack path.
  - Indirect defenders of A = elements at even distance ≥ 2.
  - Direct supporters of A = R_sup^{-1}(A); indirect supporters = R_sup^{-1}(R_sup^{-1}(A)) (transitive closure within R_sup). *(p.4)*
- **Local principles for v (P1–P3):**
  - **P1**: The valuation of an argument is a function of (i) the valuations of its direct defeaters and (ii) the valuations of its direct supporters. *(p.5)*
  - **P2**: If the quality (the valuation) of the supporters of an argument α increases, then v(α) increases (resp. decreases for defeaters). *(p.5)*
  - **P3**: If the quantity (the number) of supporters of α increases, v(α) increases (resp. decreases for defeaters). *(p.5)*
- **Global principles for v (Pg1–Pg4):**
  - **Pg1**: v(α) is a function of the valuations of the branches in the bipolar graph leading to α. *(p.5)*
  - **Pg2**: The set of branches leading to α is partitioned into pairs, each pair containing one defeat branch and one support branch of "the same length". The defeat branch in the pair, no matter the defeat part, the defence part, the support part. *(p.5)*
  - **Pg3**: The improvement of the defence or the degradation of the defeat part of an argument leads to an increase of the value of this argument. *(p.5)*
  - **Pg4**: The improvement of the defeat part or the degradation of the support part of an argument leads to a decrease of the value of the argument. *(p.5)*
- **Defeat (resp. defence) branch supports (Def.8):**
  - A *defeat (resp. defence) branch for A* is a defeat branch (resp. defence branch) of odd (resp. even) length whose first defeat element comes from a homogeneous defeat path (i.e. one made entirely of defeat edges).
  - A *support branch for A* is a branch for A composed only of support edges and leading to A. *(p.5)*
- **Selection vocabulary for desire-driven decision-making:** *(p.6–7)*
  - **Desire (Def.9):** an open propositional formula expressing what the agent wants. (Page 6 footer footnote 12.)
  - **Sub-desire (Def.10):** if D is a desire and h is a literal of D, then "h ∧ φ_1 ∧ … ∧ φ_n → h" is a sub-desire of D. (rule whose head is a literal of the desire)
  - **Partial plan (Def.11):** a pair (h, U) with h a sub-desire literal and U a defeasible explanation supporting h.
  - **Elementary partial plan (Def.12):** a partial plan (h, U) with U a single rule whose body literals are elementary, i.e. given facts.
  - **Complete plan (Def.13):** a tuple (h, U_1 ∪ … ∪ U_n) where U_1 is a partial plan whose head is h, the U_i are elementary partial plans, and the children of (h, U_1) eventually decompose into elementary plans.
  - **Conflict between complete plans (Def.14):** S is conflicting iff for some pair of plans, their explanations together with the knowledge base derive ⊥.
  - **Attack between complete plans (Def.16):** plan p_1 = (g_1, U_1) attacks plan p_2 = (g_2, U_2) iff there exists a defeat from a rule in U_1 to a rule in U_2.
  - **Conflict-free set (Def.17):** S is conflict-free iff no two distinct plans in S attack each other (the union of their explanations is consistent with K).
  - **Unachievable desire (Def.18):** a desire D is unachievable in <D, Σ, K> iff there is no complete plan whose head is D in any conflict-free set of complete plans.
- **System for handling desires (Def.18):** a triple S = <D, Σ, K> where D is the set of desires, Σ is the set of defeasible rules, K is the set of formulas. *(p.7)*
- **Axioms on the acceptable set (S of complete plans) (p.7):**
  1. The acceptable set(s) of complete plans contain the *good plans* used to achieve the corresponding desires.
  2. The class of *rejected* complete plans is the set of *self-attacked plans*.
  3. The class of complete plans *in abeyance* gathers complete plans that neither belong to (1) nor to (2).
- **Acceptable set (Def.19):** Let <D, Att, ⊆> be a SMD and S ⊆ G. S is an *acceptable set of complete plans* iff (i) S is conflict-free; and (ii) S is maximal (for set inclusion). *(p.7)*

## Figures of Interest
- **Example 4 figure (p.4, top right):** A bipolar AF with arguments A, B, C, D, E and mixed defeat (solid) / support (dashed) edges, illustrating direct vs indirect defeaters/defenders/supporters. The discussion classifies B as a direct defeater of A, F as an indirect defeater of A, D as an indirect defender of A, etc.
- **Example 5 figure (p.4, bottom right):** A bipolar AF with arguments A, B, C, D, E, F where U and D are direct defeaters of A, F is a direct defender of A, E is an indirect defender of A. Used to motivate the gradual valuation that follows.
- **Example 3 figure (p.3, embedded):** A small bipolar AF showing branch structure / homogeneous-vs-heterogeneous paths.

## Results Summary

The paper is definitional rather than empirical. Its "result" is a coherent set of definitions:

- A bipolar AF is a triple <A, R_def, R_sup> with two binary relations on the same argument set. *(p.2)*
- The bipolar graph admits direct/indirect defeaters, defenders, supporters, and indirect attackers, classified by the parity and homogeneity of paths. *(p.3–4)*
- A gradual valuation v: A → V on a bipolar AF can be defined by a compensation function g acting on aggregated defeat- and support-branch valuations, satisfying local axioms P1–P3 and global axioms Pg1–Pg4. *(p.5)*
- Selection of acceptable arguments / acceptable complete plans is reformulated in bipolar terms: arguments fall into "in favor", "against", or "in abeyance" classes, and a desire-driven decision system <D, Σ, K> selects conflict-free, maximal acceptable sets of complete plans. *(p.6–7)*

The conclusion (p.7) lists three open directions: (i) the abstract bipolar argumentation framework (in particular, its links between bipolarity in different domains, in particular in knowledge representation), (ii) the abstract bipolar valuation framework, and (iii) the abstract bipolar selection framework.

## Limitations

- The compensation function g and aggregators h_R, h_R_sup are characterized only by axioms and a worked example (1/(1+Σx_i^{-1}) form); no closed-form recommendation is fixed. *(p.5)*
- "Length" of a branch and "compatibility" of a defeat branch with a support branch are described informally; formal type discipline is incomplete. *(p.5)*
- The selection layer is sketched: Def.19 (acceptable set of complete plans) gives only conflict-freeness + maximality, deferring stronger admissibility / preferred / grounded analogues to future work. *(p.7)*
- Bipolarity in agent applications (psychology motivation) is asserted but not empirically grounded in the paper. *(p.1, p.6)*
- The independence of R_def and R_sup is stipulated, not derived; the question whether some support relations can or should be reduced to "defeat-of-defeaters" patterns is acknowledged but not settled. *(p.2)*

## Arguments Against Prior Work

- **Against Dung 1995's monolithic defeat relation R:** Dung's framework collapses positive and negative interactions into the single defeat edge, which forces support information to be encoded indirectly (e.g., as "defeat of a defeater") and obscures the bipolar structure of real argumentation processes. *(p.1)*
- **Against ad-hoc treatments in earlier bipolar-flavoured argumentation works (Karacapilidis & Papadias 2001, Verheij 2002, Bentahar et al. 2002):** These works each *implicitly* model some form of support but do not lift the distinction to an abstract framework, so they cannot be compared on uniform terms; the authors argue an abstract bipolar framework is needed to subsume them. *(p.1, intro paragraph "These bipolar relations…")*
- **Against treating "support" as synonymous with "defeat-of-defenders":** the authors argue this conflation drops information available in the original support relation and is incompatible with cognitive-psychology evidence that positive and negative preferences are processed separately. *(p.1, opening paragraphs of "Bipolarity at the argument level")*

## Design Rationale

- **Two independent relations rather than one signed relation.** Cognitive psychology (Cacioppo et al. cited p.1) distinguishes positive from negative preference processes, motivating a *bipolar* — i.e. two-dimensional — formal model rather than a single signed scale. *(p.1)*
- **Aggregator + compensation factorization (h_R, h_R_sup, g).** Decouples how multiple attackers (resp. supporters) combine from how the resulting "negative pressure" and "positive pressure" trade off, so different aggregator and compensation choices can be plugged in without redefining the framework. *(p.5)*
- **Branch-based valuation.** Anchoring v(α) on the *branches* of the bipolar graph leading to α (Pg1) ensures the value depends only on argumentation pertinent to α, not on disconnected fragments. *(p.5)*
- **Pairing defeat and support branches by length (Pg2).** Locks down a notion of "balanced" support/defeat counterevidence. *(p.5)*
- **Three-class acceptability (in favor / against / in abeyance).** Mirrors the bipolar split at the selection layer rather than forcing a binary accepted/rejected verdict. *(p.6)*
- **Plans built from desires + defeasible rules + facts.** Lets the framework apply to decision-making and planning, not just dialogue, by making the desire to be achieved an explicit conclusion of a plan. *(p.6–7)*

## Testable Properties

- **TP1 (P1):** v(α) depends only on the valuations of α's *direct* defeaters and *direct* supporters. *(p.5)*
- **TP2 (P2):** v is monotone non-increasing in the *quality* of α's defeaters and monotone non-decreasing in the *quality* of α's supporters. *(p.5)*
- **TP3 (P3):** v is monotone non-increasing in the *number* of α's defeaters and monotone non-decreasing in the *number* of α's supporters. *(p.5)*
- **TP4 (Pg1):** v(α) depends only on the valuations of branches leading to α. *(p.5)*
- **TP5 (Pg2):** Defeat branches pair with support branches of the same length. *(p.5)*
- **TP6 (Pg3):** Improving the defence / degrading the defeat part of α increases v(α). *(p.5)*
- **TP7 (Pg4):** Improving the defeat part / degrading the support part of α decreases v(α). *(p.5)*
- **TP8 (Def.17):** Conflict-freeness on complete plans = pairwise non-attack + joint consistency with K. *(p.7)*
- **TP9 (Def.19):** Acceptable sets are conflict-free *and* set-inclusion maximal. *(p.7)*

## Relevance to Project

This is a foundational reference for the **bipolar argumentation** stream in the project's collection (sits alongside `Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation`, `Amgoud_2008_BipolarityArgumentationFrameworks`). Concrete uses:

- Provides the *original* abstract bipolar AF definition `<A, R_def, R_sup>` that downstream papers (Cayrol & Lagasquie-Schiex 2005 ECSQARU, Amgoud-Cayrol-Lagasquie-Prade 2008) refine into the BAF formalism that the project's argumentation reductions can encode.
- The Pg1–Pg4 axiom set is a candidate set of *testable properties* for any gradual-semantics implementation that claims to be "bipolar-aware".
- The desire / sub-desire / partial-plan / complete-plan vocabulary (Defs 9–13) is an early formal sketch of the link between bipolar AFs and decision-/planning-style reasoning. Useful when reading later papers that connect AFs to ASP encodings of practical reasoning.
- Distinguishes positive support from "defeat-of-defenders" reduction — a useful caution when implementing reductions from bipolar to standard AFs that might silently drop information.

## Open Questions

- [ ] What concrete g, h_R, h_R_sup pair satisfies all of P1–P3 *and* Pg1–Pg4 simultaneously? The paper offers only an example.
- [ ] How does Def.19's "conflict-free + maximal" notion of acceptable plan sets relate to Dung-style preferred / grounded / stable extensions when restricted to plans?
- [ ] How does the bipolar AF's R_sup interact with attacks on supporters (R_def edges into a supporter)? The paper sketches it via indirect defeaters but does not give a closed-form valuation rule for that case.
- [ ] Does the "pair defeat-branch with same-length support-branch" axiom Pg2 always have a unique pairing, or does ambiguity arise on graphs with unbalanced support/defeat fan-in?

## Related Work Worth Reading

- Dung 1995 — the framework being extended.
- Cayrol & Lagasquie-Schiex 2005 (ECSQARU) — the immediate follow-up that turned this NMR sketch into a formal bipolar AF with a worked acceptability semantics.
- Amgoud, Cayrol, Lagasquie-Schiex, Livet 2008 (Int. J. Intelligent Systems) — the journal-length account, "Bipolarity in argumentation graphs".
- Karacapilidis & Papadias 2001 — early implicit bipolarity (Computer-supported argumentation).
- Verheij 2002 (NMR'2002) — extension multiplicity in dialectical argumentation, cited as related implicit-bipolarity work.
- Cacioppo & Berntson 1994 (cited in motivation) — cognitive-psychology evidence for separate positive/negative evaluation processes.
- Benferhat, Dubois, Kaci, Prade 2002 — bipolar representation in possibilistic-logic preferences.
- Bentahar, Moulin, Bélanger 2002 — argumentation-supported negotiation, an applied bipolar setting.
- Tan & Pearl 1994 — preferences under uncertainty (KR).

## Citation Notes

The references list contains 23 entries (pages 8–9). Key cluster: Amgoud et al. self-citations 2000, 2002, 2004a, 2004b; Cayrol & Lagasquie-Schiex 2003a, 2003b, 2004 (the Bipolar argumentation Toulouse IRIT report); Dung 1995; Bondarenko, Dung, Kowalski, Toni 1997; Pollock 1992; Pollock 1995; Prakken & Sartor 1997; Verheij 2002; Karacapilidis & Papadias 2001; Bentahar, Moulin, Bélanger 2002.
