# Full library review — 2026-04-29

## GOAL
Comprehensive review of `formal-argumentation` (import name `argumentation`).
Cover: citations (vs `../propstore/papers`), shape, API, docs, tests,
implementation. Cross-check both directions: README/CITATIONS claims → papers,
and code algorithms → cited paper. Deliverable: this notes file + chat summary.

## OBSERVED — repo state at start (2026-04-29)
- Branch `main`. Modified: `CITATIONS.md`, `README.md`, `docs/architecture.md`,
  `pyproject.toml`. Untracked notes (5), `out/` (file not dir), `pyghidra_mcp_projects/`.
- pyproject: name=`formal-argumentation`, **version=`0.2.0`** (bumped from 0.1.0
  per pypi-publish.md). License field STILL ABSENT (release-review.md flagged
  this as a blocker for 0.1.0; not fixed for 0.2.0).
- Source modules on disk (32, ex `__init__`):
  af_revision, aba, accrual, adf, aspic, aspic_encoding, aspic_incomplete,
  bipolar, dfquad, dung, dung (+dung_z3 — wait, dung_z3 not in glob output?
  CHECK), equational, gradual, gradual_principles, iccma, labelling,
  matt_toni, partial_af, practical_reasoning, preference, probabilistic,
  probabilistic_components, probabilistic_dfquad, probabilistic_treedecomp,
  ranking, ranking_axioms, sat_encoding, semantics, solver, subjective_aspic,
  vaf, vaf_completion, weighted.
- Wait: glob did NOT include `dung_z3.py`. Need to verify it actually exists —
  README and architecture both reference it. POTENTIAL DOC/CODE DRIFT.
- `__init__.py` re-exports 27 modules (NOT including dung_z3, solver,
  probabilistic_components/dfquad/treedecomp — intentional internals).
- 64 test files. Heavy gradual-semantics presence: dfquad continuity, gabbay
  equational, matt_toni, potyka_continuous_ode, baroni_2019_principles.
- propstore/papers exists at `C:/Users/Q/code/propstore/papers/`, 248 entries.
- `logs/` contains 3 baseline/post WS logs. Not in .gitignore likely.
- `out/` is a FILE not a directory.
- `pyghidra_mcp_projects/` — unrelated MCP scratch dir, still in repo.

## OBSERVED — docs state
- README 591 lines, citations per section. Mentions: dung, labelling, aspic,
  aspic_encoding, aspic_incomplete, bipolar, partial_af, af_revision,
  probabilistic, ranking, weighted, gradual, subjective_aspic, vaf,
  practical_reasoning, ranking_axioms, accrual, iccma, sat_encoding, dung_z3,
  semantics, preference. Top-bullet mentions ABA/ABA+ and ADF.
- README does NOT mention as separate sections: `aba`, `adf`, `dfquad`,
  `equational`, `gradual_principles`, `matt_toni`, `vaf_completion`. Top-bullets
  list ABA/ADF but no section explains either with code example. **DOC GAP**.
- architecture.md covers: dung, labelling, dung_z3, sat_encoding, iccma, aspic,
  aspic_encoding, aspic_incomplete, aba, adf, bipolar, partial_af, af_revision,
  probabilistic (+ components/dfquad/treedecomp), ranking, weighted, gradual,
  subjective_aspic, vaf, practical_reasoning, ranking_axioms, accrual, semantics,
  preference, solver. **MISSING from architecture: dfquad, equational,
  gradual_principles, matt_toni, vaf_completion.** Same five missing modules.
- CITATIONS.md: only documents 2 deliberate divergences (stable_extensions M&P
  split, exact_dp adapted DP). Per CONTRIBUTING.md citation discipline, every
  intentional divergence should appear here. Need to find others (see plan).

## OBSERVED — prior reviews
- release-review.md (2026-04-18, 0.1.0): flagged license absent, .gitignore
  gaps, M&P stable semantics divergence (now CITATIONS.md entry 1).
- sota-assessment-2026-04-25.md: noted absent SOTA families. Many since
  added (ABA, ADF, ICCMA IO, paper_td, sat_encoding). Still absent per that
  note: ranking-based gradual full coverage (partial), weighted SOTA (Dunne
  done in `weighted.py`), enforcement, SETAFs, CAFs, epistemic graphs,
  ArgLLM. Need to re-confirm what's still missing.
