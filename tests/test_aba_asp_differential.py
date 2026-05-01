from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

import argumentation
from argumentation import aba as native_aba
from argumentation.aba import ABAFramework
from argumentation.aba_asp import solve_aba_with_backend
from argumentation.aba_sat import support_extensions
from argumentation.aspic import GroundAtom, Literal, Rule


def test_aba_asp_module_is_exported_from_package() -> None:
    assert "aba_asp" in argumentation.__all__


def test_aba_asp_stable_matches_support_reference() -> None:
    alpha = Literal(GroundAtom("alpha"))
    beta = Literal(GroundAtom("beta"))
    not_alpha = Literal(GroundAtom("not_alpha"))
    not_beta = Literal(GroundAtom("not_beta"))
    framework = ABAFramework(
        language=frozenset({alpha, beta, not_alpha, not_beta}),
        rules=frozenset({
            Rule((alpha,), not_beta, "strict"),
            Rule((beta,), not_alpha, "strict"),
        }),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: not_alpha, beta: not_beta},
    )

    result = solve_aba_with_backend(framework, backend="asp", semantics="stable")

    assert result.status == "success"
    assert set(result.extensions) == set(support_extensions(framework, "stable"))


@st.composite
def small_aba_frameworks(draw):
    size = draw(st.integers(min_value=1, max_value=4))
    assumptions = tuple(Literal(GroundAtom(f"a{index}")) for index in range(size))
    contraries = tuple(Literal(GroundAtom(f"c{index}")) for index in range(size))
    rules: set[Rule] = set()
    for index, contrary in enumerate(contraries):
        include_rule = draw(st.booleans())
        if not include_rule:
            continue
        body_size = draw(st.integers(min_value=1, max_value=size))
        body = draw(
            st.lists(
                st.sampled_from(assumptions),
                min_size=body_size,
                max_size=body_size,
                unique=True,
            )
        )
        rules.add(Rule(tuple(body), contrary, "strict", f"r_{index}"))
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=dict(zip(assumptions, contraries, strict=True)),
    )


@given(small_aba_frameworks(), st.sampled_from(("complete", "stable", "preferred")))
@settings(deadline=10000, max_examples=50)
def test_aba_asp_matches_support_reference_on_generated_frameworks(framework, semantics) -> None:
    result = solve_aba_with_backend(framework, backend="asp", semantics=semantics)

    assert result.status == "success"
    assert set(result.extensions) == set(support_extensions(framework, semantics))


@given(small_aba_frameworks())
@settings(deadline=10000, max_examples=25)
def test_aba_asp_grounded_matches_native_on_generated_frameworks(framework) -> None:
    result = solve_aba_with_backend(framework, backend="asp", semantics="grounded")

    assert result.status == "success"
    assert result.extensions == (native_aba.grounded_extension(framework),)
