from __future__ import annotations

import pytest
from hypothesis import given, settings

from argumentation.dung import complete_extensions, preferred_extensions, stable_extensions
from tests.test_dung import argumentation_frameworks


pytestmark = [pytest.mark.property, pytest.mark.differential]


@given(argumentation_frameworks(max_args=6))
@settings(deadline=10000)
def test_complete_extensions_native_and_z3_are_equal(framework) -> None:
    assert set(complete_extensions(framework, backend="brute")) == set(
        complete_extensions(framework, backend="z3")
    )


@given(argumentation_frameworks(max_args=6))
@settings(deadline=10000)
def test_preferred_extensions_native_and_z3_are_equal(framework) -> None:
    assert set(preferred_extensions(framework, backend="brute")) == set(
        preferred_extensions(framework, backend="z3")
    )


@given(argumentation_frameworks(max_args=6))
@settings(deadline=10000)
def test_stable_extensions_native_and_z3_are_equal(framework) -> None:
    assert set(stable_extensions(framework, backend="brute")) == set(
        stable_extensions(framework, backend="z3")
    )
