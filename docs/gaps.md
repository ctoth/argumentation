# Argumentation Gaps

## WS-O-arg-aba-adf closed gaps

| Finding | Severity | Production surface | First failing test | Status |
|---|---:|---|---|---|
| P-A.1: arbitrary ADF kernel absent | HIGH | `src/argumentation/adf.py` | `tests/test_adf_acceptance_condition_ast.py` | closed `06bff8a` |
| P-A.2: flat ABA kernel absent | HIGH | `src/argumentation/aba.py` | `tests/test_aba_bondarenko_examples.py` | closed `70bc537` |
| P-A.3: ADF and ABA foundational papers had no executable kernel | HIGH | `src/argumentation/adf.py`, `src/argumentation/aba.py` | `tests/test_workstream_o_arg_aba_adf_done.py` | closed pending sentinel commit |
| P-A.4: propstore/argumentation boundary for ABA/ADF unresolved | HIGH | public package surface | `tests/test_workstream_o_arg_aba_adf_done.py` | closed pending sentinel commit |

Non-flat ABA remains out of scope. `ABAFramework` rejects rules whose heads are assumptions via `NotFlatABAError`; a future non-flat ABA workstream must own that distinct semantics.

## WS-O-arg closed gaps

| Finding | Severity | Production surface | First failing test | Status |
|---|---:|---|---|---|
| WS-O-arg Bug 1: ideal extension must not union multiple maximal admissible candidates | HIGH | `src/argumentation/dung.py` | `tests/test_dung_ideal_admissibility.py` | closed `6ea2acf`, hardened by `38f94bf` |
| WS-O-arg Bug 2: ASPIC literal ids must be valid ASP constants | HIGH | `src/argumentation/aspic_encoding.py` | `tests/test_aspic_encodings.py::test_ws_o_arg_aspic_encoding_sanitises_literal_ids_for_asp` | closed `60e9f30` |
| WS-O-arg Bug 3: duplicate defeasible rule names must fail at encode time | HIGH | `src/argumentation/aspic_encoding.py` | `tests/test_aspic_encodings.py::test_ws_o_arg_aspic_encoding_rejects_duplicate_defeasible_rule_names` | closed `60e9f30` |
| WS-O-arg Bug 4: AF revision change classification must use extension content | HIGH | `src/argumentation/af_revision.py` | `tests/test_af_revision.py::test_ws_o_arg_cayrol_2010_decisive_uses_surviving_extension_content` | closed `ac5ec44` |
| WS-O-arg Bug 5: `ExtensionRevisionState` ranking must be lazy | HIGH | `src/argumentation/af_revision.py` | `tests/test_af_revision.py::test_ws_o_arg_extension_revision_state_accepts_lazy_ranking` | closed `ac5ec44` |
| WS-O-arg Bug 6: `strictly_weaker(non-empty, empty)` must match ASPIC set lifting | HIGH | `src/argumentation/preference.py` | `tests/test_preference.py::TestStrictlyWeakerConcrete::test_ws_o_arg_non_empty_set_is_strictly_weaker_than_empty_boundary` | closed `5a48004` |
| WS-O-arg Bug 7: partial-AF skeptical acceptance must distinguish necessary and possible | HIGH | `src/argumentation/semantics.py` | `tests/test_semantics.py::test_partial_af_extensions_are_completion_based` | closed `5a48004` |
| WS-O-arg Bug 8: Monte Carlo confidence z-score must accept continuous values | HIGH | `src/argumentation/probabilistic.py` | `tests/test_probabilistic.py::test_ws_o_arg_z_for_confidence_accepts_continuous_confidence_values` | closed `5a48004` |
| WS-O-arg upstream gate | HIGH | package surface | `tests/test_workstream_o_arg_done.py` | closed `f55aeac` |

Bug 1's original "must fail today" premise was stale in the current repository: `ideal_extension` already enumerated admissible subsets of the preferred-extension intersection. The workstream still removed the impossible union fallback and added named regressions for admissibility, non-downward-closed defense, and mutual defense.
