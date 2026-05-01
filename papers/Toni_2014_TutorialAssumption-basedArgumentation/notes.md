---
title: "A tutorial on assumption-based argumentation"
authors: "Francesca Toni"
year: 2014
venue: "Argument and Computation 5(1):89-117"
doi_url: "10.1080/19462166.2013.869878"
affiliation: "Department of Computing, Imperial College London, South Kensington Campus, London SW72AZ, UK"
pages: "89-117"
---

# A tutorial on assumption-based argumentation

## One-Sentence Summary
Tutorial on Assumption-Based Argumentation (ABA): a structured argumentation framework defined as a tuple `<L, R, A, ¯>` (language, rules, assumptions, contrary mapping) where arguments are deductions from rules supported by assumptions and attacks are directed at assumptions in supports; includes multiple argument-level / assumption-level / hybrid semantics (admissible, preferred, sceptically preferred, complete, grounded, ideal, stable), correspondence with Dung AA, and dispute-derivation proof procedures (admissible, grounded, ideal) with soundness and p-acyclic completeness.

## Problem Addressed
Argumentation formalisms in AI (Dung AA, ASPIC+, DeLP, Besnard-Hunter, etc.) typically take arguments and attacks as given abstract primitives. ABA provides a *lower-level*, *structured* representation that explains **where arguments and attacks come from** — derived from inference rules, assumptions, and contraries — so as to (a) subsume multiple non-monotonic / default formalisms under one abstract skeleton (ABA is equipped to instantiate default logic, auto-epistemic logic, logic programming, circumscription), (b) give computational leverage by manipulating assumptions directly rather than whole arguments, and (c) support provably-correct dispute-derivation algorithms for computing 'winning' defence sets. *(p.89-90)*

## Key Contributions
- Tutorial introduction to ABA syntax (language L, rules R, assumptions A, contrary mapping ¯) *(p.92)*.
- Three equivalent notions of deduction: tree-style, backward-style, forward-style *(p.93)*.
- Three equivalent views of attack: argument-to-argument, assumption-set to assumption-set, hybrid (argument ↔ set-of-assumptions) *(p.95-96)*.
- Instantiation of seven Dung-style AA semantics at the assumption level, with correspondence theorems to argument-level *(p.97-100)*.
- Six concrete worked examples across ABA semantics (Ex 3.1, 5.1–5.4) *(p.97-99)*.
- Use of ABA to model non-monotonic default reasoning (birds/penguins), defeasible reasoning (DNA/racist), persuasion dialogue (minister privacy) *(p.101-102)*.
- Dispute-derivation proof procedures abstracted as two-player (proponent/opponent) zero-sum games with data-structure tuple `(P, O, D, C)` (optionally `Args, Att`), flowchart for admissible+grounded semantics, worked example, and three filtering techniques *(p.102-108)*.
- FAQ section clarifying design choices: bogus-assumption trick, contrary vs negation, consistency not imposed, only support-attacks (rebuttal/undercutting via mappings), preferences/strict rules reduced to standard ABA *(p.109-113)*.
- Mapping results: ABA is an instance of Dung AA, and every AA framework has an equivalent ABA framework (Toni 2012) *(p.111)*.

## Study Design (empirical papers)
*This is a tutorial / theoretical paper. No empirical study.*

## Methodology

The paper proceeds constructively:
1. Introduce the tuple `<L, R, A, ¯>` with semantic intuitions (§3).
2. Define deduction via finite proof-trees whose leaves are in `S ⊆ L` or `τ` ("true"); show backward/forward variants are equivalent for semantic purposes (§3).
3. Build arguments as tree-style deductions `A ⊢ σ` with `A ⊆ A` and attacks as directed relations driven by contrary-of-assumption (§4).
4. Lift Dung (1995) AA semantics to ABA at argument level, then restate at assumption level, then hybrid; prove (references Dung et al. 2007; Toni 2012) pointwise correspondence (§5).
5. Instantiate ABA for non-monotonic default, defeasible, and persuasion-dialogue examples (§6).
6. Introduce dispute derivations — sequences of tuples `(P, O, D, C)` representing a dialectical game; present a flowchart (Figure 3) unifying admissible (with bold boxes) and grounded (without) semantics; walk through a 10-step derivation (Figures 4-5) with alternatives (§7).
7. Address foundational/methodological questions via FAQ (§8).

