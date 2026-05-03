---
title: "AGM Meets Abstract Argumentation: Contraction for Dung Frameworks"
authors: "Ringo Baumann, Felix Linker"
year: 2019
venue: "JELIA 2019 (LNCS 11468)"
doi_url: "https://doi.org/10.1007/978-3-030-19570-0_3"
pdf_status: "paywalled — not on sci-hub, ResearchGate blocked by Cloudflare"
produced_by:
  agent: "claude-opus-4-6"
  skill: "paper-process (worker)"
  timestamp: "2026-03-30"
  source: "SpringerLink abstract + full reference list + Baumann & Brewka 2015 companion paper"
---
# AGM Meets Abstract Argumentation: Contraction for Dung Frameworks

## One-Sentence Summary
Defines AGM-style contraction for Dung argumentation frameworks using Dung logics, proves the Harper Identity fails (no unrestricted contraction operators exist), and shows that dropping the recovery postulate restores existence of well-behaved operators.

## Problem Addressed
Baumann & Brewka (2015) defined AGM expansion and revision for AFs using Dung logics. The third AGM operation — contraction (removing beliefs) — remained open. Classical AGM theory connects revision and contraction via the Levi Identity (revision from contraction + expansion) and the Harper Identity (contraction from revision). This paper investigates whether contraction operators exist in the AF setting.

## Key Contributions
- **First AGM-style contraction study for AFs**: reformulates the six classical AGM contraction postulates (closure, inclusion, vacuity, success, extensionality, recovery) for Dung logics
- **Negative result — Harper Identity fails**: an analog to the Harper Identity, which allows constructing a contraction operator from a given revision operator, is not available in the AF/Dung-logic setting. This means contraction operators satisfying all AGM postulates cannot be guaranteed to exist
- **Positive result — dropping recovery restores existence**: the recovery postulate (contracting by X then expanding by X recovers the original) is independently controversial in AGM theory. Dropping it yields well-behaved contraction operators for AFs
- **Builds on Dung logics**: uses the same logical framework as Baumann & Brewka (2015), where ordinary equivalence in Dung logics = strong equivalence for argumentation semantics

## Methodology
- Reformulates AGM contraction postulates for the AF/Dung-logic setting
- Investigates whether the Harper Identity K - A = K * ~A intersected with K transfers to AFs
- Proves impossibility of full AGM contraction (with recovery)
- Constructs concrete contraction operators satisfying all postulates except recovery
- Pages 41-57 in LNCS 11468

## Key Definitions (from abstract and companion paper context)

### Contraction (classical AGM)
K - A: remove formula A from belief set K such that A is no longer in K - A, while changing K minimally.

### AGM Contraction Postulates (reformulated for AFs)
1. **Closure**: K - A = Cn(K - A) — result is closed under consequence
2. **Inclusion**: K - A ⊆ K — contraction only removes, never adds
3. **Vacuity**: if A ∉ K then K - A = K — don't change if A wasn't believed
4. **Success**: if A ∉ Cn(∅) then A ∉ K - A — non-tautologies get removed
5. **Extensionality**: if A ≡ B then K - A = K - B — logically equivalent formulas contract identically
6. **Recovery**: K ⊆ (K - A) + A — expanding the contracted set by A recovers original beliefs

### Harper Identity (fails for AFs)
K - A = K * ¬A ∩ K — contraction by A equals revision by ¬A intersected with original beliefs. This identity does NOT hold in the Dung logic setting.

### Dung Logics (from Baumann & Brewka 2015)
Monotonic logics where models are AFs and ordinary equivalence coincides with strong equivalence. The key property: F₁ ≡_σ F₂ iff σ(F₁ ∪ F') = σ(F₂ ∪ F') for all F'.

## Relation to Propstore

### Direct relevance
- Propstore's branch.py implements AF change operations (Darwiche & Pearl 1997 iterated revision)
- This paper establishes what is NOT possible: full AGM contraction with recovery for AFs
- Any implementation of AF contraction in propstore must drop recovery or accept incompleteness
- The failure of Harper Identity means contraction and revision are more independent in the AF setting than in classical AGM — they cannot be derived from each other

### Implications for implementation
- Branch deletion/retraction operations should not promise recovery semantics
- The Levi Identity (revision = contraction + expansion) may also not transfer fully
- Recovery-free contraction operators from this paper could inform propstore's retraction operations
- The 2015+2019 papers together define the complete AGM landscape for AFs: expansion works, revision works, contraction works only without recovery

## Limitations of These Notes
- **PDF not obtained**: paper is paywalled (Springer LNCS), not on sci-hub, ResearchGate blocked. Notes are based on the abstract and reference list from SpringerLink, plus context from the companion 2015 paper
- **Missing**: concrete operator definitions, formal proofs, specific theorem numbers, examples
- **Confidence**: high for the main results (abstract is explicit), low for technical details

## New Leads
- Harper 1976 — "Rational conceptual change" — origin of the Harper Identity
- Hansson 1989 — "New operators for theory change" — recovery postulate critique
- Diller et al. 2018 — "An extension-based approach to belief revision in abstract argumentation" (Int. J. Approx. Reason. 93)
- Coste-Marquis et al. 2014 — "On the revision of argumentation systems: minimal change of arguments statuses" (KR 2014)
- Coste-Marquis et al. 2014b — "A translation-based approach for revision of argumentation frameworks" (JELIA 2014)
- Snaith & Reed 2017 — "Argument revision" (J. Logic Comput. 27(7))
- Binnewies et al. 2015 — "Partial meet revision and contraction in logic programs" (AAAI 2015)
- Caridroit et al. 2015 — "Contraction in propositional logic" (ECSQARU 2015)
