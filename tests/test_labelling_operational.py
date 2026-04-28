from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework, complete_extensions, grounded_extension
from argumentation.labelling import (
    Label,
    Labelling,
    complete_labellings,
    grounded_labelling,
    legally_in,
    legally_out,
    preferred_labellings,
    stable_labellings,
)


pytestmark = pytest.mark.unit


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_legally_in_predicate_caminada_2006_page_3() -> None:
    """Caminada 2006, p. 3: IN iff every defeater is OUT."""
    framework = af({"A", "B", "C"}, {("A", "B"), ("B", "C")})
    labelling = Labelling.from_statuses(
        arguments=framework.arguments,
        statuses={"A": Label.IN, "B": Label.OUT, "C": Label.IN},
    )

    assert legally_in(labelling, framework, "A") is True
    assert legally_in(labelling, framework, "C") is True
    assert legally_in(labelling, framework, "B") is False


def test_legally_out_predicate_caminada_2006_page_3() -> None:
    """Caminada 2006, p. 3: OUT iff some defeater is IN."""
    framework = af({"A", "B", "C"}, {("A", "B"), ("B", "C")})
    labelling = Labelling.from_statuses(
        arguments=framework.arguments,
        statuses={"A": Label.IN, "B": Label.OUT, "C": Label.IN},
    )

    assert legally_out(labelling, framework, "B") is True
    assert legally_out(labelling, framework, "A") is False
    assert legally_out(labelling, framework, "C") is False


def test_complete_labellings_match_complete_extensions_caminada_2006_pages_3_4() -> None:
    """Caminada 2006, pp. 3-4: Lab2Ext bridges complete labellings/extensions."""
    framework = af({"A", "B"}, {("A", "B"), ("B", "A")})

    assert {labelling.extension for labelling in complete_labellings(framework)} == set(
        complete_extensions(framework)
    )


def test_grounded_preferred_and_stable_labelling_characterisations() -> None:
    """Caminada 2006, pp. 4-5: stable=no UNDEC, preferred=max IN, grounded=min IN."""
    framework = af({"A", "B"}, {("A", "B"), ("B", "A")})

    assert grounded_labelling(framework).extension == grounded_extension(framework)
    assert {labelling.extension for labelling in preferred_labellings(framework)} == {
        frozenset({"A"}),
        frozenset({"B"}),
    }
    assert {labelling.extension for labelling in stable_labellings(framework)} == {
        frozenset({"A"}),
        frozenset({"B"}),
    }