## Key Equations / Statistical Models

### Rule schema

$$
\sigma_0 \leftarrow \sigma_1, \ldots, \sigma_m \quad (m \geq 0),\; \sigma_i \in \mathcal{L}
$$
Where: σ0 is the **head**, σ1..σm is the **body**. Empty body (m=0) allowed: `σ0 ←`. *(p.92)*

Alternative written forms: `q,a / p`, `q,a ⇒ p`. *(p.92)*

### ABA framework

$$
\langle \mathcal{L}, \mathcal{R}, \mathcal{A}, \overline{\phantom{x}} \rangle
$$
Where: `L` is the language (set of sentences), `R` a set of rules, `A ⊆ L` a non-empty set of assumptions, `¯ : A → L` a total **contrary** mapping. *(p.92)*

### Deduction

$$
S \vdash^R \sigma
$$
Where: finite tree rooted at σ ∈ L, leaves labelled with `τ` or sentences in `S ⊆ L`; non-leaf σ' has children equal to the body of some rule (with head σ') in `R`; S is the set of supports and R is the set of rules used in the tree. *(p.93)*

### Argument and attack (argument-level)

$$
A \vdash \sigma \;\;(A \subseteq \mathcal{A},\; \sigma \in \mathcal{L})
$$
Where: A ⊢ σ is a deduction for σ supported by assumption set A. *(p.95)*

$$
A_1 \vdash \sigma_1 \text{ attacks } A_2 \vdash \sigma_2 \iff \sigma_1 = \overline{a} \text{ for some } a \in A_2
$$
*(p.95)*

### Attack (set-of-assumptions level)

$$
A \text{ attacks } A' \iff \exists A'' \subseteq A,\; \exists A''' \subseteq A' \text{ such that an argument supported by } A'' \text{ attacks an argument supported by } A'''
$$
*(p.95)*

Equivalently via forward deductions (p.96).

### Attack (hybrid)

$$
\alpha \text{ attacks set } A \iff \alpha \text{ attacks some argument supported by } A' \subseteq A \iff \text{claim}(\alpha) = \overline{a} \text{ for some } a \in A
$$
*(p.96)*

$$
A \text{ attacks argument } \alpha \iff \exists A' \subseteq A \text{ such that the argument supported by } A' \text{ attacks } \alpha
$$
*(p.96)*

### Flat ABA

$$
\text{ABA framework is \emph{flat}} \iff \text{no assumption is the head of any rule in } \mathcal{R}
$$
*(p.94)*

### Closed set (for non-flat)

$$
A \subseteq \mathcal{A} \text{ is closed} \iff A \text{ contains every assumption deducible (via } \mathcal{R}) \text{ from } A
$$
*(p.113)*

## Parameters

### ABA framework components

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Language | L | set of sentences | — | arbitrary; may include classical negation ¬ and implication ⊃ | 92 | Not restricted to propositional atoms |
| Rules | R | set | — | σ0 ← σ1..σm, m≥0 | 92 | May be schemata with variables |
| Assumptions | A | subset of L | non-empty | A ⊆ L | 92 | Must be non-empty for non-trivial argumentation |
| Contrary | ¯ | total map A→L | — | — | 92 | Need NOT be bijective, symmetric, or negation |
| Flat | — | boolean | — | true/false | 94 | All known computational mechanisms require flat |
| p-acyclic | — | boolean | — | true/false | 107 | Required for completeness of dispute derivations |

