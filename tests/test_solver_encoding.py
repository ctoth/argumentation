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
from argumentation.af_sat import (
    AFSatProblem,
    find_complete_extension,
    find_preferred_extension,
    find_semi_stable_extension,
    find_stable_extension,
    find_stage_extension,
)
from argumentation.sat_encoding import (
    CNFEncoding,
    encode_stable_extensions,
    sat_extensions,
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


def test_kernel_complete_extension_handles_required_labels() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    assert find_complete_extension(framework) == frozenset({"a"})
    assert find_complete_extension(framework, require_in="a") == frozenset({"a"})
    assert find_complete_extension(framework, require_out="a") is None
    assert find_complete_extension(framework, require_out="b") == frozenset({"a"})


def test_kernel_preferred_extension_handles_required_labels() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "a"), ("c", "c")})

    assert find_preferred_extension(framework, require_in="a") == frozenset({"a"})
    assert find_preferred_extension(framework, require_in="b") == frozenset({"b"})
    assert find_preferred_extension(framework, require_in="c") is None
    assert find_preferred_extension(framework, require_out="a") == frozenset({"b"})


def test_kernel_range_maximal_extensions_handle_basic_witnesses() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    assert find_semi_stable_extension(framework) == frozenset({"a"})
    assert find_stage_extension(framework) == frozenset({"a"})


def test_kernel_conflict_free_constraints_reject_internal_attack() -> None:
    framework = af({"a", "b"}, {("a", "b")})
    problem = AFSatProblem(framework)

    problem.add_conflict_free()
    problem.require_in(frozenset({"a", "b"}))

    assert problem.check("test_conflict_free") == "unsat"


def test_kernel_admissible_constraints_require_defense() -> None:
    framework = af({"a", "b"}, {("a", "b")})
    problem = AFSatProblem(framework)

    problem.add_admissible_labelling()
    problem.require_in(frozenset({"b"}))

    assert problem.check("test_admissible") == "unsat"


def test_kernel_complete_labelling_fixes_defended_arguments() -> None:
    framework = af({"a", "b"}, {("a", "b")})
    problem = AFSatProblem(framework)

    problem.add_complete_labelling()

    assert problem.check("test_complete") == "sat"
    assert problem.model_extension() == frozenset({"a"})


def test_kernel_stable_coverage_rejects_uncovered_outsider() -> None:
    framework = af({"a", "b"}, {("a", "b")})
    problem = AFSatProblem(framework)

    problem.add_stable_coverage()
    problem.require_out(frozenset({"a"}))

    assert problem.check("test_stable") == "unsat"


def test_kernel_required_in_and_out_constraints_shape_witnesses() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})

    assert find_stable_extension(framework, require_in="a") == frozenset({"a"})
    assert find_stable_extension(framework, require_out="a") == frozenset({"b"})


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=30)
def test_stable_encoding_matches_brute_force_reference(framework) -> None:
    encoding = encode_stable_extensions(framework)

    assert set(stable_extensions_from_encoding(encoding)) == set(
        stable_extensions(framework)
    )


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_stable_extension_returns_native_stable_witness(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(stable_extensions(framework))
    witness = find_stable_extension(framework)

    if native_extensions:
        assert witness in native_extensions
    else:
        assert witness is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_sat_extensions_match_native_oracles_for_all_phase_four_semantics(
    framework: ArgumentationFramework,
) -> None:
    for semantics, oracle in SAT_EXTENSION_ORACLES.items():
        assert set(sat_extensions(framework, semantics)) == set(oracle(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_complete_extension_returns_native_complete_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = find_complete_extension(framework)

    assert witness in set(complete_extensions(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_complete_extension_required_labels_match_native_oracle(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(complete_extensions(framework))

    for query in framework.arguments:
        required_in = find_complete_extension(framework, require_in=query)
        native_with_query = {
            extension for extension in native_extensions if query in extension
        }
        if native_with_query:
            assert required_in in native_with_query
        else:
            assert required_in is None

        required_out = find_complete_extension(framework, require_out=query)
        native_without_query = {
            extension for extension in native_extensions if query not in extension
        }
        if native_without_query:
            assert required_out in native_without_query
        else:
            assert required_out is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_preferred_extension_returns_native_preferred_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = find_preferred_extension(framework)

    assert witness in set(preferred_extensions(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_preferred_extension_required_in_matches_native_oracle(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(preferred_extensions(framework))

    for query in framework.arguments:
        required_in = find_preferred_extension(framework, require_in=query)
        native_with_query = {
            extension for extension in native_extensions if query in extension
        }
        if native_with_query:
            assert required_in in native_with_query
        else:
            assert required_in is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_preferred_extension_required_out_matches_native_oracle(
    framework: ArgumentationFramework,
) -> None:
    native_extensions = set(preferred_extensions(framework))

    for query in framework.arguments:
        required_out = find_preferred_extension(framework, require_out=query)
        native_without_query = {
            extension for extension in native_extensions if query not in extension
        }
        if native_without_query:
            assert required_out in native_without_query
        else:
            assert required_out is None


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_semi_stable_extension_returns_native_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = find_semi_stable_extension(framework)

    assert witness in set(semi_stable_extensions(framework))


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=40)
def test_kernel_stage_extension_returns_native_witness(
    framework: ArgumentationFramework,
) -> None:
    witness = find_stage_extension(framework)

    assert witness in set(stage_extensions(framework))


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
