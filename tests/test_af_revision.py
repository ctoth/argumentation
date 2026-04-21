from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.af_revision import (
    AFChangeKind,
    AFKernelSemantics,
    ExtensionRevisionState,
    UnknownArgumentRank,
    _classify_extension_change,
    _extend_state,
    baumann_2015_kernel,
    baumann_2015_kernel_union_expand,
    cayrol_2014_classify_grounded_argument_addition,
    diller_2015_revise_by_formula,
    diller_2015_revise_by_framework,
    stable_kernel,
)
from argumentation.dung import ArgumentationFramework, grounded_extension, stable_extensions


pytestmark = pytest.mark.property

ARGUMENTS = frozenset({"a", "b", "c"})


class Formula(Protocol):
    def evaluate(self, extension: frozenset[str]) -> bool: ...

    def atoms(self) -> frozenset[str]: ...


@dataclass(frozen=True)
class Atom:
    name: str

    def evaluate(self, extension: frozenset[str]) -> bool:
        return self.name in extension

    def atoms(self) -> frozenset[str]:
        return frozenset((self.name,))

    def or_(self, other: Formula) -> Formula:
        return Or((self, other))


@dataclass(frozen=True)
class Not:
    formula: Formula

    def evaluate(self, extension: frozenset[str]) -> bool:
        return not self.formula.evaluate(extension)

    def atoms(self) -> frozenset[str]:
        return self.formula.atoms()


@dataclass(frozen=True)
class And:
    formulas: tuple[Formula, ...]

    def evaluate(self, extension: frozenset[str]) -> bool:
        return all(formula.evaluate(extension) for formula in self.formulas)

    def atoms(self) -> frozenset[str]:
        return frozenset(atom for formula in self.formulas for atom in formula.atoms())


@dataclass(frozen=True)
class Or:
    formulas: tuple[Formula, ...]

    def evaluate(self, extension: frozenset[str]) -> bool:
        return any(formula.evaluate(extension) for formula in self.formulas)

    def atoms(self) -> frozenset[str]:
        return frozenset(atom for formula in self.formulas for atom in formula.atoms())


def negate(formula: Formula) -> Formula:
    return Not(formula)


def conjunction(*formulas: Formula) -> Formula:
    return And(tuple(formulas))


A = Atom("a")
B = Atom("b")
C = Atom("c")
FORMULAS: tuple[Formula, ...] = (
    A,
    B,
    C,
    negate(A),
    conjunction(A, B),
    conjunction(A, negate(B)),
)

st_formula = st.sampled_from(FORMULAS)


@st.composite
def st_framework(draw) -> ArgumentationFramework:
    pairs = tuple((left, right) for left in sorted(ARGUMENTS) for right in sorted(ARGUMENTS))
    defeats = frozenset(draw(st.sets(st.sampled_from(pairs), max_size=5)))
    return ArgumentationFramework(arguments=ARGUMENTS, defeats=defeats)


@st.composite
def st_revision_state(draw) -> ExtensionRevisionState:
    extensions = tuple(frozenset(ext) for ext in stable_extensions(draw(st_framework())))
    if not extensions:
        extensions = (frozenset(),)
    ranking = {
        candidate: draw(st.integers(min_value=0, max_value=4))
        for candidate in ExtensionRevisionState.all_extensions(ARGUMENTS)
    }
    return ExtensionRevisionState.from_extensions(ARGUMENTS, extensions, ranking=ranking)


def _satisfies(extension: frozenset[str], formula: Formula) -> bool:
    return formula.evaluate(extension)


@given(st_framework(), st_framework())
@settings(deadline=None)
def test_baumann_brewka_2015_kernel_union_expansion_success_and_inclusion(
    base: ArgumentationFramework,
    new: ArgumentationFramework,
) -> None:
    expanded = baumann_2015_kernel_union_expand(base, new)
    union = ArgumentationFramework(
        arguments=base.arguments | new.arguments,
        defeats=frozenset(base.defeats | new.defeats),
        attacks=frozenset((base.attacks or base.defeats) | (new.attacks or new.defeats)),
    )

    assert base.arguments <= expanded.arguments
    assert new.arguments <= expanded.arguments
    assert expanded == stable_kernel(union)
    assert baumann_2015_kernel_union_expand(expanded, new) == expanded


def test_baumann_2015_kernel_union_removes_stable_kernel_redundant_attacks() -> None:
    """Baumann 2014 stable kernels delete non-self attacks from self-attackers."""
    base = ArgumentationFramework(
        arguments=frozenset({"self_attacker", "target"}),
        defeats=frozenset(
            {
                ("self_attacker", "self_attacker"),
                ("self_attacker", "target"),
            }
        ),
    )
    new = ArgumentationFramework(arguments=base.arguments, defeats=frozenset())

    expanded = baumann_2015_kernel_union_expand(base, new)

    assert ("self_attacker", "self_attacker") in expanded.defeats
    assert ("self_attacker", "target") not in expanded.defeats
    assert stable_extensions(expanded) == stable_extensions(base)


