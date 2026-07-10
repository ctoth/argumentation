from argumentation.core.optional_deps import OptionalDependencyUnavailable


def test_optional_dependency_unavailable_preserves_exact_guidance() -> None:
    error = OptionalDependencyUnavailable(
        feature="preferred SAT solving",
        package="python-sat",
        install_hint="Install python-sat or use backend='native'.",
    )

    assert str(error) == "preferred SAT solving requires python-sat"
    assert error.package == "python-sat"
    assert error.install_hint == "Install python-sat or use backend='native'."
