import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.gradual import gradual as gradual_module
from argumentation.gradual import llm_surface as llm_surface_module
from argumentation.gradual import sensitivity as sensitivity_module
from argumentation.gradual.gradual import (
    GradualConvergenceError,
    GradualStrengthResult,
    WeightedBipolarGraph,
)


def test_gradual_convergence_error_preserves_solver_diagnostics() -> None:
    result = GradualStrengthResult(
        strengths={"claim": 0.625},
        converged=False,
        iterations=3,
        max_delta=0.125,
        tolerance=1e-9,
        integration_method="rk4_adaptive",
    )

    error = GradualConvergenceError("acceptance explanation", result)

    assert error.operation == "acceptance explanation"
    assert error.result is result
    assert str(error) == (
        "acceptance explanation did not converge after 3 iterations "
        "(residual 0.125 exceeds tolerance 1e-09)"
    )


def _graph() -> WeightedBipolarGraph:
    return WeightedBipolarGraph(
        arguments=frozenset({"claim", "attacker"}),
        initial_weights={"claim": 0.8, "attacker": 0.7},
        attacks=frozenset({("attacker", "claim")}),
    )


def _strength_result(*, converged: bool) -> GradualStrengthResult:
    return GradualStrengthResult(
        strengths={"claim": 0.625, "attacker": 0.7},
        converged=converged,
        iterations=1,
        max_delta=0.125 if not converged else 0.0,
        tolerance=1e-9,
        integration_method="rk4_adaptive",
    )


def test_explain_acceptance_rejects_real_bounded_non_convergence() -> None:
    with pytest.raises(GradualConvergenceError) as raised:
        llm_surface_module.explain_acceptance(
            _graph(),
            "claim",
            tolerance=1e-12,
            max_iterations=1,
        )

    assert raised.value.operation == "acceptance explanation"
    assert raised.value.result.iterations == 1
    assert raised.value.result.tolerance == 1e-12
    assert raised.value.result.max_delta > raised.value.result.tolerance


def test_explain_acceptance_stops_before_shapley_after_non_convergence(
    monkeypatch,
) -> None:
    solve_calls = 0

    def non_converged(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return _strength_result(converged=False)

    def forbidden_shapley(*args, **kwargs):
        raise AssertionError("Shapley attribution must not use an unsettled strength")

    monkeypatch.setattr(
        llm_surface_module,
        "quadratic_energy_strengths",
        non_converged,
    )
    monkeypatch.setattr(
        llm_surface_module,
        "shapley_attack_impacts",
        forbidden_shapley,
    )

    with pytest.raises(GradualConvergenceError):
        llm_surface_module.explain_acceptance(_graph(), "claim")

    assert solve_calls == 1


def test_contest_stops_after_non_converged_baseline(monkeypatch) -> None:
    solve_calls = 0

    def non_converged(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return _strength_result(converged=False)

    monkeypatch.setattr(
        llm_surface_module,
        "quadratic_energy_strengths",
        non_converged,
    )

    with pytest.raises(GradualConvergenceError) as raised:
        llm_surface_module.contest(
            _graph(),
            claim="claim",
            evidence={"counter": 0.9},
            edges={("counter", "claim"): "attack"},
        )

    assert raised.value.operation == "contestation baseline"
    assert solve_calls == 1


def test_contest_rejects_mixed_convergence_after_exactly_two_solves(
    monkeypatch,
) -> None:
    outcomes = iter(
        (_strength_result(converged=True), _strength_result(converged=False))
    )
    solve_calls = 0

    def mixed(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return next(outcomes)

    monkeypatch.setattr(llm_surface_module, "quadratic_energy_strengths", mixed)

    with pytest.raises(GradualConvergenceError) as raised:
        llm_surface_module.contest(
            _graph(),
            claim="claim",
            evidence={"counter": 0.9},
            edges={("counter", "claim"): "attack"},
        )

    assert raised.value.operation == "contestation result"
    assert solve_calls == 2


def test_revised_impact_stops_at_first_non_converged_required_solve(
    monkeypatch,
) -> None:
    outcomes = iter(
        (_strength_result(converged=True), _strength_result(converged=False))
    )
    solve_calls = 0

    def mixed(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return next(outcomes)

    monkeypatch.setattr(gradual_module, "quadratic_energy_strengths", mixed)

    with pytest.raises(GradualConvergenceError) as raised:
        gradual_module.revised_direct_impact(
            _graph(),
            influencers=frozenset({"attacker"}),
            target="claim",
        )

    assert raised.value.operation == "revised impact after attack removal"
    assert solve_calls == 2


def test_shapley_impact_stops_before_pairing_a_non_converged_coalition(
    monkeypatch,
) -> None:
    solve_calls = 0

    def non_converged(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return _strength_result(converged=False)

    monkeypatch.setattr(gradual_module, "quadratic_energy_strengths", non_converged)

    with pytest.raises(GradualConvergenceError) as raised:
        gradual_module.shapley_attack_impacts(_graph(), target="claim")

    assert raised.value.operation == "Shapley attack impact before removal"
    assert solve_calls == 1


def test_attack_removal_sensitivity_stops_after_non_converged_baseline(
    monkeypatch,
) -> None:
    solve_calls = 0

    def non_converged(*args, **kwargs) -> GradualStrengthResult:
        nonlocal solve_calls
        solve_calls += 1
        return _strength_result(converged=False)

    monkeypatch.setattr(sensitivity_module, "dfquad_strengths", non_converged)
    framework = ArgumentationFramework(
        arguments=frozenset({"claim", "attacker"}),
        defeats=frozenset({("attacker", "claim")}),
    )

    with pytest.raises(GradualConvergenceError) as raised:
        sensitivity_module.attack_removal_sensitivity(
            framework,
            supports={},
            base_scores={"claim": 0.8, "attacker": 0.7},
            attack=("attacker", "claim"),
        )

    assert raised.value.operation == "attack removal sensitivity baseline"
    assert solve_calls == 1
