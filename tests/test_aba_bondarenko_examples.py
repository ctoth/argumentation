from __future__ import annotations

from argumentation.aba import (
    ABAFramework,
    admissible,
    complete_extensions,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    stable_extensions,
    well_founded_extension,
)
from argumentation.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def referendum_aba() -> ABAFramework:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")
    return ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset(
            {
                Rule((alpha,), leave, "strict"),
                Rule((beta,), stay, "strict"),
            }
        ),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )


def test_bondarenko_cyras_flat_referendum_plain_aba_extensions() -> None:
    framework = referendum_aba()
    alpha = lit("alpha")
    beta = lit("beta")

    assert admissible(framework, frozenset({alpha}))
    assert admissible(framework, frozenset({beta}))
    assert complete_extensions(framework) == (frozenset(), frozenset({alpha}), frozenset({beta}))
    assert preferred_extensions(framework) == (frozenset({alpha}), frozenset({beta}))
    assert stable_extensions(framework) == (frozenset({alpha}), frozenset({beta}))
    assert grounded_extension(framework) == frozenset()
    assert well_founded_extension(framework) == frozenset()
    assert ideal_extension(framework) == frozenset()
