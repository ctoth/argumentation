from __future__ import annotations

import re

import pytest

from argumentation.af_revision import AFChangeKind, ExtensionRevisionState, _classify_extension_change
from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)
from argumentation.aspic_encoding import encode_aspic_theory
from argumentation.dung import ArgumentationFramework, admissible, ideal_extension
from argumentation.partial_af import PartialArgumentationFramework
from argumentation.preference import strictly_weaker
from argumentation.probabilistic import _z_for_confidence
from argumentation.semantics import accepted_arguments


def test_workstream_o_arg_done() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "x", "y"}),
        defeats=frozenset(
            {
                ("x", "a"),
                ("x", "x"),
                ("b", "x"),
                ("y", "b"),
                ("y", "y"),
                ("a", "y"),
            }
        ),
    )
    ideal = ideal_extension(framework, backend="brute")
    assert ideal == frozenset({"a", "b"})
    assert admissible(ideal, framework.arguments, framework.defeats)

    p = Literal(GroundAtom("P", (1, 2)))
    not_p = p.contrary
    pref = PreferenceConfig(frozenset(), frozenset(), comparison="elitist", link="last")
    system = ArgumentationSystem(
        language=frozenset({p, not_p}),
        contrariness=ContrarinessFn(frozenset({(p, not_p)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    encoding = encode_aspic_theory(system, KnowledgeBase(frozenset({not_p}), frozenset({p})), pref)
    assert all(
        re.fullmatch(r"[a-z][A-Za-z0-9_]*", fact.removesuffix(").").split("(", 1)[1])
        for fact in encoding.facts
        if fact.startswith(("axiom(", "premise("))
    )

    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    duplicate_system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(
            {
                Rule((p,), q, "defeasible", "dup"),
                Rule((p,), r, "defeasible", "dup"),
            }
        ),
    )
    with pytest.raises(ValueError, match="duplicate defeasible rule name"):
        encode_aspic_theory(duplicate_system, KnowledgeBase(frozenset({p}), frozenset()), pref)

    assert _classify_extension_change(
        (frozenset({"a"}), frozenset({"b"})),
        (frozenset({"a"}),),
    ) is AFChangeKind.DECISIVE

    calls: list[frozenset[str]] = []

    def ranking(extension: frozenset[str]) -> int:
        calls.append(extension)
        return 0

    state = ExtensionRevisionState.from_extensions(
        frozenset(f"a{i}" for i in range(20)),
        (frozenset({"a0"}),),
        ranking=ranking,
    )
    assert calls == []
    assert state.minimal_extensions((frozenset({"a0"}),)) == (frozenset({"a0"}),)

    assert strictly_weaker([1.0], [], "elitist") is True

    partial = PartialArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b")}),
        ignorance=frozenset({("b", "a")}),
        non_attacks=frozenset({("a", "a"), ("b", "b")}),
    )
    assert accepted_arguments(partial, semantics="grounded", mode="necessary_skeptical") == frozenset()
    assert accepted_arguments(partial, semantics="grounded", mode="possible_skeptical") == frozenset({"a"})
    with pytest.raises(ValueError, match="necessary_skeptical"):
        accepted_arguments(partial, semantics="grounded", mode="skeptical")

    assert _z_for_confidence(0.975) == pytest.approx(2.2414027276)