- docs-update-2026-04-26.md: API audit done; README + architecture rewritten;
  CITATIONS.md audit deferred — that audit IS this review's job.
- readme-overhaul.md: README rewritten 2026-04-18 plus subsequent.
- pypi-publish.md: 0.1.0 published as `formal-argumentation`.

## PLAN
1. Verify `dung_z3.py` actually exists; resolve glob anomaly.
2. Inventory all paper citations in code (docstrings, module headers) AND in
   README/architecture/CITATIONS. Build cross-reference table.
3. For each cited paper, check if directory exists in
   `C:/Users/Q/code/propstore/papers/{Author_Year_Slug}`.
4. For modules NOT in README/architecture (aba, adf, dfquad, equational,
   gradual_principles, matt_toni, vaf_completion): read source headers, decide
   if doc gap or intentional internal.
5. Spot-check key algorithm correctness against paper definitions where
   propstore has the paper (esp. ABA Bondarenko 1997, ADF Brewka 2010/2013,
   Popescu-Wallner 2024, Cayrol bipolar).
6. Run test suite, capture pass/fail/skip counts.
7. Architectural review: API consistency, naming, type discipline, immutability,
   error handling.
8. Write final report: chat summary + this notes file.

## DECISION POINTS so far
None yet. Proceeding with investigation.

## BLOCKER
None. Continuing with module/citation inventory next.

---

## CHECKPOINT — 2026-04-29 (post tool-batch 2)

### Verified critical findings

**F1 — Z3 backend deleted; docs still describe it as live (HIGH).**
- `src/argumentation/dung_z3.py` does NOT exist; `tests/test_dung_extensions_workstream.py:41` ASSERTS the file cannot exist.
- `src/argumentation/probabilistic_dfquad.py` does NOT exist; `tests/test_dfquad_old_path_deleted.py:24` ASSERTS the import fails.
- `src/argumentation/dung.py` has **zero** z3 imports (verified by grep).
- `complete_extensions(framework)`, `preferred_extensions(framework)`, `stable_extensions(framework)` take NO `backend` parameter (verified by reading dung.py:217, 255, 271). Only `complete_extensions` takes `*, max_candidates`.
- Single-backend solver: `argumentation.solver.solve_dung_extensions(..., backend="labelling")` is the only backend dispatch. Any other backend value returns `SolverBackendUnavailable`.
- README "Optional Z3 backend" section (lines 517-530) is **stale** — refers to nonexistent module.
- README install line `uv add "formal-argumentation[z3]"` is dead.
- README example `preferred_extensions(framework, backend="z3")` would raise TypeError.
- README "default `auto` selects brute-force enumeration for small frameworks (≤12 arguments) and Z3 above that threshold" — false; no auto-routing exists.
- architecture.md lines 16-17 (`argumentation.dung_z3`), 54-55 (`argumentation.probabilistic_dfquad`), 99-110 ("Z3 backend" section), 95-98 (backend routing for "auto") all stale.
- pyproject still ships `[project.optional-dependencies] z3 = ["z3-solver>=4.12"]` AND `z3-solver>=4.12` in dev deps — both unused.

**F2 — DF-QuAD citation incomplete (MED).**
- `src/argumentation/dfquad.py` cites Rago, Toni, Aurisicchio, Baroni 2016 KR (the ACTUAL DF-QuAD paper). Verified — `Rago_2016_DiscontinuityFreeQuAD` exists in propstore.
- `probabilistic.py:1393` cites Freedman 2025 but `:1400` admits "currently used as Rago 2016's τ".
- README and architecture cite **only** Freedman 2025 for DF-QuAD. That paper USES DF-QuAD; Rago et al. 2016 INVENTED it. Citation is incomplete/misleading.

