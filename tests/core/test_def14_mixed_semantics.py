"""Core semantics on mixed attack/defeat frameworks (issue #90).

Contract: Modgil & Prakken 2018, Def 14 (p.14; papers/Modgil_2018_General
AccountArgumentationPreferences/notes.md). A set is conflict-free when no
member attacks another; defense and admissibility use defeats; complete,
preferred and stable are built on those notions. Grounded is the least
complete extension. Single-relation frameworks keep Dung 1995 semantics.
"""

from __future__ import annotations

from itertools import combinations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.core import dung
from argumentation.core.dung import (
    ArgumentationFramework,
    complete_extensions,
    conflict_free,
    extensions_for,
    grounded_extension,
    grounded_extensions,
    preferred_extensions,
    stable_extensions,
)
from argumentation.core.preprocessing import simplify_af
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
)
from argumentation.solving.solver import solve_dung_acceptance, solve_dung_extensions
from argumentation.structured.aspic.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
)
from tests.core import pre_def14_reference as reference
from tests.core.test_dung import argumentation_frameworks


def _failed_rebuttal_pairs(pair_count: int) -> ArgumentationFramework:
    """x_i and y_i attack each other; only y_i -> x_i succeeds as a defeat,
    the shape a preference-filtered rebuttal has (M&P 2018, Def 9, p.12)."""
    arguments = frozenset(
        name for index in range(pair_count) for name in (f"x{index}", f"y{index}")
    )
    attacks = frozenset(
        edge
        for index in range(pair_count)
        for edge in ((f"x{index}", f"y{index}"), (f"y{index}", f"x{index}"))
    )
    defeats = frozenset((f"y{index}", f"x{index}") for index in range(pair_count))
    return ArgumentationFramework(arguments, defeats, attacks=attacks)


