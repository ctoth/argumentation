from __future__ import annotations

from hypothesis import given, settings

from argumentation.dung import (
    ArgumentationFramework,
    admissible,
    ideal_extension,
    preferred_extensions,
)
from tests.test_dung import argumentation_frameworks


def test_admissibility_is_not_downward_closed() -> None:
    """A proper subset of an admissible set need not defend its members."""
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "e"}),
        defeats=frozenset(
            {
                ("e", "a"),
                ("c", "a"),
                ("b", "e"),
                ("b", "c"),
                ("d", "e"),
                ("d", "c"),
            }
        ),
    )

    assert admissible(frozenset({"a", "b"}), framework.arguments, framework.defeats)
    assert admissible(frozenset({"a", "d"}), framework.arguments, framework.defeats)
    assert not admissible(frozenset({"a"}), framework.arguments, framework.defeats)


def test_ideal_extension_requires_joint_mutual_defense() -> None:
    """Regression for single-argument greedy ideal construction."""
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

    assert tuple(preferred_extensions(framework)) == (frozenset({"a", "b"}),)
    assert not admissible(frozenset({"a"}), framework.arguments, framework.defeats)
    assert not admissible(frozenset({"b"}), framework.arguments, framework.defeats)
    assert admissible(frozenset({"a", "b"}), framework.arguments, framework.defeats)
    assert ideal_extension(framework) == frozenset({"a", "b"})


@given(argumentation_frameworks(max_args=5))
@settings(deadline=None)
def test_ideal_extension_is_admissible_and_below_every_preferred(
    framework: ArgumentationFramework,
) -> None:
    ideal = ideal_extension(framework)

    assert admissible(ideal, framework.arguments, framework.defeats)
    assert all(ideal <= preferred for preferred in preferred_extensions(framework))
