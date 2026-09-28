"""Complete acceptance must ask one query, not enumerate supports or models."""

from __future__ import annotations

import pytest
from hypothesis import given, settings

from argumentation.solving import solver as dispatch
from argumentation.structured.aba import aba, aba_asp, aba_incremental, aba_sat
from argumentation.structured.aspic.aspic import Rule
from tests.aba_hypothesis_generators import flat_aba_frameworks, lit

pytest.importorskip("clingo")


def independent_choices(pairs=10):
    assumptions = {lit("fixed")}
    contrary = {lit("fixed"): lit("never")}
    rules = set()
    for i in range(pairs):
        a, b, na, nb = (lit(f"{s}{i}") for s in ("a", "b", "na", "nb"))
        assumptions.update((a, b))
        contrary.update({a: na, b: nb})
        rules.update((Rule((a,), nb, "strict"), Rule((b,), na, "strict")))
    rules.add(Rule((lit("fixed"), lit("a0")), lit("derived"), "strict"))
    return aba.ABAFramework(
        frozenset(assumptions | set(contrary.values()) | {lit("derived")}),
        frozenset(rules),
        frozenset(assumptions),
        contrary,
    )


@pytest.mark.parametrize("backend", ["auto", "asp"])
@pytest.mark.parametrize(
    "query, expected",
    [("a0", True), ("fixed", True), ("derived", True), ("never", False)],
)
def test_complete_query_never_enumerates_and_uses_at_most_one_solve(
    monkeypatch, backend, query, expected
):
    def forbidden(*a, **kw):
        raise AssertionError(
            "complete acceptance must not enumerate supports or extensions"
        )

    monkeypatch.setattr(aba_sat, "_minimal_supports", forbidden)
    monkeypatch.setattr(aba_asp, "_minimal_supports", forbidden)
    monkeypatch.setattr(
        aba_incremental.AbaIncrementalSolver, "enumerate_complete", forbidden
    )
    calls = []
    original = aba_incremental.AbaIncrementalSolver._solve_one

    def counted(self, *a, **kw):
        calls.append(1)
        return original(self, *a, **kw)

    monkeypatch.setattr(aba_incremental.AbaIncrementalSolver, "_solve_one", counted)
    framework = independent_choices()
    result = dispatch.solve_aba_acceptance(
        framework,
        semantics="complete",
        task="credulous",
        query=lit(query),
        backend=backend,
    )
    assert isinstance(result, dispatch.AcceptanceSolverSuccess)
    assert result.answer is expected
    assert len(calls) <= 1
    if expected:
        assert result.witness is not None
        assert aba.derives(framework, result.witness, lit(query))
        assert lit("fixed") in result.witness


def test_complete_query_keeps_sat_fallback_without_clingo(monkeypatch):
    monkeypatch.setattr(dispatch, "_has_clingo", lambda: False)
    assert dispatch._auto_aba_backend("auto", "complete", task="credulous") == "sat"
    assert dispatch._auto_aba_backend("sat", "complete", task="credulous") == "sat"
    result = dispatch.solve_aba_acceptance(
        independent_choices(pairs=1),
        semantics="complete",
        task="credulous",
        query=lit("a0"),
        backend="auto",
    )
    assert isinstance(result, dispatch.AcceptanceSolverSuccess)
    assert result.answer is True


def test_complete_query_incomplete_search_stays_a_timeout(monkeypatch):
    def incomplete(*args, **kwargs):
        raise aba_incremental.ClingoSolveIncomplete("search interrupted")

    monkeypatch.setattr(
        aba_incremental.AbaIncrementalSolver,
        "is_credulously_accepted_complete",
        incomplete,
    )
    result = dispatch.solve_aba_acceptance(
        independent_choices(pairs=1),
        semantics="complete",
        task="credulous",
        query=lit("a0"),
        backend="auto",
    )
    assert isinstance(result, dispatch.SolverBackendTimeout)


@given(flat_aba_frameworks(min_assumptions=0, max_assumptions=4, max_rules=8))
@settings(max_examples=75, deadline=None)
def test_complete_query_matches_native_with_and_without_preprocessing(framework):
    extensions = set(aba.complete_extensions(framework))
    for query in framework.language:
        expected = any(aba.derives(framework, e, query) for e in extensions)
        for simplify in (False, True):
            result = aba_asp.solve_aba_with_backend(
                framework,
                backend="asp",
                semantics="complete",
                task="credulous",
                query=query,
                simplify=simplify,
            )
            assert result.status == "success"
            assert result.answer is expected
            if expected:
                assert result.witness in extensions
                assert aba.derives(framework, result.witness, query)
            assert int(result.metadata.get("solver_calls", 0)) <= 1
