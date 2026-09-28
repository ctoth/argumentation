"""Complete labellings already imply conflict-freeness over defeats."""

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.solving.af_sat import AfSatKernel

pytest.importorskip("z3")


def test_complete_labelling_has_vertex_bounded_assertions():
    arguments = frozenset(map(str, range(20)))
    framework = ArgumentationFramework(
        arguments, frozenset((a, b) for a in arguments for b in arguments)
    )
    kernel = AfSatKernel(framework)
    kernel.add_complete_labelling()
    assert len(kernel.solver.assertions()) <= 3 * len(arguments)
    before = len(kernel.solver.assertions())
    kernel.add_conflict_free()
    assert len(kernel.solver.assertions()) == before


def test_complete_labelling_keeps_additional_attack_conflicts():
    framework = ArgumentationFramework(
        frozenset({"a", "b"}), frozenset(), attacks=frozenset({("a", "b")})
    )
    kernel = AfSatKernel(framework)
    kernel.add_complete_labelling()
    # Both arguments are unattacked under defeats and must be in, but the
    # separate attack relation forbids accepting both.
    assert kernel.solver.check() == kernel.z3.unsat
