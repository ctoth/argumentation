"""Incremental multi-shot clingo CEGAR solving for flat ABA (ASPforABA).

Implements the incremental answer-set-solving scheme of Lehtonen, Wallner and
Jaervisalo, *Harnessing Incremental Answer Set Solving for Reasoning in
Assumption-Based Argumentation*, TPLP 2021 (arXiv:2108.04192):

* one ``clingo.Control``, ``ABA(F) cup pi_com`` (Listing 1, transcribed in
  ``encodings/aba_com_incremental.lp``) added and grounded **once**;
* ``solve(assumptions=...)`` for the transient ``in(I)`` / ``supported(s)``
  checks (no re-grounding);
* a fresh ``#program`` part re-grounded per refinement for the *permanent*
  ``constr(out(I)) = :- out(a1), ..., out(ak).`` accumulation -- this is the
  abstraction-refinement clause of Algorithm 1, the clingo analog of the Z3
  ``solver.add`` in :mod:`argumentation.aba_sat`.

This module *replaces* the enumerate-then-filter subprocess clingo path in
:mod:`argumentation.aba_asp` for the ``asp`` / ``clingo`` backends on flat ABA
with ``complete`` / ``stable`` / ``preferred`` / ``grounded`` semantics. The old
subprocess path is still reachable as ``backend="clingo_subprocess"`` (oracle).
``admissible`` keeps the subprocess path (no ``pi_com``-style module for it).

Composes under :func:`argumentation.aba_preprocessing.simplify_aba`: the caller
(``solve_aba_with_backend``) runs ``simplify_aba`` first and feeds this solver
the residual; lifting back is the caller's job.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from typing import Any

from argumentation.aba import ABAFramework, AssumptionSet
from argumentation.aba_asp import ABAEncoding, encode_aba_theory
from argumentation.aba_preprocessing import grounded_assumption_set_via_supports
from argumentation.aspic import Literal

_COM_MODULE_RESOURCE = "aba_com_incremental.lp"
SUPPORTED_SEMANTICS = frozenset({"complete", "stable", "preferred", "grounded"})
DEFAULT_CLINGO_CONTROL_ARGS = ("--models=0", "--warn=none")

LEHTONEN_INCREMENTAL_ASP_CITATION = "Lehtonen_2021_IncrementalASP_ABA"
LEHTONEN_INCREMENTAL_ASP_PAGE_CITATIONS = (
    "p.5: ABA(F) fact surface and Algorithm 1; "
    "p.6: pi_com Listing 1 and constr(out(I)) refinement; "
    "p.12: incremental Python interface of Clingo"
)


def lehtonen_incremental_asp_metadata() -> dict[str, str]:
    """Page-image provenance for the incremental ABA multishot backend."""
    return {
        "paper": LEHTONEN_INCREMENTAL_ASP_CITATION,
        "paper_pages": LEHTONEN_INCREMENTAL_ASP_PAGE_CITATIONS,
    }


def _load_clingo():
    try:
        return importlib.import_module("clingo")
    except ImportError as exc:  # pragma: no cover - exercised only without clingo
        raise RuntimeError("incremental ABA solving requires the clingo Python package") from exc


def _com_module_text() -> str:
    return resources.files("argumentation.encodings").joinpath(_COM_MODULE_RESOURCE).read_text(
        encoding="utf-8"
    )


@dataclass
class IncrementalTelemetry:
    """Spy hook for tests: counts iterations / refinement clauses added."""

    refinement_clauses: int = 0
    outer_iterations: int = 0
    inner_iterations: int = 0
    solver_calls: int = 0
    clingo_control_args: tuple[str, ...] = DEFAULT_CLINGO_CONTROL_ARGS
    clingo_statistics: dict[str, Any] | None = None


def _sanitize_clingo_statistics(value: Any) -> Any:
    if isinstance(value, Mapping) or hasattr(value, "items"):
        return {str(key): _sanitize_clingo_statistics(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_clingo_statistics(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


class AbaIncrementalSolver:
    """Multi-shot clingo solver state for a single flat ABA framework.

    One instance owns the grounded ``ABA(F) cup pi_com`` program. The
    *complete-set* methods (:meth:`enumerate_complete`, :meth:`enumerate_stable`)
    reuse the same ``Control`` across calls. The *preferred* methods accumulate
    query-specific ``constr(out(I))`` refinement clauses, so each preferred query
    builds a fresh ``Control`` (the L21-TPLP scheme).
    """

    def __init__(
        self,
        framework: ABAFramework,
        *,
        encoding: ABAEncoding | None = None,
        control_args: tuple[str, ...] = (),
        collect_statistics: bool = False,
    ) -> None:
        if not isinstance(framework, ABAFramework):  # defensive; callers gate this
            raise TypeError("AbaIncrementalSolver only handles flat ABAFramework")
        self.framework = framework
        if encoding is None:
            encoding = encode_aba_theory(framework, include_supports=False)
        # ABA(F) facts: encode_aba_theory emits a superset of assumption/1,
        # head/2, body/2, contrary/2 (also rule/1, body_count/2, support_*/2 --
        # the com module simply ignores those).
        self._facts_text = "\n".join(encoding.facts)
        self._com_text = _com_module_text()
        self._assumption_by_id = dict(encoding.assumption_by_id)
        self._id_by_assumption = {
            assumption: assumption_id for assumption_id, assumption in encoding.assumption_by_id.items()
        }
        self._literal_by_id = dict(encoding.literal_by_id)
        self._id_by_literal = {
            literal: literal_id for literal_id, literal in encoding.literal_by_id.items()
        }
        self._clingo = _load_clingo()
        self.control_args = DEFAULT_CLINGO_CONTROL_ARGS + tuple(control_args)
        self.collect_statistics = collect_statistics

    # -- low-level Control construction -------------------------------------

    def _new_control(self, *, extra_program: str = "") -> Any:
        ctl = self._clingo.Control(list(self.control_args))
        program = self._facts_text + "\n" + self._com_text
        if extra_program:
            program = program + "\n" + extra_program
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
        return ctl

    def _record_telemetry_control(self, telemetry: IncrementalTelemetry | None) -> None:
        if telemetry is not None:
            telemetry.clingo_control_args = self.control_args

    def _record_telemetry_statistics(self, ctl, telemetry: IncrementalTelemetry | None) -> None:
        if telemetry is not None and self.collect_statistics:
            telemetry.clingo_statistics = _sanitize_clingo_statistics(ctl.statistics)

    def _symbol_in(self, assumption: Literal):
        return self._clingo.Function("in", [self._clingo.Function(self._id_by_assumption[assumption])])

    def _symbol_supported(self, literal: Literal):
        literal_id = self._id_by_literal.get(literal)
        if literal_id is None:
            return None
        return self._clingo.Function("supported", [self._clingo.Function(literal_id)])

    def _extract_in_set(self, model) -> AssumptionSet:
        # MUST be called only inside the on_model callback -- clingo Model objects
        # are invalid afterwards.
        result: set[Literal] = set()
        for symbol in model.symbols(atoms=True):
            if symbol.name == "in" and len(symbol.arguments) == 1:
                ident = symbol.arguments[0].name
                assumption = self._assumption_by_id.get(ident)
                if assumption is not None:
                    result.add(assumption)
        return frozenset(result)

    def _solve_one(
        self,
        ctl,
        *,
        assumptions=None,
        telemetry: IncrementalTelemetry | None = None,
    ) -> AssumptionSet | None:
        """Solve for one model; return its ``in`` assumption set, or ``None`` if UNSAT."""
        captured: list[AssumptionSet] = []

        def on_model(model) -> bool:
            captured.append(self._extract_in_set(model))
            return False  # stop after first model

        self._record_telemetry_control(telemetry)
        result = ctl.solve(assumptions=assumptions or [], on_model=on_model)
        self._record_telemetry_statistics(ctl, telemetry)
        if not result.satisfiable:
            return None
        return captured[-1]

    # -- complete / stable: single solve, Control reused --------------------

    def _enumerate(self, *, stable: bool, telemetry: IncrementalTelemetry | None) -> tuple[AssumptionSet, ...]:
        extra = ":- out(X), not defeated(X)." if stable else ""
        ctl = self._new_control(extra_program=extra)
        found: list[AssumptionSet] = []

        def on_model(model) -> None:
            found.append(self._extract_in_set(model))

        if telemetry is not None:
            telemetry.solver_calls += 1
        self._record_telemetry_control(telemetry)
        ctl.solve(on_model=on_model)
        self._record_telemetry_statistics(ctl, telemetry)
        return _sorted_extensions(found)

    def enumerate_complete(self, *, telemetry: IncrementalTelemetry | None = None) -> tuple[AssumptionSet, ...]:
        return self._enumerate(stable=False, telemetry=telemetry)

    def enumerate_stable(self, *, telemetry: IncrementalTelemetry | None = None) -> tuple[AssumptionSet, ...]:
        return self._enumerate(stable=True, telemetry=telemetry)

    def find_complete_extension(self, *, telemetry: IncrementalTelemetry | None = None) -> AssumptionSet | None:
        ctl = self._new_control()
        if telemetry is not None:
            telemetry.solver_calls += 1
        return self._solve_one(ctl, telemetry=telemetry)

    def find_stable_extension(self, *, telemetry: IncrementalTelemetry | None = None) -> AssumptionSet | None:
        ctl = self._new_control(extra_program=":- out(X), not defeated(X).")
        if telemetry is not None:
            telemetry.solver_calls += 1
        return self._solve_one(ctl, telemetry=telemetry)

    def grounded_extension(self) -> AssumptionSet:
        # Use the polynomial support-mask fixpoint rather than ``aba.grounded_extension``
        # -- the latter's ``_all_subsets`` blow-up is exponential, and it historically
        # also dropped the empty attacker set (now fixed in ``aba._defends``).  The
        # support-based primitive is the C2a reference of record and handles
        # fact-contrary frameworks correctly (returns a conflict-free set).
        return grounded_assumption_set_via_supports(self.framework)

    # -- preferred: Algorithm 1 / Algorithm 4 (CEGAR loop) -----------------

    def _refinement_constraint(self, out_assumptions: frozenset[Literal]) -> str | None:
        """``constr(out(I)) = :- out(a1), ..., out(ak).`` over the OUT assumptions.

        Returns ``None`` if ``out(I)`` is empty -- then the constraint is ``:-``
        (unconditional), i.e. rules out *every* model; the caller treats that as
        permanent unsatisfiability.
        """
        if not out_assumptions:
            return None
        body = ", ".join(f"out({self._id_by_assumption[a]})" for a in sorted(out_assumptions, key=repr))
        return f":- {body}."

    def _grow_to_maximal_not_deriving(
        self,
        ctl,
        seed_in: AssumptionSet,
        query_symbol,
        *,
        add_refinement,
        telemetry: IncrementalTelemetry | None,
    ) -> AssumptionSet:
        """Inner loop of Algorithm 1 (Lines 5-7): grow a complete set not deriving
        ``s`` to a ``subseteq``-maximal one. Returns the final ``in(I)`` set.

        ``add_refinement(out_set)`` adds ``constr(out(I))`` to ``ctl`` (and bumps
        telemetry); it may signal permanent unsatisfiability by returning False.
        """
        all_assumptions = frozenset(self.framework.assumptions)
        current_in = seed_in
        while True:
            out_set = all_assumptions - current_in
            if not add_refinement(out_set):
                return current_in  # constr(out(I)) is :- ; no proper superset possible
            # search for a complete set still not deriving s with in(I) <= it
            in_assumptions = [(self._symbol_in(a), True) for a in sorted(current_in, key=repr)]
            transient = list(in_assumptions)
            if query_symbol is not None:
                transient.append((query_symbol, False))
            if telemetry is not None:
                telemetry.solver_calls += 1
                telemetry.inner_iterations += 1
            next_in = self._solve_one(ctl, assumptions=transient)
            if next_in is None:
                return current_in
            current_in = next_in

    def is_skeptically_accepted_preferred(
        self, query: Literal, *, telemetry: IncrementalTelemetry | None = None
    ) -> tuple[bool, AssumptionSet | None]:
        """Algorithm 1: decide DS-PR for ``query``.

        Returns ``(answer, counterexample)`` -- ``counterexample`` is a preferred
        assumption set not deriving ``query`` when the answer is ``False``.
        """
        query_symbol = self._symbol_supported(query)
        if query_symbol is None:
            # query not in language -> not forward-derivable from any assumption
            # set -> not in any extension's closure -> not skeptically accepted.
            # Any preferred set is a counterexample; produce one.
            return False, self.find_preferred_extension(telemetry=telemetry)
        ctl = self._new_control()
        permanently_unsat = {"flag": False}

        def add_refinement(out_set: frozenset[Literal]) -> bool:
            constraint = self._refinement_constraint(out_set)
            if constraint is None:
                permanently_unsat["flag"] = True
                return False
            # use a monotonically unique program-part name
            part = f"refine{add_refinement.counter}"  # type: ignore[attr-defined]
            add_refinement.counter += 1  # type: ignore[attr-defined]
            ctl.add(part, [], constraint)
            ctl.ground([(part, [])])
            if telemetry is not None:
                telemetry.refinement_clauses += 1
            return True

        add_refinement.counter = 0  # type: ignore[attr-defined]

        while True:
            # Line 2: find a complete set not deriving s.
            if telemetry is not None:
                telemetry.solver_calls += 1
                telemetry.outer_iterations += 1
            seed = self._solve_one(ctl, assumptions=[(query_symbol, False)])
            if seed is None:
                # all complete sets derive s -> skeptically accepted.
                return True, None
            # Lines 5-7: grow to a maximal complete set not deriving s.
            final_in = self._grow_to_maximal_not_deriving(
                ctl, seed, query_symbol, add_refinement=add_refinement, telemetry=telemetry
            )
            if permanently_unsat["flag"]:
                # the last constr(out(I)) was :- ; final_in = all assumptions and
                # it does not derive s (it was found via assumptions=[supported(s),
                # False]) -> it is a preferred set not deriving s -> counterexample.
                # But we must still confirm it is not dominated by a deriving
                # superset; with out(I) empty there is no proper superset at all,
                # so it is preferred.
                return False, final_in
            # Line 8: is there a complete set, proper superset of final_in, that
            # DOES derive s?  i.e. is  ctl ∪ in(final_in)  satisfiable (without the
            # supported(s) ban)?  The accumulated constr(out(I)) clauses rule out
            # final_in and its subsets, so any model is a *proper* superset; if it
            # also derives s, final_in is not preferred -> keep searching.
            in_assumptions = [(self._symbol_in(a), True) for a in sorted(final_in, key=repr)]
            if telemetry is not None:
                telemetry.solver_calls += 1
            superset_model = self._solve_one(ctl, assumptions=in_assumptions)
            if superset_model is None:
                # final_in is a preferred assumption set not deriving s -> NO.
                return False, final_in
            # otherwise final_in dominated; the constr(out(I)) banning final_in's
            # subsets is still in ctl; loop back to Line 2.

    def find_preferred_extension(self, *, telemetry: IncrementalTelemetry | None = None) -> AssumptionSet | None:
        extensions = self.enumerate_preferred(telemetry=telemetry, limit=1)
        return extensions[0] if extensions else None

    def enumerate_preferred(
        self, *, telemetry: IncrementalTelemetry | None = None, limit: int | None = None
    ) -> tuple[AssumptionSet, ...]:
        """Algorithm 4 (Appendix A): enumerate all preferred assumption sets.

        Same loop as Algorithm 1 with the query and Line 8 omitted: after the
        inner growth loop the candidate is preferred; collect it.
        """
        ctl = self._new_control()
        collected: list[AssumptionSet] = []
        permanently_unsat = {"flag": False}

        def add_refinement(out_set: frozenset[Literal]) -> bool:
            constraint = self._refinement_constraint(out_set)
            if constraint is None:
                permanently_unsat["flag"] = True
                return False
            part = f"refine{add_refinement.counter}"  # type: ignore[attr-defined]
            add_refinement.counter += 1  # type: ignore[attr-defined]
            ctl.add(part, [], constraint)
            ctl.ground([(part, [])])
            if telemetry is not None:
                telemetry.refinement_clauses += 1
            return True

        add_refinement.counter = 0  # type: ignore[attr-defined]

        while True:
            if telemetry is not None:
                telemetry.solver_calls += 1
                telemetry.outer_iterations += 1
            seed = self._solve_one(ctl)
            if seed is None:
                return _sorted_extensions(collected)
            final_in = self._grow_to_maximal_not_deriving(
                ctl, seed, None, add_refinement=add_refinement, telemetry=telemetry
            )
            collected.append(final_in)
            if limit is not None and len(collected) >= limit:
                return _sorted_extensions(collected)
            if permanently_unsat["flag"]:
                return _sorted_extensions(collected)

    # -- credulous helpers (NP queries) ------------------------------------

    def is_credulously_accepted_complete(self, query: Literal) -> tuple[bool, AssumptionSet | None]:
        query_symbol = self._symbol_supported(query)
        if query_symbol is None:
            return False, None
        ctl = self._new_control()
        witness = self._solve_one(ctl, assumptions=[(query_symbol, True)])
        if witness is None:
            return False, None
        return True, witness

    def is_credulously_accepted_stable(self, query: Literal) -> tuple[bool, AssumptionSet | None]:
        query_symbol = self._symbol_supported(query)
        if query_symbol is None:
            return False, None
        ctl = self._new_control(extra_program=":- out(X), not defeated(X).")
        witness = self._solve_one(ctl, assumptions=[(query_symbol, True)])
        if witness is None:
            return False, None
        return True, witness


def _sorted_extensions(extensions) -> tuple[AssumptionSet, ...]:
    unique = {frozenset(extension) for extension in extensions}
    return tuple(
        sorted(unique, key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))))
    )


__all__ = [
    "AbaIncrementalSolver",
    "IncrementalTelemetry",
    "SUPPORTED_SEMANTICS",
]
