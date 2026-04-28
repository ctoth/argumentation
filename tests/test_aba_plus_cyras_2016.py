from __future__ import annotations

from argumentation.aba import (
    ABAFramework,
    ABAPlusFramework,
    attacks_with_preferences,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    stable_extensions,
)
from argumentation.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_cyras_2016_referendum_attack_reversal_selects_beta() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")
    base = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset({Rule((alpha,), leave, "strict"), Rule((beta,), stay, "strict")}),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )
    framework = ABAPlusFramework(base, preference_order=frozenset({(alpha, beta)}))

    assert not attacks_with_preferences(framework, frozenset({alpha}), frozenset({beta}))
    assert attacks_with_preferences(framework, frozenset({beta}), frozenset({alpha}))
    assert preferred_extensions(framework) == (frozenset({beta}),)
    assert stable_extensions(framework) == (frozenset({beta}),)
    assert grounded_extension(framework) == frozenset({beta})
    assert ideal_extension(framework) == frozenset({beta})