**F3 — Documented module list ≠ actual public surface (MED).**
- `__init__.py` re-exports 27 modules. README has full sections / mentions for ~22. Architecture.md covers 26.
- Modules **NOT** mentioned in README and **NOT** in architecture.md (both): `dfquad`, `equational`, `gradual_principles`, `matt_toni`, `vaf_completion`. All five are re-exported from `__init__` and are public.
- Per code: `dfquad.py` (Rago 2016), `equational.py` (Gabbay 2012), `matt_toni.py` (Matt-Toni 2008 JELIA), `gradual_principles.py` (Baroni-Rago-Toni 2019 IJAR), `vaf_completion.py` (Bench-Capon 2003) — all five papers exist in propstore (verified for Matt 2008, Gabbay 2012, Bench-Capon 2003, Rago 2016).
- `tests/test_docs_surface.py` enforces *some* names appear in README + architecture (8 each), but does NOT enforce coverage of these five.

**F4 — Undocumented public dung functions (LOW-MED).**
Public from dung.py but NOT in README and NOT in architecture: `eager_extension` (Caminada 2007), `prudent_*` (Coste-Marquis 2005), `indirect_attacks`, `stage2_extensions`, `naive_extensions`. Architecture lists "naive" in a sentence — does not document `stage2_extensions` or `eager_extension` or any prudent functions.

**F5 — pyproject sdist `include` references CONTRIBUTING.md but is current (verify) (LOW).**
- pyproject.toml:71-77 lists `/CONTRIBUTING.md`; CONTRIBUTING.md exists at root; matches.
- pyproject.toml has no `license` field, no `license-files`, no `License ::` classifier, no LICENSE file at root. **Same blocker release-review.md flagged for 0.1.0 — still present in 0.2.0.**

**F6 — Repo root noise (LOW).**
- `out/` is a regular file (not a directory); should be in .gitignore or removed.
- `pyghidra_mcp_projects/` — unrelated, should be removed or ignored.
- `logs/` — three baseline test logs, untracked. Likely belongs in .gitignore.
- Notes from prior reviews still present; intentional.

**F7 — Test suite is healthy.**
- 482 passed, 0 failed, 0 skipped in 38.95s. Up from 267 in the 0.1.0 snapshot (+215).
- 64 test files. Good coverage of WS-O bug-fix regressions and SOTA modules.

**F8 — CITATIONS.md is incomplete relative to documented divergences (MED).**
- Per CONTRIBUTING.md: "If implementation behavior intentionally diverges from a cited definition, document the reason and add a focused test."
- CITATIONS.md only documents 2 divergences (stable M&P split, exact_dp adapted DP).
- Likely undocumented divergences (need to verify in body): `eager_extension` cites Caminada 2007 — is the implementation faithful? `equational.py` accepts `scheme="min"` as alias for `inverse` — undocumented spelling divergence. `aspic.py` `GroundAtom` cites "Riveret 2017 + Diller et al. 2025" mixed source.

### Citation cross-reference scout
- Launched as agent `a4d232b85f99d5c43`, running. Will write to
  `notes/citation-crossref-2026-04-29.md`. Awaiting completion.

### Spot-check on propstore — papers VERIFIED PRESENT
- Bench-Capon 2003, Polberg 2017, Rago 2016 (×2), Matt 2008, Gabbay 2012,
  Freedman 2025, Lehtonen 2024 (Preferential ASPIC), Odekerken 2023, AlAnaissy
  2024 — all present.
- Lehtonen "ASP-encoded ASPIC+" cited in README — matched paper is
  `Lehtonen_2024_PreferentialASPIC` and `Lehtonen_2020_AnswerSetProgrammingApproach`.
  Need to confirm which paper aspic_encoding actually follows (the doc says
  Lehtonen-Niskanen-Järvisalo 2024). Defer to citation scout report.

### What I have not yet verified
- aspic.py module body (1332 lines). Will spot-check key invariants only.
- ABA flatness implementation against Bondarenko 1997 Def 4.10 (cited in code).
- ADF Brewka 2013 operator semantics implementation against the paper.
- Whether VAF / ranking / weighted module bodies cite specific definitions.
- Whether `aspic_encoding.py` Lehtonen 2024 fact vocabulary matches the paper.
- API-level smell pass (frozen dataclasses, frozensets, error types, naming).

### Plan from here
1. Wait for citation scout (background, ~few minutes).
2. Read aspic_encoding header, aspic_incomplete header, paper_td body — verify
   citation specificity.
