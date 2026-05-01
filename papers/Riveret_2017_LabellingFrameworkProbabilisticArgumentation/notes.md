---
paper: Riveret_2017_LabellingFrameworkProbabilisticArgumentation
title: "A Labelling Framework for Probabilistic Argumentation"
authors: [Régis Riveret, Pietro Baroni, Yang Gao, Guido Governatori, Antonino Rotolo, Giovanni Sartor]
year: 2017
venue: "Annals of Mathematics and Artificial Intelligence, vol. 83, pp. 21-71"
tags: [probabilistic-argumentation, labelling-semantics, structured-argumentation, abstract-argumentation, uncertainty]
status: complete
read_date: 2026-03-30
produced_by:
  agent: "Claude Opus 4.6 (1M context)"
  skill: "paper-reader"
  timestamp: "2026-03-30"
---

# Notes: A Labelling Framework for Probabilistic Argumentation

## Overview

This paper presents a **labelling-oriented framework** for probabilistic argumentation that unifies structured (rule-based) and (semi-)abstract argumentation with diverse types of uncertainty. The framework uses **probabilistic labellings** — going beyond the traditional {IN, OUT, UN} labels — to capture different kinds of uncertainty in a unified representation. *(p.1-2)*

The key insight is that different types of probabilistic uncertainty in argumentation (structural uncertainty about premises, uncertainty about which arguments to consider, uncertainty about acceptance status) can all be captured uniformly through extended labelling sets and probabilistic labelling frames (PLFs). *(p.2)*

## Key Contributions *(p.2)*

1. Non-traditional argument labellings beyond {IN, OUT, UN} to capture different kinds of uncertainty
2. Extended labelling-based representation to statements (argument conclusions)
3. Comprehensive set of **probabilistic frames** corresponding to different uncertainty kinds at different abstraction levels
4. Analysis of enhanced expressiveness vs. influential probabilistic argumentation approaches in literature

## Section 2: Labelling of Arguments and Statements

### 2.1 Argument Construction and Argumentation Graphs *(pp.3-8)*

**Minimalist rule-based framework** akin to argumentative interpretation of Defeasible Logic, with ASPIC+ inspiration.