def test_baumann_2015_classical_kernels_are_semantics_specific() -> None:
    """Classical Baumann kernels keep self-loops but delete different non-self attacks."""

    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "x", "y"}),
        defeats=frozenset(
            {
                ("a", "a"),
                ("a", "b"),
                ("a", "x"),
                ("a", "y"),
                ("b", "b"),
                ("x", "a"),
            }
        ),
    )

    assert baumann_2015_kernel(
        framework,
        semantics=AFKernelSemantics.STABLE,
    ).defeats == frozenset({("a", "a"), ("b", "b"), ("x", "a")})
    assert baumann_2015_kernel(
        framework,
        semantics=AFKernelSemantics.ADMISSIBLE,
    ).defeats == frozenset({("a", "a"), ("a", "y"), ("b", "b"), ("x", "a")})
    assert baumann_2015_kernel(
        framework,
        semantics=AFKernelSemantics.GROUNDED,
    ).defeats == frozenset({("a", "a"), ("a", "x"), ("a", "y"), ("b", "b")})
    assert baumann_2015_kernel(
        framework,
        semantics=AFKernelSemantics.COMPLETE,
    ).defeats == frozenset(
        {("a", "a"), ("a", "x"), ("a", "y"), ("b", "b"), ("x", "a")}
    )


def test_cayrol_2010_restrictive_classification_for_strict_extension_shrink() -> None:
    before = (
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"c"}),
        frozenset({"d"}),
    )
    after = (
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"c"}),
    )

    assert _classify_extension_change(before, after) == AFChangeKind.RESTRICTIVE


def test_cayrol_2010_questioning_classification_for_more_extensions() -> None:
    before = (frozenset({"accepted"}),)
    after = (
        frozenset({"accepted"}),
        frozenset(),
    )

    assert _classify_extension_change(before, after) == AFChangeKind.QUESTIONING


def test_extend_state_unknown_rank_raises() -> None:
    state = object.__new__(ExtensionRevisionState)
    object.__setattr__(state, "arguments", frozenset({"a"}))
    object.__setattr__(state, "extensions", (frozenset({"a"}),))
    object.__setattr__(state, "ranking", {frozenset({"a"}): 0})

    with pytest.raises(UnknownArgumentRank) as exc_info:
        _extend_state(state, frozenset({"a", "x"}))

    assert "x" in str(exc_info.value)


@given(st_revision_state(), st_formula)
@settings(deadline=None)
def test_diller_2015_p_star_1_p_star_6_formula_revision(
    state: ExtensionRevisionState,
    formula: Formula,
) -> None:
    result = diller_2015_revise_by_formula(state, formula)

    assert all(_satisfies(extension, formula) for extension in result.extensions)
    if any(_satisfies(extension, formula) for extension in state.all_extensions(state.arguments)):
        assert result.extensions

    guard = Atom("__top_guard__")
    syntactic_variant = conjunction(formula, guard.or_(negate(guard)))
    variant = diller_2015_revise_by_formula(state.with_argument("__top_guard__"), syntactic_variant)
    projected = tuple(frozenset(arg for arg in ext if arg != "__top_guard__") for ext in variant.extensions)
    assert frozenset(projected) == frozenset(result.extensions)

    satisfying = tuple(
        extension
        for extension in state.all_extensions(state.arguments)
        if _satisfies(extension, formula)
    )
    assert result.extensions == state.minimal_extensions(satisfying)


@given(st_revision_state(), st_framework())
@settings(deadline=None)
def test_diller_2015_a_star_1_a_star_6_framework_revision(
    state: ExtensionRevisionState,
    framework: ArgumentationFramework,
) -> None:
    target_extensions = tuple(stable_extensions(framework)) or (frozenset(),)
    result = diller_2015_revise_by_framework(state, framework, semantics="stable")

    assert frozenset(result.extensions) <= frozenset(target_extensions)
    if frozenset(state.extensions) & frozenset(target_extensions):
        assert frozenset(result.extensions) == frozenset(state.extensions) & frozenset(target_extensions)
    if target_extensions:
        assert result.extensions
    assert result.extensions == state.minimal_extensions(target_extensions)


@given(st_framework())
@settings(deadline=None)
def test_cayrol_2014_grounded_addition_is_never_restrictive_or_questioning(
    framework: ArgumentationFramework,
) -> None:
    added = "z"
    attacks = frozenset({(added, target) for target in grounded_extension(framework)})
    kind = cayrol_2014_classify_grounded_argument_addition(framework, added, attacks)

    assert kind not in {AFChangeKind.RESTRICTIVE, AFChangeKind.QUESTIONING}
