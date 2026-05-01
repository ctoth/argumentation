# Diller et al. 2015 — An Extension-Based Approach to Belief Revision in Abstract Argumentation

## Core Problem
Previous attempts to apply AGM belief revision to Dung's abstract argumentation frameworks (AFs) failed to guarantee that the revision of an AF is representable as an AF. This paper provides a generic solution applicable to many prominent semantics (stable, semi-stable, stage, and sub-stable).

## Key Insight
The paper works at the level of *extensions* (sets of arguments) rather than at the model-theoretic level. Instead of revising the AF structure directly, they characterize what the extensions of a revised AF should look like, then show these extensions can always be represented by some AF.

## Representation Theorems
Two types of revision operators are defined:

### 1. Revision by Propositional Formulas (Section 3.1)
- Revision operator: `* : AF_A x P_Ao -> AF_A` mapping an AF and a propositional formula to a revised AF
- The formula psi describes new information to incorporate
- Six postulates P*1-P*6 defined (analogous to AGM postulates adapted for AF setting)
- Key postulates: P*1 (success — psi is satisfied), P*2 (inclusion — revision among interpretations satisfying original AF), P*3 (consistency with models), P*4 (syntax irrelevance), P*5-P*6 (minimal change)
- Restricted to consistent formulas because argumentation semantics usually cannot express the empty extension set
- Theorem 2: For any operator satisfying P*1-P*6 for proper 1-maximal semantics sigma, there exists a faithful assignment mapping every AF to a faithful ranking on 2^A, with the binary relation defined accordingly

### 2. Revision by Argumentation Frameworks (Section 3.2)
- Revision operator: `* : AF_A x AF_A -> AF_A` mapping two AFs to a revised AF
- New postulates A*1-A*6 plus Acyc (acyclicity of preference)
- The "underlying concept of a model" is given by the argumentation semantics sigma
- Correspondence between postulates and faithful rankings on 2^A (the power set of arguments)
- A*1: success (sigma(F * G) subset of sigma(G))
- A*2: if sigma(F) intersect sigma(G) != empty, then sigma(F * G) = sigma(F) intersect sigma(G)
- A*3: if sigma(G) != empty, then sigma(F * G) != empty
- A*4: if sigma(F) = sigma(F'), then sigma(F * G) = sigma(F' * G)
- A*5: sigma(F * G) intersect sigma(H) implies subset of sigma(F * (G union H))
- A*6: if sigma(F * G) intersect sigma(H) != empty, then sigma(F * (G union H)) subset of sigma(F * G) intersect sigma(H)
- Acyc: borrowed from Delgrande and Peppas 2015

## Sigma-Comparability
- Two sets S1, S2 of extensions are sigma-comparable if one can find an AF with exactly those extensions
- Definition 1: semantics sigma is "realizable" if: for any S1 in sigma, S2 subset S1; implies S1 subset S2 for sigma-comparable sets; and for any sigma-incomparable S1, S2 can find AF having exactly these as extensions
- Proposition 1: Preferred, stable, semi-stable, and stage semantics are proper 1-maximal
- Sigma-completeness (Definition 4) needed for the propositional formula approach: a pre-order is sigma-compliant if every consistent formula is expressible

## Faithful Assignments and Rankings
- Faithful assignments (Definition 3): map AFs to rankings on 2^A (total pre-orders)
- Based on Katsuno and Mendelzon [1991] faithful assignment notion
- I-faithful assignments: allow partial rankings (not requiring totality), allowing partial with respect to sigma-incomparable pairs
- Key results: Theorems 1 and 2 (propositional), Theorems 3 and 4 (AF-based)
- Theorem 1: operator satisfying P*1-A*6 and Acyc for proper 1-maximal sigma, there exists faithful assignment
- Theorem 3: For proper 1-maximal semantics, can define operator via minimal elements of faithful ranking
- Theorem 4: For AF-based revision with proper 1-maximal semantics, faithful assignment mapping exists

## Concrete Construction
- Rankings on 2^A characterize which extensions the revised AF should have
- The revision selects extensions that are "closest" to the original AF's extensions while satisfying the new information
- Edit distance / Dalal-style distance on interpretations adapted to the extension setting

## Relation to Prior Work
- Coste-Marquis et al. [2014a,b] worked on revision at the model level; their approach is the starting point
- Booth et al. [2013] developed a general AGM-like framework for AF dynamics based on labelling approach
- Diller et al. address the "fall back beliefs" problem — what to do when revision yields something not representable as an AF
- The restriction to proper 1-maximal semantics ensures representability
- Dalal [1988] operator can be directly applied to revision of AFs
- Connection to iterated revision (Darwiche and Pearl 1997)

## Limitations Noted
- Restricted to semantics that are proper 1-maximal (complete semantics excluded — only works for complete semantics in limited cases)
- Revision formulas must be consistent
- The approach yields a *set* of AFs rather than a single AF as output (unlike model-based approaches)
- Future work: (1) extend to non-proper-1-maximal semantics, (2) identify operators based on sigma-compliant rankings for specific semantics, (3) study whether insights extend to broader theory of belief change, (4) apply to iterated belief change, (5) take the syntactic form of AF into account

## Tags
- belief-revision
- abstract-argumentation
- AGM
- extension-semantics
- representation-theorems
