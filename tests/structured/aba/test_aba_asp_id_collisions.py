"""Regression tests for ABA ASP id-collision detection (BUG-2).

``_literal_id`` lossily sanitizes a literal's repr to ``[A-Za-z0-9_]``. Two
distinct literals can therefore map to the same sanitized ASP id (e.g. ``a.b``
and ``a-b`` both sanitize to ``a_b``). When that happens the dict comprehensions
in ``encode_aba_theory`` silently overwrite one entry with the other, corrupting
the ASP encoding. The encoder must instead fail loud with ``ValueError``.
"""

from __future__ import annotations

import pytest

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_asp import _literal_id, encode_aba_theory
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def test_colliding_assumption_ids_raise() -> None:
    """Two distinct assumptions sharing a sanitized id must raise, not merge."""
    a = Literal(GroundAtom("a.b"))
    b = Literal(GroundAtom("a-b"))
    # Precondition: distinct literals, identical sanitized ids.
    assert a != b
    assert _literal_id(a) == _literal_id(b)

    contrary_a = Literal(GroundAtom("ca"))
    contrary_b = Literal(GroundAtom("cb"))
    framework = ABAFramework(
        language=frozenset({a, b, contrary_a, contrary_b}),
        rules=frozenset(),
        assumptions=frozenset({a, b}),
        contrary={a: contrary_a, b: contrary_b},
    )

    with pytest.raises(ValueError, match="duplicate assumption ASP ids"):
        encode_aba_theory(framework)


def test_colliding_literal_ids_raise() -> None:
    """Distinct non-assumption literals sharing a sanitized id must raise."""
    assumption = Literal(GroundAtom("alpha"))
    contrary = Literal(GroundAtom("not_alpha"))
    # ``p.q`` and ``p-q`` both sanitize to ``p_q`` but are distinct literals.
    head = Literal(GroundAtom("p.q"))
    other = Literal(GroundAtom("p-q"))
    assert head != other
    assert _literal_id(head) == _literal_id(other)

    framework = ABAFramework(
        language=frozenset({assumption, contrary, head, other}),
        rules=frozenset({Rule((assumption,), head, "strict")}),
        assumptions=frozenset({assumption}),
        contrary={assumption: contrary},
    )

    with pytest.raises(ValueError, match="duplicate literal ASP ids"):
        encode_aba_theory(framework)


def test_collision_free_framework_encodes_without_raising() -> None:
    """Negative control: a clean framework must still encode successfully."""
    alpha = Literal(GroundAtom("alpha"))
    beta = Literal(GroundAtom("beta"))
    not_alpha = Literal(GroundAtom("not_alpha"))
    not_beta = Literal(GroundAtom("not_beta"))
    framework = ABAFramework(
        language=frozenset({alpha, beta, not_alpha, not_beta}),
        rules=frozenset(
            {
                Rule((alpha,), not_beta, "strict"),
                Rule((beta,), not_alpha, "strict"),
            }
        ),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: not_alpha, beta: not_beta},
    )

    encoding = encode_aba_theory(framework)

    # Every distinct assumption/literal kept its own id (no silent merge).
    assert len(encoding.assumption_by_id) == len(framework.assumptions)
    assert len(encoding.literal_by_id) == len(framework.language)
