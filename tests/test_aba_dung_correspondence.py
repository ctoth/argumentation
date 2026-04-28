from __future__ import annotations

from argumentation.aba import ABAFramework, aba_to_dung, grounded_extension, preferred_extensions
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.dung import grounded_extension as dung_grounded_extension
from argumentation.dung import preferred_extensions as dung_preferred_extensions


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_flat_aba_to_dung_preserves_singleton_attack_semantics() -> None:
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
    dung = aba_to_dung(framework)

    assert dung_grounded_extension(dung) == {repr(literal) for literal in grounded_extension(framework)}
    assert tuple(dung_preferred_extensions(dung)) == tuple(
        frozenset(repr(literal) for literal in extension)
        for extension in preferred_extensions(framework)
    )
