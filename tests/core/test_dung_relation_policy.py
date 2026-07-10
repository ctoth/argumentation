from itertools import combinations, product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.core import dung
from argumentation.core.dung import ArgumentationFramework


def _single_relation_framework(*, duplicate_attack_metadata: bool = False):
    relation = frozenset({("a", "b")})
    return ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=relation,
        attacks=relation if duplicate_attack_metadata else None,
    )


def _structured_distinguishing_framework() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b")}),
        defeats=frozenset(),
    )


def _admissible_extensions(
    framework: ArgumentationFramework,
) -> set[frozenset[str]]:
    candidates = (
        frozenset(candidate)
        for size in range(len(framework.arguments) + 1)
        for candidate in combinations(sorted(framework.arguments), size)
    )
    return {
        candidate
        for candidate in candidates
        if dung.admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
        )
    }


@st.composite
def _single_relation_frameworks(
    draw: st.DrawFn,
) -> ArgumentationFramework:
    size = draw(st.integers(min_value=1, max_value=4))
    arguments = frozenset(("a", "b", "c", "d")[:size])
    pairs = tuple(product(sorted(arguments), repeat=2))
    relation = frozenset(
        draw(st.sets(st.sampled_from(pairs), max_size=len(pairs)))
    )
    return ArgumentationFramework(arguments=arguments, defeats=relation)


@st.composite
def _structured_frameworks_with_blocked_attack(
    draw: st.DrawFn,
) -> ArgumentationFramework:
    size = draw(st.integers(min_value=1, max_value=4))
    arguments = frozenset(("a", "b", "c", "d")[:size])
    pairs = tuple(product(sorted(arguments), repeat=2))
    attacks = frozenset(
        draw(st.sets(st.sampled_from(pairs), min_size=1, max_size=len(pairs)))
    )
    blocked = draw(st.sampled_from(sorted(attacks)))
    remaining = tuple(sorted(attacks - {blocked}))
    defeats = (
        frozenset()
        if not remaining
        else frozenset(
            draw(st.sets(st.sampled_from(remaining), max_size=len(remaining)))
        )
    )
    return ArgumentationFramework(
        arguments=arguments,
        attacks=attacks,
        defeats=defeats,
    )


# Dung 1995, p.326:
# papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png
def test_plain_dung_naive_and_admissible_use_the_single_relation() -> None:
    framework = _single_relation_framework()

    assert set(dung.naive_extensions(framework)) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }
    assert _admissible_extensions(framework) == {
        frozenset(),
        frozenset({"a"}),
    }


# Gaggl and Woltran 2013, pp.927-929:
# papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-002.png
# papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-003.png
# papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-004.png
def test_plain_dung_stage_and_cf2_use_the_same_single_relation() -> None:
    framework = _single_relation_framework()

    assert dung.stage_extensions(framework) == [frozenset({"a"})]
    assert dung.cf2_extensions(framework) == [frozenset({"a"})]


def test_identical_attack_metadata_remains_a_single_relation_framework() -> None:
    framework = _single_relation_framework(duplicate_attack_metadata=True)

    assert set(dung.naive_extensions(framework)) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }
    assert _admissible_extensions(framework) == {
        frozenset(),
        frozenset({"a"}),
    }
    assert dung.stage_extensions(framework) == [frozenset({"a"})]
    assert dung.cf2_extensions(framework) == [frozenset({"a"})]


@given(_single_relation_frameworks())
@settings(max_examples=40, deadline=None)
def test_identical_attack_metadata_preserves_every_single_relation_semantic(
    framework: ArgumentationFramework,
) -> None:
    """Dung 1995 p.326 and Gaggl 2013 pp.927-929 use one relation."""
    duplicate = ArgumentationFramework(
        arguments=framework.arguments,
        defeats=framework.defeats,
        attacks=framework.defeats,
    )

    assert dung.naive_extensions(duplicate) == dung.naive_extensions(framework)
    assert _admissible_extensions(duplicate) == _admissible_extensions(framework)
    assert dung.stage_extensions(duplicate) == dung.stage_extensions(framework)
    assert dung.stage2_extensions(duplicate) == dung.stage2_extensions(framework)
    assert dung.cf2_extensions(duplicate) == dung.cf2_extensions(framework)


# Modgil and Prakken 2018, Defs. 9, 14-15, pp.12,14:
# papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-011.png
# papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-013.png
def test_structured_naive_is_maximal_attack_conflict_free() -> None:
    framework = _structured_distinguishing_framework()

    assert set(dung.naive_extensions(framework)) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }


@given(_structured_frameworks_with_blocked_attack())
@settings(max_examples=60, deadline=None)
def test_structured_naive_matches_maximal_attack_conflict_free_property(
    framework: ArgumentationFramework,
) -> None:
    """Modgil-Prakken 2018 page-013.png, Definition 14."""
    assert framework.attacks is not None
    conflict_free_candidates = [
        candidate
        for size in range(len(framework.arguments) + 1)
        for values in combinations(sorted(framework.arguments), size)
        if dung.conflict_free(
            candidate := frozenset(values),
            framework.attacks,
        )
    ]
    expected = {
        candidate
        for candidate in conflict_free_candidates
        if not any(candidate < other for other in conflict_free_candidates)
    }

    assert set(dung.naive_extensions(framework)) == expected


def test_structured_admissible_uses_attacks_for_conflict_and_defeats_for_defense(
) -> None:
    framework = _structured_distinguishing_framework()

    assert _admissible_extensions(framework) == {
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
    }


@pytest.mark.parametrize(
    ("solve", "semantic_name"),
    [
        (dung.stage_extensions, "stage"),
        (dung.stage2_extensions, "stage2"),
        (dung.cf2_extensions, "CF2"),
    ],
)
def test_mixed_relation_stage_and_cf2_are_rejected_before_semantic_routing(
    monkeypatch,
    solve,
    semantic_name: str,
) -> None:
    framework = _structured_distinguishing_framework()

    def forbidden_scc(*args, **kwargs):
        raise AssertionError("unsupported mixed input must stop before SCC routing")

    monkeypatch.setattr(dung, "_strongly_connected_components", forbidden_scc)

    with pytest.raises(
        ValueError,
        match=rf"{semantic_name} semantics.*distinct attack and defeat relations",
    ):
        solve(framework)
