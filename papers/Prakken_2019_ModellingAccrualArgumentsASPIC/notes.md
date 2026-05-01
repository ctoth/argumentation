---
title: "Modelling Accrual of Arguments in ASPIC+"
authors: "Henry Prakken"
year: 2019
venue: "Proceedings of the Seventeenth International Conference on Artificial Intelligence and Law (ICAIL '19)"
doi_url: "https://doi.org/10.1145/3322640.3326703"
pages: "1-10"
---

# Modelling Accrual of Arguments in ASPIC+

## One-Sentence Summary
Introduces a new accrual mechanism for ASPIC+ that represents multiple reasons for a conclusion by sets of arguments and labelling-relative defeat, avoiding the exponential blow-up, awkward premise labelling, and monotonicity problems in earlier accrual proposals. *(pp.1-2, 4-7, 10)*

## Problem Addressed
The paper studies how to model **accrual** in structured argumentation: situations where several arguments support the same conclusion and together should matter in a way that is not captured by treating each reason entirely in isolation. *(p.1)*

Prakken contrasts two broad approaches. In a **knowledge-representation** approach, reasons are combined directly in rule antecedents. In an **inference** approach, accrual is modeled at the level of arguments and their interactions. This paper works in the latter style and aims to preserve the intuitive distinction between linked, convergent, and cumulative support without making the argumentation system mathematically unstable or representationally awkward. *(p.1, pp.9-10)*

## Key Contributions
- Reformulates the relevant ASPIC+ preliminaries using **labellings** rather than extension sets, creating the setting in which accrual can be defined cleanly. *(pp.2-3)*
- Critiques Prakken (2005) and Gordon (2018), identifying exponential construction cost, cumbersome premise-labelled conclusions, and monotonicity problems as central shortcomings of prior accrual models. *(pp.3-4)*
- Defines **accrual sets**, **weakly/strongly applicable** arguments, a labelling-relative notion of **l-defeat**, and a monotone characteristic function `F` over labellings. *(pp.4-6)*
- Proves that the new model preserves the standard existence/ordering properties of grounded, complete, preferred, and stable semantics, and reduces to ordinary ASPIC+ when each conclusion has at most one argument. *(pp.6-7)*
- Demonstrates the framework on strict reasons, legislative balancing, factor-based legal reasoning, and rules/principles/exclusionary reasons. *(pp.7-10)*

## Methodology
The paper proceeds in four stages. First, it restates the needed abstract-argumentation and ASPIC+ machinery in labelling form. Second, it analyzes the two main predecessor accrual models. Third, it proposes a new formalism in which defeat is defined relative to a labelling and depends on preferences between **sets** of arguments rather than only individual arguments. Fourth, it proves monotonicity and reduction results, then works through application examples from law and argument theory. *(pp.2-10)*

## Formal Setup
- The paper starts from a Dung-style argumentation framework `AF = (A, D)` together with standard complete, grounded, preferred, and stable labellings. *(pp.2-3)*
- It uses an ASPIC+ style structured setting in which arguments are recursively built from a knowledge base `K` plus strict and defeasible rules. For this paper's variant, uncertain premises are treated as defeasible rules rather than separately attackable premises, so undermining is omitted for simplicity. *(p.2)*
- Attacks and defeats are lifted to a labelling-based notion of **p-labellings**, which the paper later generalizes to the accrual-sensitive notion of **l-labellings**. *(pp.2-3)*

## Key Equations

$$
l = (In, Out)
$$

Where `In` and `Out` are the arguments labelled in and out; arguments not in either set are undecided. Labellings are ordered by set inclusion on both components. *(pp.2-3)*

$$
F(l) = (In', Out')
$$

Where an argument is put in `In'` iff all its `l`-defeaters are in `Out` and all its immediate subarguments are in `In`; an argument is put in `Out'` iff some `l`-defeater is in `In` or some immediate subargument is in `Out`. This is the characteristic function whose fixpoints are the new l-labellings. *(pp.5-6)*

## Parameters
This is a semantics paper rather than an empirical tuning paper. It introduces no numeric hyperparameters or thresholds. The important formal objects are structural:

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Labelling | `l = (In, Out)` | - | - | subsets of arguments | 2-3 | Base object for complete/grounded/preferred/stable semantics |
| Accrual set | `AS(A,l)` | - | - | nonempty sets of same-conclusion arguments | 4 | Includes all strongly applicable arguments for a conclusion |
| Characteristic function | `F` | - | - | labellings to labellings | 5-6 | Must remain monotone to recover grounded semantics |

## Existing Accrual Models
### Prakken (2005)
The 2005 proposal can express accrual inside ASPIC+, but it does so by generating an argument for every subset of the reasons supporting a conclusion. This preserves intuitive accrual principles, yet makes the representation exponential and requires labeling conclusions with their supporting premise sets in a way that is awkward both formally and for knowledge engineering. *(pp.3-4)*

