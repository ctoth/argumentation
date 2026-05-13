# README sync scout — 2026-05-02

Phase 1 scout for README restructure of the `argumentation` Python package
(`C:\Users\Q\code\argumentation`). Read-only. All cited line numbers are 1-based.

## 1. Verified gaps (high-confidence drift)

| README section | Current claim | Code reality | Recommended action |
|---|---|---|---|
| Install (README.md:33-37) | Only the `[z3]` extra is shown | `pyproject.toml:52-61` declares three extras: `z3`, `asp` (`clingo>=5.7`), `grounding` (`gunray`, sourced from git per pyproject.toml:102-103) | Document `asp` and `grounding` extras; explain what each unlocks |
| Probabilistic argumentation (README.md:374) | "dispatches across six strategies" | Seven distinct strategy names are accepted: `deterministic`, `mc`, `exact_enum`, `exact_dp`, `paper_td`, `dfquad_quad`, `dfquad_baf`. Code branches at probabilistic.py:682, 694, 709, 721, 745, 757-762; `dfquad` is a deprecated/ambiguous alias that raises (probabilistic.py:759) | Change "six strategies" to "seven" or reorganize as "5 PrAF + 2 dfquad" |
| Probabilistic argumentation (README.md:387-388) | "exact_dp ... default when the framework has at most thirteen arguments" — wait, that's for `exact_enum`. README says exact_enum is brute-force, exact_dp is the auto-router's choice for treewidth ≤ 15 | probabilistic_treedecomp.py:14-19: known-limitation note that exact_dp gives "zero asymptotic improvement over brute-force enumeration"; effective for treewidth ≤ ~15. README and module agree, just verify wording stays accurate | Keep current explanation; tighten language |
| Ranking, weighted, gradual (README.md:434-436) | `ranking.ordered_tiers` | `RankingResult` (ranking.py:12-23) has `scores`, `ranking`, `converged`, `iterations`, `semantics` — no `ordered_tiers`. `ranking` is a `tuple[frozenset[str], ...]` of tiers | Replace `.ordered_tiers` with `.ranking` in the example |
| AF revision citations (README.md:336-341) | "Cayrol, de Saint-Cyr, & Lagasquie-Schiex (2014). Change in abstract argumentation frameworks: adding an argument." | af_revision.py:335 cites "Cayrol, de Saint-Cyr, and Lagasquie-Schiex 2010, JAIR 38, Table 3" for the seven-way classification | Reconcile dates; the JAIR 38 (2010) paper is "Change in abstract argumentation frameworks: adding an argument", not 2014 |
| Non-goals (README.md:643-648) | "does not own ... CLI presentation" | `iccma_cli.py` exists (47 lines docstring + argparse `main`); module docstring at iccma_cli.py:1 says "Command-line entry point for ICCMA-style AF and ABA solving" | Remove "CLI presentation" from non-goals OR add a "Tools / CLI" section. Note: pyproject.toml has NO `[project.scripts]` entry — the CLI exists in source but is not installed as a console script |
| Solver surfaces (README.md:570-600) | Mentions `solve_dung_single_extension`, `solve_aba_single_extension`, `solve_dung_extensions` | Confirmed: solver.py:138 (aba_single), 180 (aba_acceptance), 229 (dung_extensions), 260 (dung_single), 360 (dung_acceptance), plus `solve_adf_models` (102), `solve_setaf_extensions` (120). README does not mention `solve_adf_models` or `solve_setaf_extensions` or `solve_*_acceptance` | Add ADF/SETAF/acceptance entries to the solver section |
| Probabilistic claim (README.md:14-16) | "Probabilistic argumentation frameworks (PrAFs) with Monte Carlo, exact enumeration, tree-decomposition DP, and DF-QuAD gradual semantics" | Missing: `paper_td` paper-faithful Popescu & Wallner backend (probabilistic.py:745) is a separate code path | Mention paper_td or fold it into "tree-decomposition DP" with a footnote |
| Three-valued labellings (README.md:100-114) | Shows `Labelling.from_extension`, `in_arguments`, `out_arguments`, `undecided_arguments`, `range` | Verified labelling.py:79-126; matches | PASS — example is correct |
| `argumentation.dung` extra semantics list (README.md:84-89) | Lists `naive_extensions`, `semi_stable_extensions`, `stage_extensions`, `cf2_extensions`, `stage2_extensions`, `eager_extension`, `ideal_extension`, "prudent-semantics helpers" | All present in dung.py grep (cited above) | PASS |
| ASPIC+ surface bullet (README.md:172-181) | Lists fields/functions including `transposition_closure`, `strict_closure`, `is_c_consistent`, `CSAF` | All present (aspic.py:375, 473, 506, 1365) | PASS |

