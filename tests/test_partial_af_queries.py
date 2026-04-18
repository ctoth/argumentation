"""Tests for completion-based query semantics over partial frameworks."""

from __future__ import annotations

from itertools import product

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from argumentation.dung import grounded_extension, preferred_extensions, stable_extensions
from argumentation.partial_af import (
    PartialArgumentationFramework,
    credulously_accepted_arguments,
    enumerate_completions,
    skeptically_accepted_arguments,
)


PAIR_ORDER = [("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")]
st_states = st.lists(
    st.sampled_from(["attack", "ignorance", "non_attack"]),
    min_size=len(PAIR_ORDER),
    max_size=len(PAIR_ORDER),
)
ALL_STATE_ASSIGNMENTS = list(product(["attack", "ignorance", "non_attack"], repeat=len(PAIR_ORDER)))


def _example_paf() -> PartialArgumentationFramework:
    return PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks={("A", "B")},
        ignorance={("B", "A")},
        non_attacks={("A", "A"), ("B", "B")},
    )


def _paf_from_states(states: tuple[str, ...] | list[str]) -> PartialArgumentationFramework:
    attacks = set()
    ignorance = set()
    non_attacks = set()
    for pair, state in zip(PAIR_ORDER, states, strict=True):
        if state == "attack":
            attacks.add(pair)
        elif state == "ignorance":
            ignorance.add(pair)
        else:
            non_attacks.add(pair)
    return PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks=attacks,
        ignorance=ignorance,
        non_attacks=non_attacks,
    )


def _extensions_for_completion(
    paf: PartialArgumentationFramework,
    semantics: str,
) -> list[frozenset[str]]:
    extensions: list[frozenset[str]] = []
    for completion in enumerate_completions(paf):
        if semantics == "grounded":
            extensions.append(grounded_extension(completion))
        elif semantics == "preferred":
            extensions.extend(frozenset(ext) for ext in preferred_extensions(completion))
        elif semantics == "stable":
            extensions.extend(frozenset(ext) for ext in stable_extensions(completion))
        else:
            raise AssertionError(f"unexpected semantics {semantics}")
    return extensions


def _bruteforce_skeptical(paf: PartialArgumentationFramework, semantics: str) -> frozenset[str]:
    extensions = _extensions_for_completion(paf, semantics)
    if not extensions:
        return frozenset()
    skeptical = set(paf.arguments)
    for extension in extensions:
        skeptical.intersection_update(extension)
    return frozenset(skeptical)


def _bruteforce_credulous(paf: PartialArgumentationFramework, semantics: str) -> frozenset[str]:
    credulous: set[str] = set()
    for extension in _extensions_for_completion(paf, semantics):
        credulous.update(extension)
    return frozenset(credulous)


def test_grounded_skeptical_and_credulous_acceptance_follow_completions():
    paf = _example_paf()

    skeptical = skeptically_accepted_arguments(paf, semantics="grounded")
    credulous = credulously_accepted_arguments(paf, semantics="grounded")

    assert skeptical == frozenset()
    assert credulous == frozenset({"A"})


def test_single_completion_matches_ordinary_dung_query():
    paf = PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks={("A", "B")},
        ignorance=set(),
        non_attacks={("A", "A"), ("B", "A"), ("B", "B")},
    )

    assert skeptically_accepted_arguments(paf, semantics="grounded") == frozenset({"A"})
    assert credulously_accepted_arguments(paf, semantics="grounded") == frozenset({"A"})


def test_query_helpers_match_bruteforce_completion_semantics_on_tiny_profiles():
    for semantics in ("grounded", "preferred", "stable"):
        for states in ALL_STATE_ASSIGNMENTS:
            paf = _paf_from_states(states)
            assert skeptically_accepted_arguments(paf, semantics=semantics) == _bruteforce_skeptical(
                paf, semantics
            )
            assert credulously_accepted_arguments(paf, semantics=semantics) == _bruteforce_credulous(
                paf, semantics
            )


@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(states=st_states, fixed_relation=st.sampled_from(["attack", "non_attack"]))
def test_fixing_ignorance_grows_skeptical_and_shrinks_credulous(
    states: list[str],
    fixed_relation: str,
):
    paf = _paf_from_states(states)
    if not paf.ignorance:
        return

    fixed_pair = next(iter(sorted(paf.ignorance)))
    fixed_framework = PartialArgumentationFramework(
        arguments=paf.arguments,
        attacks=(paf.attacks | {fixed_pair}) if fixed_relation == "attack" else paf.attacks,
        ignorance=paf.ignorance - {fixed_pair},
        non_attacks=(
            paf.non_attacks | {fixed_pair}
            if fixed_relation == "non_attack"
            else paf.non_attacks
        ),
    )

    original_skeptical = skeptically_accepted_arguments(paf, semantics="grounded")
    fixed_skeptical = skeptically_accepted_arguments(fixed_framework, semantics="grounded")
    original_credulous = credulously_accepted_arguments(paf, semantics="grounded")
    fixed_credulous = credulously_accepted_arguments(fixed_framework, semantics="grounded")

    assert original_skeptical <= fixed_skeptical
    assert fixed_credulous <= original_credulous