### Gordon (2018)
Gordon's approach compresses the representation by combining all reasons for a conclusion into one argument and using statement labellings plus proof standards to decide which reasons are active. The paper argues that this is elegant in size, but the relevant characteristic operator is not monotone in general, contrary to Gordon's claim, so the intended grounded-construction story breaks. *(pp.4-5)*

## Core Definitions
### Weakly and Strongly Applicable Arguments
An argument is **weakly applicable** in a labelling `l` when it has no undercutter in `In` and no immediate subargument in `Out`. It is **strongly applicable** when, additionally, all undercutters are in `Out` and all immediate subarguments are in `In`. *(p.4)*

### Accrual Set
An **accrual set** is a nonempty set of same-conclusion arguments that contains every strongly applicable argument for that conclusion and may also contain weakly applicable arguments. Allowing the weakly applicable case is what keeps the new characteristic function monotone. *(pp.4-6)*

### aSAF and Set-Based Preferences
The paper extends a structured argumentation framework to an **aSAF**, where preferences may compare **sets of arguments** rather than only single arguments. This is how cumulative vs non-cumulative accrual can affect defeat. *(pp.4-5)*

### l-Defeat
An argument `A` **l-defeats** `B` if `A` undercuts `B`, or if `A` rebuts `B` and some accrual set of `A` is preferred to some accrual set of `B` under the set-ordering. Defeat therefore depends on the current labelling because accrual sets depend on weak/strong applicability in that labelling. *(pp.4-5)*

## Formal Results
### Monotonicity
Lemma 5.1 proves that `l`-defeat is monotone in the labelling order. Proposition 5.2 then shows that the induced characteristic function `F` is monotone as well. This is the key technical repair: it guarantees existence of a least fixpoint and therefore a well-behaved grounded l-labelling. *(p.6)*

### Reduction to Ordinary ASPIC+
Lemmas 5.3 and 5.4, together with Proposition 5.5, show that when each conclusion is supported by at most one argument, the new l-labellings collapse back to the ordinary p-labellings of ASPIC+. In other words, the new formalism is conservative over the non-accrual case. *(pp.6-7)*

### Semantic Preservation
The paper concludes that the standard existence and relationship results for grounded, complete, preferred, and stable semantics continue to hold in the new setting. The model therefore adds accrual without sacrificing the usual abstract-argumentation semantics story. *(pp.6-7)*

## Why Weak Applicability Matters
Example 4.8 is the turning point of the paper. If accrual sets contained only strongly applicable arguments, then the new characteristic function could fail to be monotone, which would destroy uniqueness of grounded semantics. Allowing weakly applicable arguments into accrual sets avoids this pathology while still constraining the model through set preferences. *(pp.5-6)*

## Implementation Details
- Represent same-conclusion support as **sets of candidate arguments**, not by generating one argument for every subset of reasons. *(pp.3-5)*
- Track applicability relative to a current labelling using two grades: weak and strong. *(p.4)*
- Compute defeat relative to accrual sets and the current labelling, not as a static relation fixed in advance. *(pp.4-5)*
- Use a monotone characteristic operator `F` over labellings so that grounded semantics can still be obtained by least-fixpoint iteration. *(pp.5-6)*
- Preserve ordinary ASPIC+ behavior automatically in cases where each conclusion has only one supporting argument. *(pp.6-7)*
- Keep strict arguments and strict structure visible rather than collapsing everything into statement-level labels; this matters in the strict-reasons example and in legal explanations. *(pp.5, 7-9)*

## Figures of Interest
- **Figure 1 (p.5):** Running example graph illustrating the arguments and attacks used to motivate the new labelling-sensitive treatment of accrual.
- **Figure 2 (p.8):** Legislative proposal example showing how several positive and negative consequences are represented.
- **Figure 3 (p.8):** Partial CATO factor hierarchy used to illustrate factor-based accrual and preference handling.

## Results Summary
- The paper delivers a monotone accrual semantics for ASPIC+ where the grounded labelling is again the least fixpoint of a monotone operator. *(pp.5-6)*
- It avoids the exponential subset explosion of the 2005 model while preserving the intended accrual principles. *(pp.3-4, 7-10)*
- It rejects Gordon's compact model as formally unstable because the relevant operator can fail to be monotone. *(pp.4-5)*
- It shows that accrual can be handled while preserving the ordinary relationships between grounded, complete, preferred, and stable semantics. *(pp.6-7)*

## Applications
### Accrual of Strict Reasons
The paper argues that earlier claims that strict arguments never accrue are too strong. If two defeasible reasons feed into the same strict conclusion, the system should allow them to accrue in a natural way. The witness-testimony example shows how two testimonies can jointly matter for a location claim without distorting the strict/deductive backbone. *(pp.7-8)*

### Legislative Proposals
A bill with several positive and negative consequences can be modeled compactly because the new approach no longer requires explicit undercutters for every lesser subset of reasons. This gives a cleaner account of balancing multiple policy consequences. *(p.8)*

