"""Skeptical acceptance of literals no rule can derive (issue #72).

A literal is in an extension's closure only if rules derive it from the
assumptions (Bondarenko et al. 1997, Th(T), p.69). Lehtonen et al. 2021
(Sec 4.2.3) decide skeptical acceptance by searching for a counterexample
that does not derive the query: UNSAT means accepted. When ``supported(q)``
is not a ground atom at all, no set derives q, so a counterexample always
exists; clingo's negative assumption on an absent atom must not be read as
UNSAT (potassco/clingo#671).
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.solving.solver import solve_aba_acceptance
from argumentation.structured.aba import aba
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from tests.aba_hypothesis_generators import flat_aba_frameworks

pytest.importorskip("clingo")

from argumentation.structured.aba.aba_asp import solve_aba_with_backend  # noqa: E402

Q = Literal(GroundAtom("q"))


def _assumption_free(rules: frozenset[Rule] = frozenset()) -> aba.ABAFramework:
    return aba.ABAFramework(frozenset({Q}), rules, frozenset(), {})


@pytest.mark.parametrize("simplify", [False, True])
def test_incremental_skeptical_preferred_rejects_underivable_literal(
    simplify: bool,
) -> None:
    """Issue #72: the only preferred extension is {}, whose closure lacks q,
    so q is not skeptically accepted and {} is the counterexample."""
    framework = _assumption_free()
    assert set(aba.preferred_extensions(framework)) == {frozenset()}
    assert not aba.derives(framework, frozenset(), Q)

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="preferred",
        task="skeptical",
        query=Q,
        simplify=simplify,
    )

    assert result.answer is False
    assert result.counterexample == frozenset()
    assert int(result.metadata["solver_calls"]) <= 2


@pytest.mark.parametrize("backend", ["native", "sat", "asp", "auto"])
@pytest.mark.parametrize("semantics", ["complete", "preferred", "stable"])
@pytest.mark.parametrize("task", ["credulous", "skeptical"])
def test_every_acceptance_route_rejects_underivable_literal(
    backend: str,
    semantics: str,
    task: str,
) -> None:
    """Issue #72: no route may accept q when nothing derives it."""
    result = solve_aba_acceptance(
        _assumption_free(),
        semantics=semantics,
        task=task,
        query=Q,
        backend=backend,
    )

    assert result.answer is False  # type: ignore[union-attr]


@pytest.mark.parametrize("backend", ["native", "sat", "asp", "auto"])
@pytest.mark.parametrize("semantics", ["complete", "preferred", "stable"])
@pytest.mark.parametrize("task", ["credulous", "skeptical"])
def test_every_acceptance_route_accepts_derivable_fact_control(
    backend: str,
    semantics: str,
    task: str,
) -> None:
    """Issue #72 control: with the fact rule -> q, q is in the closure of the
    empty extension, so every route accepts it."""
    framework = _assumption_free(frozenset({Rule((), Q, "strict")}))

    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=Q,
        backend=backend,
    )

    assert result.answer is True  # type: ignore[union-attr]


@given(
    flat_aba_frameworks(min_assumptions=0, max_assumptions=0, max_rules=5),
    st.sampled_from(["complete", "preferred", "stable"]),
    st.sampled_from(["credulous", "skeptical"]),
)
@settings(max_examples=60, deadline=None)
def test_asp_acceptance_matches_native_on_assumption_free_frameworks(
    framework: aba.ABAFramework,
    semantics: str,
    task: str,
) -> None:
    """Issue #72 guard: the audit's failures were all assumption-free, so for
    every language literal the ASP route must agree with the native reference
    on generated assumption-free frameworks (the regression itself is pinned
    by the explicit cases above)."""
    for query in sorted(framework.language, key=repr):
        native = solve_aba_acceptance(
            framework, semantics=semantics, task=task, query=query, backend="native"
        )
        asp = solve_aba_acceptance(
            framework, semantics=semantics, task=task, query=query, backend="asp"
        )
        assert asp.answer is native.answer  # type: ignore[union-attr]
