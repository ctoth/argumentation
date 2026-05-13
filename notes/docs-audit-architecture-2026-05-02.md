# docs/architecture.md audit — 2026-05-02

Scout audit of `docs/architecture.md` against current code under
`src/argumentation/`. Read-only. Cites are 1-based.

Sources consulted:
- `docs/architecture.md` (236 lines)
- `notes/readme-sync-2026-05-02.md` (drift catalogue — referenced rather than re-discovered)
- Module sample under `src/argumentation/` and `src/argumentation/solver_adapters/`
- Sibling docs under `docs/`

## 1. Verified gaps

| doc-line | claim | code-reality | recommended-action |
|---|---|---|---|
| architecture.md:9-12 | Dung extended semantics list: "naive, semi-stable, stage, CF2, ideal" | dung.py also exports `stage2_extensions`, `eager_extension`, prudent helpers (notes/readme-sync-2026-05-02.md:19) | Add stage2, eager, and prudent to the bullet, or punt to a family doc with a cross-link |
| architecture.md:20-22 | Lists `argumentation.solver_adapters.iccma_af` as a single module | `src/argumentation/solver_adapters/` is a sub-package: `__init__.py`, `clingo.py`, `iccma_aba.py`, `iccma_af.py` (verified by directory listing) | Replace with one bullet for the sub-package naming all three adapters |
| architecture.md:116-119 | "supported in-package Dung backend is `native`" | `af_sat.py` exists with `AfSatKernel`/`SATCheck`/`SATTraceSink`; `solver.py` exposes `SATConfig` (notes/readme-sync-2026-05-02.md:28,32). docs/backends.md:14-16 also lists `asp` and `sat` as routable backends | Either qualify "native is the only enumeration backend" or expand to mention SAT acceptance + ASP grounded routing |
| architecture.md:121-126 ("Backend policy") | Section is Dung-only despite the heading | ADF/SETAF/ABA backends exist via `solver.solve_adf_models`, `solve_setaf_extensions`, `solve_aba_*` (notes/readme-sync-2026-05-02.md:32) | Rename section "Dung backend policy" or extend to cover the other families |
| architecture.md:142 | "A single ICCMA `SE` answer is one witness: one ICCMA witness is not full enumeration." | Claim is correct; sentence is repetitive | Tighten: "ICCMA `SE` returns one witness, not full enumeration" |
| architecture.md:148 | Sentence begins lowercase: "unsupported combinations…" | Style nit | Capitalize "Unsupported" |
| architecture.md:150 | Names `solver_capability_matrix` | Hosted in `solver_differential.py` (notes/readme-sync-2026-05-02.md, surface tier proposal); module not named in architecture.md | Name the host module |
| architecture.md:158-164 ("Z3 usage") | "Without `z3-solver`, those functions raise a runtime error" | Verified at epistemic.py:585: `raise RuntimeError("linear epistemic constraint reasoning requires z3-solver") from exc` | PASS |
| architecture.md:168-170 | "selects among six strategies: `deterministic`, `exact_enum`, `mc`, `exact_dp`, `paper_td`, `dfquad_quad`, and `dfquad_baf`" | Count says six; list has seven. notes/readme-sync-2026-05-02.md:11 already records seven distinct strategies branched at probabilistic.py:682,694,709,721,745,757-762 | Change "six" → "seven", or split as "5 PrAF + 2 DF-QuAD" |
| architecture.md:182 | "treewidth ... at most the cutoff (default twelve)" | Verified at probabilistic.py:659 — `treewidth_cutoff: int = 12` | PASS |
| architecture.md:194-197 | exact_dp "effective in practice for primal-graph treewidth ≤ ~15" | Aligns with probabilistic_treedecomp.py per notes/readme-sync-2026-05-02.md:12 | PASS |
| architecture.md:226-229 | Non-goals lists "CLI presentation" | `iccma_cli.py` exists with argparse `main(argv)` (notes/readme-sync-2026-05-02.md:31). Not registered as a console script in pyproject. | Reconcile: drop "CLI presentation" from non-goals, or qualify it to "no application CLI; an ICCMA-protocol entry point is provided for solver-protocol parity" |

## 2. Undocumented architectural surfaces (architecture.md scope)

These modules exist in `src/argumentation/` but are absent from architecture.md "Modules" (`docs/architecture.md:7-119`). Sourced from notes/readme-sync-2026-05-02.md:22-39 plus directory listing.

| Module | Belongs in architecture.md? | Rationale |
|---|---|---|
| `aba_asp` | yes (one bullet) | ABA solver path; companion to `aba` |
| `aba_sat` | yes (one bullet) | ABA solver path; companion to `aba` |
| `af_sat` | yes (one bullet) | SAT acceptance kernel for Dung; architectural peer of `sat_encoding` |
| `backends` | yes (one bullet) | Cross-cutting capability detection + default routing — already referenced indirectly by the Backend policy section |
| `datalog_grounding` | yes (one bullet) | Cross-cutting projection layer (Gunray → ASPIC+) |
| `iccma_cli` | conditional | Document only if CLI status changes (see notes/readme-sync-2026-05-02.md:154 open Q1) |
| `solver_results` | mention under "Solver contracts" | Names the typed unavailable/process/protocol error dataclasses already alluded to at architecture.md:148 |
| `solver_differential` | yes (one bullet) | Hosts `solver_capability_matrix` named at architecture.md:150 — currently unattributed |
| `solver_adapters/clingo` | fold into `solver_adapters` bullet | Architectural peer of `iccma_af` |
| `solver_adapters/iccma_aba` | fold into `solver_adapters` bullet | Same |
| `probabilistic_components` | already present (architecture.md:75) | PASS |
| `probabilistic_treedecomp` | already present (architecture.md:80) | PASS |
| `encodings/` (LP files) | optional | Mention under "Backend policy" if exhaustiveness desired; otherwise omit |

