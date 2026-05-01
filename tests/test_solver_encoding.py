from __future__ import annotations

import pytest
from hypothesis import given, settings

from argumentation.dung import (
    ArgumentationFramework,
    _attackers_index,
    admissible,
    complete_extensions,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)
from argumentation.sat_encoding import (
    CNFEncoding,
    encode_stable_extensions,
    sat_complete_extension,
    sat_extensions,
    sat_preferred_extension,
    stable_extensions_from_encoding,
)
from tests.test_dung import af, argumentation_frameworks


SAT_EXTENSION_ORACLES = {
    "admissible": lambda framework: _admissible_sets(framework),
    "complete": complete_extensions,
    "grounded": lambda framework: [grounded_extension(framework)],
    "preferred": preferred_extensions,
    "stable": stable_extensions,
    "semi-stable": semi_stable_extensions,
    "stage": stage_extensions,
    "ideal": lambda framework: [ideal_extension(framework)],
}


def test_stable_encoding_uses_deterministic_variable_ids() -> None:
    framework = af({"b", "a"}, {("a", "b")})

    encoding = encode_stable_extensions(framework)

    assert encoding.variables == (("a", 1), ("b", 2))
    assert encoding.argument_for_variable(1) == "a"
    assert encoding.argument_for_variable(2) == "b"


def test_stable_encoding_contains_conflict_and_outsider_coverage_clauses() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    encoding = encode_stable_extensions(framework)

    assert encoding.clauses == (
        (-1, -2),
        (1,),
        (1, 2),
    )


def test_cnf_encoding_rejects_unknown_variable_ids() -> None:
    encoding = CNFEncoding(
        variables=(("a", 1),),
        clauses=((1,),),
    )

    with pytest.raises(ValueError, match="variable"):
        encoding.argument_for_variable(2)


def test_stable_encoding_models_round_trip_to_extensions() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})

    assert set(stable_extensions_from_encoding(encode_stable_extensions(framework))) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }


def test_sat_complete_extension_handles_required_labels() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    assert sat_complete_extension(framework) == frozenset({"a"})
    assert sat_complete_extension(framework, require_in="a") == frozenset({"a"})
    assert sat_complete_extension(framework, require_out="a") is None
    assert sat_complete_extension(framework, require_out="b") == frozenset({"a"})


def test_sat_preferred_extension_handles_required_labels() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "a"), ("c", "c")})

    assert sat_preferred_extension(framework, require_in="a") == frozenset({"a"})
    assert sat_preferred_extension(framework, require_in="b") == frozenset({"b"})
    assert sat_preferred_extension(framework, require_in="c") is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=30)
def test_stable_encoding_matches_brute_force_reference(framework) -> None:
    encoding = encode_stable_extensions(framework)

    assert set(stable_extensions_from_encoding(encoding)) == set(
        stable_extensions(framework)
    )


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_extensions_match_native_oracles_for_all_phase_four_semantics(
    framework: ArgumentationFramework,
) -> None:
    for semantics, oracle in SAT_EXTENSION_ORACLES.items():
        assert set(sat_extensions(framework, semantics)) == set(oracle(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_complete_extension_returns_native_complete_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = sat_complete_extension(framework)

    assert witness in set(complete_extensions(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_complete_extension_required_labels_match_native_oracle(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(complete_extensions(framework))

    for query in framework.arguments:
        required_in = sat_complete_extension(framework, require_in=query)
        native_with_query = {
            extension for extension in native_extensions if query in extension
        }
        if native_with_query:
            assert required_in in native_with_query
        else:
            assert required_in is None

        required_out = sat_complete_extension(framework, require_out=query)
        native_without_query = {
            extension for extension in native_extensions if query not in extension
        }
        if native_without_query:
            assert required_out in native_without_query
        else:
            assert required_out is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_preferred_extension_returns_native_preferred_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = sat_preferred_extension(framework)

    assert witness in set(preferred_extensions(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_preferred_extension_required_in_matches_native_oracle(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(preferred_extensions(framework))

    for query in framework.arguments:
        required_in = sat_preferred_extension(framework, require_in=query)
        native_with_query = {
            extension for extension in native_extensions if query in extension
        }
        if native_with_query:
            assert required_in in native_with_query
        else:
            assert required_in is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=30)
def test_sat_extensions_are_invariant_under_argument_renaming(
    framework: ArgumentationFramework,
) -> None:
    renamed = _rename_framework(framework)
    original_by_renamed = {
        f"renamed_{argument}": argument
        for argument in framework.arguments
    }

    for semantics in SAT_EXTENSION_ORACLES:
        renamed_extensions = {
            frozenset(original_by_renamed[argument] for argument in extension)
            for extension in sat_extensions(renamed, semantics)
        }

        assert renamed_extensions == set(sat_extensions(framework, semantics))


def _admissible_sets(framework: ArgumentationFramework) -> list[frozenset[str]]:
    attackers_index = _attackers_index(framework.defeats)
    arguments = sorted(framework.arguments)
    results: list[frozenset[str]] = []
    for mask in range(1 << len(arguments)):
        candidate = frozenset(
            argument
            for index, argument in enumerate(arguments)
            if mask & (1 << index)
        )
        if admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        ):
            results.append(candidate)
    return results


def _rename_framework(framework: ArgumentationFramework) -> ArgumentationFramework:
    renamed = {argument: f"renamed_{argument}" for argument in framework.arguments}
    return ArgumentationFramework(
        arguments=frozenset(renamed.values()),
        defeats=frozenset(
            (renamed[attacker], renamed[target])
            for attacker, target in framework.defeats
        ),
        attacks=None
        if framework.attacks is None
        else frozenset(
            (renamed[attacker], renamed[target])
            for attacker, target in framework.attacks
        ),
    )
