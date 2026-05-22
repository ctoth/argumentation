"""Semantics-preserving preprocessing for flat ABA frameworks.

Wave C2a of the graph-theory speedup workstream: the ABA analog of
:mod:`argumentation.core.preprocessing`'s Dung grounded reduct. Before a flat ABA
framework is handed to the Z3 SAT path or the clingo ASP path, fix the part of
the answer that is polynomially computable -- the well-founded (grounded)
assumption set and the assumptions whose contrary it already derives -- then
solve only the residual and lift the answer back.

* **``fixed_in``** -- ``G_ABA``, the grounded assumption set (least fixed point of
  the ABA characteristic / ``def`` operator, Bondarenko et al. 1997; Toni 2014).
  It equals the intersection of all complete assumption sets, so it is IN in every
  complete / preferred / stable / ideal extension.
* **``fixed_out``** -- ``{a : contrary(a) in Th(G_ABA)}``: assumptions whose
  contrary is already forward-derivable from ``G_ABA`` alone. Every complete /
  preferred / stable extension contains ``G_ABA`` and is conflict-free, so it
  cannot contain any ``fixed_out`` assumption. This is the ABA analog of ``G+``.
* **Residual.** The conservative "pin the search space, don't restructure the
  proof system" form recommended in the spec: an :class:`ABAFramework` over the
  surviving assumptions only, with the rules rewritten just enough to make this
  exact -- ``fixed_in`` assumptions are unconditionally derivable, so their
  occurrences as rule antecedents are deleted; any rule whose antecedents mention
  a ``fixed_out`` assumption can never fire in a conflict-free superset of
  ``fixed_in`` and so is dropped. No further proof-system rewriting.
* **Lift.** ``residual_extension | fixed_in``.

The grounded assumption set is computed with a **support-mask fixpoint**
(:func:`grounded_assumption_set_via_supports`), reusing the
``aba_sat._SupportState`` machinery, because ``aba.grounded_extension`` /
``aba.def_operator`` as written iterate ``_all_subsets`` (exponential). The
brute-force ``aba.grounded_extension`` is kept untouched as the differential
oracle.

**Gate.** ``GROUNDED_REDUCT_ABA_SEMANTICS = {grounded, complete, preferred,
stable, ideal}``. ``admissible`` is excluded (the empty set is admissible, so the
constant offset would drop every admissible set that does not already contain
``fixed_in``). ABA+ frameworks (:class:`ABAPlusFramework`) get a no-op
simplification -- reverse attacks via preferences break the ``fixed_out``
characterisation.

Soundness of the residual-lift identity ``complete(F) = {fixed_in u E : E in
complete(residual)}`` (and the preferred / stable / ideal analogs) is validated by
the differential oracle in ``tests/test_aba_preprocessing.py`` against both the
brute-force ``aba.py`` reference and the unsimplified solver -- the same way
Wave A validated its AF reduct.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain

from argumentation.aba import (
    ABAFramework,
    ABAInput,
    ABAPlusFramework,
    AssumptionSet,
)
from argumentation.aspic import Literal, Rule


# Semantics for which the grounded ABA reduct is semantics-preserving.
GROUNDED_REDUCT_ABA_SEMANTICS: frozenset[str] = frozenset(
    {
        "grounded",
        "complete",
        "preferred",
        "stable",
        "ideal",
    }
)


@dataclass(frozen=True)
class AbaSimplification:
    """Result of :func:`simplify_aba`.

    ``residual`` is the flat ABA framework to actually solve. ``fixed_in`` are
    assumptions forced IN in every extension of the gated semantics; they are
    *not* assumptions of ``residual``. ``fixed_out`` are assumptions forced OUT;
    they are *not* assumptions of ``residual`` either. ``original`` is the
    framework that was simplified.
    """

    original: ABAFramework
    residual: ABAFramework
    fixed_in: AssumptionSet
    fixed_out: AssumptionSet

    @property
    def is_trivial(self) -> bool:
        """True when nothing was fixed (the residual is the original framework)."""
        return not self.fixed_in and not self.fixed_out

    def lift(self, residual_extension: Iterable[Literal]) -> AssumptionSet:
        """Map an extension of ``residual`` back to an extension of ``original``."""
        return frozenset(residual_extension) | self.fixed_in

    def lift_all(
        self, residual_extensions: Iterable[Iterable[Literal]]
    ) -> list[AssumptionSet]:
        """Map a collection of residual extensions back, de-duplicated, order-stable."""
        seen: set[AssumptionSet] = set()
        lifted: list[AssumptionSet] = []
        for extension in residual_extensions:
            value = self.lift(extension)
            if value not in seen:
                seen.add(value)
                lifted.append(value)
        return lifted


def grounded_assumption_set_via_supports(framework: ABAFramework) -> AssumptionSet:
    """Compute the grounded assumption set with a polynomial support-mask fixpoint.

    Equivalent to ``aba.grounded_extension`` on flat ABA but without the
    exponential ``_all_subsets`` blow-up of ``aba.def_operator``: it iterates the
    ``def`` operator over the precomputed minimal derivation supports, the same
    cost class as the rest of the SAT path. Implementation note: each outer round
    computes ``attacked_by(S)`` once and tests each candidate's attack supports
    against it, rather than recomputing attack relations inside every ``defends``
    check.
    """
    from argumentation.aba_sat import _SupportState

    state = _SupportState.from_framework(framework)
    n = len(state.assumptions)
    if n == 0:
        return frozenset()
    # For each assumption index, the integer masks of its minimal attack supports
    # (the assumption sets that forward-derive its contrary).
    attack_support_masks: list[tuple[int, ...]] = [
        tuple(state.attack_supports.get(assumption, ()))
        for assumption in state.assumptions
    ]
    selected = 0
    while True:
        # attacked := { b : some minimal attack support of b is a subset of selected }
        attacked = 0
        for index in range(n):
            for support in attack_support_masks[index]:
                if (support & selected) == support:
                    attacked |= 1 << index
                    break
        next_selected = selected
        for index in range(n):
            if next_selected & (1 << index):
                continue
            supports = attack_support_masks[index]
            # An empty attack support is an unblockable attack -> never defended.
            defended = True
            for support in supports:
                if support == 0 or (support & attacked) == 0:
                    defended = False
                    break
            if defended:
                next_selected |= 1 << index
        if next_selected == selected:
            return state.extension(selected)
        selected = next_selected


def _forward_closure(framework: ABAFramework, premises: AssumptionSet) -> frozenset[Literal]:
    from argumentation.aba import _closure

    return _closure(framework, premises)


def _residual_framework(
    framework: ABAFramework,
    *,
    fixed_in: AssumptionSet,
    fixed_out: AssumptionSet,
) -> ABAFramework:
    survivors = framework.assumptions - fixed_in - fixed_out
    rules: list[Rule] = []
    for rule in framework.rules:
        if any(antecedent in fixed_out for antecedent in rule.antecedents):
            # A rule mentioning a fixed-out assumption literal can never fire in a
            # conflict-free superset of fixed_in (the assumption is OUT in every
            # gated-semantics extension), so it is dead in the residual.
            continue
        new_antecedents = tuple(
            antecedent for antecedent in rule.antecedents if antecedent not in fixed_in
        )
        rules.append(
            Rule(
                antecedents=new_antecedents,
                consequent=rule.consequent,
                kind=rule.kind,
                name=rule.name,
            )
        )
    contrary = {assumption: framework.contrary[assumption] for assumption in survivors}
    rule_literals = frozenset(
        chain.from_iterable(rule.antecedents for rule in rules)
    ) | frozenset(rule.consequent for rule in rules)
    language = (
        rule_literals
        | frozenset(survivors)
        | frozenset(contrary.values())
    )
    return ABAFramework(
        language=language,
        rules=frozenset(rules),
        assumptions=frozenset(survivors),
        contrary=contrary,
    )


def simplify_aba(
    framework: ABAInput,
    *,
    semantics: str | None = None,
) -> AbaSimplification:
    """Compute a semantics-preserving reduced flat ABA framework and lift data.

    When ``semantics`` is given and not in :data:`GROUNDED_REDUCT_ABA_SEMANTICS`,
    or when ``framework`` is an :class:`ABAPlusFramework`, the simplification is a
    no-op (``residual`` is the framework itself, ``fixed_in == fixed_out == set()``).
    When ``semantics`` is ``None`` the grounded reduct is applied -- callers are
    responsible for only calling this for gated semantics.
    """
    if isinstance(framework, ABAPlusFramework):
        base = framework.framework
        return AbaSimplification(base, base, frozenset(), frozenset())
    if semantics is not None and _normalize_semantics(semantics) not in GROUNDED_REDUCT_ABA_SEMANTICS:
        return AbaSimplification(framework, framework, frozenset(), frozenset())

    # Cheap O(|rules|) bail-out: if every assumption's contrary is forward-derivable
    # from the full assumption set then no assumption is initially unattacked, so the
    # grounded set is empty; and unless some contrary is a rule fact the OUT set is
    # empty too -- the simplification is then trivially a no-op. This avoids building
    # the support-mask machinery on the common "everything attacks something" case.
    fact_closure = _forward_closure(framework, frozenset())
    all_closure = _forward_closure(framework, framework.assumptions)
    if all(
        framework.contrary[assumption] in all_closure for assumption in framework.assumptions
    ) and not any(
        framework.contrary[assumption] in fact_closure for assumption in framework.assumptions
    ):
        return AbaSimplification(framework, framework, frozenset(), frozenset())

    grounded = grounded_assumption_set_via_supports(framework)
    closure = _forward_closure(framework, grounded)
    fixed_in = grounded
    fixed_out = frozenset(
        assumption
        for assumption in framework.assumptions
        if assumption not in fixed_in and framework.contrary[assumption] in closure
    )
    if not fixed_in and not fixed_out:
        return AbaSimplification(framework, framework, frozenset(), frozenset())
    residual = _residual_framework(framework, fixed_in=fixed_in, fixed_out=fixed_out)
    return AbaSimplification(
        original=framework,
        residual=residual,
        fixed_in=fixed_in,
        fixed_out=fixed_out,
    )


def _normalize_semantics(semantics: str) -> str:
    return semantics.strip().lower().replace("-", "_")


__all__ = [
    "AbaSimplification",
    "GROUNDED_REDUCT_ABA_SEMANTICS",
    "grounded_assumption_set_via_supports",
    "simplify_aba",
]
