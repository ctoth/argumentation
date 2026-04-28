from __future__ import annotations

import pytest
from hypothesis import given, settings

from argumentation.dung import stable_extensions
from argumentation.sat_encoding import (
    CNFEncoding,
    encode_stable_extensions,
    stable_extensions_from_encoding,
)
from tests.test_dung import af, argumentation_frameworks


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


@given(argumentation_frameworks(max_args=4))
@settings(deadline=10000, max_examples=30)
def test_stable_encoding_matches_brute_force_reference(framework) -> None:
    encoding = encode_stable_extensions(framework)

    assert set(stable_extensions_from_encoding(encoding)) == set(
        stable_extensions(framework)
    )
