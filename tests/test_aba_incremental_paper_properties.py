from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation import aba as native_aba
from argumentation.aba import ABAFramework, AssumptionSet, derives
from argumentation.aba_asp import encode_aba_theory, solve_aba_with_backend
from argumentation.aba_incremental import (
    AbaIncrementalSolver,
    LEHTONEN_INCREMENTAL_ASP_CITATION,
    LEHTONEN_INCREMENTAL_ASP_PAGE_CITATIONS,
)
from tests.aba_hypothesis_generators import flat_aba_frameworks


PAPER_PAGE_NOTE = (
    "Read from papers/Lehtonen_2021_IncrementalASP_ABA_pngs page images: "
    "p.5 defines ABA(F) as assumption/head/body/contrary facts and Algorithm 1; "
    "p.6 states constr(out(I)) rules out a complete set and its subsets; "
    "p.12 says the implementation uses Clingo's incremental Python interface."
)


@given(flat_aba_frameworks(max_assumptions=4, max_rules=7))
@settings(max_examples=40)
def test_lehtonen_p5_core_fact_surface_is_structural(framework: ABAFramework) -> None:
    """Lehtonen et al. p.5: ABA(F) is assumption/head/body/contrary facts."""
    encoding = encode_aba_theory(framework, include_supports=False)
    facts = set(encoding.facts)
    id_by_literal = {literal: ident for ident, literal in encoding.literal_by_id.items()}

    assert PAPER_PAGE_NOTE
    assert encoding.metadata["encoding"] == "flat_aba_core_facts"
    assert not any(fact.startswith("support_") for fact in facts)

    for assumption_id, assumption in encoding.assumption_by_id.items():
        assert f"assumption({assumption_id})." in facts
        assert f"contrary({assumption_id},{id_by_literal[framework.contrary[assumption]]})." in facts

    for index, rule in enumerate(sorted(framework.rules, key=repr)):
        rule_id = f"r_{index}"
        assert f"head({rule_id},{id_by_literal[rule.consequent]})." in facts
        for antecedent in rule.antecedents:
            assert f"body({rule_id},{id_by_literal[antecedent]})." in facts


@given(flat_aba_frameworks(max_assumptions=4, max_rules=7), st.data())
@settings(max_examples=40)
def test_lehtonen_p6_refinement_blocks_candidate_and_subsets(
    framework: ABAFramework, data
) -> None:
    """Lehtonen et al. pp.5-6: constr(out(I)) excludes in(I) and its subsets."""
    pytest.importorskip("clingo")
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    candidate = frozenset(
        data.draw(st.lists(st.sampled_from(assumptions), unique=True), label="candidate")
    )
    out_set = frozenset(framework.assumptions - candidate)

    solver = AbaIncrementalSolver(framework)
    constraint = solver._refinement_constraint(out_set)

    if not out_set:
        assert constraint is None
        assert candidate == framework.assumptions
        return

    assert constraint is not None
    assert constraint.startswith(":- out(")
    assert constraint.endswith(").")

    for tested in _all_subsets(framework.assumptions):
        blocked_by_constraint_body = out_set <= (framework.assumptions - tested)
        assert blocked_by_constraint_body is (tested <= candidate)


@given(flat_aba_frameworks(max_assumptions=3, max_rules=5))
@settings(max_examples=20, deadline=None)
def test_multishot_results_carry_page_image_provenance(framework: ABAFramework) -> None:
    """Lehtonen et al. p.12: Clingo incremental Python implementation path."""
    pytest.importorskip("clingo")

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="preferred",
        task="single-extension",
        simplify=False,
    )

    assert result.status == "success"
    assert result.metadata["paper"] == LEHTONEN_INCREMENTAL_ASP_CITATION
    assert result.metadata["paper_pages"] == LEHTONEN_INCREMENTAL_ASP_PAGE_CITATIONS
    assert "p.5" in result.metadata["paper_pages"]
    assert "p.6" in result.metadata["paper_pages"]
    assert "p.12" in result.metadata["paper_pages"]


@given(flat_aba_frameworks(max_assumptions=4, max_rules=7))
@settings(max_examples=40, deadline=None)
def test_direct_stable_witness_matches_native_stable_extensions(
    framework: ABAFramework,
) -> None:
    """Lehtonen pp.5-6: stable witness uses ABA(F) facts and supported closure."""
    pytest.importorskip("clingo")

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="stable",
        task="single-extension",
        simplify=False,
    )
    stable = native_aba.stable_extensions(framework)

    assert result.status == "success"
    assert result.metadata["algorithm"] == "direct-stable-witness"
    assert result.metadata["paper"] == LEHTONEN_INCREMENTAL_ASP_CITATION
    if result.witness is None:
        assert stable == tuple()
    else:
        assert result.witness in stable


@given(flat_aba_frameworks(max_assumptions=3, max_rules=5), st.data())
@settings(max_examples=20, deadline=None)
def test_ds_pr_algorithm_one_metadata_and_answer_match_reference(
    framework: ABAFramework, data
) -> None:
    """Lehtonen et al. pp.5-6: Algorithm 1 decides skeptical preferred."""
    pytest.importorskip("clingo")
    query = data.draw(st.sampled_from(tuple(sorted(framework.language, key=repr))), label="query")
    preferred = native_aba.preferred_extensions(framework)

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="preferred",
        task="skeptical",
        query=query,
        simplify=False,
    )

    assert result.status == "success"
    assert result.metadata["algorithm"] == "L21-TPLP-Alg1"
    assert result.metadata["paper"] == LEHTONEN_INCREMENTAL_ASP_CITATION
    assert result.answer is all(derives(framework, extension, query) for extension in preferred)
    if result.answer is False:
        assert result.counterexample is not None
        assert not derives(framework, result.counterexample, query)


def _all_subsets(items: frozenset) -> tuple[AssumptionSet, ...]:
    ordered = tuple(sorted(items, key=repr))
    subsets: list[AssumptionSet] = []
    for mask in range(1 << len(ordered)):
        subsets.append(frozenset(item for index, item in enumerate(ordered) if mask & (1 << index)))
    return tuple(subsets)
