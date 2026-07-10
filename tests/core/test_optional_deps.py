import builtins

import pytest

from argumentation.core.optional_deps import OptionalDependencyUnavailable, load_z3


def test_optional_dependency_unavailable_preserves_exact_guidance() -> None:
    error = OptionalDependencyUnavailable(
        feature="preferred SAT solving",
        package="python-sat",
        install_hint="Install python-sat or use backend='native'.",
    )

    assert str(error) == "preferred SAT solving requires python-sat"
    assert error.package == "python-sat"
    assert error.install_hint == "Install python-sat or use backend='native'."


def test_load_z3_maps_only_import_absence_to_exact_dependency_error(
    monkeypatch,
) -> None:
    original_import = builtins.__import__

    def import_without_z3(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "z3":
            raise ImportError("simulated missing z3")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_z3)

    with pytest.raises(OptionalDependencyUnavailable) as raised:
        load_z3("stable SAT solving")

    assert str(raised.value) == "stable SAT solving requires z3-solver"
    assert raised.value.package == "z3-solver"
    assert raised.value.install_hint == (
        "Install the z3-solver extra or use backend='native'."
    )
    assert isinstance(raised.value.__cause__, ImportError)
