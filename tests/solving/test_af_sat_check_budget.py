"""Per-check Z3 time budget plumbing and honest unknown handling for AF SAT."""

from __future__ import annotations

import random

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.core.solver_results import SolverTimeout
from argumentation.solving import af_sat
from argumentation.solving import solver as solver_module
from argumentation.solving.af_sat import (
    AfSatCheckTimeout,
    AfSatKernel,
    SATCheck,
    _apply_check_budget,
    _PreferredSkepticalAttackerSolver,
    find_stable_extension,
)
from argumentation.solving.solver import (
    SATConfig,
    solve_dung_acceptance,
    solve_dung_single_extension,
)


def _cyclic_framework(size: int = 60, seed: int = 7) -> ArgumentationFramework:
    """Nontrivial cyclic AF: attack ring plus deterministic pseudo-random attacks."""
    rng = random.Random(seed)
    arguments = [f"a{index}" for index in range(size)]
    defeats = {
        (arguments[index], arguments[(index + 1) % size]) for index in range(size)
    }
    for _ in range(size * 4):
        attacker = rng.randrange(size)
        target = rng.randrange(size)
        if attacker != target:
            defeats.add((arguments[attacker], arguments[target]))
    return ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
    )


def _three_cycle() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c"), ("c", "a")}),
    )


class _RecordingSolver:
    def __init__(self) -> None:
        self.set_calls: list[tuple[str, object]] = []

    def set(self, name: str, value: object) -> None:
        self.set_calls.append((name, value))


class TestBudgetReachesSolverParams:
    def test_budget_seconds_become_z3_timeout_milliseconds(self) -> None:
        solver = _RecordingSolver()

        _apply_check_budget(solver, 1.5)

        assert solver.set_calls == [("timeout", 1500)]

    def test_sub_millisecond_budget_clamps_to_one_millisecond(self) -> None:
        solver = _RecordingSolver()

        _apply_check_budget(solver, 0.0001)

        assert solver.set_calls == [("timeout", 1)]

    def test_none_budget_sets_nothing(self) -> None:
        solver = _RecordingSolver()

        _apply_check_budget(solver, None)

        assert solver.set_calls == []

    def test_kernel_stores_budget_and_defaults_to_none(self) -> None:
        framework = _three_cycle()

        assert AfSatKernel(framework).check_budget_seconds is None
        assert (
            AfSatKernel(framework, check_budget_seconds=2.5).check_budget_seconds
            == 2.5
        )


class TestUnknownIsHonest:
    def test_kernel_check_raises_on_unknown_instead_of_negative(self) -> None:
        seen: list[SATCheck] = []
        kernel = AfSatKernel(_cyclic_framework(), trace_sink=seen.append)
        kernel.add_stable_coverage()
        kernel.solver.set("rlimit", 10)

        with pytest.raises(AfSatCheckTimeout):
            kernel.check("stable_extension")

        assert [check.result for check in seen] == ["unknown"]

    def test_attacker_solver_raises_on_unknown_instead_of_accepting(self) -> None:
        framework = _cyclic_framework()
        attacker_solver = _PreferredSkepticalAttackerSolver(
            framework,
            required_in=frozenset({"a0"}),
            trace_sink=None,
            metadata=None,
        )
        attacker_solver.solver.set("rlimit", 10)

        with pytest.raises(AfSatCheckTimeout):
            attacker_solver.find_attacker(loop_index=0)

    def test_finder_threads_budget_into_kernel(self, monkeypatch) -> None:
        created: list[float | None] = []

        class RecordingKernel(AfSatKernel):
            def __init__(self, framework, **kwargs) -> None:
                created.append(kwargs.get("check_budget_seconds"))
                super().__init__(framework, **kwargs)

        monkeypatch.setattr(af_sat, "AfSatKernel", RecordingKernel)

        find_stable_extension(_three_cycle(), check_budget_seconds=4.0)

        assert created == [4.0]

    def test_preferred_skeptical_threads_budget_into_every_kernel(
        self, monkeypatch
    ) -> None:
        created: list[float | None] = []

        class RecordingKernel(AfSatKernel):
            def __init__(self, framework, **kwargs) -> None:
                created.append(kwargs.get("check_budget_seconds"))
                super().__init__(framework, **kwargs)

        monkeypatch.setattr(af_sat, "AfSatKernel", RecordingKernel)

        af_sat.is_preferred_skeptically_accepted(
            _three_cycle(), "a", check_budget_seconds=6.0
        )

        assert created
        assert set(created) == {6.0}


class TestSolverLayerPlumbing:
    def test_sat_config_budget_defaults_to_none(self) -> None:
        assert SATConfig().check_budget_seconds is None

    def test_single_extension_passes_budget_to_finder(self, monkeypatch) -> None:
        captured: dict[str, object] = {}

        def fake_finder(framework, **kwargs):
            captured.update(kwargs)
            return frozenset()

        monkeypatch.setitem(
            solver_module._SAT_SINGLE_EXTENSION_FINDERS, "stable", fake_finder
        )

        solve_dung_single_extension(
            _three_cycle(),
            semantics="stable",
            backend="sat",
            sat=SATConfig(check_budget_seconds=7.5),
        )

        assert captured["check_budget_seconds"] == 7.5

    def test_single_extension_maps_check_timeout_to_solver_timeout(
        self, monkeypatch
    ) -> None:
        def exhausted_finder(framework, **kwargs):
            raise AfSatCheckTimeout("stable_extension", check_budget_seconds=7.5)

        monkeypatch.setitem(
            solver_module._SAT_SINGLE_EXTENSION_FINDERS, "stable", exhausted_finder
        )

        result = solve_dung_single_extension(
            _three_cycle(),
            semantics="stable",
            backend="sat",
            sat=SATConfig(check_budget_seconds=7.5),
        )

        assert isinstance(result, SolverTimeout)
        assert result.backend == "sat"

    def test_credulous_acceptance_maps_check_timeout_to_solver_timeout(
        self, monkeypatch
    ) -> None:
        def exhausted_finder(framework, **kwargs):
            raise AfSatCheckTimeout("stable_extension", check_budget_seconds=0.5)

        monkeypatch.setattr(
            solver_module, "find_stable_extension", exhausted_finder
        )

        result = solve_dung_acceptance(
            _three_cycle(),
            semantics="stable",
            task="credulous",
            query="a",
            backend="sat",
            sat=SATConfig(check_budget_seconds=0.5),
        )

        assert isinstance(result, SolverTimeout)
        assert result.backend == "sat"

    def test_skeptical_acceptance_never_answers_true_on_timeout(
        self, monkeypatch
    ) -> None:
        def exhausted_finder(framework, **kwargs):
            raise AfSatCheckTimeout("stable_extension", check_budget_seconds=0.5)

        monkeypatch.setattr(
            solver_module, "find_stable_extension", exhausted_finder
        )

        result = solve_dung_acceptance(
            _three_cycle(),
            semantics="stable",
            task="skeptical",
            query="a",
            backend="sat",
            sat=SATConfig(check_budget_seconds=0.5),
        )

        assert isinstance(result, SolverTimeout)


class TestDefaultBehaviorUnchanged:
    def test_stable_finder_without_budget_still_solves(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            defeats=frozenset({("a", "b")}),
        )

        assert find_stable_extension(framework) == frozenset({"a"})

    def test_acceptance_without_budget_still_answers(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            defeats=frozenset({("a", "b")}),
        )

        result = solve_dung_acceptance(
            framework,
            semantics="stable",
            task="credulous",
            query="a",
            backend="sat",
        )

        assert result.answer is True