## 2. Undocumented modules

| Module | One-sentence summary (verified from source) | Recommendation |
|---|---|---|
| `aba_asp` (aba_asp.py:1) | Clingo-backed flat ABA extension queries; encodes ABAFramework into deterministic ASP facts and dispatches to the `asp` extra. | mention-in-passing — under "Solver surfaces" or new "ABA solver paths" subsection |
| `aba_sat` (aba_sat.py:1) | Task-directed support-mask SAT enumeration for flat ABA stable/complete/preferred extensions. | mention-in-passing — pair with sat_encoding section |
| `af_sat` (af_sat.py:1) | Incremental SAT kernel for Dung AFs with telemetry (`SATCheck`, `SATTraceSink`, `AfSatKernel`). | prime — promote to "SAT-backed acceptance" subsection alongside sat_encoding |
| `backends` (backends.py:1) | Capability detection (`has_clingo`, `has_z3`) and `default_backend(...)` / `backend_choice_reason(...)` for routing. | mention-in-passing — install/feature-detection note |
| `datalog_grounding` (datalog_grounding.py:1) | Ground a Gunray `DefeasibleTheory` into propositional ASPIC+ (`ground_defeasible_theory(theory, ...) -> GroundedDatalogTheory`); requires the `grounding` extra. | prime — needs its own subsection; explain that it consumes Gunray, not redefines a schema |
| `iccma_cli` (iccma_cli.py:1) | Argparse `main(argv)` for the ICCMA AF/ABA CLI dispatching to `solver.solve_*_single_extension`/`solve_*_acceptance`; supports `DC`/`DS`/`SE` and CO/GR/PR/ST/SST/STG/ID/CF2 problem codes. | prime if Q wants it visible; otherwise omit. Note: not registered as a console script |
| `solver` (solver.py) | Typed solver-result wrappers — `solve_dung_*`, `solve_aba_*`, `solve_adf_models`, `solve_setaf_extensions`, plus `ICCMAConfig`, `SATConfig`. README cites the symbols but never names the module. | mention by name in the "Solver surfaces" prose |
| `solver_results` (solver_results.py:1) | Shared dataclasses `SolverUnavailable`, `SolverProcessError`, `SolverProtocolError`. | mention-in-passing — only when explaining typed unavailable returns |
| `solver_adapters/clingo` (solver_adapters/clingo.py:1) | Subprocess helper for clingo with output regex parsing. | mention-in-passing |
| `solver_adapters/iccma_aba` (solver_adapters/iccma_aba.py:1) | Subprocess adapter for ICCMA flat-ABA solvers; uses `ASPFORABA_SOLVER`-style env. | already covered by README's mention of `ICCMA_ABA_SOLVER` and `ASPFORABA_SOLVER` env vars (README.md:587-588) |
| `solver_adapters/iccma_af` (solver_adapters/iccma_af.py:1) | Subprocess adapter for ICCMA AF solvers. | already covered |
| `probabilistic_components` (probabilistic_components.py:1) | Connectivity helper `connected_components(praf)` per Hunter & Thimm 2017 Prop 18. | omit (internal helper) — already alluded to in README.md:382 |
| `probabilistic_treedecomp` (probabilistic_treedecomp.py:1) | Tree decomposition DP for PrAF; the `exact_dp` backend; module-level limitation note already mirrored in README.md:386-388. | omit by name (the strategy is what users pick) |
| `encodings/` | LP files (Datalog/clingo encodings): aba_admissible/complete/stable, aspic_admissible/complete/stable, dung_admissible/complete/stable. | mention-in-passing — these ship in the wheel per pyproject.toml:75-76 |

