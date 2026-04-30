from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.caf import (
    ClaimAugmentedAF,
    claim_range,
    claim_level_extensions,
    concurrence_holds,
    defeated_claims,
    extensions,
    inherited_extensions,
    is_i_maximal,
    is_well_formed,
)
from argumentation.dung import (
    ArgumentationFramework,
    naive_extensions,
    preferred_extensions,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def example_1_caf() -> ClaimAugmentedAF:
    return ClaimAugmentedAF(
        framework=af(
            {"x1", "y1", "z", "x2", "y2"},
            {
                ("y1", "x1"),
                ("y1", "z"),
                ("z", "y1"),
                ("z", "x2"),
                ("x2", "y2"),
            },
        ),
        claims={"x1": "x", "x2": "x", "y1": "y", "y2": "y", "z": "z"},
    )


def example_2_caf() -> ClaimAugmentedAF:
    return ClaimAugmentedAF(
        framework=af(
            {"x1", "y1", "x2", "z1", "x3"},
            {
                ("y1", "x1"),
                ("y1", "x2"),
                ("z1", "x2"),
                ("z1", "x3"),
            },
        ),
        claims={"x1": "x", "x2": "x", "x3": "x", "y1": "y", "z1": "z"},
    )


def example_3_caf() -> ClaimAugmentedAF:
    return ClaimAugmentedAF(
        framework=af(
            {"a", "b1", "b2", "c", "d", "e", "f1", "f2"},
            {
                ("e", "e"),
                ("e", "b2"),
                ("c", "e"),
                ("c", "b2"),
                ("b2", "c"),
                ("a", "c"),
                ("b1", "c"),
                ("a", "b1"),
                ("a", "d"),
                ("d", "a"),
                ("a", "f1"),
                ("f1", "f1"),
                ("f1", "f2"),
                ("f2", "f1"),
                ("f2", "f2"),
            },
        ),
        claims={
            "a": "a",
            "b1": "b",
            "b2": "b",
            "c": "c",
            "d": "d",
            "e": "e",
            "f1": "f",
            "f2": "f",
        },
    )


def example_4_caf() -> ClaimAugmentedAF:
    return ClaimAugmentedAF(
        framework=af(
            {"a", "b1", "b2", "c", "d"},
            {
                ("a", "a"),
                ("b1", "a"),
                ("b1", "b2"),
                ("b2", "b1"),
                ("b1", "c"),
                ("c", "b1"),
                ("c", "d"),
                ("d", "d"),
            },
        ),
        claims={"a": "a", "b1": "b", "b2": "b", "c": "c", "d": "d"},
    )


def example_5_caf() -> ClaimAugmentedAF:
    return ClaimAugmentedAF(
        framework=af(
            {"a", "b", "c1", "c2"},
            {
                ("a", "b"),
                ("b", "a"),
                ("b", "c1"),
                ("c1", "c1"),
                ("c1", "c2"),
                ("c2", "c1"),
                ("c2", "c2"),
            },
        ),
        claims={"a": "a", "b": "b", "c1": "c", "c2": "c"},
    )


def example_6_caf() -> ClaimAugmentedAF:
    base = example_5_caf()
    return ClaimAugmentedAF(
        framework=af(
            set(base.framework.arguments) | {"d1", "d2"},
            set(base.framework.defeats) | {("d1", "d2"), ("d2", "d2"), ("b", "d1")},
        ),
        claims={**base.claims, "d1": "d", "d2": "d"},
    )


def claim_sets(values: set[frozenset[str]]) -> set[frozenset[str]]:
    return values


def test_kr2020_example_1_cl_preferred_strengthens_inherited_preferred() -> None:
    caf = example_1_caf()

    assert set(inherited_extensions(caf, semantics="preferred")) == claim_sets(
        {
            frozenset({"x", "y"}),
            frozenset({"x", "y", "z"}),
        }
    )
    assert set(claim_level_extensions(caf, semantics="preferred")) == {
        frozenset({"x", "y", "z"})
    }


def test_kr2020_example_2_cl_naive_selects_i_maximal_claim_sets() -> None:
    caf = example_2_caf()

    assert set(inherited_extensions(caf, semantics="naive")) == claim_sets(
        {
            frozenset({"x"}),
            frozenset({"x", "y"}),
            frozenset({"x", "z"}),
            frozenset({"y", "z"}),
        }
    )
    assert set(claim_level_extensions(caf, semantics="naive")) == {
        frozenset({"x", "y"}),
        frozenset({"x", "z"}),
        frozenset({"y", "z"}),
    }
    assert is_i_maximal(claim_level_extensions(caf, semantics="naive")) is True


def test_kr2020_figure_3_cl_stable_relaxes_stable_realization() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a2", "a2"), ("a2", "a1"), ("a1", "b")}),
        claims={"a1": "a", "a2": "a", "b": "b"},
    )

    assert inherited_extensions(caf, semantics="stable") == ()
    assert claim_level_extensions(caf, semantics="stable") == (frozenset({"a"}),)
    assert claim_level_extensions(caf, semantics="stable-admissible") == ()