- **Def 2.1 (Literal):** atomic formula or negation of atomic formula *(p.3)*
- **Def 2.2 (Complementary literal):** ~φ for negation as failure (distinguished from ¬) *(p.3)*
- **Def 2.3 (Defeasible rule):** r: φ₁,...,φₙ, ~φ'₁,...,~φ'ₘ ⇒ φ — only defeasible rules *(p.3)*
- **Def 2.4 (Conflict relation):** over set of literals Φ, binary conflict relation *(p.4)*
- **Def 2.5 (Superiority relation):** binary relation over Rules, r >ₛ r' *(p.4)*
- **Def 2.6 (Defeasible theory):** tuple (Rules, conflict, >ₛ) *(p.4)*
- **Def 2.7 (Argument):** A: A₁,...,Aₙ, ~φ'₁,...,~φ'ₘ ⇒ φ — finite construct with unique identifier *(p.4)*
- **Def 2.8 (Subarguments and rules):** Sub(A), DirectSub(A), TopRule(A), Rules(A) *(p.4)*
- **Def 2.9 (Attack relation):** Two types: *(p.5)*
  - **B rebuts A** (on A') iff conclusions conflict and no superiority
  - **B undercuts A** (on A') iff ~conc(B) in body of TopRule(A')
- **Def 2.10 (Direct subargument relation):** ⇒_G over argument set *(p.6)*
- **Def 2.11 (Abstract argumentation graph):** (A, ↝) — Dung-style *(p.6)*
- **Def 2.12 (Semi-abstract argumentation graph):** (A, ↝, ⇒) with attack AND direct subargument relations *(p.6)*
- **Def 2.13 (Well-formed):** ⇒ acyclic/antireflexive, attack on subarg propagates up *(p.6)*
- **Def 2.14 (Argumentation graph from theory):** G constructed from defeasible theory T *(p.6)*
- **Def 2.15 (Subgraph):** H of G induced by A_H ⊆ A_G *(p.7)*
- **Def 2.16 (Subargument-complete set):** all direct subarguments included *(p.8)*
- **Def 2.17 (Rule-complete set):** all rule-derivable arguments included *(p.8)*
- **Def 2.18 (Subargument-complete subgraph):** subgraph with subargument-complete argument set *(p.8)*
- **Def 2.19 (Rule-complete subgraph):** induced by rule-complete set from theory *(p.8)*
- **Def 2.20 (Defeasible subtheory):** subset of rules inducing a sub-theory *(p.9)*

**Semi-abstract argumentation graphs** are the paper's key structural contribution — intermediate between Dung's abstract AFs (attacks only) and full structured formalisms. They include both attack and subargument relations, which is motivated by probabilistic needs: an argument cannot exist without its subarguments being believed. *(p.6-7)*

### 2.2 Labelling of Arguments *(pp.9-13)*

Key innovation: introduces {ON, OFF} labels alongside traditional {IN, OUT, UN}.

- **ON/OFF distinction:** ON = argument is actually included and has effect; OFF = not included or no effect *(p.9)*
- Combined labelling {IN, OUT, UN, OFF} allows simultaneous representation of structural and acceptance uncertainty *(p.9)*
- **Def 2.26 ({ON,OFF}-labelling specification):** Can be subargument-complete, rule-complete, or legal (both) *(p.11)*
- **Def 2.27 ({ON,OFF}-labelling w.r.t. subgraph):** maps to subgraph membership *(p.11)*
- **Def 2.28 (Argumentation semantics):** an X-{IN,OUT,UN}-labelling specification *(p.11)*
- **Def 2.29 (Conflict-free):** no IN argument attacked by IN argument *(p.12)*
- **Def 2.30 (Complete):** IN iff all attackers OUT, OUT iff has attacker IN *(p.12)*
- **Def 2.31 (Grounded):** minimal complete labelling (w.r.t. set inclusion on IN) *(p.12)*
- **Def 2.32 (Preferred):** maximal complete labelling *(p.12)*
- **Def 2.33 (Stable):** complete with empty UN set *(p.12)*
- **Def 2.34 (X-{IN,OUT,UN,OFF}-labelling specification):** Combines {ON,OFF}-labelling with {IN,OUT,UN}-labelling of the subgraph induced by ON arguments. Legal = both subargument-complete and rule-complete *(p.13)*
- **Def 2.35 (Grounded {IN,OUT,UN,OFF}-labelling specification):** Grounded semantics on the subargument-complete subgraph — every argument in A_G labelled according to grounded {IN,OUT,UN}-labelling of subgraph H, and every argument in A_G\A_H labelled OFF *(p.13)*

**Justification labellings** introduced via "semi-skeptical" scheme: *(p.14)*

- **Def 2.36 ({OFJ,SKJ,CRJ,NOJ}-labelling):** Semi-skeptical justification labels *(p.14)*
  - OFJ: argument OFF in all labellings
  - SKJ: argument IN in all labellings
  - CRJ: argument IN in some but not all labellings
  - NOJ: argument never IN (but not always OFF)

**NOTE:** Page 010 (page-010.png) is corrupted/black — content lost. This likely contains Definitions 2.21-2.25 covering multi-labelling and mono-labelling foundations.

### 2.3 Labelling of Statements *(pp.15-16)*

Labellings extend from arguments to their conclusions (literals/statements).

- **Def 2.37 (Labelling of literals):** function K: Φ → LitLabels *(p.15)*
- **Def 2.38 (Acceptance labelling of literals):** K: L^X_ArgLab(G) × Φ → LitLabels *(p.15)*
- **Def 2.39 (Bivalent labelling of literals):** {in, no} — in iff ∃A ∈ IN(L) with conc(A) = φ *(p.15)*
- **Def 2.40 (Worst-case sensitive labelling of literals):** {in, out, un, off, unp} labels *(p.15-16)*
  - **in:** ∃A ∈ IN(L) with conc(A) = φ
  - **out:** ∃A ∈ OUT(L) ∪ OFF(L) with conc(A) = φ, and all such arguments are OUT or OFF
  - **un:** ∃A ∈ IN(L) with conc(A) = φ and ∃A ∈ UN(L) with conc(A) = φ
  - **off:** ∃A with conc(A) = φ and all such arguments OFF
  - **unp (unprovable):** no argument in L with conclusion φ *(p.16)*

## Section 3: Probabilistic Labelling of Arguments and Statements

### 3.1 Probabilistic Argumentation Frames *(pp.16-21)*

Three levels of probabilistic frames, each capturing different uncertainty:

#### 3.1.1 Structural Uncertainty: PTFs and PGFs *(pp.17-18)*

- **Def 3.1 (Probabilistic Theory Frame / PTF):** tuple (T, ⟨Ω_PTF, F_PTF, P_PTF⟩) where sample space = Sub(T) (subtheories), σ-algebra = power set, P satisfies Kolmogorov *(p.17)*
- **Def 3.2 (Probabilistic Graph Frame / PGF):** tuple (G, ⟨Ω_PGF, F_PGF, P_PGF⟩) where sample space = Sub(G) (subgraphs) *(p.17)*
- **Def 3.3 (PGF corresponding to PTF):** Maps PTF distributions to PGF distributions — mapping is non-injective non-surjective *(p.18)*
- PTFs and PGFs capture **structural uncertainty** — uncertainty about which rules/arguments exist *(p.18)*
- PGFs are strictly more expressive than PTFs for argumentation graph uncertainty *(p.18)*

#### 3.1.2 Acceptance Uncertainty: PLFs *(pp.18-21)*

- **Def 3.4 (Probabilistic Labelling Frame / PLF):** tuple (G, S, ⟨Ω_PLF, F_PLF, P_PLF⟩) where sample space = set of X-ArgLab-labellings of G *(p.20)*
- **Def 3.5 (PLF corresponding to PGF):** Maps PGF to PLF by summing over labellings *(p.20)*
- **Def 3.6 (PGF corresponding to PLF):** Reverse mapping via summing over labellings for each subgraph *(p.20)*
- **Expressiveness hierarchy:** PLFs ⊃ PGFs ⊃ PTFs *(p.21)*
  - PLFs using {ON,OFF} capture structural uncertainty
  - PLFs using {IN,OUT,UN} capture acceptance uncertainty
  - PLFs using {IN,OUT,UN,OFF} combine both types

### 3.2 Probabilistic Labelling of Arguments *(pp.21-24)*

#### 3.2.1 Probabilistic Argument Acceptance Labellings *(pp.21-22)*

- Random variable L_A for each argument A, taking values from label set *(p.21)*
- **Prop 3.1:** Label probabilities sum to 1 for each argument *(p.22)*
  - For {ON,OFF}: P(L_A=ON) + P(L_A=OFF) = 1
  - For {IN,OUT,UN}: P(L_A=IN) + P(L_A=OUT) + P(L_A=UN) = 1
  - For {IN,OUT,UN,OFF}: all four sum to 1
  - For stable-{IN,OUT,UN}: P(L_A=IN) + P(L_A=OUT) = 1
  - For stable-{IN,OUT,UN,OFF}: P(L_A=IN) + P(L_A=OUT) + P(L_A=OFF) = 1

#### 3.2.2 Probabilistic Argument Justification Labellings *(pp.23-24)*

- Four justification labels: OFJ, SKJ, CRJ, NOJ *(p.23)*
- **Prop 3.2:** Relates justification labels to acceptance probabilities: *(p.23)*
  - L_J(A) = OFJ iff P(L_A=OFF) = 1
  - L_J(A) = SKJ iff P(L_A=IN) = 1
  - L_J(A) = CRJ iff 0 < P(L_A=IN) < 1
  - L_J(A) = NOJ iff P(L_A=OUT) > 0 or P(L_A=UN) > 0, and P(L_A=IN) = 0

### 3.3 Probabilistic Labelling of Statements *(pp.24-26)*

- Random variable K_φ for each literal φ, taking values from LitLabels *(p.24)*
- **Prop 3.3:** Statement label probabilities sum to 1 *(p.24)*
- **Prop 3.4:** For two conflicting literals φ₁, φ₂: P(K_φ₁ = in) + P(K_φ₂ = in) ≤ 1 *(p.25)*
- **Prop 3.5:** For conflicting literals: P(K_φ₁ ≠ in) = P(K_φ₂ = no) for bivalent; more complex for worst-case sensitive *(p.25)*
- This is a **probabilistic notion of consistency**: conflicting statements cannot both be highly probable *(p.25)*

**Running Example concluding computation (p.26):** Using grounded semantics with preferred {IN,OUT,UN,OFF}-labellings, the paper derives that P(program running = in) ≈ 0.61 while P(program not running = in) ≈ 0.39.

## Section 4: On Uncertainty about Inclusion and Acceptance Status *(pp.27-33)*

### 4.1 Constellations Approach *(pp.27-29)*

Relates the framework to Li et al.'s Probabilistic Argumentation Graphs (PAGs) [27]:

- **Def 4.1 (Probabilistic argumentation graph / PAG):** tuple (A, ↝, P_PAG) where P_PAG: A → [0,1] — each argument has independent inclusion probability *(p.27)*
- **Def 4.2 (PGF corresponding to PAG):** P_PGF(S) = Σ P_PAG(H) for subgraphs *(p.28)*
- PAG probability of a subgraph H: P_PAG(H) = ∏(A∈A_H) P_PAG(A) × ∏(A∉A_H) (1-P_PAG(A)) — **independence assumption** *(p.27)*
- **Prop 4.1:** P(L_B = ON) ≤ P(L_A = ON) when A is subargument of B — inclusion probability bounded by subarguments *(p.28)*
- **Prop 4.2:** P_PLF(L_A = ON) for any A in A_G links PTF rule probabilities to PLF argument inclusion *(p.28)*
- **Equation 14:** P^X_PAG(A) = Σ_{H∈H^X(A)} P_PAG(H) — extension-based probability sums over subgraphs where A is in an extension *(p.28)*
- PLFs can capture constellations approach but NOT vice versa — PLFs provide finer-grained acceptance uncertainty within individual labellings *(p.29)*

### 4.2 Epistemic Approach *(pp.29-31)*

- **Def 4.3 (Probabilistic epistemic frame / PEF):** tuple (G, ⟨Ω_PEF, F_PEF, P_PEF⟩) where sample space = subsets of A (2^A), each element is a set of "believed" arguments *(p.30)*
- Epistemic probability P_PEF(A) = degree of belief in argument A *(p.30)*
- **Coherence property:** P_PEF(A) + P_PEF(B) ≤ 1 for A attacks B (from Li et al. [27]) *(p.31)*
- **Foundedness:** P(L_A = IN) = 1 if no arguments attack A *(p.31)*
- **Def 4.4 (PLF corresponding to PEF):** Maps PEF to PLF via labelling correspondence — each subset of believed arguments maps to an {IN,OUT,UN}-labelling *(p.30)*
- **Def 4.5 (PEF corresponding to PLF):** Reverse mapping *(p.30)*
- Epistemic probabilities directly correspond to PLFs based on {IN,OUT,UN}-labellings *(p.31)*
- **Eq 17:** Optimistic distribution constraint: P(L_A = IN) ≥ 1 - Σ_{B∈B} P(L_B = IN) where B attacks A *(p.31)*

### 4.3 Combining Constellations and Epistemic *(pp.32-33)*

- PLFs based on {IN,OUT,UN,OFF}-labellings can jointly capture both kinds of uncertainty *(p.32)*
- **Prop 4.5:** P(L_A = IN) + P(L_B = IN) ≤ 1 (for A attacks B) — holds in combined framework *(p.32)*
- **Prop 4.6:** P(L_A = IN) + P(L_A = OFF) = 1 for complete labellings with no attackers *(p.32)*
- **Prop 4.7:** P(L_A = IN) ≤ P(L_A = ON) — acceptance probability bounded by inclusion probability *(p.32)*
- **Corollary 4.1:** P(L_B = IN) ≤ P(L_A = ON) when A is subargument of B *(p.32)*
- Constellations approach can be captured by probabilistic labellings but NOT vice versa — labellings yield finer-grained probabilistic evaluation *(p.33)*

## Section 5: Discussion of Related Literature *(pp.34-38)*

### 5.1 Probabilistic Structured Argumentation *(pp.34-35)*

#### 5.1.1 Related to Dung's framework *(p.34)*

- Prakken & Sartor [47]: probabilistic Dung-style systems for legal disputes
- Riveret et al. [53]: success chances in argument games, probability of event of construction × probability of acceptance
- Riveret et al. [52]: rule-based with reinforcement learning for softmax policies
- Lam et al. [34]: ASPIC+ inspired probabilistic rule-based system — close to PTFs
- Roth et al. [54]: assumption-based argumentation for jury-based dispute resolution
- CHRiSM [57]: rule-based probabilistic argumentation logic — related to PTFs

#### 5.1.2 Other probabilistic structured argumentation *(pp.35)*

- Garcia & Simari [24]: probabilistic setting for non-monotonic reasoning with probabilistic variables and scenarios
- Sneyers et al. [56,57]: CHRiSM probabilistic logic programming for argumentation — related to PTF
- Riveret et al. [51]: CHRiSM probabilistic argumentation

### 5.2 Probabilistic Abstract Argumentation *(pp.35-37)*

#### 5.2.1 Constellations approach *(pp.35-36)*

- Li et al. [36]: original constellations approach — independence assumption on argument inclusion
- Fazzinga et al. [15,16]: computational complexity of probabilistic abstract argumentation
- Fazzinga et al. [17]: Monte Carlo simulations for efficient probability estimation
- Liao et al. [38,39]: semantics of probabilistic argumentation by characterizing subgraphs
- Dondio [11]: computational analysis of probabilistic argumentation frameworks
- Hunter & Thimm [42,43]: evidential argumentation with special η argument for support — PrEAFs
- The independence assumption in constellations approach is a key limitation; this paper's framework does not require it *(p.36)*
- MARF (Markov Argumentation Random Field) by Tang et al. [58]: argument acceptability with four values (A, R, U, I) and Markov random fields *(p.36)*

#### 5.2.2 Epistemic approach *(p.37)*

- Hunter & Thimm [27,28,29]: epistemic probabilities for abstract argumentation
- Gabbay & Rodrigues [20]: equational approach to probabilistic abstract argumentation
- Baroni et al. [4]: rationality conditions for epistemic probabilities
- Paper's framework captures epistemic probabilities as special case of PLFs on {IN,OUT,UN} *(p.37)*
- Pollock [45]: used statistical syllogism for prima facie reasons with conditional probability threshold 0.5 *(p.37)*

### 5.3 Other Connections: Argumentation and Probability *(pp.37-38)*

- Wigmore charts and Bayesian networks share graph-based reasoning with argumentation *(p.38)*
- Fenton et al. [18]: Bayesian networks for legal arguments about evidence
- Grabmair et al. [23]: Carneades argument model to Bayesian network translation
- Timmer et al. [60,61,62]: bidirectional translation between Bayesian networks and argumentation
- Verheij [64,65,66,67,68]: extensive work on arguments, scenarios, and probabilities in evidential reasoning

## Section 6: Conclusion *(pp.38-39)*

**Main contribution:** A labelling-oriented framework for probabilistic argumentation covering four stages: rule-based argument construction, argument graph definition, argument evaluation, and statement evaluation. *(p.38)*

Key distinguishing features:
- Semi-abstract argumentation graphs where subargument relation plays a key role for inclusion/exclusion events *(p.38)*
- Novel {IN,OUT,UN,OFF}-labellings combining inclusion and acceptance uncertainty *(p.38)*
- Framework captures both constellations and epistemic approaches, and their combination *(p.38)*
- Properties easily retrieved by the formalism include coherence and foundedness *(p.38)*

**NOTE:** Page 039 is corrupted/black — likely contains remainder of conclusion.

## Implementation Relevance for propstore

### Direct Relevance

1. **PLF as unifying frame:** The PLF concept directly relates to propstore's probabilistic argumentation layer (Hunter & Thimm 2017 implementation). PLFs generalize both the constellations (Li et al. 2012 PrAF) and epistemic approaches into a single labelling framework.

2. **{ON,OFF} labels for structural uncertainty:** propstore's ATMS-based branch reasoning could benefit from the ON/OFF distinction — an argument being "OFF" (not constructed) vs "OUT" (constructed but defeated) vs "UN" (undecided) carries different information for branch merging.

3. **Statement labellings:** The worst-case sensitive labelling (Def 2.40) with {in, out, un, off, unp} provides a principled way to propagate argument-level uncertainty to claim-level conclusions, which is exactly what propstore's render layer needs.

4. **Justification labellings (OFJ/SKJ/CRJ/NOJ):** These map naturally to propstore's multi-branch reasoning — SKJ (skeptically justified) = accepted in all branches, CRJ (credulously justified) = accepted in some, NOJ = never justified.

5. **Proposition 3.4 (consistency constraint):** P(K_φ₁ = in) + P(K_φ₂ = in) ≤ 1 for conflicting literals — this is a probabilistic coherence constraint that should hold in propstore's opinion algebra.

### Architectural Alignment

- PTF → corresponds to propstore's defeasible theory level (knowledge/)
- PGF → corresponds to subgraph/branch level (repo/)
- PLF → corresponds to render-time evaluation (world/)
- The expressiveness hierarchy PTF ⊂ PGF ⊂ PLF mirrors propstore's storage → render pipeline

### Potential Enhancements

- The paper's approach to combining structural and acceptance uncertainty in a single labelling could improve propstore's IC merge operations
- Prop 4.7 (P(IN) ≤ P(ON)) establishes that acceptance probability is bounded by inclusion probability — relevant for branch-weighted rendering

## New Leads

- Li et al. [36,37]: Probabilistic argumentation frameworks and relaxing independence — already in collection as Li_2012
- Hunter & Thimm [27,28,29]: Epistemic approach to probabilistic abstract argumentation — Hunter_Thimm_2017 already in collection
- Liao et al. [38,39]: Semantics of probabilistic argumentation by characterizing subgraphs
- Tang et al. [58]: MARF — Markov argumentation random fields (AAAI 2016)
- Fazzinga et al. [15,16,17]: Complexity and efficient estimation for probabilistic abstract argumentation
- Verheij [64-68]: Arguments, scenarios, probabilities in evidential reasoning
- Riveret et al. [52]: Probabilistic rule-based argumentation for norm-governed learning agents

## Corrupted Pages

- Page 010 (page-010.png): Black — likely contains Defs 2.21-2.25 on multi/mono-labelling
- Page 039 (page-039.png): Black — likely contains end of conclusion section