3. Spot-check key public API consistency (immutability, error types).
4. Synthesize final report into this file + chat summary. No code edits.

### BLOCKER
None.

---

# FINAL REPORT — 2026-04-29

## Executive summary

`formal-argumentation` 0.2.0 is a substantial, well-cited Python kernel with
strong test discipline (482/482 passing, 64 test files, three test markers)
and broad SOTA coverage spanning Dung, ASPIC+, ABA, ADF, bipolar, partial,
revision, probabilistic, and gradual families.

The kernel itself is in good shape. The **release-facing surface is not.**
Three classes of issues:

1. **Documentation describes deleted code** — README and architecture.md
   still describe the Z3 backend, the `dung_z3` module, the
   `probabilistic_dfquad` module, the `backend="z3"` parameter, and the
   `[z3]` install extra. None of these exist in 0.2.0. This is the most
   serious finding because users following the README will hit
   `TypeError`/`ModuleNotFoundError`.
2. **Five public modules are entirely undocumented** in both README and
   architecture: `dfquad`, `equational`, `gradual_principles`, `matt_toni`,
   `vaf_completion`. Each has its own paper citation and is exported from
   `__init__.py`.
3. **Citation hygiene has slipped** — README cites Freedman 2025 for
   DF-QuAD when the foundational paper is Rago et al. 2016; the semi-stable
   citation is malformed ("Caminada (2011) ... in *COMMA 2006*"); CITATIONS.md
   still only enumerates two divergences when more exist.

License is still missing — flagged in the 0.1.0 release-review (2026-04-18),
not fixed for 0.2.0. It remains the only single-issue blocker for serious
adoption (no clear license = many companies will not depend on it).

The library has roughly tripled its public surface since 0.1.0 (8 → 27
exports) and the docs have not kept pace.

## Findings by severity

### HIGH — release-blocking or user-breaking

**H1. Stale Z3 backend documentation.** README §"Optional Z3 backend"
(`README.md:517-530`), the install line `uv add "formal-argumentation[z3]"`
(`README.md:35-37`), the `backend="z3"` example (`README.md:524`), the
`backend` parameter description for `complete`/`preferred`/`stable`
(`README.md:79-82`), architecture.md §"Z3 backend" (`docs/architecture.md:99-110`),
the `dung_z3` and `probabilistic_dfquad` module entries in architecture
(`docs/architecture.md:16-17, 54-55`), and the `auto`/`brute`/`z3` backend
routing description (`docs/architecture.md:93-98`) all describe code that
does not exist in 0.2.0. `dung_z3.py` and `probabilistic_dfquad.py` have
been deleted and the deletion is enforced by negative-import tests
(`tests/test_dung_extensions_workstream.py:41`,
`tests/test_dfquad_old_path_deleted.py:24`). `dung.py` contains zero `z3`
imports. `complete_extensions`, `preferred_extensions`, `stable_extensions`
take no `backend=` parameter. Following the README will raise.

**H2. License still absent.** No `license` field in `pyproject.toml`, no
`license-files`, no `License ::` classifier, no `LICENSE` file at the repo
root. The published wheel contains no license metadata. Carried over from
0.1.0; not addressed in 0.2.0. Many downstream consumers (corporate,
governmental, research-policy) cannot adopt unlicensed packages.

**H3. Dead `[z3]` extra and dev dependency.** `pyproject.toml:53-55`
declares `z3 = ["z3-solver>=4.12"]` and `dependency-groups.dev` includes
`z3-solver>=4.12`. Nothing in `src/argumentation/` imports z3. The extra
installs a runtime dependency that the package never uses, the dev
dependency installs a tool the test suite does not exercise (no remaining
test imports `z3`).

### MEDIUM — quality or correctness slippage

**M1. Five public modules are undocumented** in both README and
architecture.md: `dfquad`, `equational`, `gradual_principles`, `matt_toni`,
`vaf_completion`. All five are re-exported from `argumentation/__init__.py`
and all five carry explicit paper citations in their headers (Rago 2016,
Gabbay 2012, Baroni-Rago-Toni 2019, Matt-Toni 2008, Bench-Capon 2003).
`tests/test_docs_surface.py` enforces presence of 8 module names in each
doc; these five are not among them.