### Factor-Based Reasoning
The partial CATO factor hierarchy example shows that the model can express legal factors and priorities while retaining losing arguments for explanation. That explanatory retention is contrasted with approaches that collapse directly to accepted nodes. *(pp.8-9)*

### Rules, Principles, and Exclusionary Reasons
The final application relates accrual to Raz-style exclusionary reasons and to the linked/convergent/cumulative terminology. The paper's notion of accrual is broader than the standard linked/convergent distinction and is intended to give a unified treatment. *(pp.9-10)*

## Limitations
- The paper is semantic and conceptual; it does not provide an algorithmic implementation or empirical evaluation. *(pp.5-10)*
- Set-based preferences over accrual sets must be supplied externally; the paper does not solve how such preferences should always be chosen. *(pp.4-5, 7-10)*
- The terminology discussion at the end clarifies several distinctions, but the author explicitly notes that some applications still need careful modelling choices to decide which supports count as cumulative rather than merely convergent. *(pp.9-10)*

## Arguments Against Prior Work
- The 2005 accrual model is criticized for requiring exponentially many arguments and awkward premise-labelled conclusions. *(pp.3-4)*
- Gordon's 2018 model is criticized because its claim to monotonicity fails; the paper presents counterexamples showing that the grounded operator can misbehave. *(pp.4-5)*
- Statement-labelling approaches are treated as too coarse for preserving the explanatory granularity of structured arguments in settings such as legal reasoning. *(pp.4-5, 8-9)*

## Design Rationale
- **Why use accrual sets?** To represent multiple reasons for one conclusion without generating one argument per subset of those reasons. *(pp.4-5)*
- **Why make defeat labelling-relative?** Because whether a group of reasons should count as active depends on which arguments are currently in or out. *(pp.4-5)*
- **Why allow weakly applicable arguments into accrual sets?** Because otherwise monotonicity fails and grounded semantics becomes unstable. *(pp.5-6)*
- **Why compare sets of arguments rather than only single arguments?** Because cumulative support is a property of combined reasons, not of any one argument taken alone. *(pp.4-5, 9-10)*

## Testable Properties
- If every conclusion has at most one supporting argument, the new framework must reproduce ordinary ASPIC+ p-labellings. *(pp.6-7)*
- If an argument has an undercutter in `In` or an immediate subargument in `Out`, it cannot count as strongly applicable in the current labelling. *(p.4)*
- If accrual sets are restricted to strongly applicable arguments only, monotonicity can fail; allowing weakly applicable arguments avoids this. *(pp.5-6)*
- Grounded l-labellings must be obtainable as least fixpoints of the monotone characteristic function `F`. *(p.6)*

## Relevance to Project
This paper is directly useful for any propstore design that needs to preserve multiple supporting reasons for one conclusion without blowing up the argument graph. It suggests a concrete way to model accumulative support at the structured-argument level while still keeping a Dung/ASPIC+ semantics pipeline intact. *(pp.4-10)*

It is especially relevant if the project needs:
- explanation-preserving legal or factor-based reasoning *(pp.8-9)*
- a distinction between linked, convergent, and cumulative support *(pp.9-10)*
- accumulation of several reasons without enumerating all subsets as separate arguments *(pp.3-5)*

## Open Questions
- [ ] How should set-preference relations over accrual sets be learned, engineered, or justified in concrete applications? *(pp.4-5, 10)*
- [ ] What efficient implementation strategies can compute l-labellings at scale for realistic ASPIC+ theories? *(not addressed explicitly; implementation gap visible across the paper)*
- [ ] How should the model interact with richer preference schemes already studied in later ASPIC+ work? *(conceptual follow-up from pp.6-10)*

## Collection Cross-References

### Already in Collection
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — the core ASPIC+ machinery this paper adapts for accrual. *(pp.2-3, 6-7)*
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — closest in spirit on preferences within ASPIC+, though this paper focuses on set-based accrual comparisons. *(conceptual)*
- [[Prakken_2013_FormalisationArgumentationSchemesLegalCaseBasedReasoningASPICPlus]] — relevant to the legal and factor-based applications discussed here. *(pp.8-9)*
- [[Brewka_2010_AbstractDialecticalFrameworks]] — useful contrast because the paper explicitly compares its legal-factor encoding against ADF-style approaches. *(p.8)*
- [[Walton_2015_ClassificationSystemArgumentationSchemes]] — relevant to the linked/convergent/cumulative terminology clarified near the end. *(pp.9-10)*

### New Leads (Not Yet in Collection)
- Gordon (2018) — direct predecessor and main critical target. *(pp.4-5)*
- Prakken (2005) — original accrual proposal inside ASPIC+. *(pp.3-4)*
- Horty (2012) — cited for reasons, defaults, and exclusionary considerations. *(p.9)*

### Cited By (in Collection)
- (none found)
