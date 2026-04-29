"""WS-F upstream ASPIC API contracts required by propstore.

These tests pin the public surfaces propstore needs for Modgil 2014
Section 4.2 indirect-consistency closure and for avoiding private helper
imports at the package boundary.
"""

from argumentation import aspic


def test_transposition_closure_returns_closed_rules_and_post_closure_language():
    """Modgil 2014 Section 4.2 needs closure rules and their language together."""

    p = aspic.Literal(aspic.GroundAtom("p"))
    not_p = p.contrary
    q = aspic.Literal(aspic.GroundAtom("q"))
    not_q = q.contrary
    seed = aspic.Rule(
        antecedents=(p,),
        consequent=q,
        kind="strict",
    )
    language = frozenset({p, not_p, q, not_q})
    contrariness = aspic.ContrarinessFn(
        contradictories=frozenset({(p, not_p), (q, not_q)})
    )

    result = aspic.transposition_closure(frozenset({seed}), language, contrariness)

    assert isinstance(result, tuple)
    closed_rules, post_closure_language = result
    assert seed in closed_rules
    assert aspic.Rule(antecedents=(not_q,), consequent=not_p, kind="strict") in closed_rules
    assert post_closure_language >= language
    assert {
        literal
        for rule in closed_rules
        for literal in (*rule.antecedents, rule.consequent)
    } <= post_closure_language


def test_contraries_of_is_public_boundary_symbol():
    """Propstore must not import private ASPIC helpers from argumentation."""

    assert hasattr(aspic, "contraries_of")
