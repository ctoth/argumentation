# Docs update — 2026-04-26

## GOAL
Plan a user-facing docs update. Q said "check it all out and all user-facing
docs/readme/etc. go grok state."

## OBSERVED — user-facing surfaces today
- `README.md` (15756 bytes, last edit Apr 25 19:54)
- `docs/architecture.md` (only file in docs/)
- `CITATIONS.md` (single section: dung.stable_extensions only)
- `CONTRIBUTING.md` (resurrected — readme-overhaul note said it was deleted; was re-added)
- `pyproject.toml` keywords/classifiers
- PyPI dist: `formal-argumentation` 0.1.0 already published (per pypi-publish.md)

## OBSERVED — package surface today (src/argumentation/*.py vs __init__)
24 modules on disk. `__init__.py` re-exports 18 modules:
af_revision, accrual, aspic, aspic_encoding, aspic_incomplete, bipolar, dung,
gradual, iccma, labelling, partial_af, preference, probabilistic, ranking,
sat_encoding, semantics, value_based, weighted.

NOT re-exported (intentional — solver/backend internals):
dung_z3, solver, probabilistic_components, probabilistic_dfquad,
probabilistic_treedecomp.

## OBSERVED — gap (modules missing from README)
README mentions: dung, aspic, bipolar, partial_af, af_revision, probabilistic,
ranking, weighted, gradual, value_based, accrual, dung_z3, semantics, preference.
README does NOT mention: **labelling, sat_encoding, iccma, aspic_encoding,
aspic_incomplete**.

docs/architecture.md module list also MISSING: labelling, sat_encoding, iccma,
aspic_encoding, aspic_incomplete.

## OBSERVED — recent feature work since last user-facing-doc touch
README last edited Apr 25 19:54. Architecture last touched in commit 07ccb33
"docs: update architecture module inventory" — but I haven't yet diffed to confirm
which modules were added there. The recent `docs:` commits cc903a6 / 62032b1 /
6fee5be / 50fc0d0 appear to live in `plans/` (workstream ledger), not user docs.

Major features the kernel has gained that the README/architecture appear to
not yet describe (from commit subjects):
- **Dung semantics expansion**: ideal, range-based (semi-stable / stage), CF2
- **labelling.py**: Dung labelling primitives + accrual grounded labelling
- **sat_encoding.py / iccma.py**: stable CNF encoding + ICCMA AF IO
- **aspic_encoding.py**: deterministic ASPIC encoding + module export
- **aspic_incomplete.py**: incomplete ASPIC completion oracle + module export
- **typed aspic backend dispatch**: aspic grounded query surface, backend absence result
- **subjective aspic theory projection**
- **gradual.shapley_impact** (in addition to revised direct impact)
- **probabilistic_treedecomp**: paper TD row introduction / forget+join /
  exact extension evaluator / lifted witnesses / strategy routing —
  this is the FULL Popescu-Wallner DP, superseding the README's caveat
  "not the full Popescu & Wallner I/O/U witness-table DP"
- **typed solver backend availability** + **ASPIC abstract projection**

Plus AF-revision and partial-AF correctness tightening (kernel union deletes
stable-redundant attacks; merges report candidate ceilings; Cayrol classifier
fixes) — internal correctness, less doc-relevant unless we surface it.

## NOT YET CHECKED
- `plans/*.md` content — confirm those `docs:` commits are workstream-internal
  not user-facing (high confidence yes, but unverified).
- Architecture.md vs commit 07ccb33 diff — what new modules did that doc commit
  add? Need to confirm what's still missing.
- Whether `labelling`, `sat_encoding`, `iccma`, `aspic_encoding`,
  `aspic_incomplete` have docstrings I should pull from.
- Whether the README's exact-DP caveat ("not the full Popescu & Wallner ...")
  is still true after the paper-TD evaluator landed.
- CONTRIBUTING.md was deleted per readme-overhaul.md but currently exists —
  is the current version Q's, or was it re-added? File mtime says Apr 18 15:28
  which actually predates the deletion claim. Check git history.
- Whether PyPI-published 0.1.0 README/metadata has drifted from current source.
- LICENSE file — release-review.md flagged absence as a blocker. Still missing
  per `ls` — unrelated to docs but should at least mention.

## PLAN SHAPE (draft, to refine after gap-confirmation)
1. README: add Dung labelling + extra semantics (ideal/CF2/range), ICCMA IO,
   stable CNF encoding, ASPIC encoding/incomplete, paper-TD probabilistic
   strategy. Update probabilistic-DP caveat.
2. docs/architecture.md: add labelling, sat_encoding, iccma, aspic_encoding,
   aspic_incomplete to module list. Update probabilistic backend routing if
   paper-TD changes it.
