# Diller et al. 2015 — An Extension-Based Approach to Belief Revision in Abstract Argumentation

## Core Problem
Previous attempts to apply AGM belief revision to Dung's abstract argumentation frameworks (AFs) failed to guarantee a **single AF** as revision output. This paper provides a generic solution for proper I-maximal semantics, including preferred, stable, semi-stable, and stage. The symbol is capital I, not the numeral 1, and sub-stable is not among the listed semantics. *([pp.2926-2927 images](pngs/page-000.png), [Proposition 1](pngs/page-001.png))*

## Key Insight
The paper works at the level of *extensions* (sets of arguments) rather than at the model-theoretic level. Instead of revising the AF structure directly, they characterize what the extensions of a revised AF should look like, then show these extensions can always be represented by some AF.

## Representation Theorems
Two types of revision operators are defined:

### 1. Revision by Propositional Formulas (Section 3.1)
- Revision operator: `* : AF_A x P_Ao -> AF_A` mapping an AF and a propositional formula to a revised AF
- The formula psi describes new information to incorporate
- Six postulates P*1-P*6 defined (analogous to AGM postulates adapted for AF setting)
- P*1: sigma(F * phi) is a subset of the models of phi.
- P*2: if sigma(F) shares a model with phi, sigma(F * phi) equals that intersection.
- P*3: if phi has a model, sigma(F * phi) is nonempty.
- P*4: logically equivalent revising formulas yield equal extension families.
- P*5: sigma(F * phi) intersect models(psi) is a subset of sigma(F * (phi and psi)).
- P*6: if that intersection is nonempty, sigma(F * (phi and psi)) is also a subset of it. *([postulates, p.2928 image](pngs/page-002.png))*
- Restricted to consistent formulas because argumentation semantics usually cannot express the empty extension set; footnote 1 explicitly says the results also apply without this restriction for semantics such as stable that can realize it. *([p.2928 image](pngs/page-002.png))*
- Theorem 1 constructs an operator from a sigma-compliant faithful ranking: F * phi = f_sigma(min([phi], <=_F)). Theorem 2 gives the converse representation for operators satisfying P*1-P*6 under proper I-maximal sigma. The selected minimum set must be realizable, which is precisely what compliance ensures. *([Theorem 1](pngs/page-002.png), [Theorem 2](pngs/page-003.png))*

### 2. Revision by Argumentation Frameworks (Section 3.2)
- Revision operator: `* : AF_A x AF_A -> AF_A` mapping two AFs to a revised AF
- New postulates A*1-A*6 plus Acyc (acyclicity of preference)
- The "underlying concept of a model" is given by the argumentation semantics sigma
- Correspondence between postulates and faithful rankings on 2^A (the power set of arguments)
- A*1: success (sigma(F * G) subset of sigma(G))
- A*2: if sigma(F) intersect sigma(G) != empty, then sigma(F * G) = sigma(F) intersect sigma(G)
- A*3: if sigma(G) != empty, then sigma(F * G) != empty
- A*4: if sigma(G) = sigma(H), then sigma(F * G) = sigma(F * H).
- A*5: sigma(F * G) intersect sigma(H) is a subset of sigma(F * f_sigma(sigma(G) intersect sigma(H))).
- A*6: if sigma(F * G) intersect sigma(H) != empty, then sigma(F * f_sigma(sigma(G) intersect sigma(H))) is a subset of sigma(F * G) intersect sigma(H).
- Acyc: borrowed from Delgrande and Peppas 2015

The revising AF in A*5-A*6 is a realization of the **intersection of extension sets**, not the graph union G union H. *([postulates, p.2929 image](pngs/page-003.png))*