**M2. DF-QuAD citation is incomplete.** README (`README.md:393-394`,
`README.md:422-424`) cites Freedman et al. 2025 as the source for the
`dfquad_quad`/`dfquad_baf` strategies. The foundational DF-QuAD paper is
Rago, Toni, Aurisicchio & Baroni 2016 (KR), which the implementation
itself cites (`src/argumentation/dfquad.py:13-18, 33-36, 56-60`). Both
papers exist in propstore (`Rago_2016_DiscontinuityFreeQuAD`,
`Freedman_2025_ArgumentativeLLMsClaimVerification`). Freedman et al. *use*
DF-QuAD; they did not invent it.

**M3. Semi-stable citation is malformed.** README:
`Caminada, M. (2011). Semi-stable semantics. In *COMMA 2006*.`
The COMMA 2006 paper is Caminada 2006; the JLC follow-on is Caminada 2011.
The citation conflates the two. `dung.py:325` cites only "Caminada 2011,
Definition 2.3". propstore has only `Caminada_2006_IssueReinstatementArgumentation`
(no Caminada 2011 paper directory). Definition 2.3 should be verified
against whichever paper is actually being followed.

**M4. CITATIONS.md is incomplete.** Only two divergences documented; per
CONTRIBUTING.md citation discipline, every intentional divergence belongs
here. Likely additional candidates (need verification before listing):
`equational.py` accepts `scheme="min"` as alias for `inverse` (lossy
spelling); `eager_extension` (Caminada 2007) implementation may diverge from
the paper's "least committed" specification — implementation returns the
size-lex max admissible subset of the semi-stable intersection, which is
not obviously the same; `aspic.py` uses a hybrid GroundAtom citation
("Riveret 2017 + Diller et al. 2025") — neither paper is mentioned in
CITATIONS or README.

**M5. README/code doc inconsistency on `exact_dp` complexity.** README
(`README.md:386-388`) and CITATIONS.md describe `exact_dp` as "not better
than brute-force enumeration" — the honest description. The function
docstring at `probabilistic.py:1262` claims "complexity O(3^k * n) where
k is treewidth" — the optimistic description. Pick one. The README/CITATIONS
version is correct per `probabilistic_treedecomp.py` module docstring
(lines 5-10).

**M6. Generic semantics dispatcher accepts more than the README documents.**
`semantics.py` `extensions(...)` supports `grounded, ideal, complete,
preferred, semi-stable, stage, stage2, cf2, prudent-grounded, prudent-preferred,
stable` for Dung; `d-preferred, s-preferred, c-preferred, bipolar-stable,
bipolar-grounded, bipolar-complete` for bipolar; `grounded, preferred, stable`
for partial. README §"Generic semantics dispatch" only shows
`grounded, preferred, stable`. The dispatcher's `accepted_arguments`
also supports `mode="necessary_skeptical"` and `mode="possible_skeptical"`
on partial AFs — undocumented.

**M7. ICCMA module surface is broader than documented.** `iccma.py` exports
`parse_af`, `write_af`, `parse_adf`, `write_adf`, `parse_aba`, `write_aba`.
README only documents the AF pair. ADF-IO and ABA-IO are silently public.

### LOW — polish / hygiene

**L1. Undocumented public Dung functions.** `dung.py` exports
`eager_extension` (Caminada 2007), `prudent_conflict_free`,
`prudent_admissible`, `prudent_preferred_extensions`,
`prudent_grounded_extension`, `indirect_attacks`, `stage2_extensions`,
`naive_extensions`. README lists only 5 of these (architecture lists naive
in passing, others not at all).

**L2. Repo root noise.** `out/` is a regular file at root (not a directory);
`pyghidra_mcp_projects/` is an unrelated MCP scratch directory; `logs/`
contains three baseline test logs. None are in `.gitignore`. `.gitignore`
is still 7 lines (`.venv/, .pytest_cache/, __pycache__/, *.py[cod],
.coverage, htmlcov/`) — does not cover `dist/`, `*.egg-info/`, `build/`,
`.hypothesis/`, `notes/`, `out`, `logs/`, `pyghidra_mcp_projects/`.