def test_kr2020_example_3_cl_semi_stable_and_i_semi_stable_are_incomparable() -> None:
    caf = example_3_caf()

    assert is_well_formed(caf) is True
    assert set(claim_level_extensions(caf, semantics="semi-stable")) == {
        frozenset({"b", "d"})
    }
    assert set(inherited_extensions(caf, semantics="semi-stable")) == {
        frozenset({"a"})
    }


def test_kr2020_example_4_cl_semi_stable_is_not_i_maximal_for_general_cafs() -> None:
    caf = example_4_caf()

    assert is_well_formed(caf) is False
    assert inherited_extensions(caf, semantics="stable") == ()
    assert claim_level_extensions(caf, semantics="stable") == ()
    assert claim_level_extensions(caf, semantics="stable-admissible") == ()
    assert set(claim_level_extensions(caf, semantics="semi-stable")) == {
        frozenset({"b"}),
        frozenset({"b", "c"}),
    }


def test_kr2020_example_5_cl_stage_and_i_stage_are_incomparable() -> None:
    caf = example_5_caf()

    assert set(inherited_extensions(caf, semantics="stage")) == {
        frozenset({"b"})
    }
    assert set(claim_level_extensions(caf, semantics="stage")) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }


def test_kr2020_example_6_stage_claim_level_counterexample() -> None:
    caf = example_6_caf()

    assert set(inherited_extensions(caf, semantics="stage")) == {
        frozenset({"a", "d"}),
        frozenset({"b"}),
    }
    assert set(claim_level_extensions(caf, semantics="stage")) == {
        frozenset({"a", "d"})
    }


def test_duplicate_argument_claims_collapse_inherited_extensions() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2"}, set()),
        claims={"a1": "A", "a2": "A"},
    )

    assert inherited_extensions(caf, semantics="preferred") == (frozenset({"A"}),)


def test_claim_level_extensions_maximize_claim_sets() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a1", "b"), ("b", "a1")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )

    assert claim_level_extensions(caf, semantics="naive") == (
        frozenset({"A", "B"}),
    )


def test_bijective_claims_have_inherited_claim_level_concurrence() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a", "b"}, {("a", "b"), ("b", "a")}),
        claims={"a": "A", "b": "B"},
    )

    assert concurrence_holds(caf, semantics="stable") is True
    assert extensions(caf, semantics="stable", view="inherited") == inherited_extensions(
        caf,
        semantics="stable",
    )
    assert extensions(caf, semantics="stable", view="claim_level") == claim_level_extensions(
        caf,
        semantics="stable",
    )


def test_claim_level_stage_discards_range_dominated_claim_sets() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a", "b", "c1", "c2"}, {("b", "a"), ("b", "c1"), ("c1", "c1"), ("c2", "c2")}),
        claims={"a": "A", "b": "B", "c1": "C", "c2": "C"},
    )

    assert claim_level_extensions(caf, semantics="stage") == (frozenset({"B"}),)