## 3. Code-example verification

| Block (README.md lines) | Verdict | Notes |
|---|---|---|
| Dung example, README.md:51-73 | PASS | All imports + class/function signatures verified in dung.py grep |
| Three-valued labellings, README.md:106-113 | PASS | `Labelling.from_extension`, `in_arguments`, `out_arguments`, `undecided_arguments`, `range` all in labelling.py:44-126 |
| ASPIC+ build/attack/defeat, README.md:131-170 | PASS | Verified `Rule.kind`, `PreferenceConfig.comparison`/`link` (aspic.py:159-161, 308-309); `build_arguments`/`compute_attacks`/`compute_defeats` at aspic.py:682, 995, 1246 |
| ASPIC+ encoding, README.md:194-208 | PASS — minor caveat | `encode_aspic_theory`, `solve_aspic_grounded`, `solve_aspic_with_backend` all present (aspic_encoding.py). `result.backend` value `"materialized_reference"` is referenced at backends.py:30 — assumed identical (not directly verified by reading solve_aspic_grounded body) |
| ASPIC+ incomplete, README.md:221-234 | PASS | `PartialASPICTheory`, `evaluate_incomplete_grounded` at aspic_incomplete.py |
| Bipolar, README.md:248-264 | PASS | All imports verified |
| Partial AF, README.md:278-297 | PASS | All imports verified |
| AF revision, README.md:316-333 | PASS — citation caveat | `cayrol_2014_classify_grounded_argument_addition` exists (af_revision.py:314) with `(framework, argument, attacks)` signature; `AFChangeKind` enum at af_revision.py:22-29 has DECISIVE, RESTRICTIVE, QUESTIONING, DESTRUCTIVE, EXPANSIVE, CONSERVATIVE, ALTERING — matches README.md:332-333 |
| Probabilistic, README.md:351-372 | PASS | `ProbabilisticAF(framework=..., p_args=..., p_defeats=...)` matches probabilistic.py:163-180 |
| Probabilistic extension query, README.md:399-406 | PASS — not directly executed | Signature accepts `**kwargs`; `query_kind`/`queried_set` paths exist in probabilistic.py (verified by grep elsewhere) |
| Ranking, README.md:431-436 | **FAIL** | `categoriser_ranking` exists (ranking.py:88) but `result.ordered_tiers` does not — `RankingResult` exposes `ranking` (ranking.py:20). Replace `ranking.ordered_tiers` with `ranking.ranking` |
| Weighted, README.md:443-444 | PASS | `weighted_grounded_extensions` at weighted.py:81 |
| Gradual, README.md:455-461 | PASS | `quadratic_energy_strengths(graph)` (gradual.py:87), `revised_direct_impact(graph, influencers=..., target=...)` (gradual.py:289), `shapley_attack_impacts(graph, target=...)` (gradual.py:352). `shapley.attack_impacts` field not directly verified; `ShapleyAttackImpactResult` is at gradual.py:78 |
| ICCMA, README.md:548-551 | PASS | `parse_aba`, `parse_adf`, `parse_af`, `write_af` at iccma.py:178, 126, 21, 54 |
| sat_encoding, README.md:561-567 | PASS | `encode_stable_extensions` (sat_encoding.py:66), `stable_extensions_from_encoding` (sat_encoding.py:97) |
| Generic semantics dispatch, README.md:607-612 | PASS | `extensions`, `accepted_arguments` at semantics.py:129, 144 |

## 4. Citation audit

