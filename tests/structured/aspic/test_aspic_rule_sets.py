"""Rule antecedents are read as sets (issue #102, maintainer decision).

Modgil & Prakken 2018 (Def 2, p.8; Def 5, p.9) and Prakken 2010 (Def 3.6)
write a rule as phi_1, ..., phi_n -> phi and build A_1, ..., A_n -> phi
from it. Neither fixes whether the antecedents form a sequence or a set;
this library adopts the set reading for strict and defeasible rules as a
chosen convention: a repeated antecedent literal is dropped, and rules with
the same kind, antecedent set, consequent and name are one rule. Named
defeasible rules stay distinct by name n(r).
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from argumentation.core.dung import (
    complete_extensions,
    grounded_extensions,
    preferred_extensions,
    stable_extensions,
)
from argumentation.structured.aspic.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
    build_arguments,
    conc,
    transposition_closure,
)
from tests.structured.aspic.test_aspic import (
    defeasible_rules,
    knowledge_base,
    logical_language,
    strict_rules,
)

P, Q, R = (Literal(GroundAtom(name)) for name in "pqr")
MAX_ENUMERATED_ARGUMENTS = 12


def test_strict_rule_drops_repeated_antecedent_literal() -> None:
    """Set reading: ``~q, ~q -> p`` is the rule ``~q -> p``."""
    repeated = Rule((Q.contrary, Q.contrary), P, "strict")

    assert repeated.antecedents == (Q.contrary,)
    assert repeated == Rule((Q.contrary,), P, "strict")


def test_permuted_strict_rules_are_one_rule() -> None:
    """Set reading: ``~p, ~q -> r`` and ``~q, ~p -> r`` are the same rule."""
    first = Rule((P.contrary, Q.contrary), R, "strict")
    second = Rule((Q.contrary, P.contrary), R, "strict")

    assert first == second
    assert len({first, second}) == 1


def test_defeasible_rule_drops_repeated_antecedent_literal() -> None:
    """Set reading also applies to defeasible rules: ``a, a => b`` is ``a => b``."""
    repeated = Rule((P, P), R, "defeasible", "d0")

    assert repeated.antecedents == (P,)
    assert repeated == Rule((P,), R, "defeasible", "d0")


def test_permuted_unnamed_defeasible_rules_are_one_rule() -> None:
    first = Rule((P, Q), R, "defeasible")
    second = Rule((Q, P), R, "defeasible")

    assert first == second
    assert len({first, second}) == 1


def test_named_defeasible_rules_stay_distinct_by_name() -> None:
    """n(r) is part of the rule: same body and head, different names, two rules."""
    forward = Rule((P, Q), R, "defeasible", "d0")
    backward = Rule((Q, P), R, "defeasible", "d1")

    assert forward.antecedents == backward.antecedents
    assert forward != backward


def test_repeated_defeasible_antecedent_does_not_square_arguments() -> None:
    """With two arguments for q, ``q, q => p`` builds one p-argument per
    q-argument under the set reading, not one per ordered pair."""
    s, t = Literal(GroundAtom("s")), Literal(GroundAtom("t"))
    system = ArgumentationSystem(
        frozenset({P, Q, s, t, P.contrary, Q.contrary, s.contrary, t.contrary}),
        ContrarinessFn(frozenset((atom, atom.contrary) for atom in (P, Q, s, t))),
        frozenset({Rule((s,), Q, "strict"), Rule((t,), Q, "strict")}),
        frozenset({Rule((Q, Q), P, "defeasible", "d0")}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({s, t}))

    arguments = build_arguments(system, kb)

    assert sum(1 for argument in arguments if conc(argument) == Q) == 2
    assert sum(1 for argument in arguments if conc(argument) == P) == 2


def test_repeated_antecedent_does_not_square_arguments() -> None:
    """Issue #102: with two arguments for ~q, the sequence reading of
    ``~q, ~q -> p`` built 2 x 2 = 4 arguments for p, one per ordered pair of
    ~q arguments; the set reading builds one per ~q argument."""
    not_q, s, t = Q.contrary, Literal(GroundAtom("s")), Literal(GroundAtom("t"))
    system = ArgumentationSystem(
        frozenset({P, not_q, s, t, P.contrary, Q, s.contrary, t.contrary}),
        ContrarinessFn(frozenset((atom, atom.contrary) for atom in (P, Q, s, t))),
        frozenset(
            {
                Rule((s,), not_q, "strict"),
                Rule((t,), not_q, "strict"),
                Rule((not_q, not_q), P, "strict"),
            }
        ),
        frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({s, t}))

    arguments = build_arguments(system, kb)

    assert sum(1 for argument in arguments if conc(argument) == not_q) == 2
    assert sum(1 for argument in arguments if conc(argument) == P) == 2


def test_datalog_grounding_merges_permuted_strict_bodies() -> None:
    """Producer audit: Datalog strict rules whose bodies are the same set
    (permuted, with a repeated literal) ground to one strict rule, and the
    projection keeps both authored source ids (#67)."""
    gunray = pytest.importorskip("gunray")
    from argumentation.structured.aspic.datalog_grounding import (
        ground_defeasible_theory,
    )

    theory = gunray.DefeasibleTheory(
        facts={"bird": {("a",)}, "wing": {("a",)}},
        strict_rules=[
            gunray.Rule(id="s1", head="flies(X)", body=["bird(X)", "wing(X)"]),
            gunray.Rule(
                id="s2", head="flies(X)", body=["wing(X)", "bird(X)", "bird(X)"]
            ),
        ],
    )

    grounded = ground_defeasible_theory(theory, simplify=False)

    (rule,) = tuple(grounded.system.strict_rules)
    assert len(rule.antecedents) == 2
    assert (
        grounded.source_to_ground_rules["s1"] == grounded.source_to_ground_rules["s2"]
    )


def test_transposition_closure_emits_canonical_rules() -> None:
    """Producer audit: transposing ``p, q -> r`` yields ``~r, q -> ~p`` and
    ``p, ~r -> ~q`` as set-read rules, with no permuted duplicates."""
    not_p, not_q, not_r = (atom.contrary for atom in (P, Q, R))
    language = frozenset({P, Q, R, not_p, not_q, not_r})
    contrariness = ContrarinessFn(
        frozenset((atom, atom.contrary) for atom in (P, Q, R))
    )

    closed, _language = transposition_closure(
        frozenset({Rule((Q, P), R, "strict")}), language, contrariness
    )

    assert closed == frozenset(
        {
            Rule((P, Q), R, "strict"),
            Rule((not_r, Q), not_p, "strict"),
            Rule((P, not_r), not_q, "strict"),
        }
    )
    assert all(
        rule.antecedents == tuple(sorted(set(rule.antecedents), key=repr))
        for rule in closed
    )


def _extension_conclusions(system, kb) -> dict[str, frozenset[frozenset[Literal]]]:
    """Each semantics' extensions as sets of conclusions, which identifies
    arguments up to clones."""
    preferences = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )
    projection = build_abstract_framework(system, kb, preferences)
    framework = projection.framework

    def conclusions(extensions) -> frozenset[frozenset[Literal]]:
        return frozenset(
            frozenset(
                conc(projection.id_to_argument[argument]) for argument in extension
            )
            for extension in extensions
        )

    return {
        "grounded": conclusions(grounded_extensions(framework)),
        "complete": conclusions(complete_extensions(framework)),
        "preferred": conclusions(preferred_extensions(framework)),
        "stable": conclusions(stable_extensions(framework)),
    }