## Sigma-Comparability
- Two distinct extensions E1, E2 are **inclusion-comparable** if E1 subset E2 or E2 subset E1; otherwise they are inclusion-incomparable. This is a set relation, not a sigma-realizability test.
- The signature Sigma_sigma is the collection of extension families realizable under sigma.
- Definition 1 calls sigma **proper I-maximal** when: (i) every realizable family is an inclusion-antichain; (ii) every nonempty subfamily of a realizable family is realizable; and (iii) every pair of inclusion-incomparable sets is realizable as exactly a two-extension family.
- Proposition 1: Preferred, stable, semi-stable, and stage semantics are proper I-maximal.
- Definition 2 fixes a realization function f_sigma returning one AF with the requested extension family whenever realizable (and the empty AF otherwise). Realization can introduce auxiliary arguments, as the paper explicitly notes.
- Definition 4: a preorder is **sigma-compliant** iff min([phi], <=) belongs to Sigma_sigma for every consistent phi. It is the selected minimal models that must be realizable, not every formula's full model set. *([definitions, p.2927](pngs/page-001.png), [compliance, p.2928](pngs/page-002.png))*

## Faithful Assignments and Rankings
- Faithful assignments (Definition 3): map AFs to rankings on 2^A (total pre-orders)
- Based on Katsuno and Mendelzon [1991] faithful assignment notion
- I-faithful assignments use I-total preorders: every pair of **inclusion-incomparable** extensions must be comparable in the ranking; inclusion-comparable pairs may remain unranked. Faithfulness conditions are correspondingly imposed on the incomparable pairs. *([Definition 3, p.2928](pngs/page-002.png), [motivation, p.2930](pngs/page-004.png))*
- Key results: Theorems 1 and 2 (propositional), Theorems 3 and 4 (AF-based)
- Theorem 1: a sigma-compliant faithful ranking constructs formula revision satisfying P*1-P*6; Theorem 2 proves its converse.
- Theorem 3: an I-faithful ranking constructs AF revision F * G = f_sigma(min(sigma(G), <=_F)) satisfying A*1-A*6 and Acyc.
- Theorem 4: every AF-revision operator satisfying A*1-A*6 and Acyc for proper I-maximal sigma has such an I-faithful representation. *([p.2928](pngs/page-002.png), [p.2929](pngs/page-003.png), [p.2930](pngs/page-004.png))*

## Concrete Construction
- Rankings on 2^A characterize which extensions the revised AF should have
- The revision selects extensions that are "closest" to the original AF's extensions while satisfying the new information
- Edit distance / Dalal-style distance on interpretations adapted to the extension setting

## Relation to Prior Work
- Coste-Marquis et al. [2014a] also revise extension outcomes, then construct a **set of AFs** realizing selected extensions; [2014b] uses a propositional translation. The present paper requires one AF, potentially with auxiliary arguments. *([discussion, p.2931 image](pngs/page-005.png))*
- Booth et al. [2013] developed a general AGM-like framework for AF dynamics based on labelling approach
- Diller et al. address the "fall back beliefs" problem — what to do when revision yields something not representable as an AF
- Proper I-maximality ensures nonempty subfamilies of a revising AF's extensions are realizable; formula revision additionally requires sigma-compliance of the ranking.
- Dalal [1988] operator can be directly applied to revision of AFs
- Connection to iterated revision (Darwiche and Pearl 1997)

## Limitations Noted
- The representation results assume proper I-maximal semantics; Proposition 1 lists preferred, stable, semi-stable, and stage.
- The general formula-revision presentation restricts formulas to consistency, with the explicit stable-semantics exception in footnote 1.
- The result is a **single AF**, unlike the set-of-AFs output of the earlier approach. Auxiliary arguments can be required; a result restricted to changing attacks only is not promised. *([p.2926](pngs/page-000.png), [p.2927](pngs/page-001.png), [p.2931](pngs/page-005.png))*
- I-faithfulness permits incomparability only on inclusion-comparable extension pairs; it does not allow arbitrary partial orders over realizable pairs.
- Formula-revision operators need compliant rankings; arbitrary distance rankings cannot automatically be used there. AF-by-AF revision can use standard faithful rankings through Theorem 3. *([p.2928](pngs/page-002.png), [p.2931](pngs/page-005.png))*

## Tags
- belief-revision
- abstract-argumentation
- AGM
- extension-semantics
- representation-theorems
