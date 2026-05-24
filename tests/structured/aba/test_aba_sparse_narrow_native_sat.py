from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aba import aba_sat
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


@st.composite
def small_sparse_narrow_frameworks(draw) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=1, max_value=7))
    atom_count = draw(st.integers(min_value=max(assumption_count + 1, 3), max_value=12))
    assumptions = tuple(lit(f"a{index}") for index in range(assumption_count))
    atoms = tuple(lit(f"x{index}") for index in range(atom_count))
    body_pool = (*assumptions, *atoms)
    max_rules = max(assumption_count, min(18, assumption_count * 3))
    rule_count = draw(st.integers(min_value=0, max_value=max_rules))
    rule_specs = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=atom_count - 1),
                st.lists(
                    st.integers(min_value=0, max_value=len(body_pool) - 1),
                    min_size=0,
                    max_size=min(2, len(body_pool)),
                    unique=True,
                ),
            ),
            min_size=rule_count,
            max_size=rule_count,
        )
    )
    rules = tuple(
        Rule(tuple(body_pool[index] for index in body), atoms[head], "strict")
        for head, body in rule_specs
    )
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary={
            assumption: atoms[(index + 1) % atom_count]
            for index, assumption in enumerate(assumptions)
        },
        rules=frozenset(rules),
    )


@given(small_sparse_narrow_frameworks())
@settings(max_examples=30, deadline=None)
def test_native_sparse_narrow_stable_matches_oracle(framework: ABAFramework) -> None:
    result = aba_sat.native_sparse_narrow_sat_extension(framework, "stable")
    oracle = aba_sat.support_extensions(framework, "stable")

    if oracle:
        assert result.extension in oracle
    else:
        assert result.extension is None
    assert result.telemetry["clingo_solver_calls"] == 0
    assert result.telemetry["native_sparse_narrow_solver_checks"] >= 1
    assert len(result.telemetry["native_sparse_narrow_solve_times_ms"]) == result.telemetry[
        "native_sparse_narrow_solver_checks"
    ]
    assert all(
        elapsed_ms >= 0
        for elapsed_ms in result.telemetry["native_sparse_narrow_solve_times_ms"]
    )
    assert result.telemetry["native_sparse_narrow_z3_main_checks"] == 0


@given(small_sparse_narrow_frameworks())
@settings(max_examples=30, deadline=None)
def test_native_sparse_narrow_preferred_matches_oracle(framework: ABAFramework) -> None:
    result = aba_sat.native_sparse_narrow_sat_extension(framework, "preferred")
    oracle = aba_sat.support_extensions(framework, "preferred")

    assert result.extension in oracle
    assert _is_subset_maximal_admissible(framework, result.extension)
    assert result.telemetry["clingo_solver_calls"] == 0
    assert result.telemetry["native_sparse_narrow_solver_checks"] >= 1
    assert result.telemetry["native_sparse_narrow_learned_clauses"] <= (
        result.telemetry["native_sparse_narrow_solver_checks"] + len(framework.assumptions)
    )
    assert result.telemetry["native_sparse_narrow_z3_main_checks"] == 0


@given(small_sparse_narrow_frameworks())
@settings(max_examples=20, deadline=None)
def test_native_sparse_narrow_required_assumptions_are_enforced(
    framework: ABAFramework,
) -> None:
    required = frozenset({next(iter(framework.assumptions))})
    result = aba_sat.native_sparse_narrow_sat_extension(
        framework,
        "preferred",
        require_assumptions=required,
    )
    oracle = tuple(
        extension
        for extension in aba_sat.support_extensions(framework, "preferred")
        if required <= extension
    )

    if oracle:
        assert result.extension in oracle
        assert required <= result.extension
    else:
        assert result.extension == frozenset()
    assert result.telemetry["clingo_solver_calls"] == 0


def _is_subset_maximal_admissible(
    framework: ABAFramework,
    extension: AssumptionSet,
) -> bool:
    admissible = [
        candidate
        for candidate in aba_sat.support_extensions(framework, "complete")
        if candidate <= extension or extension <= candidate
    ]
    return not any(extension < candidate for candidate in admissible)


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))
