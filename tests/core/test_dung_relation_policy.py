from itertools import combinations

import pytest

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


# Modgil and Prakken 2018, Defs. 9, 14-15, pp.12,14:
# papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-011.png
# papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-013.png
def test_structured_naive_is_maximal_attack_conflict_free() -> None:
    framework = _structured_distinguishing_framework()

    assert set(dung.naive_extensions(framework)) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }


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
