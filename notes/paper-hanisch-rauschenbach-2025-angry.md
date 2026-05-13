# ANGRY paper retrieval — Hanisch & Rauschenbach 2025

## 2026-05-02 — Retrieval checkpoint

**Task:** Retrieve "ANGRY: A grounder for rule-based argumentation" via paper-retriever, then paper-reader. No full pipeline.

**Searched titles:**
- Verbatim title via S2: returned unrelated CMS/LHCb paper (search noise).
- "ANGRY grounder rule-based argumentation" via S2: top hit is a strong candidate.
- arxiv "ANGRY Hanisch Rauschenbach": same candidate appears as #2.

**Strong candidate identified:**
- Title: "Grounding Rule-Based Argumentation Using Datalog"
- Authors: Martin Diller, Sarah Alice Gaggl, Philipp Hanisch, Giuseppina Monterosso, Fritz Rauschenbach
- Year: 2025
- arxiv: 2508.10976
- DOI: 10.48550/arXiv.2508.10976
- Abstract describes a Datalog-based grounding procedure for ASPIC+ — matches "grounder for rule-based argumentation".

**Mismatch consideration:** The requested title is "ANGRY: A grounder for rule-based argumentation" — title differs. Candidates: (a) ANGRY is the system name described in this paper (not in the title) and the requested title may be a system-paper variant; (b) there is a separate ANGRY paper. Authors Hanisch and Rauschenbach are both on the candidate. Topic, year, and authors all align. No other ANGRY-named argumentation paper appeared in arxiv search.

**Decision:** Proceed with arXiv 2508.10976 download. After download, verify by checking the paper content for "ANGRY" mention. If the paper does not refer to ANGRY as a system name, report mismatch.

**Next steps:**
1. Run fetch_paper.py on arxiv 2508.10976.
2. Verify paper.pdf is real and contains ANGRY system reference.
3. If verified, run paper-reader.
4. Write final report to reports/paper-hanisch-rauschenbach-2025.md.

## 2026-05-02 — Download checkpoint

**Downloaded:** papers/Diller_2025_GroundingRule-BasedArgumentationDatalog/paper.pdf (668KB, 17 pages, arXiv 2508.10976).

**ANGRY verification:** Searched the extracted text for "ANGRY" — zero matches. The paper does NOT use the name ANGRY. The system described is the Datalog-based grounding procedure for ASPIC+; if it has a name, it is not ANGRY.

## 2026-05-02 — Identity confirmed

The earlier "0 ANGRY hits" was a regex artifact (line breaks). The PDF actually mentions ANGRY 29 times. Key excerpts:

- "We present a prototype grounder, ANGRY, which utilizes the Datalog engine Nemo"
- "evaluate ANGRY as part of a ground+solve pipeline for ASPIC+"
- "implemented in the prototypical grounder ANGRY (Monterosso et al. 2025a), which is written in Rust"

**Verdict:** This IS the right paper. ANGRY is the system name; the published title is "Grounding Rule-Based Argumentation Using Datalog" (arXiv 2508.10976). The user's reference to "ANGRY: A grounder for rule-based argumentation" is a system-paper paraphrase.

**Note on authorship:** The full author list is Diller, Gaggl, Hanisch, Monterosso, Rauschenbach — Hanisch and Rauschenbach are co-authors but not the full set. Matches user's hint of "Hanisch and Rauschenbach 2025".

**Next:** Run paper-reader on papers/Diller_2025_GroundingRule-BasedArgumentationDatalog/.