def _forbid_subset_enumeration(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("mixed preferred must not enumerate every subset")

    monkeypatch.setattr(dung, "_all_subsets", forbidden)
    monkeypatch.setattr(dung, "iter_subsets_bitmask", forbidden)


def test_mixed_preferred_search_is_bounded_on_failed_rebuttal_pairs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operational contract: 20 failed-rebuttal pairs (40 arguments, 2^40
    subsets) have the single preferred extension {y_0..y_19}; the search
    visits a number of nodes polynomial in the argument count and never
    enumerates subsets."""
    _forbid_subset_enumeration(monkeypatch)
    framework = _failed_rebuttal_pairs(20)

    extensions, nodes = dung._mixed_preferred_search(framework)

    assert extensions == [frozenset(f"y{index}" for index in range(20))]
    assert nodes <= 4 * len(framework.arguments) ** 2


def test_mixed_preferred_search_is_bounded_on_isolated_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operational contract: 38 unattacked arguments plus one failed rebuttal
    pair; every unattacked argument is in the unique preferred extension."""
    _forbid_subset_enumeration(monkeypatch)
    isolated = frozenset(f"i{index}" for index in range(38))
    framework = ArgumentationFramework(
        isolated | {"x", "y"},
        frozenset({("y", "x")}),
        attacks=frozenset({("x", "y"), ("y", "x")}),
    )

    extensions, nodes = dung._mixed_preferred_search(framework)

    assert extensions == [isolated | {"y"}]
    assert nodes <= 4 * len(framework.arguments) ** 2


def test_mixed_preferred_public_api_uses_bounded_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operational contract: preferred_extensions on a 40-argument mixed AF
    goes through the search, not subset enumeration."""
    _forbid_subset_enumeration(monkeypatch)

    assert preferred_extensions(_failed_rebuttal_pairs(20)) == [
        frozenset(f"y{index}" for index in range(20))
    ]


def _issue_repro() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset(),
        attacks=frozenset({("a", "b")}),
    )


def test_grounded_raises_when_no_complete_extension_exists() -> None:
    """Issue #90 repro: a attacks b but neither defeats the other, so both
    are defended by every set, and any complete extension would contain the
    attacking pair; there is no complete extension (Def 14, p.14)."""
    framework = _issue_repro()

    with pytest.raises(ValueError, match="no complete extension"):
        grounded_extension(framework)
    assert complete_extensions(framework) == []
    assert stable_extensions(framework) == []
    assert sorted(preferred_extensions(framework), key=sorted) == [
        frozenset({"a"}),
        frozenset({"b"}),
    ]


def _lit(name: str, negated: bool = False) -> Literal:
    return Literal(GroundAtom(name), negated=negated)


def _transposition_closed_aspic_framework() -> ArgumentationFramework:
    """M&P 2018 well-defined system (closed under transposition, Def 12,
    p.13): premises p < q, strict rules p -> ~q and q -> ~p. [p; p->~q]
    attacks [q] without defeating it, and [q] does not attack back."""
    p, q, not_q, not_p = _lit("p"), _lit("q"), _lit("q", True), _lit("p", True)
    system = ArgumentationSystem(
        language=frozenset({p, q, not_q, not_p}),
        contrariness=ContrarinessFn(
            contradictories=frozenset({(q, not_q), (p, not_p)})
        ),
        strict_rules=frozenset(
            {Rule((p,), not_q, "strict"), Rule((q,), not_p, "strict")}
        ),
        defeasible_rules=frozenset(),
    )
    knowledge_base = KnowledgeBase(axioms=frozenset(), premises=frozenset({p, q}))
    preferences = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset({(p, q)}),
        comparison="elitist",
        link="last",
    )
    return build_abstract_framework(system, knowledge_base, preferences).framework


def test_aspic_transposition_closed_control() -> None:
    """Issue #90 control: grounded exists, is conflict-free on attacks, is the
    least complete extension, and preferred equals the maximal complete
    extensions."""
    framework = _transposition_closed_aspic_framework()
    assert framework.attacks is not None
    assert framework.attacks != framework.defeats

    grounded = grounded_extension(framework)
    completes = complete_extensions(framework)

    assert conflict_free(grounded, framework.attacks)
    assert grounded in completes
    assert all(grounded <= extension for extension in completes)
    assert set(preferred_extensions(framework)) == set(_maximal(completes))


def _maximal(sets: list[frozenset[str]]) -> list[frozenset[str]]:
    return [candidate for candidate in sets if not any(candidate < s for s in sets)]


@st.composite
def pairwise_wellformed_mixed_frameworks(draw: st.DrawFn) -> ArgumentationFramework:
    """Mixed AFs where defeats are attacks and every attack has a defeat in
    at least one direction (the shape of a preference-filtered attack)."""
    arguments = sorted(
        draw(st.frozensets(st.sampled_from("abcdef"), min_size=1, max_size=6))
    )
    pairs = [(x, y) for x in arguments for y in arguments]
    attacks = draw(st.frozensets(st.sampled_from(pairs), max_size=len(pairs)))
    defeats: set[tuple[str, str]] = set()
    for source, target in sorted(attacks):
        if (target, source) in attacks and draw(st.booleans()):
            continue
        defeats.add((source, target))
    for source, target in sorted(attacks):
        if (source, target) not in defeats and (target, source) not in defeats:
            defeats.add((source, target))
    return ArgumentationFramework(
        frozenset(arguments), frozenset(defeats), attacks=attacks
    )


@given(pairwise_wellformed_mixed_frameworks())
@settings(max_examples=150, deadline=None)
def test_mixed_semantics_follow_def14(framework: ArgumentationFramework) -> None:
    """Issue #90 property: on mixed AFs with a complete extension, grounded
    is complete and least, preferred equals the maximal complete extensions,
    and every extension is conflict-free on attacks (M&P 2018, Def 14)."""
    assert framework.attacks is not None
    completes = complete_extensions(framework)
    preferred = preferred_extensions(framework)
    stable = stable_extensions(framework)

    for extension in [*completes, *preferred, *stable]:
        assert conflict_free(extension, framework.attacks)
    assert set(preferred) == set(_brute_force_preferred(framework))
    if not completes:
        with pytest.raises(ValueError, match="no complete extension"):
            grounded_extension(framework)
        return
    grounded = grounded_extension(framework)
    assert grounded in completes
    assert all(grounded <= extension for extension in completes)
    assert set(preferred) == set(_maximal(completes))


@st.composite
def arbitrary_mixed_frameworks(draw: st.DrawFn) -> ArgumentationFramework:
    """Any mixed AF with defeats contained in attacks, including attacks
    that fail in both directions (outside M&P's well-defined domain)."""
    arguments = sorted(
        draw(st.frozensets(st.sampled_from("abcdef"), min_size=1, max_size=6))
    )
    pairs = [(x, y) for x in arguments for y in arguments]
    attacks = draw(st.frozensets(st.sampled_from(pairs), max_size=len(pairs)))
    defeats = (
        draw(st.frozensets(st.sampled_from(sorted(attacks))))
        if attacks
        else frozenset()
    )
    return ArgumentationFramework(
        frozenset(arguments), frozenset(defeats), attacks=attacks
    )


@given(arbitrary_mixed_frameworks())
@settings(max_examples=200, deadline=None)
def test_def14_preferred_and_grounded_on_arbitrary_mixed_frameworks(
    framework: ArgumentationFramework,
) -> None:
    """Issue #90: preferred is the set of maximal Def 14 admissible sets
    (checked by brute force), and grounded is the least complete extension
    when one exists and raises otherwise (M&P 2018, Def 14)."""
    assert set(preferred_extensions(framework)) == set(
        _brute_force_preferred(framework)
    )
    completes = complete_extensions(framework)
    if not completes:
        with pytest.raises(ValueError, match="no complete extension"):
            grounded_extension(framework)
        return
    grounded = grounded_extension(framework)
    assert grounded in completes
    assert all(grounded <= extension for extension in completes)


def _brute_force_preferred(framework: ArgumentationFramework) -> list[frozenset[str]]:
    ordered = sorted(framework.arguments)
    admissible_sets = [
        frozenset(combo)
        for size in range(len(ordered) + 1)
        for combo in combinations(ordered, size)
        if dung.admissible(
            frozenset(combo),
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
        )
    ]
    return _maximal(admissible_sets)


@given(argumentation_frameworks(max_args=6), st.booleans())
@settings(max_examples=150, deadline=None)
def test_single_relation_semantics_unchanged(
    framework: ArgumentationFramework,
    attacks_equal_defeats: bool,
) -> None:
    """Issue #90: frameworks with one relation (attacks None or equal to
    defeats) give the same results as the pre-change implementation."""
    if attacks_equal_defeats:
        framework = ArgumentationFramework(
            framework.arguments, framework.defeats, attacks=framework.defeats
        )

    assert grounded_extension(framework) == reference.grounded_extension(framework)
    assert set(complete_extensions(framework)) == set(
        reference.complete_extensions(framework)
    )
    assert set(preferred_extensions(framework)) == set(
        reference.preferred_extensions(framework)
    )
    assert set(stable_extensions(framework)) == set(
        reference.stable_extensions(framework)
    )


def _unresolved_attack_framework() -> ArgumentationFramework:
    """a attacks c without either defeating the other; a and b defeat each
    other. Def 14 preferred: {a} and {b, c}; complete: {c} and {b, c}."""
    return ArgumentationFramework(
        frozenset("abc"),
        frozenset({("a", "b"), ("b", "a")}),
        attacks=frozenset({("a", "b"), ("a", "c"), ("b", "a")}),
    )


@pytest.mark.parametrize("backend", ["native", "sat"])
def test_solver_backends_follow_def14_on_unresolved_attack(backend: str) -> None:
    """Issue #90: the solver layer returned {a, c}, which is not
    conflict-free on attacks, because its grounded reduct fixed c in and its
    SCC recursion over defeats ignored the attack a -> c."""
    framework = _unresolved_attack_framework()

    result = solve_dung_extensions(framework, semantics="preferred", backend=backend)

    assert set(result.extensions) == {frozenset({"a"}), frozenset({"b", "c"})}  # type: ignore[union-attr]


@pytest.mark.parametrize("backend", ["native", "sat", "auto"])
def test_preferred_skeptical_acceptance_follows_def14(backend: str) -> None:
    """Issue #90: c has no defeaters but is not in the preferred extension
    {a}, so it is not skeptically accepted; the SAT shortcut for unattacked
    queries answered True."""
    result = solve_dung_acceptance(
        _unresolved_attack_framework(),
        semantics="preferred",
        task="skeptical",
        query="c",
        backend=backend,
    )

    assert result.answer is False  # type: ignore[union-attr]


def test_grounded_reduct_skipped_for_unresolved_attacks() -> None:
    """Issue #90: fixing the defeat-based grounded set {c} would exclude the
    preferred extension {a}, so the reduct is not applied."""
    reduct = simplify_af(_unresolved_attack_framework(), semantics="preferred")

    assert reduct.fixed_in == frozenset()
    assert reduct.residual == _unresolved_attack_framework()


def test_probabilistic_worlds_without_grounded_extension_accept_nothing() -> None:
    """Issue #90 caller audit: PrAF world sampling can drop the reverse attack
    of a failed rebuttal, leaving attack a -> b with no defeat. That world has
    no complete, hence no grounded, extension and accepts nothing (Li et al.
    2011, Eq 2, p.4); the other world has grounded {b}."""
    framework = ArgumentationFramework(
        frozenset({"a", "b"}),
        frozenset({("b", "a")}),
        attacks=frozenset({("a", "b"), ("b", "a")}),
    )
    praf = ProbabilisticAF(
        framework,
        {"a": 1.0, "b": 1.0},
        {("b", "a"): 0.5},
        p_attacks={("a", "b"): 1.0, ("b", "a"): 0.5},
    )

    result = compute_probabilistic_acceptance(
        praf, semantics="grounded", strategy="exact_enum"
    )

    assert result.acceptance_probs == pytest.approx({"a": 0.0, "b": 0.5})


def test_grounded_extensions_tuple_is_empty_without_complete_extension() -> None:
    """Issue #90: plural APIs report no grounded extension, like complete and
    stable, instead of raising."""
    assert grounded_extensions(_issue_repro()) == ()
    assert extensions_for(_issue_repro(), "grounded") == ()


@given(arbitrary_mixed_frameworks(), st.sampled_from(["native", "sat"]))
@settings(max_examples=60, deadline=None)
def test_solver_backends_agree_with_core_on_mixed_frameworks(
    framework: ArgumentationFramework,
    backend: str,
) -> None:
    """Issue #90: every solver backend follows the core Def 14 semantics on
    arbitrary mixed frameworks, for enumeration and acceptance."""
    query = sorted(framework.arguments)[0]
    for semantics, expected in (
        ("grounded", list(grounded_extensions(framework))),
        ("complete", complete_extensions(framework)),
        ("preferred", preferred_extensions(framework)),
        ("stable", stable_extensions(framework)),
    ):
        result = solve_dung_extensions(framework, semantics=semantics, backend=backend)
        assert set(result.extensions) == set(expected)  # type: ignore[union-attr]
        for task, answer in (
            ("credulous", any(query in extension for extension in expected)),
            ("skeptical", all(query in extension for extension in expected)),
        ):
            acceptance = solve_dung_acceptance(
                framework,
                semantics=semantics,
                task=task,
                query=query,
                backend=backend,
            )
            assert acceptance.answer is answer  # type: ignore[union-attr]
