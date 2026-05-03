# Limitations and gaps

This document tracks what `argumentation` does **not** do. Closed-bug
changelogs are in the appendix; the main body is current limitations only.

## Currently-known limitations

| # | Limitation | Source |
|---|---|---|
| L1 | Non-flat ABA is out of scope. `ABAFramework` rejects rules whose heads are assumptions via `NotFlatABAError`. A future non-flat ABA workstream must own that distinct semantics. | `src/argumentation/aba.py:27,62` |
| L2 | The `exact_dp` PrAF backend tracks full edge sets and forgotten arguments in tree-decomposition table keys. Asymptotic complexity is **not better** than brute-force enumeration; effective in practice for primal-graph treewidth ≤ ~15. This is *not* the full Popescu & Wallner I/O/U witness-table DP. | `src/argumentation/probabilistic_treedecomp.py:7-17` |
| L3 | `exact_dp` accepts only grounded semantics on defeat-only PrAFs (no supports, attacks ≡ defeats). Other configurations route to `mc` or `exact_enum`. | `src/argumentation/probabilistic_treedecomp.py:32-43` |
| L4 | The `paper_td` Popescu & Wallner backend is opt-in only and supports `query_kind="extension_probability"` exclusively. The auto-router does not select it. | `src/argumentation/probabilistic.py` |
| L5 | The ABA+ ASP backend is not implemented. Calls return a typed `unavailable_backend` result with reason "ABA+ ASP backend is not implemented". | `src/argumentation/aba_asp.py:97-106` |
| L6 | The ASPIC+ clingo backend supports grounded semantics only. Non-grounded queries return `unavailable_backend`. | `notes/workstream-asp-backend-2026-05-01.md:22-24` |
| L7 | The ASP backend covers last-link preference lifting only; weakest-link preference lifting is not yet implemented in the encoding even though `PreferenceConfig` exposes both modes. | `notes/workstream-asp-backend-2026-05-01.md:69-71` |
| L8 | `practical_reasoning.critical_question_objections` implements the Atkinson & Bench-Capon CQ5, CQ6, and CQ11 only. Any other critical question raises `NotImplementedError`. | `src/argumentation/practical_reasoning.py:139-145` |
| L9 | `enforcement.py` is a brute-force minimal-change reference oracle, **not** Baumann-style normal/strong/weak-expansion enforcement. It may add or remove edges and arguments to satisfy the target. | `src/argumentation/enforcement.py:1-12` |
| L10 | `datalog_grounding` consumes Gunray's conservative DeLP-compatible `inspect_grounding` only. The Diller (2025) Definition 12 NAP analysis is not implemented. | `src/argumentation/datalog_grounding.py:1-7`, `notes/workstream-datalog-grounding-2026-05-01.md:22` |
| L11 | The probabilistic strategy alias `dfquad` is accepted by `_ALLOWED_STRATEGIES` but raises downstream — only `dfquad_quad` and `dfquad_baf` are live. | `src/argumentation/probabilistic.py:25-39,757-762` |
| L12 | Clingo is invoked as a subprocess binary, not via the `clingo` Python package's in-process API. Telemetry is parsed from stdout. | `notes/workstream-asp-backend-2026-05-01.md:24-27` |
| L13 | `accrual.py` provides Prakken-style weak/strong applicability checks and accrual envelopes only. There is no enumeration of subset accruals and no comparator over accruals. | `src/argumentation/accrual.py:20-92` |
| L14 | `af_sat` (Dung) and `aba_sat` paths are different code paths despite the shared name. `af_sat` requires Z3 (the `[z3]` extra); `aba_sat` is pure-Python bitmask enumeration. | `src/argumentation/af_sat.py`, `src/argumentation/aba_sat.py` |
| L15 | `iccma_cli` is a thin solver-protocol shim. The package does not own application-level CLI presentation, source calibration, persistent storage, or repository workflow. | `src/argumentation/iccma_cli.py` |

## Non-goals

`argumentation` does not own:

- application provenance, audit trails, or source calibration;
- subjective-logic opinion calculi (these are upstream concerns);
- persistent storage, schema versioning, or repository workflow;
- application-level argument rendering or domain-specific UI;
- argument-mining or natural-language pre-processing;
- a non-flat ABA semantics (see L1).

Callers translate those concerns into finite formal objects before invoking
this package.

## Closed gaps (appendix)

The remainder of this document is a historical changelog of bug-class gaps
that have been closed. Workstream tags refer to internal numbering.

### WS-O-arg-aba-adf