3. CITATIONS.md: extend to cover the new cited algorithms (CF2, ideal, range,
   Popescu-Wallner full DP, etc.) — currently only documents one stable-ext
   semantic decision.
4. CONTRIBUTING.md: confirm Q's intent (currently exists, prior note said
   deleted).
5. Decide on a CHANGELOG since 0.1.0 is published — release-review.md flagged
   absence.

## BLOCKER
None. Plan approved phases 1, 2, 4, 3. Items 13/14 dropped.

## VERIFIED API surfaces (post-approval read)
**labelling**: `Label{IN,OUT,UNDEC}`, `Labelling` (from_statuses, from_extension,
in_arguments, out_arguments, undecided_arguments, range, extension).
**sat_encoding**: `CNFEncoding`, `encode_stable_extensions`,
`stable_extensions_from_encoding`. Stable only — not preferred/complete.
**iccma**: `parse_af`, `write_af`. ICCMA `p af n` numeric format. Defeats only.
**aspic_encoding**: `ASPICEncoding`, `ASPICQueryResult`, `encode_aspic_theory`
(Lehtonen-Niskanen-Järvisalo 2024 ASP fact vocabulary), `solve_aspic_grounded`
(materialized reference projection backend), `solve_aspic_with_backend`
(returns status="unavailable_backend" when not registered).
**aspic_incomplete**: `PartialASPICTheory`, `IncompleteASPICResult`,
`evaluate_incomplete_grounded`. Statuses: stable / relevant / unknown /
unsupported (Odekerken/Diller/Borg style). Exhaustive completion enumeration.
**dung extras**: `semi_stable_extensions` (Caminada 2011), `stage_extensions`,
`naive_extensions`, `cf2_extensions` (Gaggl-Woltran 2013), `ideal_extension`
(Dung-Mancarella-Toni 2007). All accept `backend="auto"|"brute"` (no Z3 yet).
**gradual extras**: `shapley_attack_impacts` (Al Anaissy 2024 Def 13), exact
Shapley over coalitions of other attacks on the same target.

## VERIFIED probabilistic router (probabilistic.py)
- Strategies: auto, exact_enum, exact_dp, paper_td, mc, dfquad_quad, dfquad_baf,
  deterministic. **`paper_td` is a NEW strategy not mentioned in current README.**
- `treewidth_cutoff: int = 12` — confirms architecture.md's "default twelve".
- Auto: small AF (<=13 args) → exact_enum; relation-rich → MC; defeat-only +
  treewidth <= cutoff + grounded → exact_dp; else → MC.
- exact_dp limitation per `probabilistic_treedecomp.py` docstring: still NOT
  the full Popescu-Wallner I/O/U DP; row count O(2^|defeats| * 2^|args|);
  effective for treewidth ≤ ~15.
- **`paper_td` strategy** appears to be a separate explicit-only path (need
  to read its body to be sure). Currently unmentioned in user docs.

## REVISED PLAN deltas
- README needs to mention `paper_td` strategy alongside exact_dp, with the
  caveat that auto-routing uses exact_dp and `paper_td` is opt-in.
- README ASPIC section gets a NEW subsection covering `solve_aspic_grounded`
  + `solve_aspic_with_backend` + `encode_aspic_theory` + `aspic_incomplete`.
- README Dung section gets paragraphs for ideal/CF2/semi-stable/stage/naive.
- Stage and CF2 are brute-only currently — call this out in the docs.
- Labelling section: introduce `Labelling.from_extension` as the bridge from
  extensions → labellings.
- Architecture.md probabilistic backend routing section needs `paper_td`
  added as a fifth strategy distinct from `exact_dp`.

## NEXT
- Read `_compute_paper_td` to know what it does that exact_dp doesn't.
- Then write README + architecture.md changes.
- Then keywords in pyproject.toml.
- Then audit CITATIONS.md for any new divergences.

## STATUS — execution log

### paper_td confirmed (probabilistic.py L1237+)
- `_compute_paper_td` calls `compute_paper_exact_extension_probability`
- Only accepts `query_kind="extension_probability"`, requires `queried_set`
- `paper_conformance: "popescu_wallner_2024_algorithm_1"` in metadata
- Distinct from `exact_dp` which is grounded-acceptance edge-tracker
- Auto-router does NOT pick paper_td (opt-in only)

### README.md edits — DONE
- Dung section: added paragraph for naive/semi_stable/stage/cf2/ideal with code
  block and citations (Caminada 2011, Gaggl-Woltran 2013, DMT 2007).
- Dung section: added "Three-valued labellings" subsection with `Labelling`
  and `from_extension`.
