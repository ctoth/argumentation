"""Query-directed SCC-cone acceptance (exp 6A) — soundness and routing tests.

Derivation: experiments/2026-07-10-af-scc-acceptance.md. The cone path must be
answer-equivalent to the flat/native path for complete (DC/DS) and preferred
(DS); for stable it is one-sided (conclusive cone answers only, flat fallback
otherwise) and must preserve the vacuous-YES convention when no stable
extension exists globally.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from argumentation.core.dung import (
    ArgumentationFramework,
    complete_extensions,
)
from argumentation.solving.af_scc_cone import (
    LAST_CONE,
    least_complete_closure,
    query_cone_arguments,
    solve_cone_acceptance,
)
from argumentation.solving.solver import solve_dung_acceptance


# ── strategies ──────────────────────────────────────────────────────


@st.composite
def multi_scc_frameworks(draw):
    """AFs with >= 2 SCCs: cyclic blocks joined by forward-only cross attacks."""
    block_count = draw(st.integers(min_value=2, max_value=4))
    blocks: list[list[str]] = []
    index = 0
    for _ in range(block_count):
        size = draw(st.integers(min_value=1, max_value=3))
        blocks.append([f"n{index + offset}" for offset in range(size)])
        index += size
    defeats: set[tuple[str, str]] = set()
    for block in blocks:
        if len(block) > 1:
            for position, argument in enumerate(block):
                defeats.add((argument, block[(position + 1) % len(block)]))
        defeats |= draw(
            st.frozensets(
                st.tuples(st.sampled_from(block), st.sampled_from(block)),
                max_size=4,
            )
        )
    for i in range(block_count):
        for j in range(i + 1, block_count):
            defeats |= draw(
                st.frozensets(
                    st.tuples(
                        st.sampled_from(blocks[i]), st.sampled_from(blocks[j])
                    ),
                    max_size=3,
                )
            )
    arguments = frozenset(a for block in blocks for a in block)
    return ArgumentationFramework(arguments=arguments, defeats=frozenset(defeats))


@st.composite
def multi_scc_queries(draw):
    framework = draw(multi_scc_frameworks())
    query = draw(st.sampled_from(sorted(framework.arguments)))
    return framework, query


# ── hand-built fixtures ─────────────────────────────────────────────

# SCC chain A -> B -> C -> D plus an off-cone sibling E attacked from C:
#   A = {a1, a2} 2-cycle, B = {b1, b2} 2-cycle, C = {c1}, D = {d1, d2} 2-cycle.
CHAIN_AF = ArgumentationFramework(
    arguments=frozenset({"a1", "a2", "b1", "b2", "c1", "d1", "d2", "e1"}),
    defeats=frozenset(
        {
            ("a1", "a2"),
            ("a2", "a1"),
            ("b1", "b2"),
            ("b2", "b1"),
            ("a1", "b1"),
            ("b2", "c1"),
            ("c1", "d1"),
            ("d1", "d2"),
            ("d2", "d1"),
            ("c1", "e1"),
        }
    ),
)

# Stable vacuity trap: p -> q plus a disconnected 3-cycle {x, y, z}.
# SE(full) = {} (vacuous-YES for DS-ST), but the cone of q is {p, q} with
# SE(cone) = {{p}} — a naive cone DS-ST answer of NO would be unsound.
VACUITY_AF = ArgumentationFramework(
    arguments=frozenset({"p", "q", "x", "y", "z"}),
    defeats=frozenset(
        {("p", "q"), ("x", "y"), ("y", "z"), ("z", "x")}
    ),
)


# ── cone extraction ─────────────────────────────────────────────────


def test_query_cone_is_ancestor_closure_of_query_scc() -> None:
    assert query_cone_arguments(CHAIN_AF, "c1") == frozenset(
        {"a1", "a2", "b1", "b2", "c1"}
    )
    assert query_cone_arguments(CHAIN_AF, "a1") == frozenset({"a1", "a2"})
    assert query_cone_arguments(CHAIN_AF, "e1") == frozenset(
        {"a1", "a2", "b1", "b2", "c1", "e1"}
    )


def test_query_cone_on_single_scc_is_everything() -> None:
    triangle = ArgumentationFramework(
        arguments=frozenset({"x", "y", "z"}),
        defeats=frozenset({("x", "y"), ("y", "z"), ("z", "x")}),
    )
    assert query_cone_arguments(triangle, "x") == triangle.arguments


# ── routing telemetry ───────────────────────────────────────────────


def test_auto_complete_acceptance_uses_cone_path_on_multi_scc_af() -> None:
    result = solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="credulous", query="c1", backend="auto"
    )
    assert result.answer is True
    assert LAST_CONE.fired is True
    assert LAST_CONE.cone_argument_count == 5
    assert LAST_CONE.total_argument_count == 8


def test_explicit_sat_backend_keeps_flat_path() -> None:
    LAST_CONE.reset()
    result = solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="credulous", query="c1", backend="sat"
    )
    assert result.answer is True
    assert LAST_CONE.fired is None


def test_single_scc_framework_keeps_flat_path() -> None:
    LAST_CONE.reset()
    triangle = ArgumentationFramework(
        arguments=frozenset({"x", "y", "z"}),
        defeats=frozenset({("x", "y"), ("y", "z"), ("z", "x")}),
    )
    result = solve_dung_acceptance(
        triangle, semantics="complete", task="credulous", query="x", backend="auto"
    )
    assert result.answer is False
    assert LAST_CONE.fired is None


# ── stable: one-sided cone rules + vacuity trap ─────────────────────


def test_ds_stable_vacuous_yes_survives_cone_routing() -> None:
    result = solve_dung_acceptance(
        VACUITY_AF, semantics="stable", task="skeptical", query="q", backend="auto"
    )
    assert result.answer is True  # vacuously: SE(full) is empty
    assert LAST_CONE.fired is True
    assert LAST_CONE.conclusive is False  # cone had a q-free stable extension


def test_dc_stable_cone_no_is_conclusive() -> None:
    result = solve_dung_acceptance(
        VACUITY_AF, semantics="stable", task="credulous", query="q", backend="auto"
    )
    assert result.answer is False
    assert LAST_CONE.fired is True
    assert LAST_CONE.conclusive is True  # no cone-stable extension contains q


def test_cone_path_skips_frameworks_with_preference_filtered_attacks() -> None:
    # With attacks != defeats, conflict-freeness uses the attack layer
    # (Modgil & Prakken Def 14); the cone derivation covers pure Dung only.
    LAST_CONE.reset()
    framework = ArgumentationFramework(
        arguments=CHAIN_AF.arguments,
        defeats=CHAIN_AF.defeats,
        attacks=CHAIN_AF.defeats | {("d2", "a1")},
    )
    result = solve_dung_acceptance(
        framework, semantics="complete", task="credulous", query="c1", backend="auto"
    )
    assert LAST_CONE.fired is None
    assert result.answer == solve_dung_acceptance(
        framework, semantics="complete", task="credulous", query="c1", backend="native"
    ).answer


def test_cone_solver_returns_none_when_cone_spans_framework() -> None:
    triangle = ArgumentationFramework(
        arguments=frozenset({"x", "y", "z"}),
        defeats=frozenset({("x", "y"), ("y", "z"), ("z", "x")}),
    )
    assert (
        solve_cone_acceptance(
            triangle, semantics="complete", task="credulous", query="x"
        )
        is None
    )


# ── witness lifting (complete) ──────────────────────────────────────


def test_dc_complete_witness_is_full_framework_complete_extension() -> None:
    result = solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="credulous", query="b2", backend="auto"
    )
    assert result.answer is True
    assert LAST_CONE.fired is True
    assert result.witness is not None
    assert "b2" in result.witness
    assert result.witness in complete_extensions(CHAIN_AF)


def test_ds_complete_counterexample_is_full_framework_complete_extension() -> None:
    result = solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="skeptical", query="a1", backend="auto"
    )
    assert result.answer is False
    assert LAST_CONE.fired is True
    assert result.counterexample is not None
    assert "a1" not in result.counterexample
    assert result.counterexample in complete_extensions(CHAIN_AF)


def test_least_complete_closure_extends_cone_extension_without_touching_cone() -> None:
    # Admissible-in-full cone extension {a1}: closure must add the defended
    # downstream nodes ({b2} reinstated, then c1 killed -> d-cycle untouched)
    closure = least_complete_closure(CHAIN_AF, frozenset({"a1"}))
    assert closure in complete_extensions(CHAIN_AF)
    assert closure & frozenset({"a1", "a2"}) == frozenset({"a1"})


# ── sat-core kernel engine (used by the cone path) ──────────────────


def test_kernel_sat_core_engine_matches_native_oracle() -> None:
    from argumentation.solving.af_sat import AfSatKernel

    extensions = complete_extensions(CHAIN_AF)
    for argument in sorted(CHAIN_AF.arguments):
        kernel = AfSatKernel(CHAIN_AF, engine="sat-core")
        kernel.add_complete_labelling()
        kernel.require_in(frozenset({argument}))
        expected = (
            "sat" if any(argument in ext for ext in extensions) else "unsat"
        )
        assert kernel.check(f"probe_{argument}") == expected


def test_kernel_rejects_unknown_engine() -> None:
    import pytest

    from argumentation.solving.af_sat import AfSatKernel

    with pytest.raises(ValueError):
        AfSatKernel(CHAIN_AF, engine="cnf")


def test_cone_path_uses_sat_core_engine() -> None:
    solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="credulous", query="c1", backend="auto"
    )
    assert LAST_CONE.engine == "sat-core"


def test_ds_complete_on_cone_is_grounded_membership_no_sat() -> None:
    # DS-CO == grounded membership; the cone path answers it without SAT.
    result = solve_dung_acceptance(
        CHAIN_AF, semantics="complete", task="skeptical", query="c1", backend="auto"
    )
    assert result.answer is False
    assert LAST_CONE.fired is True
    assert any("grounded" in note for note in LAST_CONE.notes)


# ── property: cone-routed auto path == native oracle ────────────────


@given(multi_scc_queries(), st.sampled_from(["credulous", "skeptical"]))
@settings(deadline=10000, max_examples=60)
def test_auto_complete_acceptance_matches_native_on_multi_scc(case, task) -> None:
    framework, query = case
    auto = solve_dung_acceptance(
        framework, semantics="complete", task=task, query=query, backend="auto"
    )
    native = solve_dung_acceptance(
        framework, semantics="complete", task=task, query=query, backend="native"
    )
    assert auto.answer == native.answer


@given(multi_scc_queries())
@settings(deadline=10000, max_examples=60)
def test_auto_preferred_skeptical_matches_native_on_multi_scc(case) -> None:
    framework, query = case
    auto = solve_dung_acceptance(
        framework, semantics="preferred", task="skeptical", query=query, backend="auto"
    )
    native = solve_dung_acceptance(
        framework, semantics="preferred", task="skeptical", query=query, backend="native"
    )
    assert auto.answer == native.answer


@given(multi_scc_queries(), st.sampled_from(["credulous", "skeptical"]))
@settings(deadline=10000, max_examples=60)
def test_auto_stable_acceptance_matches_native_on_multi_scc(case, task) -> None:
    framework, query = case
    auto = solve_dung_acceptance(
        framework, semantics="stable", task=task, query=query, backend="auto"
    )
    native = solve_dung_acceptance(
        framework, semantics="stable", task=task, query=query, backend="native"
    )
    assert auto.answer == native.answer


@given(multi_scc_queries(), st.sampled_from(["credulous", "skeptical"]))
@settings(deadline=10000, max_examples=40)
def test_cone_witnesses_are_full_framework_complete_extensions(case, task) -> None:
    framework, query = case
    result = solve_dung_acceptance(
        framework, semantics="complete", task=task, query=query, backend="auto"
    )
    certificate = result.witness if task == "credulous" else result.counterexample
    if certificate is not None:
        assert certificate in complete_extensions(framework)
        if task == "credulous":
            assert query in certificate
        else:
            assert query not in certificate
