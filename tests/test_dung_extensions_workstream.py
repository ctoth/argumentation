from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.bipolar import (
    BipolarArgumentationFramework,
    bipolar_complete_extensions,
    bipolar_grounded_extension,
    characteristic_fn as bipolar_characteristic_fn,
)
from argumentation.dung import (
    ArgumentationFramework,
    admissible,
    complete_extensions,
    eager_extension,
    indirect_attacks,
    preferred_extensions,
    conflict_free,
    prudent_admissible,
    prudent_conflict_free,
    prudent_grounded_extension,
    prudent_preferred_extensions,
    semi_stable_extensions,
    stage2_extensions,
    stage_extensions,
)
from argumentation.labelling import complete_labellings


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_no_z3_dung_module_or_solver_surface() -> None:
    """Codex 2.17 deletion gate: no Dung extension-semantics Z3 backend remains."""
    root = Path("src/argumentation")
    assert not (root / "dung_z3.py").exists()
    forbidden = (
        "argumentation.dung_z3",
        "_AUTO_BACKEND_MAX_ARGS",
        "z3_complete_extensions",
        "z3_preferred_extensions",
        "z3_stable_extensions",
        "backend=\"z3\"",
    )
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, f"{needle} remains in {path}"


def test_semi_stable_floating_reinstatement_caminada_2006_page_8() -> None:
    """Caminada 2006, p. 8: floating `A`/`B` choices reinstate `D`."""
    framework = af(
        {"A", "B", "C", "D"},
        {("A", "B"), ("B", "A"), ("A", "C"), ("B", "C"), ("C", "D")},
    )

    assert set(semi_stable_extensions(framework)) == {
        frozenset({"A", "D"}),
        frozenset({"B", "D"}),
    }


def test_eager_selects_largest_admissible_subset_of_semi_stable_intersection() -> None:
    """Caminada 2006 p. 8 plus Caminada 2007 eager: reject undefended common `D`."""
    framework = af(
        {"A", "B", "C", "D"},
        {("A", "B"), ("B", "A"), ("A", "C"), ("B", "C"), ("C", "D")},
    )

    assert eager_extension(framework) == frozenset()
    assert admissible(eager_extension(framework), framework.arguments, framework.defeats)


def test_stage2_collapses_to_stage_on_single_scc_gaggl_2013_pages_927_929() -> None:
    """Gaggl and Woltran 2013, pp. 927-929: SCC base case is local semantics."""
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")})

    assert set(stage2_extensions(framework)) == set(stage_extensions(framework))


def test_prudent_conflict_free_excludes_odd_indirect_attack_coste_marquis_2005_pages_1_2() -> None:
    """Coste-Marquis et al. 2005, pp. 1-2: indirect attacks are odd paths."""
    framework = af({"a", "b", "c", "d"}, {("a", "b"), ("b", "c"), ("c", "d")})

    assert ("a", "c") not in indirect_attacks(framework)
    assert ("a", "d") in indirect_attacks(framework)
    assert prudent_conflict_free(framework, frozenset({"a", "c"})) is True
    assert prudent_conflict_free(framework, frozenset({"a", "d"})) is False


def test_prudent_example_af1_coste_marquis_2005_pages_1_3() -> None:
    """Coste-Marquis et al. 2005, pp. 1-3: AF1 has prudent extension {i,n}."""
    framework = af(
        {"a", "b", "c", "e", "n", "i"},
        {("b", "a"), ("c", "a"), ("n", "c"), ("i", "b"), ("e", "c"), ("i", "e")},
    )

    assert ("i", "a") in indirect_attacks(framework)
    assert prudent_conflict_free(framework, frozenset({"a", "i", "n"})) is False
    assert prudent_preferred_extensions(framework) == [frozenset({"i", "n"})]
    assert prudent_grounded_extension(framework) == frozenset({"i", "n"})


def test_bipolar_grounded_and_complete_cayrol_2005_pages_383_386() -> None:
    """Cayrol 2005, pp. 383-386: use set-defeat in the characteristic function."""
    framework = BipolarArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("b", "c")}),
        supports=frozenset({("a", "b")}),
    )

    assert bipolar_characteristic_fn(frozenset(), framework) == frozenset({"a", "b"})
    assert bipolar_grounded_extension(framework) == frozenset({"a", "b"})
    assert frozenset({"a", "b"}) in bipolar_complete_extensions(framework)


@st.composite
def small_afs(draw):
    args = draw(st.frozensets(st.sampled_from(tuple("abcde")), min_size=1, max_size=5))
    attacks = draw(
        st.frozensets(
            st.tuples(st.sampled_from(sorted(args)), st.sampled_from(sorted(args))),
            max_size=len(args) ** 2,
        )
    )
    return ArgumentationFramework(arguments=args, defeats=attacks)


@pytest.mark.property
@given(small_afs())
@settings(deadline=None, max_examples=40)
def test_eager_is_unique_and_admissible(framework: ArgumentationFramework) -> None:
    extension = eager_extension(framework)

    assert extension <= framework.arguments
    assert admissible(extension, framework.arguments, framework.defeats)


@pytest.mark.property
@given(small_afs())
@settings(deadline=None, max_examples=40)
def test_prudent_preferred_extensions_are_prudent_admissible(
    framework: ArgumentationFramework,
) -> None:
    for extension in prudent_preferred_extensions(framework):
        assert prudent_admissible(framework, extension)


@pytest.mark.property
@given(small_afs())
@settings(deadline=None, max_examples=40)
def test_stage2_extensions_are_conflict_free(framework: ArgumentationFramework) -> None:
    for extension in stage2_extensions(framework):
        assert extension <= framework.arguments
        assert conflict_free(extension, framework.defeats)


@pytest.mark.property
@given(small_afs())
@settings(deadline=None, max_examples=40)
def test_complete_extensions_match_labelling_projection(
    framework: ArgumentationFramework,
) -> None:
    assert set(complete_extensions(framework)) == {
        labelling.extension
        for labelling in complete_labellings(framework)
    }
