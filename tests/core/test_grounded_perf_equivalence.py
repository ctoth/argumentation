"""Grounded-extension equivalence and scaling coverage."""

from __future__ import annotations

import random
import time

from argumentation.core.bipolar import (
    BipolarArgumentationFramework,
    bipolar_grounded_extension,
    derived_set_defeats,
)
from argumentation.core.dung import ArgumentationFramework, grounded_extension


def _af(
    arguments: set[str],
    defeats: set[tuple[str, str]],
) -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
    )


def _baf(
    arguments: set[str],
    defeats: set[tuple[str, str]],
    supports: set[tuple[str, str]],
) -> BipolarArgumentationFramework:
    return BipolarArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
        supports=frozenset(supports),
    )


def _reference_defends(
    candidate: frozenset[str],
    argument: str,
    defeats: frozenset[tuple[str, str]],
) -> bool:
    attackers = frozenset(
        attacker
        for attacker, target in defeats
        if target == argument
    )
    return all(
        any((defender, attacker) in defeats for defender in candidate)
        for attacker in attackers
    )


def _reference_grounded(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    current: frozenset[str] = frozenset()
    while True:
        next_current = frozenset(
            argument
            for argument in arguments
            if _reference_defends(current, argument, defeats)
        )
        if next_current == current:
            return current
        current = next_current


def _reference_dung_grounded(
    framework: ArgumentationFramework,
) -> frozenset[str]:
    return _reference_grounded(framework.arguments, framework.defeats)


def _reference_bipolar_grounded(
    framework: BipolarArgumentationFramework,
) -> frozenset[str]:
    return _reference_grounded(framework.arguments, derived_set_defeats(framework))


def _random_dung_frameworks() -> list[ArgumentationFramework]:
    rng = random.Random(20260512)
    frameworks: list[ArgumentationFramework] = []
    for index in range(50):
        size = rng.randint(1, 30)
        density = 0.02 + (index % 10) * 0.035
        arguments = {f"a{index}_{node}" for node in range(size)}
        defeats = {
            (source, target)
            for source in arguments
            for target in arguments
            if rng.random() < density
        }
        frameworks.append(_af(arguments, defeats))
    return frameworks


def _random_bipolar_frameworks() -> list[BipolarArgumentationFramework]:
    rng = random.Random(20260513)
    frameworks: list[BipolarArgumentationFramework] = []
    for index in range(50):
        size = rng.randint(1, 12)
        attack_density = 0.03 + (index % 6) * 0.025
        support_density = 0.02 + (index % 5) * 0.03
        arguments = {f"b{index}_{node}" for node in range(size)}
        pairs = [(source, target) for source in arguments for target in arguments]
        defeats = {
            pair
            for pair in pairs
            if rng.random() < attack_density
        }
        supports = {
            pair
            for pair in pairs
            if pair not in defeats and rng.random() < support_density
        }
        frameworks.append(_baf(arguments, defeats, supports))
    return frameworks


def test_dung_grounded_matches_reference_fixpoint_on_small_corpus() -> None:
    frameworks = [
        _af(set(), set()),
        _af({"A"}, set()),
        _af({"A", "B"}, {("A", "B"), ("B", "A")}),
        _af({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")}),
        _af({"A", "B", "C", "D"}, {("A", "B"), ("B", "C"), ("C", "D")}),
        _af(
            {"Tweety", "Bird", "Penguin", "Flies"},
            {
                ("Penguin", "Flies"),
                ("Bird", "Penguin"),
                ("Tweety", "Bird"),
            },
        ),
        _af({"A", "B", "C", "D"}, {("B", "A"), ("C", "A"), ("B", "C"), ("C", "B")}),
        _af({"A"}, {("A", "A")}),
        _af({"A", "B", "C"}, {("A", "B"), ("A", "C"), ("B", "C"), ("C", "B")}),
        _af({"A", "B", "C"}, set()),
    ]
    frameworks.extend(_random_dung_frameworks())

    for framework in frameworks:
        assert grounded_extension(framework) == _reference_dung_grounded(framework)


def test_bipolar_grounded_matches_reference_fixpoint_on_small_corpus() -> None:
    frameworks = [
        _baf(set(), set(), set()),
        _baf({"A"}, set(), set()),
        _baf({"A", "B"}, {("A", "B")}, set()),
        _baf({"A", "B"}, {("A", "B"), ("B", "A")}, set()),
        _baf({"A", "B"}, set(), {("A", "B")}),
        _baf({"A", "B", "C"}, {("B", "C")}, {("A", "B")}),
        _baf({"A", "B", "C"}, {("A", "B")}, {("B", "C")}),
        _baf({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")}, set()),
        _baf({"A"}, set(), {("A", "A")}),
        _baf(
            {"A", "B", "C", "D", "F"},
            {("C", "D")},
            {("A", "B"), ("B", "C"), ("F", "D")},
        ),
    ]
    frameworks.extend(_random_bipolar_frameworks())

    for framework in frameworks:
        assert bipolar_grounded_extension(framework) == _reference_bipolar_grounded(framework)


def test_dung_grounded_scales_on_sparse_50k_node_graph() -> None:
    group_count = 8_334
    arguments: set[str] = set()
    defeats: set[tuple[str, str]] = set()
    expected: set[str] = set()

    for group in range(group_count):
        base = group * 6
        chain_in = f"a{base}"
        chain_out = f"a{base + 1}"
        chain_reinstated = f"a{base + 2}"
        cycle_a = f"a{base + 3}"
        cycle_b = f"a{base + 4}"
        cycle_c = f"a{base + 5}"
        arguments.update(
            {
                chain_in,
                chain_out,
                chain_reinstated,
                cycle_a,
                cycle_b,
                cycle_c,
            }
        )
        defeats.update(
            {
                (chain_in, chain_out),
                (chain_out, chain_reinstated),
                (cycle_a, cycle_b),
                (cycle_b, cycle_c),
                (cycle_c, cycle_a),
            }
        )
        expected.update({chain_in, chain_reinstated})

    framework = _af(arguments, defeats)

    started = time.perf_counter()
    result = grounded_extension(framework)
    elapsed = time.perf_counter() - started

    assert result == expected
    assert elapsed < 1.0