### Dispute-derivation tuple components

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Proponent to-do | P | set of potential arguments | {initial {} ⊢ σ_target} | — | 103 | Arguments to construct supporting / defending |
| Opponent to-do | O | set of potential arguments | {} | — | 103 | Arguments to construct attacking P's arguments |
| Defence set | D | set of assumptions | {} | ⊆ A | 103 | All assumptions in supports of P's arguments |
| Culprits | C | set of assumptions | {} | ⊆ A | 103 | Opponent assumptions chosen to counter-attack |
| Argument store | Args | set of arguments | {} | — | 103 | All arguments constructed (Toni 2013) |
| Attack store | Att | set of (arg,arg) | {} | ⊆ Args×Args | 103 | Attack edges in dialectical tree |

### Notation for marked/unmarked arguments

| Name | Symbol | Meaning | Page |
|------|--------|---------|------|
| marked support | A (left of ⊢) | already processed | 105 |
| unmarked support | S (right of ⊢) | not yet processed | 105 |
| Argument shorthand | `A ⊢_S σ` | claim σ, marked A ⊆ A, unmarked S ⊆ L | 105 |
| Unmarked part | `um(π)` | unmarked premises of potential argument π | 104 |

## Effect Sizes / Key Quantitative Results

*Not an empirical paper. No effect sizes. Formal soundness/completeness results are summarized below.*

| Property | Scope | Holds when | Page |
|---|---|---|---|
| Dispute derivations sound | all semantics covered (admissible, grounded, ideal) | any flat ABA framework | 107, 112 |
| Dispute derivations complete | admissible, grounded, ideal | **p-acyclic** flat ABA framework | 107, 113 |
| Every stable set is preferred | ABA semantics | always | 98 |
| Grounded ⊆ every preferred set | ABA semantics | always | 98 |
| Sceptically preferred = ∩ preferred | by definition | always | 97 |
| grounded / ideal / sceptically preferred unique | ABA semantics | always | 99 |

## Methods & Implementation Details

### Inference-rule form
- Rules `σ0 ← σ1,...,σm` may be:
  - domain-independent (e.g. modus ponens `p ← q⊃p, q`) *(p.92)*
  - domain-dependent (factual) — old ABA (Bondarenko 1993, 1997) segregated these as a theory `T ⊆ L`; tutorial absorbs them as empty-body rules. *(p.92, p.110)*
- Variables instantiated over implicit vocabulary (e.g. schema `p(X) ← q(X), a(X)` expands to `p(1) ← q(1), a(1)`, `p(f(1)) ← q(f(1)), a(f(1))`, ...). *(p.93)*

### Deduction styles
- **Tree-style**: root σ, leaves in S or τ; each non-leaf σ' has children = body of some rule. This is the default. *(p.93)*
- **Backward-style** (Dung et al. 2006): sequence {p},{q,a},{a} — each frontier in tree construction. Equivalent to tree-style. *(p.93)*
- **Forward-style** (Bondarenko 1997): a sequence `a, b, q, p` where each element is τ, an assumption, or derivable via some rule from earlier elements. NOT strictly equivalent — loses 'relevance' (b in the sequence but not needed for p). However, for every tree-style there's a forward-style and for every forward-style there's a tree-style with smaller-or-equal support. Semantically equivalent. *(p.93)*

### Argument computation
- In flat ABA: any argument whose claim is assumption `a` is necessarily `{a} ⊢ a` with empty rule set. *(p.95)*
- Argument `{} ⊢ q` (supported by empty set of assumptions) is possible when q is derivable by a rule with empty body. *(p.95)*
- `{a,b} ⊢ p` is NOT an argument when `b` is irrelevant — tree-style enforces relevance. *(p.95)*
- Attacks are solely at assumption level; sub-argument notion is implicit (sub-trees) and plays no semantic or computational role. *(p.96)*

### Dispute-derivation step types (flowchart, Figure 3, p.104)

Root decision: if P and O both empty → **return (D, C, Args, Att)** (successful derivation).
Otherwise whose turn?

