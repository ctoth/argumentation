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

The grounded assumption set is computed with a **forward-closure fixpoint**
(:func:`grounded_assumption_set_via_closures`), iterating the ``def`` operator
with two Horn closures per round, because ``aba.grounded_extension`` /
``aba.def_operator`` as written iterate ``_all_subsets`` (exponential), and the
earlier support-mask fixpoint enumerated minimal derivation supports (worst-case
exponential in rule-body width; the aba_2000 SE-ST pre-solve hang). The
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

from argumentation.core.reduct import SemanticReduct
from argumentation.structured.aba.aba import (
    ABAFramework,
    ABAInput,
    ABAPlusFramework,
    AssumptionSet,
)
from argumentation.structured.aspic.aspic import Literal, Rule


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


def _simplified_query_decision(
    simplification: SemanticReduct[ABAFramework, Literal],
    query: Literal,
) -> str:
    """Classify a query against a non-trivial grounded ABA reduct."""
    if query in simplification.fixed_in:
        return "fixed_in"
    if query in simplification.fixed_out:
        return "fixed_out"
    if query in _forward_closure(simplification.original, simplification.fixed_in):
        return "fixed_in_closure"
    if query not in simplification.residual.language:
        return "outside_residual"
    return "residual"


@dataclass(frozen=True)
class _PreparedAbaResidual:
    """ABA reduct plus requirements projected into the residual framework."""

    reduct: SemanticReduct[ABAFramework, Literal]
    projected_requirements: AssumptionSet | None

    @property
    def residual(self) -> ABAFramework:
        return self.reduct.residual

    @property
    def is_trivial(self) -> bool:
        return self.reduct.is_trivial

    @property
    def is_unsatisfiable(self) -> bool:
        return self.projected_requirements is None

    def lift(self, residual_extension: Iterable[Literal]) -> AssumptionSet:
        return self.reduct.lift(residual_extension)


def _prepare_residual_requirements(
    framework: ABAFramework,
    *,
    semantics: str,
    require_assumptions: Iterable[Literal] = frozenset(),
    simplify: bool = True,
) -> _PreparedAbaResidual:
    """Prepare ABA residual solving and project required assumptions.

    A required assumption fixed IN by the grounded reduct is already present in
    every lifted extension, so it disappears from the residual requirement. A
    required assumption fixed OUT is inconsistent with every lifted extension:
    its contrary is derivable from the fixed IN part, and ABA extensions are
    conflict-free. The residual solver should therefore never receive it.
    """
    reduct = (
        simplify_aba(framework, semantics=semantics)
        if simplify
        else SemanticReduct(framework, framework, frozenset(), frozenset())
    )
    projection = reduct.project_requirements(required_in=require_assumptions)
    residual_required = None if projection is None else projection[0]
    return _PreparedAbaResidual(
        reduct=reduct,
        projected_requirements=residual_required,
    )


def grounded_assumption_set_via_closures(framework: ABAFramework) -> AssumptionSet:
    """Compute the grounded assumption set with a polynomial forward-closure fixpoint.

    Equivalent to ``aba.grounded_extension`` on flat ABA but without exponential
    enumeration: it iterates the ``def`` operator using two Horn closures per
    round instead of precomputed minimal derivation supports (whose count is
    worst-case exponential in rule-body width -- the aba_2000 SE-ST pre-solve
    hang, exp 4B).

    Per round, for the current candidate set ``S``:

    * ``attacked_by(S) = {b : contrary(b) in Th(S)}`` -- one closure;
    * ``a`` is defended by ``S`` iff every assumption set deriving
      ``contrary(a)`` contains an attacked assumption; by monotonicity of
      ``Th`` that holds iff ``contrary(a) not in Th(assumptions - attacked_by(S))``
      -- one more closure.

    Both closures are linear in total rule-body size, and the monotone fixpoint
    takes at most ``|assumptions| + 1`` rounds.
    """
    assumptions = framework.assumptions
    selected: AssumptionSet = frozenset()
    while True:
        closure_of_selected = _forward_closure(framework, selected)
        attacked = frozenset(
            assumption
            for assumption in assumptions
            if framework.contrary[assumption] in closure_of_selected
        )
        survivor_closure = _forward_closure(framework, assumptions - attacked)
        next_selected = selected | frozenset(
            assumption
            for assumption in assumptions
            if framework.contrary[assumption] not in survivor_closure
        )
        if next_selected == selected:
            return selected
        selected = next_selected


def _forward_closure(
    framework: ABAFramework, premises: AssumptionSet
) -> frozenset[Literal]:
    from argumentation.structured.aba.aba import _closure

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
    language = rule_literals | frozenset(survivors) | frozenset(contrary.values())
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
) -> SemanticReduct[ABAFramework, Literal]:
    """Compute a semantics-preserving reduced flat ABA framework and lift data.

    When ``semantics`` is given and not in :data:`GROUNDED_REDUCT_ABA_SEMANTICS`,
    or when ``framework`` is an :class:`ABAPlusFramework`, the simplification is a
    no-op (``residual`` is the framework itself, ``fixed_in == fixed_out == set()``).
    When ``semantics`` is ``None`` the grounded reduct is applied -- callers are
    responsible for only calling this for gated semantics.
    """
    if isinstance(framework, ABAPlusFramework):
        base = framework.framework
        return SemanticReduct(base, base, frozenset(), frozenset())
    if (
        semantics is not None
        and _normalize_semantics(semantics) not in GROUNDED_REDUCT_ABA_SEMANTICS
    ):
        return SemanticReduct(framework, framework, frozenset(), frozenset())

    # Cheap O(|rules|) bail-out: if every assumption's contrary is forward-derivable
    # from the full assumption set then no assumption is initially unattacked, so the
    # grounded set is empty; and unless some contrary is a rule fact the OUT set is
    # empty too -- the simplification is then trivially a no-op. This avoids building
    # the support-mask machinery on the common "everything attacks something" case.
    fact_closure = _forward_closure(framework, frozenset())
    all_closure = _forward_closure(framework, framework.assumptions)
    if all(
        framework.contrary[assumption] in all_closure
        for assumption in framework.assumptions
    ) and not any(
        framework.contrary[assumption] in fact_closure
        for assumption in framework.assumptions
    ):
        return SemanticReduct(framework, framework, frozenset(), frozenset())

    grounded = grounded_assumption_set_via_closures(framework)
    closure = _forward_closure(framework, grounded)
    fixed_in = grounded
    fixed_out = frozenset(
        assumption
        for assumption in framework.assumptions
        if assumption not in fixed_in and framework.contrary[assumption] in closure
    )
    if not fixed_in and not fixed_out:
        return SemanticReduct(framework, framework, frozenset(), frozenset())
    residual = _residual_framework(framework, fixed_in=fixed_in, fixed_out=fixed_out)
    return SemanticReduct(
        original=framework,
        residual=residual,
        fixed_in=fixed_in,
        fixed_out=fixed_out,
    )


def _normalize_semantics(semantics: str) -> str:
    return semantics.strip().lower().replace("-", "_")


__all__ = [
    "GROUNDED_REDUCT_ABA_SEMANTICS",
    "grounded_assumption_set_via_closures",
    "simplify_aba",
]
