from __future__ import annotations

from hypothesis import given, settings

from argumentation import aba_sat
from argumentation import aba_decomposition
from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from tests.test_aba_real_prefsat_contract import small_flat_aba_for_real_prefsat


NATIVE_CNF_PREFSAT_PAGE_IMAGES = (
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png",
    "papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png",
    "papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png",
    "papers/Thimm_2021_FudgeLight-weightSolverAbstract/pngs/page-002.png",
    "papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png",
    "papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-007.png",
    "../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png",
)

REQUIRED_NATIVE_CNF_TELEMETRY = (
    "native_cnf_variables",
    "native_cnf_clauses",
    "native_cnf_solver_checks",
    "native_cnf_candidate_models",
    "native_cnf_candidate_blocks",
    "native_cnf_z3_main_checks",
)


def test_native_cnf_prefsat_page_image_contract_is_complete() -> None:
    assert len(NATIVE_CNF_PREFSAT_PAGE_IMAGES) == 9
    assert all(path.endswith(".png") for path in NATIVE_CNF_PREFSAT_PAGE_IMAGES)


def test_dense_flat_prefsat_dispatches_to_native_cnf(monkeypatch) -> None:
    framework = _dense_flat_framework(151, rules_per_assumption=26)
    calls = []

    def native_spy(
        received: ABAFramework,
        *,
        require_assumptions=frozenset(),
    ) -> aba_sat.RealPrefSatResult:
        calls.append((received, require_assumptions))
        return aba_sat.RealPrefSatResult(
            extension=frozenset(),
            prefsat_in={assumption: False for assumption in received.assumptions},
            prefsat_out={assumption: False for assumption in received.assumptions},
            prefsat_undec={assumption: True for assumption in received.assumptions},
            telemetry={
                "native_cnf_variables": 3 * len(received.assumptions),
                "native_cnf_clauses": len(received.assumptions),
                "native_cnf_solver_checks": 1,
                "native_cnf_candidate_models": 1,
                "native_cnf_candidate_blocks": 0,
                "native_cnf_z3_main_checks": 0,
                "prefsat_solver_checks": 1,
            },
            progress_events=(),
            route_metadata={"backend": "sat", "algorithm": "native-cnf-prefsat"},
        )

    def real_spy(*args, **kwargs):
        raise AssertionError("dense flat preferred dispatch must not use Z3 PrefSat")

    monkeypatch.setattr(aba_sat, "native_cnf_prefsat_extension", native_spy)
    monkeypatch.setattr(aba_sat, "real_prefsat_extension", real_spy)

    result = aba_decomposition.decomposed_prefsat_extension(framework)

    assert calls == [(framework, frozenset())]
    assert result.component_results[0].route_metadata["algorithm"] == "native-cnf-prefsat"


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=30, deadline=None)
def test_native_cnf_prefsat_matches_preferred_oracle(framework: ABAFramework) -> None:
    result = aba_sat.native_cnf_prefsat_extension(framework)

    assert result.extension in aba_sat.support_extensions(framework, "preferred")


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=30, deadline=None)
def test_native_cnf_prefsat_reports_operational_contract(framework: ABAFramework) -> None:
    result = aba_sat.native_cnf_prefsat_extension(framework)
    telemetry = result.telemetry

    assert set(REQUIRED_NATIVE_CNF_TELEMETRY) <= set(telemetry)
    assert telemetry["native_cnf_variables"] >= 3 * len(framework.assumptions)
    assert telemetry["native_cnf_clauses"] >= len(framework.assumptions)
    assert telemetry["native_cnf_solver_checks"] >= 1
    assert telemetry["native_cnf_candidate_models"] <= telemetry["native_cnf_solver_checks"]
    assert telemetry["native_cnf_candidate_blocks"] <= len(framework.assumptions) + 2
    assert telemetry["native_cnf_z3_main_checks"] == 0


@given(small_flat_aba_for_real_prefsat())
@settings(max_examples=20, deadline=None)
def test_native_cnf_prefsat_respects_required_assumptions(framework: ABAFramework) -> None:
    oracle_extensions = aba_sat.support_extensions(framework, "preferred")
    required = next(iter(framework.assumptions))
    expected = tuple(extension for extension in oracle_extensions if required in extension)

    result = aba_sat.native_cnf_prefsat_extension(
        framework,
        require_assumptions=frozenset({required}),
    )

    if expected:
        assert result.extension in expected
    else:
        assert result.extension == frozenset()


def _dense_flat_framework(size: int, *, rules_per_assumption: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    atoms = tuple(lit(f"x{index}") for index in range(size))
    rules = []
    for index in range(size * rules_per_assumption):
        head = atoms[index % size]
        body = (
            assumptions[index % size],
            assumptions[(index + 1) % size],
            assumptions[(index + 2) % size],
        )
        rules.append(Rule(body, head, "strict"))
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary={assumption: atoms[index] for index, assumption in enumerate(assumptions)},
        rules=frozenset(rules),
    )


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))
