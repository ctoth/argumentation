from __future__ import annotations

from argumentation.structured.aba._closure import horn_closure
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def _lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


a, b, c, d, f = (_lit(name) for name in ("a", "b", "c", "d", "f"))


def test_chain_propagates_through_rules() -> None:
    rules = [Rule((a,), b, "strict"), Rule((b,), c, "strict")]
    assert horn_closure([a], rules) == frozenset({a, b, c})


def test_branching_rules_fire_all_reachable() -> None:
    rules = [
        Rule((a,), b, "strict"),
        Rule((a,), c, "strict"),
        Rule((b,), d, "strict"),
    ]
    assert horn_closure([a], rules) == frozenset({a, b, c, d})


def test_multi_antecedent_rule_needs_all_antecedents() -> None:
    rules = [Rule((a, b), c, "strict")]
    assert horn_closure([a], rules) == frozenset({a})
    assert horn_closure([a, b], rules) == frozenset({a, b, c})


def test_cycle_terminates_at_fixpoint() -> None:
    rules = [Rule((a,), b, "strict"), Rule((b,), a, "strict")]
    assert horn_closure([a], rules) == frozenset({a, b})
    # The cycle is unreachable without an entry point into it.
    assert horn_closure([c], rules) == frozenset({c})


def test_empty_seed_and_rules_yields_empty() -> None:
    assert horn_closure([], []) == frozenset()


def test_fact_rules_fire_from_empty_seed() -> None:
    rules = [Rule((), f, "strict"), Rule((f,), c, "strict")]
    assert horn_closure([], rules) == frozenset({f, c})


def test_already_closed_seed_is_unchanged() -> None:
    rules = [Rule((a,), b, "strict")]
    assert horn_closure([a, b], rules) == frozenset({a, b})


def test_duplicate_antecedents_do_not_block_firing() -> None:
    rules = [Rule((a, a), b, "strict")]
    assert horn_closure([a], rules) == frozenset({a, b})


def test_rule_order_does_not_change_result() -> None:
    forward = [Rule((a,), b, "strict"), Rule((b,), c, "strict")]
    reverse = [Rule((b,), c, "strict"), Rule((a,), b, "strict")]
    assert (
        horn_closure([a], forward) == horn_closure([a], reverse) == frozenset({a, b, c})
    )
