from argumentation.gradual.gradual import (
    GradualConvergenceError,
    GradualStrengthResult,
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