| Citation | Verdict | Notes |
|---|---|---|
| Dung 1995 (README.md:116-118) | still-correct | Foundational |
| Caminada 2011 (README.md:119-121) | review needed | README says "*COMMA 2006*" but cites Caminada 2011; the 2006 paper would be Caminada's "Semi-stable semantics" which originally appeared at COMMA 2006. The 2011 reference is a journal version. Needs Q's call on which to cite |
| Gaggl & Woltran 2013 (README.md:120-122) | still-correct | Matches dung.py docstrings |
| DMT 2007 (Dung-Mancarella-Toni) (README.md:122-123) | still-correct | Matches |
| Modgil & Prakken 2018 (README.md:183-184) | still-correct | Cited throughout aspic.py |
| Lehtonen-Niskanen-Järvisalo 2024 (README.md:236-237) | still-correct | Cited at aspic_encoding.py |
| Odekerken-Borg-Bex 2023 (README.md:238-239) | still-correct | Aligns with aspic_incomplete |
| Cayrol & Lagasquie-Schiex 2005 (README.md:267-268) | review needed | `notes/paper-cayrol-lagasquie-2004.md` exists for the 2004 paper. README cites "ECSQARU 2005". Q may want both or the 2004 base paper |
| Baumann 2015 / Diller 2015 / Cayrol-2014 (README.md:336-341) | needs-update | Cayrol "2014" entry: af_revision.py:335 cites "Cayrol, de Saint-Cyr, and Lagasquie-Schiex 2010, JAIR 38". Reconcile date |
| Li-Oren-Norman 2012 (README.md:416-417) | still-correct | Matches probabilistic.py |
| Hunter-Thimm 2017 (README.md:418-419) | still-correct | Prop 18 mirrored in probabilistic_components.py:13 |
| Popescu-Wallner 2024 (README.md:420-421) | still-correct | Cited at probabilistic_treedecomp.py:3 |
| Freedman et al. 2025 (README.md:422-424) | still-correct | DFQuad / argumentative-LLM citation |
| Al Anaissy et al. 2024 (README.md:466) | still-correct | Definitions 12, 13 referenced in gradual.py:299, 361 |
| New papers in `notes/` not yet in README | new-paper-to-add candidates | `paper-yin-2023-attribution-retrieval.md` (Yin/Potyka/Toni 2023, attribution explanations in QBAF) — relevant to gradual/attribution surface; `paper-egly-gaggl-woltran-2010-retrieval.md` (ASPARTIX encodings) — relevant to ASP backend / aspic_encoding; `paper-hanisch-rauschenbach-2025-angry.md` (ANGRY grounder for rule-based argumentation) — possibly relevant to datalog_grounding. Q's call |

## 5. Surface tier proposal

Proposed grouping for the new TOC, based on observed `__init__.py` exports and module docstrings:

### Core (Dung labelling preference)
- `dung` (dung.py — Dung 1995 + Caminada/Gaggl-Woltran/DMT extensions, prudent variants)
- `labelling` (labelling.py — three-valued labellings, complete/grounded/preferred/stable/semi-stable/eager/stage2)
- `preference` (preference.py — strict_partial_order_closure, strictly_weaker, defeat_holds)
- `semantics` (semantics.py — generic dispatch)

### Structured (ASPIC+ ABA)
- `aspic` (aspic.py — ArgumentationSystem, KnowledgeBase, build/attacks/defeats, CSAF, ASPICAbstractProjection)
- `aspic_encoding` (aspic_encoding.py — Lehtonen-Niskanen-Järvisalo facts)
- `aspic_incomplete` (aspic_incomplete.py — Odekerken et al.)
- `subjective_aspic` (subjective_aspic.py — Wallner-style filter)
- `aba` (aba.py — flat ABA, ABA+)
- `aba_asp` (aba_asp.py — clingo-backed)
- `aba_sat` (aba_sat.py — SAT support)
- `accrual` (accrual.py — Prakken accrual envelopes)

### Quantitative-bipolar (gradual, ranking, weighted, dfquad, equational, matt_toni)
- `bipolar` (bipolar.py — Cayrol & Lagasquie-Schiex)
- `gradual` (gradual.py — Potyka quadratic-energy + Al Anaissy revised-impact + Shapley)
- `gradual_principles` (gradual_principles.py — Baroni-Rago-Toni principles)
- `ranking` (ranking.py — Categoriser, Burden, Discussion, Counting, Tuples, h-Categoriser, iterated graded)
- `ranking_axioms` (ranking_axioms.py — preorder/void/cardinality predicates)
- `weighted` (weighted.py — Dunne-style budgets)
- `dfquad` (dfquad.py — DF-QuAD)
- `equational` (equational.py — Gabbay equational)
- `matt_toni` (matt_toni.py — zero-sum game strength)