| Finding | Severity | Production surface | First failing test | Status |
|---|---:|---|---|---|
| P-A.1: arbitrary ADF kernel absent | HIGH | `src/argumentation/adf.py` | `tests/test_adf_acceptance_condition_ast.py` | closed `06bff8a` |
| P-A.2: flat ABA kernel absent | HIGH | `src/argumentation/aba.py` | `tests/test_aba_bondarenko_examples.py` | closed `70bc537` |
| P-A.3: ADF and ABA foundational papers had no executable kernel | HIGH | `src/argumentation/adf.py`, `src/argumentation/aba.py` | `tests/test_workstream_o_arg_aba_adf_done.py` | closed `4719640` |
| P-A.4: downstream/package boundary for ABA/ADF unresolved | HIGH | public package surface | `tests/test_workstream_o_arg_aba_adf_done.py` | closed `4719640` |

### WS-O-arg

| Finding | Severity | Production surface | First failing test | Status |
|---|---:|---|---|---|
| Bug 1: ideal extension must not union multiple maximal admissible candidates | HIGH | `src/argumentation/dung.py` | `tests/test_dung_ideal_admissibility.py` | closed `6ea2acf`, hardened `38f94bf` |
| Bug 2: ASPIC literal ids must be valid ASP constants | HIGH | `src/argumentation/aspic_encoding.py` | `tests/test_aspic_encodings.py::test_ws_o_arg_aspic_encoding_sanitises_literal_ids_for_asp` | closed `60e9f30` |
| Bug 3: duplicate defeasible rule names must fail at encode time | HIGH | `src/argumentation/aspic_encoding.py` | `tests/test_aspic_encodings.py::test_ws_o_arg_aspic_encoding_rejects_duplicate_defeasible_rule_names` | closed `60e9f30` |
| Bug 4: AF revision change classification must use extension content | HIGH | `src/argumentation/af_revision.py` | `tests/test_af_revision.py::test_ws_o_arg_cayrol_2010_decisive_uses_surviving_extension_content` | closed `ac5ec44` |
| Bug 5: `ExtensionRevisionState` ranking must be lazy | HIGH | `src/argumentation/af_revision.py` | `tests/test_af_revision.py::test_ws_o_arg_extension_revision_state_accepts_lazy_ranking` | closed `ac5ec44` |
| Bug 6: `strictly_weaker(non-empty, empty)` must match ASPIC set lifting | HIGH | `src/argumentation/preference.py` | `tests/test_preference.py::TestStrictlyWeakerConcrete::test_ws_o_arg_non_empty_set_is_strictly_weaker_than_empty_boundary` | closed `5a48004` |
| Bug 7: partial-AF skeptical acceptance must distinguish necessary and possible | HIGH | `src/argumentation/semantics.py` | `tests/test_semantics.py::test_partial_af_extensions_are_completion_based` | closed `5a48004` |
| Bug 8: Monte Carlo confidence z-score must accept continuous values | HIGH | `src/argumentation/probabilistic.py` | `tests/test_probabilistic.py::test_ws_o_arg_z_for_confidence_accepts_continuous_confidence_values` | closed `5a48004` |
| WS-O-arg upstream gate | HIGH | package surface | `tests/test_workstream_o_arg_done.py` | closed `f55aeac` |

Bug 1's original "must fail today" premise was stale in the current repository: `ideal_extension` already enumerated admissible subsets of the preferred-extension intersection. The workstream still removed the impossible union fallback and added named regressions for admissibility, non-downward-closed defense, and mutual defense.

### WS-O-arg-vaf-completion

| Finding | Severity | Production surface | First failing test | Status |
|---|---:|---|---|---|
| Bench-Capon p. 438 argument chains absent | MED | `src/argumentation/vaf_completion.py` | `tests/test_vaf_completion.py::test_argument_chain_validates_definition_6_3_and_parity` | closed |
| Bench-Capon p. 439 lines of argument absent | MED | `src/argumentation/vaf_completion.py` | `tests/test_vaf_completion.py::test_line_of_argument_builds_distinct_value_chains_and_stops_on_repeat` | closed |
| Bench-Capon pp. 440-441 Theorem 6.6 / Corollary 6.7 helpers absent | MED | `src/argumentation/vaf_completion.py` | `tests/test_vaf_completion.py::test_corollary_6_7_two_value_cycle_matches_preferred_extension` | closed |
| Bench-Capon pp. 444-447 fact-as-highest-value and factual uncertainty absent | MED | `src/argumentation/vaf_completion.py` | `tests/test_vaf_completion.py::test_fact_argument_blocks_ordinary_attack_and_uncertainty_has_multiple_extensions` | closed |
