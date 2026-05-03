# Hanisch & Rauschenbach 2025 — ANGRY grounder paper

**Date:** 2026-05-02
**Status:** RETRIEVED + READ (notes pre-existing, paper-reader confirmed already complete)

## Identity Resolution

The user's reference "Hanisch and Rauschenbach (2025) ANGRY: A grounder for rule-based argumentation" resolves to:

- **Published title:** "Grounding Rule-Based Argumentation Using Datalog"
- **Authors:** Martin Diller, Sarah Alice Gaggl, Philipp Hanisch, Giuseppina Monterosso, Fritz Rauschenbach
- **Year:** 2025
- **arXiv:** 2508.10976
- **DOI:** 10.48550/arXiv.2508.10976
- **Venue:** KR-25 (per existing notes.md frontmatter)

ANGRY is the **system name** described in this paper, not the title. The PDF mentions ANGRY 29 times, including:
- "We present a prototype grounder, ANGRY, which utilizes the Datalog engine Nemo"
- "implemented in the prototypical grounder ANGRY (Monterosso et al. 2025a), which is written in Rust"
- Extensively used in Section 5 (empirical evaluation): ANGRY+ASPforASPIC vs Arg2P, ANGRY vs Gringo

The user's title attribution is a system-paper paraphrase. Hanisch and Rauschenbach are co-authors but not the only authors.

## Retrieval Steps Performed

1. `paper-retriever` invoked with arg `Hanisch Rauschenbach 2025 ANGRY: A grounder for rule-based argumentation`.
2. Initial verbatim S2 search returned unrelated noise (CMS/LHCb particle-physics paper).
3. S2 search for "ANGRY grounder rule-based argumentation" returned the right paper as top hit.
4. Cross-checked arxiv search "ANGRY Hanisch Rauschenbach" — same paper appears.
5. `fetch_paper.py 2508.10976` succeeded: PDF downloaded via arXiv direct (668KB, 17 pages).
6. Verified ANGRY mention in extracted text (29 occurrences).

## Files at the Paper Directory

`papers/Diller_2025_GroundingRule-BasedArgumentationDatalog/`:

- `paper.pdf` — 668 KB, 17 pages (downloaded fresh by retriever).
- `metadata.json` — re-written by retriever today.
- `pngs/page-000.png` … `page-016.png` — 17 PNG page images (pre-existing from prior run).
- `notes.md` — 23 KB, comprehensive paper-reader output dated 2026-04-10. Frontmatter says `produced_by: agent: claude-opus-4-6, skill: paper-reader`. Covers all sections: one-sentence summary, problem, contributions, methodology, key equations, parameters table, methods/implementation, figures, results summary, limitations, arguments against prior work, design rationale, testable properties.
- `abstract.md` — 1.8 KB, pre-existing.
- `citations.md` — 5.9 KB, pre-existing.
- `description.md` — 0.7 KB, pre-existing.
- `claims.yaml`, `justifications.yaml`, `stances.yaml` — pre-existing propstore artifacts (NOT touched per user instruction not to invoke extract-claims, etc.).

## paper-reader Outcome

The paper-reader skill, on inspection, hit Case B "All files present" — `notes.md`, `abstract.md`, `citations.md` already exist for this paper and are correct/comprehensive. Per the skill: "Report 'Already complete,' stop."

The skill was not re-run for note regeneration; existing high-quality notes are preserved.

## Per User Instruction — Not Executed

These pipeline steps were explicitly out of scope and were NOT run:
- source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context
- source-promote, reconcile, papers/index.md update
- (paper-reader Steps 7, 8, 9 were skipped accordingly)

## Summary

Retrieval succeeded. The paper is the right one despite the title divergence: ANGRY is the system, the paper title is "Grounding Rule-Based Argumentation Using Datalog". Comprehensive notes already exist from a previous April 10, 2026 paper-reader run by claude-opus-4-6. No re-extraction needed.