### Probabilistic
- `probabilistic` (probabilistic.py — `ProbabilisticAF`, `compute_probabilistic_acceptance`, 7 strategies)
- `probabilistic_components` (internal — connected components)
- `probabilistic_treedecomp` (internal — exact_dp + paper_td)
- `epistemic` (epistemic.py — epistemic graphs, belief constraints, projection to constellation PrAF; the only Z3-backed surface)

### Specialized frameworks (ADF SETAF CAF VAF practical-reasoning)
- `adf` (adf.py — Brewka-Woltran ADFs, AcceptanceCondition AST, JSON/formula I/O)
- `setaf` (setaf.py — collective-attack frameworks)
- `setaf_io` (setaf_io.py — ASPARTIX + compact)
- `caf` (caf.py — claim-augmented AFs, concurrence)
- `vaf` (vaf.py — Bench-Capon value-based)
- `vaf_completion` (vaf_completion.py — chains, lines, fact-uncertainty)
- `practical_reasoning` (practical_reasoning.py — AATS, Atkinson & Bench-Capon CQs)

### Dynamics, revision, and enforcement
- `partial_af` (partial_af.py — completion-based reasoning, merges)
- `af_revision` (af_revision.py — Baumann/Diller/Cayrol)
- `dynamic` (dynamic.py — DynamicArgumentationFramework, IncrementalDynamicArgumentationFramework, update streams)
- `enforcement` (enforcement.py — minimal-change oracle, expansion-typed)
- `approximate` (approximate.py — k-stable, bounded grounded, semi-stable approximation)

### Encoding and interop
- `iccma` (iccma.py — AF/ADF/ABA exchange formats)
- `iccma_cli` (iccma_cli.py — argparse CLI; tier depends on Q's stance)
- `sat_encoding` (sat_encoding.py — pure-Python CNF for stable)
- `af_sat` (af_sat.py — incremental SAT kernel)
- `datalog_grounding` (datalog_grounding.py — Gunray projection to ASPIC+)

### Solver orchestration
- `solver` (solver.py — typed solver entry points)
- `solver_results` (solver_results.py — typed unavailable/process/protocol errors)
- `solver_differential` (solver_differential.py — `solver_capability_matrix`, benchmark smoke)
- `backends` (backends.py — capability detection / default routing)
- `solver_adapters/` (clingo, iccma_aba, iccma_af)

### LLM adapter
- `llm_surface` (llm_surface.py — `build_qbaf_from_proposition_set`, `explain_acceptance`, `contest`)

## 6. Open questions for Q

1. **CLI status.** `iccma_cli.py` exists with a working `main(argv)`, but pyproject.toml has no `[project.scripts]` entry. Should the README (a) advertise the CLI and add a console-script entry, (b) advertise the CLI as `python -m argumentation.iccma_cli`, or (c) keep the non-goals statement and treat iccma_cli as internal?

2. **Strategy count wording.** Should "six strategies" become "seven" or be reorganized into "5 PrAF strategies + 2 dfquad strategies"? The dfquad ones are conceptually different (gradual scores, not acceptance probabilities).

3. **Cayrol citation date.** README cites "Cayrol et al. 2014" for argument-addition classification; af_revision.py docstring cites "2010 JAIR 38". Which is the canonical reference?

4. **Optional extras documentation.** Should `[asp]` and `[grounding]` get the same install treatment as `[z3]`, or are they "internal" extras for now?

5. **Gunray dependency footprint.** `datalog_grounding` requires Gunray (sourced via git in pyproject.toml:102-103). Should the README explain this is a sister project, or treat it as an opaque optional dep?

6. **New papers (notes/paper-*.md).** Yin 2023 (attribution explanations in QBAF), Egly-Gaggl-Woltran 2010 (ASPARTIX), Hanisch-Rauschenbach 2025 (ANGRY). Add to README citations, or keep in notes only?

7. **paper_td vs. exact_dp.** Both are tree-decomposition based; paper_td is opt-in for extension-probability queries only. Should the README treat them as one bullet or two?

8. **README's "Cayrol 2014" / Caminada "COMMA 2006"-vs-"2011" mismatches.** Same pattern: README and module docstrings disagree on year/venue. Worth a bulk citation pass?