- Added new "ASPIC+ encodings and incomplete reasoning" section (after ASPIC+):
  encode_aspic_theory, solve_aspic_grounded, solve_aspic_with_backend,
  PartialASPICTheory, evaluate_incomplete_grounded. Cites Lehtonen 2024 and
  Odekerken-Borg-Bex 2023.
- Probabilistic strategy list: bumped from "five" to "six" strategies; added
  `paper_td` entry; rewrote `exact_dp` caveat to match the module docstring's
  honest "not better than brute-force, effective for treewidth ≤ ~15".
- Gradual section: added `shapley_attack_impacts` with code + Al Anaissy 2024.
- Added new "ICCMA interop and pure SAT encoding" section before Z3 backend:
  `parse_af`, `write_af`, `encode_stable_extensions`,
  `stable_extensions_from_encoding`.

### docs/architecture.md edits — DONE
- Module list: added labelling, sat_encoding, iccma, aspic_encoding,
  aspic_incomplete; expanded dung entry for the additional semantics; expanded
  gradual for shapley.
- Probabilistic backend routing: bumped to six strategies; added paper_td
  paragraph (paper-faithful Popescu-Wallner Alg 1, opt-in); revised exact_dp
  caveat with the brute-force-asymptotic note.

### pyproject.toml — DONE
- Added keywords: aspic-plus, incomplete-argumentation, ranking-semantics,
  argument-labelling, iccma.

### REMAINING
- CITATIONS.md audit. Current scope is divergence-from-paper notes only.
  Need to check if any of the new modules embed deliberate divergences.
  My current read: aspic_encoding follows Lehtonen 2024 fact vocab as-is
  (no deliberate divergence flagged in module docstring). aspic_incomplete
  uses "Odekerken/Diller/Borg style" with status vocab matching the paper.
  paper_td asserts "popescu_wallner_2024_algorithm_1" conformance.
  exact_dp DOES diverge (adapted edge-tracker, not full I/O/U DP) — but
  this divergence is already documented in the module docstring AND in the
  README. May be worth surfacing in CITATIONS as well for completeness.

## BLOCKER
None. About to verify the README still parses end-to-end (mental scan of the
new sections for broken anchors), then audit CITATIONS, then report.

## FOLLOW-ON: SOTA workstream spec drafted
Q asked for a full workstream that another agent will execute. Drafted
`plans/sota-completeness-and-ecosystem-workstream-2026-04-26.md` (863 lines).

Structure: 12 phases (0=baseline, 1=self-confessed gaps, 2=ICCMA ecosystem,
3=ADFs, 4=ABA+ABA+, 5=SETAFs, 6=Enforcement, 7=CAFs, 8=Dynamic, 9=Approximate,
10=Epistemic graphs, 11=ArgLLM surface, 12=Quality bar/release).

Real SOTA papers cited (web-researched, not memory-cited):
- Meier-Niskanen-Mailly 2024 KR (arxiv 2407.05058) — bag-local PrAF DP
- Lehtonen-Niskanen-Järvisalo 2024 — ASPIC ASP
- Niskanen-Wallner-Järvisalo 2020 — mu-toksia
- Bistarelli-Kotthoff-Lagniez 2025 AAC — ICCMA report
- Brewka-Strass 2013 IJCAI — ADFs
- Linsbichler-Pichler-Spendier 2022 AI 305 — ADF SAT solving
- Keshavarzi-Zafarghandi 2022 AAC — strong-admissible ADFs
- Bondarenko-Dung-Kowalski-Toni 1997 AI 93 — ABA
- Cyras-Toni 2016 KR — ABA+
- Apostolakis-Toni-Rapberger 2024 KR — ABA abstraction
- Rapberger 2024 AAAI — ABA+ via set-to-set attacks
- Nielsen-Parsons 2006 — SETAFs
- Dvořák-König-Woltran 2024 JAIR 79 / 2025 JOAR — collective attacks
- Flouris-Bikakis IJCAI 2024 — collective attack acceptance
- Baumann 2012 ECAI — enforcement
- Wallner-Niskanen-Järvisalo 2017 JAIR 60 — extension enforcement
- Mailly 2024 AIC — constrained incomplete
- Dvořák-Greßler-Rapberger-Woltran 2023 AI 322 — CAFs
- Skiba-Thimm 2024 KR — k-stable approximation
- Hunter-Polberg-Thimm 2018-2020 AI — epistemic graphs
- Bona-Hunter-Vesic 2019 TAFA — polynomial epistemic updates
- Fichte-Hecher-Meier 2024 JAIR — counting via TD
- Freedman-Toni 2024-2025 AAAI — ArgLLMs

Control rule unique to this workstream: "Reach up, not down" — when given a
chance to do less, do more. Per Q's instruction to the executing agent.