def test_kr2020_definition_3_well_formed_requires_same_outgoing_attacks() -> None:
    well_formed = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a1", "b"), ("a2", "b")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )
    not_well_formed = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a1", "b")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )

    assert is_well_formed(well_formed) is True
    assert is_well_formed(not_well_formed) is False


def test_aij2023_definition_6_defeated_claims_require_attacking_all_occurrences() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("b", "a1")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )

    assert defeated_claims(caf, frozenset({"b"})) == frozenset()
    assert claim_range(caf, frozenset({"b"})) == frozenset({"B"})


@st.composite
def cafs(draw: st.DrawFn, *, max_arguments: int = 4, max_claims: int = 3) -> ClaimAugmentedAF:
    argument_count = draw(st.integers(min_value=0, max_value=max_arguments))
    arguments = [f"a{index}" for index in range(argument_count)]
    possible_defeats = [(source, target) for source in arguments for target in arguments]
    defeats = draw(st.sets(st.sampled_from(possible_defeats), max_size=len(possible_defeats))) if possible_defeats else set()
    claim_bound = max(1, min(max_claims, max(1, argument_count)))
    claim_numbers = draw(
        st.lists(
            st.integers(min_value=0, max_value=claim_bound - 1),
            min_size=argument_count,
            max_size=argument_count,
        )
    )
    return ClaimAugmentedAF(
        framework=ArgumentationFramework(arguments=frozenset(arguments), defeats=frozenset(defeats)),
        claims={argument: f"c{claim}" for argument, claim in zip(arguments, claim_numbers, strict=True)},
    )


@st.composite
def well_formed_cafs(draw: st.DrawFn, *, max_arguments: int = 4, max_claims: int = 3) -> ClaimAugmentedAF:
    argument_count = draw(st.integers(min_value=0, max_value=max_arguments))
    arguments = [f"a{index}" for index in range(argument_count)]
    claim_bound = max(1, min(max_claims, max(1, argument_count)))
    claim_numbers = draw(
        st.lists(
            st.integers(min_value=0, max_value=claim_bound - 1),
            min_size=argument_count,
            max_size=argument_count,
        )
    )
    claims = {argument: f"c{claim}" for argument, claim in zip(arguments, claim_numbers, strict=True)}
    claim_ids = sorted(set(claims.values()))
    possible_claim_attacks = [(source, target) for source in claim_ids for target in claim_ids]
    claim_attacks = draw(st.sets(st.sampled_from(possible_claim_attacks), max_size=len(possible_claim_attacks))) if possible_claim_attacks else set()
    defeats = {
        (source, target)
        for source in arguments
        for target in arguments
        if (claims[source], claims[target]) in claim_attacks
    }
    return ClaimAugmentedAF(
        framework=ArgumentationFramework(arguments=frozenset(arguments), defeats=frozenset(defeats)),
        claims=claims,
    )


@st.composite
def unique_claim_cafs(draw: st.DrawFn, *, max_arguments: int = 4) -> ClaimAugmentedAF:
    caf = draw(cafs(max_arguments=max_arguments, max_claims=max_arguments))
    return ClaimAugmentedAF(
        framework=caf.framework,
        claims={argument: argument for argument in caf.framework.arguments},
    )


def project(caf: ClaimAugmentedAF, extensions_: tuple[frozenset[str], ...] | list[frozenset[str]]) -> set[frozenset[str]]:
    return {frozenset(caf.claims[argument] for argument in extension) for extension in extensions_}


@given(cafs())
@settings(max_examples=60)
def test_definition_4_inherited_extensions_are_projected_dung_extensions(caf: ClaimAugmentedAF) -> None:
    assert set(inherited_extensions(caf, semantics="preferred")) == project(
        caf,
        preferred_extensions(caf.framework),
    )


@given(well_formed_cafs())
@settings(max_examples=60)
def test_lemma_1_well_formed_same_claim_sets_have_same_defeated_claims(caf: ClaimAugmentedAF) -> None:
    subsets = [
        frozenset(argument for index, argument in enumerate(sorted(caf.framework.arguments)) if mask & (1 << index))
        for mask in range(1 << len(caf.framework.arguments))
    ]
    for left in subsets:
        for right in subsets:
            if project(caf, [left]) == project(caf, [right]):
                assert defeated_claims(caf, left) == defeated_claims(caf, right)