Family-specific docs (`backends.md`, `caf-semantics.md`, `setaf.md`,
`iccma-data.md`, `iccma-2025-data.md`) already exist; architecture.md
should cross-link rather than duplicate their depth.

## 3. Code-example verification

architecture.md contains no executable code examples. No FAIL cases.

## 4. Citation/reference audit

Cross-checked against notes/readme-sync-2026-05-02.md:64-80.

| Citation in architecture.md | Status | Notes |
|---|---|---|
| Dung 1995 (l.9) | still-correct | |
| Caminada 2011 (l.11) | review needed | Original is COMMA 2006; 2011 is journal version (notes/readme-sync-2026-05-02.md:67) |
| Gaggl & Woltran 2013 (l.11-12) | still-correct | |
| Dung-Mancarella-Toni 2007 (l.12) | still-correct | |
| Modgil & Prakken 2018 (l.25) | still-correct | |
| Lehtonen, Niskanen & Järvisalo 2024 (l.27) | still-correct | |
| Bondarenko et al. 1997, Čyras & Toni 2016 (l.34) | still-correct | |
| Brewka & Woltran 2010, Brewka et al. 2013 (l.37) | still-correct | |
| Cayrol-style bipolar (l.46/61) | review needed | Open question 2004 vs 2005 (notes/readme-sync-2026-05-02.md:73) |
| Baumann 2015, Diller 2015 (l.68) | still-correct | |
| Cayrol 2014 (l.69) | needs-update | af_revision.py:335 cites JAIR 38 (2010), not 2014 (notes/readme-sync-2026-05-02.md:74) |
| Li et al. 2012 (l.73) | still-correct | |
| Popescu & Wallner 2024 (l.74) | still-correct | |
| Freedman et al. 2025 (l.74) | still-correct | |
| Hunter & Thimm 2017 Prop 18 (l.76-77) | still-correct | |
| Al Anaissy et al. 2024 (l.94) | still-correct | |
| Atkinson & Bench-Capon (l.106-107) | still-correct (no year) | Add year for parity |
| Modgil & Prakken 2018 Def 19 (l.115) | still-correct | |
| Modgil & Prakken 2018 Def 14 + Dung 1995 Def 6 (l.219-221) | still-correct | |

## 5. Prose recommendations (severe issues only)

- architecture.md:168-170 list/count mismatch (six vs. seven) is the single most user-confusing defect. Fix first.
- architecture.md:7-119 "Modules" is one ~30-bullet flat list. Group by tier (Core / Structured / Quantitative / Probabilistic / Specialized / Dynamics / Encoding-interop / Solver-orchestration / LLM) per the proposal in notes/readme-sync-2026-05-02.md:84-150 so the doc teaches the kernel's tier structure rather than presenting alphabetical noise.
- architecture.md:135-154 "Solver contracts" mixes three concerns: result-type taxonomy, ICCMA routing, capability-matrix promise. Split into two subsections.
- architecture.md:121-132 "Backend policy" is Dung-only despite the broad heading; either rename or extend to cover the other families.
- architecture.md:142 sentence is repetitive; architecture.md:148 starts lowercase. Both are quick edits.

## 6. Cross-doc dependencies

architecture.md does not link to any sibling doc. Sibling docs in `docs/`:

- `backends.md` — overlaps with architecture.md "Backend policy" and "Z3 usage". docs/backends.md:1-17 documents `default_backend(...)` rule (`weakest_link`/`grounded`/`asp`/`sat`/`materialized_reference`); architecture.md does not mention this surface.
- `caf-semantics.md` — depth for CAF (architecture.md:46-47).
- `setaf.md` — depth for SETAF (architecture.md:38-41).
- `iccma-data.md`, `iccma-2025-data.md` — likely overlap with "Solver contracts" (ICCMA routing); not deeply read this pass.
- `gaps.md` — likely tracks open work; potential overlap with "Non-goals".

Recommendation: architecture.md should add a bottom "See also" pointing to each sibling, and explicitly defer ASP/SAT routing detail to `backends.md` rather than restate it.

## 7. Verdict

architecture.md is structurally sound and citation-rich but has slipped behind the codebase: it omits `af_sat`, `aba_asp`, `aba_sat`, `backends`, `datalog_grounding`, `solver_differential`, and `solver_results`; it contradicts the code on the strategy count (six vs. seven) and the CLI non-goal; it leaves `solver_adapters` mis-described as a single module; and the `solver_capability_matrix` host module is unnamed. A targeted rewrite plus light tier-grouping can fix every gap without restructuring the whole doc.
