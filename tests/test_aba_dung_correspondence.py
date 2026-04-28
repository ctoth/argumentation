from __future__ import annotations

from argumentation.aba import ABAFramework, aba_to_dung, grounded_extension, preferred_extensions
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.dung import grounded_extension as dung_grounded_extension
from argumentation.dung import preferred_extensions as dung_preferred_extensions


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def argument_label(support: frozenset[Literal], conclusion: Literal) -> str:
    support_text = ",".join(sorted(repr(assumption) for assumption in support))
    return f"{{{support_text}}} |- {conclusion!r}"


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

    assert dung_grounded_extension(dung) == {
        argument_label(frozenset({literal}), literal)
        for literal in grounded_extension(framework)
    }
    assert tuple(dung_preferred_extensions(dung)) == tuple(
        frozenset(argument_label(frozenset({literal}), literal) for literal in extension)
        for extension in preferred_extensions(framework)
    )


def test_flat_aba_to_dung_preserves_joint_support_attacks() -> None:
    """Bondarenko et al. 1997 p.76: a set attacks by deriving a contrary."""
    alpha = lit("alpha")
    beta = lit("beta")
    gamma = lit("gamma")
    block_gamma = lit("block_gamma")
    not_alpha = lit("not_alpha")
    not_beta = lit("not_beta")
    framework = ABAFramework(
        language=frozenset({alpha, beta, gamma, block_gamma, not_alpha, not_beta}),
        rules=frozenset({Rule((alpha, beta), block_gamma, "strict")}),
        assumptions=frozenset({alpha, beta, gamma}),
        contrary={alpha: not_alpha, beta: not_beta, gamma: block_gamma},
    )
    dung = aba_to_dung(framework)

    assert argument_label(frozenset({alpha, beta}), block_gamma) in dung.arguments
    grounded = dung_grounded_extension(dung)
    assert argument_label(frozenset({alpha}), alpha) in grounded
    assert argument_label(frozenset({beta}), beta) in grounded
    assert argument_label(frozenset({gamma}), gamma) not in grounded