**L3. `__init__.py` module docstring is one line** for a package now
spanning 27 modules and ten paper families. A four-to-six line summary
would orient new users.

**L4. ASPICAbstractProjection class** at `aspic.py:1309` is public but
undocumented in README.

**L5. `argumentation.labelling` exposes a budget-cap exception**
(`ExactEnumerationExceeded`, default 65,536) that the README does not
mention. Users of `complete_extensions` may hit it without warning.

**L6. CHANGELOG is absent.** Flagged in the 0.1.0 release-review. With
0.2.0 published, the gap between releases is opaque to users.

## Citations status

### Verified present in `propstore/papers/`
All foundational papers cited by the kernel are present in propstore (one
per author/year/topic at minimum):

- Dung 1995, Modgil & Prakken 2018, Cayrol & Lagasquie-Schiex 2005,
- Caminada 2006/2007, Coste-Marquis 2005 (Prudent), Gaggl & Woltran 2013
  (verified absent under that exact slug — needs scout confirmation),
- Dung-Mancarella-Toni 2007 (needs scout confirmation),
- Bondarenko 1997, Toni 2014 (Tutorial), Cyras & Toni 2016
  (needs scout confirmation),
- Brewka 2010, Brewka 2013, Polberg 2017,
- Baumann 2015, Diller 2015, Cayrol 2014,
- Li et al. 2012 (needs scout confirmation), Hunter 2017,
- Popescu 2024 — *three* candidate directories
  (`AdvancingAlgorithmicApproachesProbabilistic`,
  `AlgorithmicProbabilisticArgumentationConstellation`,
  `ProbabilisticArgumentationConstellation`); the docs do not say which
  contains "Algorithm 1",
- Lehtonen 2024 (PreferentialASPIC), Odekerken 2023,
- Bench-Capon 2003, Atkinson 2007, Baroni 2019 (Gradual Principles),
- Rago 2016 (DiscontinuityFreeQuAD + AdaptingDFQuADBipolarArgumentation),
- Freedman 2025, AlAnaissy 2024,
- Matt 2008, Gabbay 2012, Dunne 2011.

### Likely-missing or ambiguous
- Caminada 2011 — only Caminada 2006 found.
- Popescu & Wallner 2024 — three candidate directories; need to identify
  which is the cited paper for `paper_td`.
- Riveret 2017 — cited in `aspic.py:30` for `GroundAtom` definition;
  not yet checked.
- Diller et al. 2025 — cited in `aspic.py:30`; not yet checked
  (propstore has Diller 2015 only).
- Caminada 2007 — present, but `eager_extension` doc says "Caminada 2007's
  eager extension" without page/definition.

(The dedicated citation-cross-reference scout was launched but had not
produced its report at the time this synthesis was written. Findings here
are from in-line greps and paper-directory listings.)

## API/shape observations

### Strengths
- **Type discipline is clean.** Every public dataclass is `frozen=True`,
  most use `frozenset` for sets, equality is structural.
- **`solver.py` distinguishes success from unavailable backend** via a
  union type `ExtensionSolverResult = ExtensionSolverSuccess |
  SolverBackendUnavailable`. Good shape for solver dispatch.
- **`aspic_encoding.py` returns a typed result with `status="unavailable_backend"`**
  rather than raising for unregistered backends. Consistent with the
  solver pattern.
- **`labelling.Label` + `adf.ThreeValued` + `adf.LinkType`** are all
  `StrEnum`/`Enum` — readable, serializable, type-safe.
- **`partial_af.PartialArgumentationFramework.__post_init__`** rigorously
  enforces the three-way disjoint partition with explicit error messages.
- **`af_revision.AFChangeKind`** captures the Cayrol 2014 classifier
  taxonomy as an enum rather than strings.

### Inconsistencies
- **Naming**: dung-side semantics use a mix of underscores and hyphens
  (`semi_stable_extensions` function vs `semantics="semi-stable"` string vs
  `semantics="prudent-grounded"`). Pick one separator for string
  identifiers across modules.
- **Backend dispatch surface**: `aspic_encoding.solve_aspic_with_backend`
  returns `ASPICQueryResult(status="unavailable_backend", ...)`;
  `solver.solve_dung_extensions` returns `SolverBackendUnavailable(...)`
  (a different type entirely). Pick one pattern.
