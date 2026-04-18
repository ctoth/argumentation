from __future__ import annotations

import random

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF, compute_probabilistic_acceptance


def _random_praf(seed: int) -> ProbabilisticAF:
    rng = random.Random(seed)
    args = [f"a{i}" for i in range(rng.randint(2, 5))]
    defeats = {
        (src, tgt)
        for src in args
        for tgt in args
        if src != tgt and rng.random() < 0.35
    }
    if not defeats:
        defeats.add((args[0], args[-1]))
    framework = ArgumentationFramework(
        arguments=frozenset(args),
        defeats=frozenset(defeats),
    )
    return ProbabilisticAF(
        framework=framework,
        p_args={arg: rng.choice([0.5, 0.7, 0.9, 1.0]) for arg in args},
        p_defeats={edge: rng.choice([0.4, 0.6, 0.8, 1.0]) for edge in defeats},
    )


@pytest.mark.differential
def test_exact_dp_matches_exact_enum_under_repeated_randomized_runs() -> None:
    for seed in range(10):
        praf = _random_praf(seed)
        exact = compute_probabilistic_acceptance(
            praf,
            semantics="grounded",
            strategy="exact_enum",
        )
        routed = compute_probabilistic_acceptance(
            praf,
            semantics="grounded",
            strategy="exact_dp",
        )

        assert routed.strategy_used == "exact_dp"
        assert routed.acceptance_probs == pytest.approx(exact.acceptance_probs)