@given(data=st.data())
@settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_merging_permuted_duplicate_strict_rules_preserves_extensions(data) -> None:
    """A1: a permuted duplicate of a strict rule only produces clones (same
    premises, defeasible rules and attack points), so extensions are
    unchanged up to clones. The pre-merge representation is emulated by a
    duplicate carrying a name, which keeps it a separate rule value."""
    language, contrariness = data.draw(logical_language(max_atoms=3))
    strict = data.draw(strict_rules(language, contrariness, max_rules=3))
    defeasible = data.draw(defeasible_rules(language, max_rules=2))
    kb = data.draw(knowledge_base(language, strict, defeasible))
    multi_antecedent = sorted(
        (rule for rule in strict if len(rule.antecedents) > 1), key=repr
    )
    assume(multi_antecedent)
    duplicated = data.draw(st.sampled_from(multi_antecedent))
    # Make the duplicated rule fire: its antecedents become ordinary premises.
    kb = KnowledgeBase(
        axioms=kb.axioms - frozenset(duplicated.antecedents),
        premises=kb.premises | frozenset(duplicated.antecedents),
    )
    duplicate = Rule(
        tuple(reversed(duplicated.antecedents)), duplicated.consequent, "strict", "dup"
    )

    merged = ArgumentationSystem(language, contrariness, strict, defeasible)
    with_clones = ArgumentationSystem(
        language, contrariness, strict | {duplicate}, defeasible
    )
    clone_arguments = build_arguments(with_clones, kb)
    # Every example must actually contain clone arguments, and exact
    # complete-labelling enumeration needs a small argument count.
    assume(len(clone_arguments) > len(build_arguments(merged, kb)))
    assume(len(clone_arguments) <= MAX_ENUMERATED_ARGUMENTS)

    assert _extension_conclusions(with_clones, kb) == _extension_conclusions(merged, kb)