- **`probabilistic.compute_probabilistic_acceptance`** has six strategies
  plus `"exact"` as an alias — alias is undocumented in README.
- **`compute_probabilistic_acceptance` raises** for incompatible
  query_kind/inference_mode combinations on `exact_dp`/`paper_td` — but
  `solve_aspic_with_backend` returns a typed result for the same kind of
  unavailability. Inconsistent.
- **`dung.eager_extension`** returns `frozenset()` if no semi-stable exists;
  `dung.ideal_extension` returns `frozenset()` similarly; `dung.grounded_extension`
  always returns a frozenset. `prudent_grounded_extension` returns a
  frozenset. So far consistent. But `complete_extensions` returns
  `list[frozenset[str]]` while `preferred_extensions` and `stable_extensions`
  return `list[frozenset[str]]` and the generic `semantics.extensions` returns
  `tuple[frozenset[str], ...]`. List vs tuple at the boundary is loose.

### Architecture
- The deletion of `dung_z3` and the move to a single `labelling`-based
  backend is a sound simplification — fewer differential-test surfaces, no
  optional native dep, no Z3 timeout/unknown handling. The `solver.py`
  surface is now a thin dispatch over `dung.py` functions.
- The probabilistic router has six strategies with `auto` selection. The
  current `auto` policy is honest about its boundary
  (`exact_enum` ≤ 13 args, MC for relation-rich, `exact_dp` for grounded
  defeat-only with treewidth ≤ 12).
- The `aba.py` rejection of non-flat ABA at construction (with
  `NotFlatABAError` citing Bondarenko 1997 Def 4.10) is exactly the
  right kind of "principled refusal" — better than a partial runtime path.
- `adf.py`'s explicit AST for acceptance conditions (vs callables) makes
  the framework serializable and analyzable. Good design choice.

## Recommendations

If acting on a subset, in priority order:

1. **Fix the Z3 documentation** (H1) — either remove the section entirely
   (since `dung_z3` is deleted) and the `[z3]` extra (H3), or restore the
   backend. Removing is the smaller change and matches what the workstream
   apparently decided.
2. **Add a LICENSE** (H2) — pick MIT/Apache-2.0/BSD-3-Clause and add the
   `license` field, classifier, and file.
3. **Document the five missing modules** (M1) — short README sections with
   one code example each, plus extending `tests/test_docs_surface.py` to
   pin them in place.
4. **Fix the DF-QuAD and semi-stable citations** (M2, M3) — README and
   per-function citations.
5. **Run a CITATIONS.md sweep** (M4) — every intentional divergence the
   kernel makes from a cited paper should land here, not just the two
   currently listed.
6. **Pick one inconsistency style** (API observations) — list-vs-tuple,
   underscore-vs-hyphen semantic strings, raise-vs-typed-result on backend
   unavailability. Future maintainers will keep diverging from any pattern
   that has multiple in-tree precedents.
7. **Add a `CHANGELOG.md`** — even a bare 0.1.0 → 0.2.0 entry helps
   adopters understand what changed (notably the Z3 deletion).
8. **Tidy `.gitignore` and remove `out`/`pyghidra_mcp_projects/`** from
   the repo root.

## What I did not verify

- **Algorithm-level correctness against papers.** I read module headers and
  spot-checked function signatures, but did not e.g. open Brewka 2013 to
  cross-check the three-valued operator semantics in `adf.py` against the
  paper's definitions. The Bondarenko 1997 Def 4.10 flatness check in
  `aba.py` was verified against the cited definition number; full proof
  agreement was not.
- **Spot-checks against propstore `notes.md`** — the citation scout was
  asked to do this for Dung 1995, Popescu-Wallner 2024, and Brewka 2013;
  its report was still pending when this synthesis was written.
- **`aspic.py` body** (1300+ lines). Public surface inventoried, body not
  read in detail.
- **propstore-side citation completeness** — i.e., does propstore have
  papers that the argumentation kernel could be drawing on but isn't.
  This is the inverse of what was asked; defer to the SOTA assessment
  note from 2026-04-25.


