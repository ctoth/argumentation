# Paper Report — Amgoud, Cayrol, Lagasquie-Schiex (2004)

## Paper Identity

- **Title:** On the bipolarity in argumentation frameworks
- **Authors:** Leila Amgoud, Claudette Cayrol, Marie-Christine Lagasquie-Schiex (3 authors, all IRIT-UPS Toulouse)
- **Year:** 2004 (publication date 2004-06-06)
- **Venue:** 10th International Workshop on Non-Monotonic Reasoning (NMR 2004), Uncertainty Frameworks subworkshop, Whistler, Canada (June 2004)
- **Identifier:** HAL hal-03198386 (https://hal.science/hal-03198386). No DOI.
- **Pages:** 9 (PDF page 1 = HAL cover banner; paper text pages 1–9)
- **Local path:** `papers/Amgoud_2004_BipolarityArgumentationFrameworks/`

**Identity verified.** Title, authors, year, and venue all match the target. Not the 2009 book chapter ("Bipolar abstract argumentation systems"), not the 2005 ECSQARU paper.

## Retrieval

- Source: HAL (https://hal.science/hal-03198386v1/file/article-nmr04.pdf), HTTP 200, 248 071 bytes, valid 10-page PDF.
- Semantic Scholar metadata API was avoided (per caller's S2-rate-limit constraint). Metadata was sourced entirely from the HAL landing page meta tags.
- Page images regenerated at 200 DPI with a white background (the default ImageMagick render produced a black page-002 due to alpha-layer interaction; explicit `-background white -alpha remove -alpha off` fixed it).

## Core Contributions

1. **Position paper for *bipolarity* in argumentation.** Names the missing distinction in Dung-style AFs: positive (support) vs. negative (defeat/attack) interactions are independent dimensions and should be modeled separately.
2. **Abstract bipolar AF:** triple `<A, R_def, R_sup>` extending Dung's pair `<A, R>` with an explicit support relation.
3. **Branch / direct-vs-indirect taxonomy:** defines defeat branches, support branches, and direct/indirect classifications of defeaters, defenders, supporters, and indirect attackers (Defs 4–5).
4. **Gradual valuation framework:** `v(α) = g(h_R(v(C_1),…,v(C_n)), h_R_sup(v(B_1),…,v(B_p)))` where g is a compensation function combining defeat-branch and support-branch aggregations; constrained by local axioms P1–P3 (functional dependence on direct neighbors; monotone in attacker/supporter quality and quantity) and global axioms Pg1–Pg4 (dependence on branches; same-length pairing of defeat and support branches; monotone improvement under defence/support).
5. **Selection layer for desire-driven decision making:** desire / sub-desire / partial plan / complete plan vocabulary (Defs 9–14), conflict and attack relations on plans (Defs 15–17), system for handling desires `<D, Σ, K>` (Def 18), acceptable set of complete plans = conflict-free + maximal (Def 19), with three governing axioms (good plans accepted, self-attacked rejected, others in abeyance).

## Key Definitions and Results

- **Def 1–3 (recap of Dung):** AF = `<A, R>`; admissibility, defence, conflict-freeness, characteristic function F_<A,R>(S).
- **Abstract bipolar AF:** `<A, R_def, R_sup>` with R_def, R_sup ⊆ A × A independent.
- **Def 4 (graphical representation):** bipartite graph G_b with two edge types; defeat branch = path of length ≥ 1 ending in a defeat edge; support branch = path ending in a support edge; branch is *direct* if A has only one predecessor, otherwise *indirect*.
- **Def 5 (defeaters / defenders / supporters):** direct defeaters of A = R_def^{-1}(A); direct defenders = R_def^{-1}(R_def^{-1}(A)); indirect defeaters at odd distance ≥ 3, indirect defenders at even distance ≥ 2; direct supporters = R_sup^{-1}(A); indirect supporters via R_sup transitively.
- **Local valuation principles (P1–P3):** P1 = functional in direct defeaters and direct supporters; P2 = monotone in valuation quality of those neighbors; P3 = monotone in their counts.
- **Def 7 (gradual valuation):** v: A → V given by v(α) = g(h_R(…), h_R_sup(…)).
- **Global valuation principles (Pg1–Pg4):** Pg1 = depends only on the branches reaching α; Pg2 = pair each defeat branch with a same-length support branch; Pg3 = improving defence / degrading defeat raises v(α); Pg4 = improving defeat / degrading support lowers v(α).
- **Def 8 (defeat / support branches for valuation):** restricts to homogeneous branches (defeat branches consisting only of defeat edges, etc.) so the valuation pairing is well-defined.
- **Def 9–13 (selection vocabulary):** desire (open propositional formula), sub-desire (rule whose head is a literal of the desire), partial plan `(h, U)`, elementary partial plan, complete plan (`(h, U_1 ∪ … ∪ U_n)` decomposing into elementary plans).
- **Def 14–17:** conflict between complete plans (joint inconsistency with K), attack between plans (defeat between rules in their explanations), conflict-free set, unachievable desire.
- **Def 18 (system for handling desires):** triple `S = <D, Σ, K>`.
- **Def 19 (acceptable set):** S ⊆ G is acceptable iff conflict-free and maximal under set inclusion, subject to three axioms: (1) good plans included, (2) self-attacked plans rejected, (3) others in abeyance.

No theorems are stated; this is a definitional/position paper. The "results" are the new abstract definitions plus the axiom system on the gradual valuation.

## Notable Connections

- **Direct ancestor of:** Cayrol & Lagasquie-Schiex 2005 (ECSQARU), Amgoud-Cayrol-Lagasquie-Prade 2008 — the formal BAF papers already in the project collection (`Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation`, `Amgoud_2008_BipolarityArgumentationFrameworks`). This NMR paper is the *origin sketch* those refine into the now-standard bipolar argumentation framework.
- **Builds on:** Dung 1995 (`<A, R>` framework, acceptability semantics, characteristic function).
- **Cross-domain motivation:** cites Cacioppo & Berntson 1994 (cognitive psychology — separate positive/negative evaluation processes) and Benferhat-Dubois-Kaci-Prade 2002 (bipolar preferences in possibilistic logic) to argue bipolarity is a domain-general modeling primitive, not specific to argumentation.
- **Implicit bipolar predecessors flagged:** Karacapilidis & Papadias 2001 (HERMES), Verheij 2002 (NMR'02 dialectical extensions), Bentahar et al. 2002 (argumentation-supported negotiation). The paper argues these implicitly bipolar systems lacked an abstract framework and motivates one.
- **Relevance to project's reductions work:** any reduction encoding BAFs must respect the independence of R_def and R_sup that this paper stipulates; "support = defeat-of-defenders" reductions silently drop information per the paper's argument. The Pg1–Pg4 axiom set is a candidate property battery for testing gradual-semantics implementations claimed to be bipolar-aware.
- **Open theoretical questions raised by the paper:** existence of a closed-form (g, h_R, h_R_sup) satisfying P1–P3 ∧ Pg1–Pg4 jointly; relationship between Def 19's "conflict-free + maximal" plan-acceptability and Dung's preferred / grounded / stable extensions when restricted to plans; behavior of R_def edges into supporters; uniqueness of the same-length defeat/support branch pairing on unbalanced graphs.

## Artifacts Produced

- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/paper.pdf` (248 KB, 10 pages)
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/metadata.json`
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/notes.md` (dense notes with all definitions, P/Pg axioms, parameter table, branch taxonomy, plan vocabulary)
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/abstract.md` (verbatim abstract + interpretation)
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/citations.md` (full reference list, 27 entries, with 5-paper follow-up shortlist)
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/description.md` (single-paragraph summary with tags)
- `papers/Amgoud_2004_BipolarityArgumentationFrameworks/pngs/page-{000..009}.png` (page images at 200 DPI)

## Skipped Steps (per caller instruction)

The following downstream paper-reader steps were intentionally NOT run:

- Step 7 reconcile (cross-reference collection)
- Step 8 papers/index.md update
- Step 9 provenance stamp via `pks source stamp-provenance`
- Source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote, reconcile

## Usefulness to This Project

- **Rating:** High (foundational reference for bipolar argumentation).
- **What it provides:** The original abstract definition of bipolar AF `<A, R_def, R_sup>`, the branch-based defeater/defender/supporter taxonomy, the P1–P3 / Pg1–Pg4 axiom set for gradual bipolar valuation, and an early link from BAFs to plan-based decision making.
- **Actionable next steps:**
  - Use the Pg1–Pg4 axioms as a property battery when testing any gradual-semantics module that claims bipolar awareness in the project's reductions catalog.
  - Cite this paper alongside `Cayrol_2005_…` and `Amgoud_2008_…` in any documentation describing the project's BAF reduction support.
  - When reading the 2005 ECSQARU paper, cross-check that its formal BAF definitions match Defs 1–8 here (they should, since same authors).
- **Skip if:** the project is working only on Dung's monopolar AFs with no support-relation extension and no plan/desire-style decision layer.