@given(cafs())
@settings(max_examples=60)
def test_proposition_1_cl_preferred_is_subset_of_i_preferred(caf: ClaimAugmentedAF) -> None:
    assert set(claim_level_extensions(caf, semantics="preferred")) <= set(
        inherited_extensions(caf, semantics="preferred")
    )


@given(cafs())
@settings(max_examples=60)
def test_proposition_2_cl_preferred_is_i_maximal(caf: ClaimAugmentedAF) -> None:
    assert is_i_maximal(claim_level_extensions(caf, semantics="preferred")) is True


@given(well_formed_cafs())
@settings(max_examples=60)
def test_proposition_3_well_formed_preferred_concurrence(caf: ClaimAugmentedAF) -> None:
    assert set(claim_level_extensions(caf, semantics="preferred")) == set(
        inherited_extensions(caf, semantics="preferred")
    )


@given(cafs())
@settings(max_examples=60)
def test_proposition_5_cl_naive_is_subset_of_i_naive(caf: ClaimAugmentedAF) -> None:
    assert set(claim_level_extensions(caf, semantics="naive")) <= set(
        inherited_extensions(caf, semantics="naive")
    )


@given(cafs())
@settings(max_examples=60)
def test_proposition_6_cl_naive_is_i_maximal(caf: ClaimAugmentedAF) -> None:
    assert is_i_maximal(claim_level_extensions(caf, semantics="naive")) is True


@given(well_formed_cafs())
@settings(max_examples=60)
def test_proposition_8_well_formed_stable_variants_coincide(caf: ClaimAugmentedAF) -> None:
    assert set(inherited_extensions(caf, semantics="stable")) == set(
        claim_level_extensions(caf, semantics="stable")
    )
    assert set(claim_level_extensions(caf, semantics="stable")) == set(
        claim_level_extensions(caf, semantics="stable-admissible")
    )


@given(well_formed_cafs())
@settings(max_examples=60)
def test_proposition_10_well_formed_semi_stable_outputs_are_i_maximal(caf: ClaimAugmentedAF) -> None:
    assert is_i_maximal(inherited_extensions(caf, semantics="semi-stable")) is True
    assert is_i_maximal(claim_level_extensions(caf, semantics="semi-stable")) is True


@given(well_formed_cafs())
@settings(max_examples=60)
def test_proposition_11_well_formed_stage_outputs_are_i_maximal(caf: ClaimAugmentedAF) -> None:
    assert is_i_maximal(inherited_extensions(caf, semantics="stage")) is True
    assert is_i_maximal(claim_level_extensions(caf, semantics="stage")) is True


@given(unique_claim_cafs())
@settings(max_examples=60)
def test_lemma_3_unique_claims_coincide_with_dung_semantics(caf: ClaimAugmentedAF) -> None:
    assert set(inherited_extensions(caf, semantics="preferred")) == project(caf, preferred_extensions(caf.framework))
    assert set(claim_level_extensions(caf, semantics="preferred")) == project(caf, preferred_extensions(caf.framework))
    assert set(inherited_extensions(caf, semantics="naive")) == project(caf, naive_extensions(caf.framework))
    assert set(claim_level_extensions(caf, semantics="naive")) == project(caf, naive_extensions(caf.framework))
    assert set(inherited_extensions(caf, semantics="stable")) == project(caf, stable_extensions(caf.framework))
    assert set(claim_level_extensions(caf, semantics="stable")) == project(caf, stable_extensions(caf.framework))
    assert set(inherited_extensions(caf, semantics="semi-stable")) == project(caf, semi_stable_extensions(caf.framework))
    assert set(claim_level_extensions(caf, semantics="semi-stable")) == project(caf, semi_stable_extensions(caf.framework))
    assert set(inherited_extensions(caf, semantics="stage")) == project(caf, stage_extensions(caf.framework))
    assert set(claim_level_extensions(caf, semantics="stage")) == project(caf, stage_extensions(caf.framework))
