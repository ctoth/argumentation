from __future__ import annotations

import pytest

from argumentation.aba import ABAArgument, ABAFramework, NotFlatABAError, argument_for, attacks, derives
from argumentation.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_toni_forward_deduction_and_attack_views() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")
    framework = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset({Rule((alpha,), leave, "strict"), Rule((beta,), stay, "strict")}),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )

    assert derives(framework, frozenset({alpha}), leave)
    assert not derives(framework, frozenset({alpha}), stay)
    assert argument_for(framework, leave) == ABAArgument(frozenset({alpha}), leave)
    assert attacks(framework, frozenset({alpha}), frozenset({beta}))
    assert attacks(framework, frozenset({beta}), frozenset({alpha}))


def test_non_flat_aba_is_rejected_at_construction() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    delta = lit("delta")
    stay = lit("stay")

    with pytest.raises(NotFlatABAError, match="flat"):
        ABAFramework(
            language=frozenset({alpha, beta, delta, stay}),
            rules=frozenset({Rule((delta,), beta, "strict")}),
            assumptions=frozenset({alpha, beta, delta}),
            contrary={alpha: stay, beta: alpha, delta: beta},
        )