**Branch [1] P's turn**: choose potential argument π from P, select an unmarked premise σ from π.
- **[1(i)]** σ ∈ A (assumption): mark σ in π; start attack in O (add new potential argument `{} ⊢_{σ̄} σ̄`); get rid of π if um(π) is empty.
- **[1(ii)]** σ ∉ A: find a "good" rule for σ (head σ, no culprit in body). If no good rule → abort. If found: unfold σ with ONE good rule to get new π'; mark π' using D (subtract D from um(π')); get rid of π' if um(π') is empty.

**Branch [2] O's turn**: choose π from O. If um(π) is empty → abort. Otherwise select premise σ.
- **[2(i)]** σ ∈ A (assumption): non-deterministic choice — either ignore σ (mark σ; important for completeness per Dung 2006), or:
  - **[2(i)(a)]** (ignore case) mark σ in π.
  - **[2(i)(b)]** σ ∈ D already (culprit is already a defence) → get rid of π (already dealt with).
  - **[2(i)(c)]** σ ∉ D: add σ to C; expand by σ; start counter-attack in P (add new `{} ⊢_{σ̄} σ̄`); possibly expand D; get rid of π.
- **[2(ii)]** σ ∉ A: unfold σ with **ALL** rules to get potential p-args π1'..πk' (k≥0); get rid of "dealt with" πi'.

The two forms of **bold** (defence-by-defence filtering, culprit-by-culprit filtering) appear only in admissible semantics — removed for grounded.

Branch [1] choice of one rule is non-deterministic; branch [2] enumerates all rules.

### Termination / outcome
- **Successful**: P and O both become empty → return `(D, C)` and optionally `(Args, Att)` giving the dialectical tree. *(p.103)*
- **Aborted**: a non-deterministic choice that failed; same input may have another successful derivation. *(p.106)*

### Three forms of filtering (used in admissible/ideal) *(p.107-108)*:

1. **Filtering of culprits by defences**: at step [2(i)], if chosen culprit is already in D → abort (the selected assumption to make culprit is already a defence, so making it a culprit would create a self-attack).

2. **Filtering of defences by culprits**: at step [1(ii)], the "good" rule must not contain any culprit in its body. Otherwise accepting it would put a culprit into the defence set, contradicting admissibility.

3. **Filtering of defences by defences**: at step [1(ii)], if unmarked support of newly generated π' is subset of D → skip. Avoids recomputation / loops.

The first two forms are **necessary for correctness** (guarantee defence set does not attack itself → admissibility/groundedness). The third is an **efficiency** optimization used by admissible and ideal semantics to terminate in the presence of loops.

### Worked example (Figure 4, p.105) — admissibility/groundedness of `d` in Example 5.4:

- Example 5.4: R = {p ← q,a; q ←; r ← b,c}, A = {a,b,c,d}, ā = r, b̄ = s, c̄ = t, d̄ = p (as 3.1 + d). Input: sentence `d`. *(p.99)*

| Step | P | O | D | C | Notes |
|------|---|---|---|---|-------|
| 0 | {{}⊢_{d} d} | {} | {d} | {} | initial set-up |
| 1 | {} | {{}⊢_{p} p} | {d} | {} | P: selected d, applied 1(i); contrary of d is p |
| 2 | {} | {{}⊢_{q,a} p} | {d} | {} | O: selected p, applied 2(ii); unfold with rule p←q,a |
| 3 | {} | {{}⊢_{a} p} | {d} | {} | O: selected q, applied 2(ii); unfold with rule q← |
| 4 | {{}⊢_{r} r} | {} | {d} | {a} | O: selected a, applied 2(i)(c); add a to C, counter-attack contrary r |
| 5 | {{}⊢_{b,c} r} | {} | {d,b,c} | {a} | P: selected r, applied 1(ii); unfold with rule r←b,c |
| 6 | {{b}⊢_{c} r} | {{}⊢_{s} s} | {d,b,c} | {a} | P: selected b, applied 1(i); attack by s on O |
| 7 | {} | {{}⊢_{s} s, {}⊢_{t} t} | {d,b,c} | {a} | P: selected c, applied 1(i); attack by t on O |
| 8 | {} | {{}⊢_{t} t} | {d,b,c} | {a} | O: selected s, applied 2(ii); no rules for s → π disappears |
| 9 | {} | {} | {d,b,c} | {a} | O: selected t, applied 2(ii); no rules for t → π disappears |

Result: `d` admissible/grounded with defence D = {d,b,c}, culprits C = {a}. Dialectical tree (Figure 5, p.105): `{d}⊢d ← {a}⊢p ← {b,c}⊢r`.

### Alternative derivation (Figure 4 variant, p.106) using **non-patient** selection:
- Steps 0-2, 4-9 (skipping step 3): select `a` rather than `q` at step 3, yielding 7-step derivation with same D, C but dialectical tree containing potential (non-actual) argument `{a}⊢_{q} p`.

### Selection operators
- **Selection operator** decides which premise σ to pick from π's unmarked part. Parameter of the derivation. Choices don't affect soundness but may affect termination/speed. *(p.106)*
- **Non-patient**: eagerly selects assumptions from unmarked supports.
- **Patient**: may delay. Default in Dung et al. 2006, 2007.

### Systems *(p.108)*
- **CaSAPI** (Gaertner & Toni 2007) — Prolog, admissible+grounded. `www.doc.ic.ac.uk/~ft/CaSAPI/` (note: no longer maintained).
- **proxdd** (Toni 2013) — Prolog. `www.doc.ic.ac.uk/~rac101/proarg/`.
- **grapharg** (Craven, Toni, Williams 2013) — Prolog; graph-based; incorporates minimality.

### Non-flat ABA (§8.3 p.113)
For non-flat frameworks, assumption sets must be **closed** under `R`. Example:
- R = {x ← c, z ← b, a ← b}, A = {a,b,c}, ā = x, b̄ = y, c̄ = z. Input: sentence c.
- {b} attacks c but {b} is not closed — closed form is {a,b} (via rule a←b).
- {a,b} is counter-attacked by {c} (since c̄ = z not addressed, but ā = x and rule x ← c gives {c} attacks {a,b}).
- Thus c is admissible.

## Figures of Interest

- **Figure 1 (p.93):** Three tree-style deductions for Example 3.1 — `{q,a}⊢p` with R1={p←q,a}, `{}⊢q` with R2={q←}, and `{a}⊢p` with R3=R1∪R2. Shows how tree structure enforces relevance.
- **Figure 2 (p.103):** Potential arguments (left, middle) vs actual argument (right) for `p` in Example 3.1. Potential arguments have unexpanded non-assumption premises; actual arguments have all leaves at assumptions or τ.
- **Figure 3 (p.104):** Master flowchart for admissible and grounded dispute derivations. Admissible uses bold boxes (ignore choice at [2(i)], defence-by-defence and culprit-by-culprit filtering); grounded omits them. Central decision points: (i) P&O empty? (ii) whose turn? (iii) σ ∈ A? (iv) for O: um(π) empty? ignore σ? σ ∈ D? σ ∈ C?
- **Figure 4 (p.105):** 10-row derivation table for `d` in Example 5.4. Columns Step, P, O, D, C, Notes. Shows exact sequence of 9 iterations.
- **Figure 5 (p.105):** Three views of the dialectical tree output: (a) with marked/unmarked notation showing construction steps, (b) intermediate potential args at each step, (c) final actual argument tree `{d}⊢d ← {a}⊢p ← {b,c}⊢r`.

## Results Summary

ABA provides a single abstract structured-argumentation skeleton that (i) is an instance of Dung AA while also admitting Dung AA as an instance (Toni 2012), (ii) has three equivalent semantic views (argument-level, assumption-level, hybrid), (iii) supports seven standard Dung semantics lifted to the assumption level, (iv) admits sound dispute-derivation proof procedures (with completeness for p-acyclic frameworks) implemented in CaSAPI, proxdd, grapharg. The tutorial walks through default reasoning (birds/penguins/Tweety), defeasible legal reasoning (DNA/racist), and persuasion dialogues (minister's private life) showing concretely how to encode such problems as ABA. *(p.89-115)*

## Limitations

- All existing computational mechanisms (and most tutorial content) assume **flat** ABA frameworks *(p.94, p.110)*.
- Dispute derivations are **query-oriented** — compute a winning defence for a specific input sentence. No mechanism currently for computing full winning extensions *(p.113)*.
- Completeness of dispute derivations only guaranteed for **p-acyclic** frameworks *(p.107)*.
- The paper does **not** cover computational complexity (Dimopoulos-Nebel-Toni 2002; Dunne 2009) or multi-agent deployment (Fan & Toni 2011/2012) *(p.114)*.
- Consistency of support is not enforced (unlike most structured argumentation formalisms) — implied only when L closed under negation and contrary coincides with negation *(p.111)*.
- Knowledge acquisition bottleneck: ABA frameworks typically require hand-crafting; Fan et al. 2013 gives automatic extraction from tabular clinical-trial data as one exception *(p.110)*.
- Preferences and strict-vs-defeasible distinctions are **not** first-class — must be encoded via transformations (last-link, Brewka 1989, Thang & Luong 2013 for defaults; Toni 2008 for Caminada-Amgoud postulates) *(p.110)*.
- Only support-attacks; rebuttal and undercutting must be compiled away via Kowalski-Toni 1996 / Dung-Kowalski-Toni 2006/2009 mappings *(p.112)*.

## Arguments Against Prior Work

- Against **abstract argumentation (Dung AA)** alone: AA "does not address the issue as to where arguments and attacks are coming from"; extracting full AA from ABA has "very severe computational implications" because ABA-filtered dispute derivations avoid generating irrelevant arguments that a direct AA computation would enumerate *(p.111)*.
- Against **consistency-imposing approaches** (e.g. Besnard-Hunter, Modgil-Prakken ASPIC+): "Consistency of the support of arguments is costly to check/ensure" (Dung et al. 2010). ABA's weaker condition (winning set of args doesn't attack itself) is more computation-friendly *(p.111)*.
- Against **rule-support arguments**: Most dispute-derivation variants don't need rules in arguments, so ABA omits them from the computational shorthand; rules are retained only where useful (Craven 2013) *(p.112)*.
- Against **explicit theory T component**: early ABA (Bondarenko 1993, 1997) had a fifth component (theory/knowledge base) separate from rules; Toni folds it into R as empty-body rules without loss of generality *(p.110)*.
- Against **strict-vs-defeasible rule distinctions** (DeLP, ASPIC+): ABA has a *single* defeasibility mechanism — assumptions — and shows this is sufficient (Dung et al. 2009; Toni 2008; Caminada-Amgoud 2007 postulates) *(p.110)*.
- Against **preference-extended argumentation frameworks** (Modgil-Prakken 2013 etc.): better to map preference reasoning onto plain ABA than extend ABA with preferences, to keep the framework simple (follows last-link principle Kowalski-Toni 1996; Brewka 1989) *(p.110-111)*.
- Against **computing full extensions**: in practice, query-oriented dispute derivations suffice (Fan et al. 2013 medical app; Matt et al. 2008 e-procurement — handful of input sentences suffices) *(p.113)*.
- Against **classical logic for non-monotonic reasoning**: trivialises in the presence of inconsistencies and cannot withdraw conclusions due to monotonicity; ABA handles this naturally *(p.101)*.

## Design Rationale

- **Tuple `<L, R, A, ¯>` with contrary map, NOT negation**: generality — allows ABA to instantiate default logic (use assumption `Mσ` with contrary `¬σ` ≠ `Mσ`), auto-epistemic logic, logic programming; contrary can be asymmetric, non-bijective, and not even an assumption *(p.94, p.110)*.
- **Tree-style deductions as default**: encodes relevance — `{a,b} ⊢ p` with irrelevant `b` is not an argument in tree-style even though it would be in forward-style *(p.93, p.95)*.
- **Attacks at assumption level only**: arguments with empty support are invulnerable; supports the semantic shortcut `A ⊢_S σ` for marked/unmarked computation; reduces to single operational attack primitive; avoids multiple attack types (rebuttal, undercutting) which are instead compiled away via mappings — keeps dispute derivations small and avoids costly rebuttal bookkeeping *(p.95, p.112)*.
- **Flat restriction for computation**: all dispute-derivation variants assume flat; non-flat requires closed sets and generalized semantics (Dimopoulos et al. 2002 shows "computationally demanding") *(p.94, p.113)*.
- **Focus on admissible, grounded, ideal dispute derivations** in §7: preferred/complete/stable can be derived via relationships to these three (Toni 2013); grounded is cheapest; admissible gives credulous winning; ideal gives sceptical with loop termination *(p.103)*.
- **Non-deterministic choice of "ignore" at step [2(i)]**: needed for completeness (Dung et al. 2006) — otherwise derivation may miss valid defences *(p.106)*.
- **"Filtering of culprits by defences" and "defences by culprits"**: both enforce that defence set does not attack itself (prerequisite for admissibility and groundedness) *(p.108)*.
- **Selection operator as up-front parameter**: soundness is invariant to operator choice; operator choice affects speed and termination, enabling parallel exploration (Craven et al. 2012) *(p.107)*.

## Testable Properties

- **P1 (p.94):** An ABA framework is flat iff no assumption appears as head of any rule.
- **P2 (p.93):** Tree-style ⊢ is equivalent to backward-style ⊢.
- **P3 (p.93):** Every tree-style argument is a forward-style argument; for every forward-style argument supported by A there exists a tree-style argument supported by `A' ⊆ A`.
- **P4 (p.95):** In flat ABA, any argument whose claim is assumption `a` has support exactly `{a}` and empty rule set.
- **P5 (p.95):** An argument with empty support cannot be attacked.
- **P6 (p.98):** Every stable set of arguments is preferred.
- **P7 (p.98):** The grounded set is contained in every preferred set.
- **P8 (p.99):** The sceptically preferred, ideal, and grounded sets are always unique.
- **P9 (p.99-100):** For any ABA framework, argument-level and assumption-level semantics pointwise correspond: A set of arguments `A` is admissible/preferred/sceptically preferred/complete/grounded/ideal/stable iff `⋃{supp(α) : α ∈ A}` is admissible/preferred/sceptically preferred/complete/grounded/ideal/stable at the assumption level. And vice versa.
- **P10 (p.107, p.112):** Dispute derivations are sound for all covered semantics; complete for p-acyclic ABA frameworks.
- **P11 (p.108):** Filtering of culprits by defences ⟹ defence set cannot attack itself.
- **P12 (p.113):** For non-flat ABA, admissibility requires sets of assumptions to be closed under R.
- **P13 (p.106):** Ignoring an assumption in branch [2(i)] is necessary for completeness; not ignoring may cause a successful derivation to not exist even when input is acceptable.

## Relevance to Project

This paper is **foundational** for propstore's argumentation/reasoning layer (layer 4 per `CLAUDE.md`). Direct implementation touch-points:

1. **`propstore.aspic_bridge` / ASPIC+ bridge**: ABA and ASPIC+ are sister structured-argumentation frameworks. ABA's three equivalent views (argument / assumption-set / hybrid) and contrary-driven attacks give a lean alternative architecture for the ASPIC bridge. ABA argument construction is simpler (tree of rule applications rooted at assumptions) and maps cleanly to the recursive `aspic.py` argument builder.

2. **Dung AF construction from claims/stances**: propstore's flow from claims → AF can be modelled as building an ABA framework whose assumptions are defeasible claims, whose rules are inference/combination steps, and whose contraries are stance conflicts. The `<L, R, A, ¯>` tuple is a natural data structure for propstore's conflict/contrariness mapping (see `conflict-contrariness-mapping.md`).

3. **Dispute derivations for goal-directed queries**: propstore's `query_claim()` / `build_arguments_for()` backward-chaining functions are the analogue of ABA dispute derivations. The flowchart (Figure 3) gives an exact algorithmic specification with filtering techniques that propstore can port to reduce recomputation during worldline construction.

4. **Assumption-level ATMS**: Because ABA operates on labelled sets of assumptions, it composes directly with the ATMS-backed world model (`propstore.world`). ABA's `D` (defence set) corresponds to the environment of an ATMS node; culprits `C` correspond to the nogood-like conflict store.

5. **Non-commitment discipline**: ABA's multi-semantics (credulous vs sceptical) aligns with propstore's core principle that the system must hold rival positions without collapsing disagreement — different render-time policies can apply admissible, preferred, grounded, or ideal semantics over the same underlying frameworks.

6. **Preferences via compilation**: rather than extending propstore's argumentation core with preferences, follow Toni's advice: compile preferences (source/date/overlay) into assumption-level rules (last-link, Brewka-style) so that the core argumentation engine stays lean.

7. **Tutorial value**: this paper is the single best on-ramp for new propstore contributors to ABA; cross-reference it with Bondarenko-Toni-Dung-Kowalski 1997 (original ABA) and Dung 1995 (AA) both already in `papers/`.

## Open Questions

- [ ] How does propstore's current `aspic_bridge` recursive-argument builder compare in practice to the ABA tree-style deduction construction? Could we consolidate?
- [ ] Which of CaSAPI, proxdd, grapharg is most appropriate as a reference implementation model? grapharg (Craven et al. 2013) adds minimality and may match propstore's need for relevance-filtered argumentation.
- [ ] Is propstore's `support_revision` adapter (currently support-incision only) consistent with ABA's "filtering of defences" operation, and if so should they be unified?
- [ ] Should propstore adopt ABA's **p-acyclic** test as a precondition for completeness guarantees during worldline rendering?
- [ ] For non-flat cases (which propstore's micropublication model implies when claims assume other claims), how does the closed-set requirement interact with the ATMS environment computation?
- [ ] How to map probabilistic/subjective-logic annotations (Jøsang) onto ABA? Dung-Thang 2010 gives probabilistic ABA — should be a follow-up reading.

## Related Work Worth Reading

- **Bondarenko, Dung, Kowalski, Toni (1997)** — original ABA paper; the theoretical companion that this tutorial complements. Already in `papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/`.
- **Dung (1995)** — AA framework, already in corpus.
- **Dung, Kowalski, Toni (2006)** — "Dialectic proof procedures for assumption-based, admissible argumentation", Artificial Intelligence 170. Original dispute derivations.
- **Dung, Mancarella, Toni (2007)** — "Computing ideal sceptical argumentation", AI Journal 171. Ideal-semantics dispute derivations.
- **Dung, Kowalski, Toni (2009)** — "Assumption-based argumentation", chapter in *Argumentation in AI*, Springer. Overview paper.
- **Toni (2013)** — "A generalised framework for dispute derivations in ABA", AI Journal 195:1-43. Extended derivation types.
- **Toni (2012)** — "Reasoning on the web with ABA". Ontology integration; also proves AA ⇔ ABA equivalence.
- **Gaertner & Toni (2007)** — CaSAPI implementation.
- **Craven, Toni, Williams (2013)** — grapharg (graph-based dispute derivations).
- **Dung & Thang (2010)** — probabilistic ABA for jury-based dispute resolution.
- **Fan et al. (2013)** — ABA for medical decision-making with preferences (tabular extraction).
- **Caminada & Amgoud (2007)** — evaluation of argumentation formalisms via rationality postulates.
- **Modgil & Prakken (2013)** — general account of argumentation with preferences (ASPIC+).
- **García & Simari (2004)** — DeLP (companion structured framework).
- **Dimopoulos, Nebel, Toni (2002)** — computational complexity of ABA.
- **Dunne (2009)** — complexity of ideal semantics.
- **Sartor (1994); Prakken & Vreeswijk (2002); Cayrol, Devred, Lagasquie-Schiex (2006)** — persuasion-dialogue antecedents cited in §6.
- **Kowalski & Toni (1996)** — "Abstract argumentation" (last-link principle for preferences).
- **Kakas, Kowalski, Toni (1992, 1998)** — abductive logic programming foundations.
- **Reiter (1980); McCarthy (1980); Lin & Shoham (1989); Pollock (1987); Kakas & Toni (1999); Eshghi & Kowalski (1989)** — non-monotonic reasoning and argumentation lineage.
