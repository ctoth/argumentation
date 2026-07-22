"""Task-directed SAT solving for flat ABA stable and support semantics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any

from argumentation.core.optional_deps import OptionalDependencyUnavailable, load_z3
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet, _closure
from argumentation.structured.aba.aba_bitset_closure import _BitsetHornClosure
from argumentation.structured.aba.aba_support_model import (
    _SupportState,
    _minimal_supports,
)
from argumentation.structured.aba.aba_kernel import AssumptionKernel
from argumentation.structured.aba.aba_preprocessing import (
    _prepare_residual_requirements,
    _simplified_query_decision,
)
from argumentation.structured.aba.aba_route_policy import (
    SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
    native_cnf_prefsat_dense_shape,
)
from argumentation.structured.aspic.aspic import Literal, Rule


@dataclass(frozen=True)
class RealPrefSatResult:
    extension: AssumptionSet
    prefsat_in: dict[Literal, bool]
    prefsat_out: dict[Literal, bool]
    prefsat_undec: dict[Literal, bool]
    telemetry: dict[str, int]
    progress_events: tuple[dict[str, int], ...]
    route_metadata: dict[str, Any]


@dataclass(frozen=True)
class NativeSparseNarrowSatResult:
    extension: AssumptionSet | None
    telemetry: dict[str, int]
    route_metadata: dict[str, Any]


def _positive_solver_model(solver: Any) -> frozenset[int]:
    model = solver.get_model()
    if model is None:
        raise RuntimeError("SAT solver reported satisfiable without a model")
    return frozenset(literal for literal in model if literal > 0)


def _aba_simplification(framework: ABAFramework, semantics: str):
    """Lazily import to avoid a module import cycle (aba_preprocessing -> aba_sat)."""
    from argumentation.structured.aba.aba_preprocessing import simplify_aba

    return simplify_aba(framework, semantics=semantics)


def support_extensions(
    framework: ABAFramework,
    semantics: str,
) -> tuple[AssumptionSet, ...]:
    """Enumerate ABA extensions using precomputed derivation support masks."""
    state = _SupportState.from_framework(framework)
    if semantics == "stable":
        masks = [
            mask for mask in range(1 << len(state.assumptions)) if state.stable(mask)
        ]
    elif semantics == "complete":
        masks = [
            mask for mask in range(1 << len(state.assumptions)) if state.complete(mask)
        ]
    elif semantics == "preferred":
        admissible = [
            mask
            for mask in range(1 << len(state.assumptions))
            if state.admissible(mask)
        ]
        masks = [
            mask
            for mask in admissible
            if not any(
                mask != other and (mask | other) == other for other in admissible
            )
        ]
    else:
        raise ValueError(f"unsupported ABA support semantics: {semantics}")
    return tuple(
        sorted(
            (state.extension(mask) for mask in masks),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )


def real_prefsat_attack_edge_count(framework: ABAFramework) -> int:
    """Count singleton-closure attack edges without enumerating supports."""
    count = 0
    for source in framework.assumptions:
        closure = _closure(framework, frozenset({source}))
        count += sum(
            1
            for target in framework.assumptions
            if framework.contrary[target] in closure
        )
    return count


def real_prefsat_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> RealPrefSatResult:
    solver = _RealPrefSatSolver(framework)
    extension = solver.preferred_extension(require_assumptions=require_assumptions)
    return solver.result(extension)


def native_cnf_prefsat_extension(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> RealPrefSatResult:
    solver = _NativeCnfPrefSatSolver(framework)
    extension = solver.preferred_extension(require_assumptions=require_assumptions)
    return solver.result(extension)


# Strong CDCL engine for the flat one-shot stable solve. The Wave-2 experiment
# (experiments/2026-07-18-aba-cadical-engine-prod.md) measured direct CaDiCaL
# 2.2.1 winning ~23x on the c35 flat CNF. Gate D0 FAILED for pysat's bundled
# cadical195 (1.9.5 ran >300s vs the <=76s gate on the byte-identical CNF), so
# per the preregistration the strong engine is the vendored CaDiCaL 2.2.1
# binary driven as a batch DIMACS solver (scripts/build_cadical221.sh). If the
# binary is unavailable, _stable_extension_with_fallback rebuilds on glucose4 —
# a missing dependency can never lose a row.
_STABLE_ENGINE_STRONG = "cadical221-batch"

_CADICAL221_ENV = "ARGUMENTATION_CADICAL221"


def _find_cadical221_binary() -> Path:
    """Resolve the vendored CaDiCaL 2.2.1 batch binary.

    Order: explicit env override, then the repo-local vendored build produced
    by scripts/build_cadical221.sh. Raising here is safe: the flat stable path
    catches it and falls back to glucose4.
    """
    override = os.environ.get(_CADICAL221_ENV)
    if override:
        path = Path(override)
        if path.is_file():
            return path
        raise OptionalDependencyUnavailable(
            feature="flat-stable strong SAT engine",
            package=f"CaDiCaL 2.2.1 ({_CADICAL221_ENV}={override} not found)",
            install_hint="Run scripts/build_cadical221.sh or fix the env path.",
        )
    repo_root = Path(__file__).resolve().parents[4]
    vendored = repo_root / "tools" / "solvers" / "cadical-2.2.1" / "cadical.exe"
    if vendored.is_file():
        return vendored
    raise OptionalDependencyUnavailable(
        feature="flat-stable strong SAT engine",
        package="CaDiCaL 2.2.1 (vendored binary missing)",
        install_hint="Run scripts/build_cadical221.sh (see its header).",
    )


class _BatchDimacsCadical:
    """pysat-shaped adapter driving a CaDiCaL binary as a batch DIMACS solver.

    Supports exactly the surface `_NativeSparseNarrowStableSolver` uses:
    add_clause / set_phases / solve(assumptions=...) / get_model. Each solve
    writes base clauses plus assumption unit clauses to a temp DIMACS file and
    reruns the binary; the flat eager-arc stable path is effectively one-shot
    (cycle-refinement clauses are rare), which is the exact configuration the
    Wave-1 evidence measured. Phases are recorded but not passed: the measured
    2.2.1 win was in default (no-phase) mode.
    """

    def __init__(self, binary: Path) -> None:
        self._binary = binary
        self._clauses: list[list[int]] = []
        self._nvars = 0
        self._model: list[int] | None = None
        self.recorded_phases: list[int] | None = None

    def add_clause(self, clause: list[int]) -> None:
        for literal in clause:
            variable = abs(literal)
            if variable > self._nvars:
                self._nvars = variable
        self._clauses.append(list(clause))

    def set_phases(self, vector: list[int]) -> None:
        self.recorded_phases = list(vector)
        for literal in vector:
            variable = abs(literal)
            if variable > self._nvars:
                self._nvars = variable

    def solve(self, assumptions: list[int] | tuple[int, ...] = ()) -> bool:
        units = [[literal] for literal in assumptions]
        clauses = self._clauses + units
        with tempfile.TemporaryDirectory(prefix="cadical221-") as tmp:
            cnf_path = Path(tmp) / "problem.cnf"
            with cnf_path.open("w", encoding="ascii", newline="\n") as handle:
                handle.write(f"p cnf {self._nvars} {len(clauses)}\n")
                for clause in clauses:
                    handle.write(" ".join(str(x) for x in clause) + " 0\n")
            completed = subprocess.run(
                [str(self._binary), "-q", str(cnf_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        if completed.returncode == 10:
            model: list[int] = []
            for line in completed.stdout.splitlines():
                if line.startswith("v "):
                    model.extend(
                        int(tok) for tok in line[2:].split() if tok and tok != "0"
                    )
            if not model:
                raise RuntimeError("cadical221 reported SAT without v-lines")
            self._model = model
            return True
        if completed.returncode == 20:
            self._model = None
            return False
        raise RuntimeError(
            f"cadical221 batch solve failed (rc={completed.returncode}): "
            f"{completed.stderr.strip()[:200]}"
        )

    def get_model(self) -> list[int] | None:
        return self._model


# Provisional structural thresholds; frozen after the dev-slice calibration in
# the Wave-2 record. Routes only the giant recursive-core class (glucose4 times
# out) to the strong engine, keeping glucose4 for everything it already solves.
_STABLE_STRONG_MIN_RULES = 24000
_STABLE_STRONG_MIN_RECURSIVE_RULES = 300


def _stable_engine_for(
    *,
    recursive_rules: int,
    edges: int,
    assumptions: int,
    rules: int,
) -> str:
    """Pick the flat-stable SAT engine from measured structural features.

    Structural, never family-name based. Returns the strong engine only above a
    conservative threshold (the giant recursive core where glucose4 times out);
    otherwise the unchanged glucose4 default. The safety gate (no dev row solved
    by glucose4 but not by the routed build) validates the threshold.
    """
    if (
        rules >= _STABLE_STRONG_MIN_RULES
        or recursive_rules >= _STABLE_STRONG_MIN_RECURSIVE_RULES
    ):
        return _STABLE_ENGINE_STRONG
    return "glucose4"


def _stable_extension_with_fallback(
    framework: ABAFramework,
    *,
    require_assumptions: AssumptionSet,
) -> tuple[AssumptionSet | None, dict]:
    """Flat-stable build+solve with a no-row-loss glucose4 fallback.

    The structural predicate may route to the strong engine; if that engine
    fails to build or solve (bad binding, load error, crash surfaced as an
    exception), rebuild on glucose4 so an engine/dependency failure can never
    lose a row. A genuine engine-independent bug re-raises below (clause
    construction is identical for every engine) and is not masked.
    """
    try:
        solver = _NativeSparseNarrowStableSolver(framework, engine=None)
        extension = solver.stable_extension(require_assumptions=require_assumptions)
        return extension, dict(solver.telemetry)
    except Exception:
        pass
    fallback = _NativeSparseNarrowStableSolver(framework, engine="glucose4")
    extension = fallback.stable_extension(require_assumptions=require_assumptions)
    return extension, dict(fallback.telemetry)


def native_sparse_narrow_sat_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_assumptions: AssumptionSet = frozenset(),
) -> NativeSparseNarrowSatResult:
    if len(framework.assumptions) >= 700:
        stable_result = _native_sparse_narrow_stable_extension(
            framework,
            semantics,
            require_assumptions=require_assumptions,
        )
        if stable_result is not None:
            return stable_result
    if semantics == "preferred":
        result = native_cnf_prefsat_extension(
            framework,
            require_assumptions=require_assumptions,
        )
        telemetry = _native_sparse_narrow_telemetry(result.telemetry)
        return NativeSparseNarrowSatResult(
            extension=result.extension,
            telemetry=telemetry,
            route_metadata=_native_sparse_narrow_route_metadata("preferred", telemetry),
        )
    if semantics == "stable":
        extension, telemetry = _stable_extension_with_fallback(
            framework, require_assumptions=require_assumptions
        )
        return NativeSparseNarrowSatResult(
            extension=extension,
            telemetry=telemetry,
            route_metadata=_native_sparse_narrow_route_metadata("stable", telemetry),
        )
    raise ValueError(f"unsupported sparse/narrow native SAT semantics: {semantics}")


def should_use_native_cnf_prefsat(framework: ABAFramework) -> bool:
    assumption_count = len(framework.assumptions)
    return native_cnf_prefsat_dense_shape(
        is_flat=True,
        assumptions=assumption_count,
        rule_density=(len(framework.rules) / assumption_count)
        if assumption_count
        else 0.0,
    )


def support_acceptance(
    framework: ABAFramework,
    *,
    semantics: str,
    task: str,
    query: Literal,
) -> tuple[bool, AssumptionSet | None]:
    """Return a decision and witness/counterexample for exact ABA support solving."""
    state = _SupportState.from_framework(framework)
    extensions = support_extensions(framework, semantics)
    if task == "credulous":
        witness = next(
            (
                extension
                for extension in extensions
                if state.derives_extension(extension, query)
            ),
            None,
        )
        return witness is not None, witness
    if task == "skeptical":
        counterexample = next(
            (
                extension
                for extension in extensions
                if not state.derives_extension(extension, query)
            ),
            None,
        )
        return counterexample is None, counterexample
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def sat_support_acceptance(
    framework: ABAFramework,
    *,
    semantics: str,
    task: str,
    query: Literal,
    simplify: bool = True,
) -> tuple[bool, AssumptionSet | None]:
    """Return an ABA acceptance decision using support-aware SAT witnesses."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
    if simplify:
        simplification = _aba_simplification(framework, semantics)
        if not simplification.is_trivial:
            return _simplified_support_acceptance(
                simplification, semantics=semantics, task=task, query=query
            )
    if task == "credulous":
        witness = sat_support_extension(
            framework,
            semantics,
            require_derived=query,
        )
        return witness is not None, witness
    if task == "skeptical":
        if semantics == "preferred":
            counterexample = _sat_preferred_counterexample_not_deriving(
                framework, query
            )
            return counterexample is None, counterexample
        counterexample = sat_support_extension(
            framework,
            semantics,
            require_not_derived=query,
        )
        return counterexample is None, counterexample
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def _simplified_support_acceptance(
    simplification,
    *,
    semantics: str,
    task: str,
    query: Literal,
) -> tuple[bool, AssumptionSet | None]:
    if task not in {"credulous", "skeptical"}:
        raise ValueError(f"unsupported ABA acceptance task: {task}")
    residual = simplification.residual

    def _residual_witness() -> AssumptionSet | None:
        witness = sat_support_extension(residual, semantics, simplify=False)
        return None if witness is None else simplification.lift(witness)

    decision = _simplified_query_decision(simplification, query)
    if decision in {"fixed_in", "fixed_in_closure"}:
        if task == "credulous":
            return True, _residual_witness()
        return True, None
    if decision in {"fixed_out", "outside_residual"}:
        if task == "credulous":
            return False, None
        return False, _residual_witness()
    answer, witness = sat_support_acceptance(
        residual,
        semantics=semantics,
        task=task,
        query=query,
        simplify=False,
    )
    if witness is None:
        return answer, None
    return answer, simplification.lift(witness)


def sat_support_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
    require_assumptions: AssumptionSet = frozenset(),
    simplify: bool = True,
) -> AssumptionSet | None:
    """Return one complete/preferred ABA extension using support-aware SAT."""
    if semantics not in {"complete", "preferred"}:
        raise ValueError(f"unsupported ABA support SAT semantics: {semantics}")
    if (
        semantics == "preferred"
        and require_derived is None
        and require_not_derived is None
    ):
        stable_witness = sat_stable_extension(framework, simplify=False)
        if stable_witness is not None and require_assumptions <= stable_witness:
            return stable_witness
        if should_use_native_cnf_prefsat(framework):
            native_result = native_cnf_prefsat_extension(
                framework,
                require_assumptions=require_assumptions,
            )
            if require_assumptions <= native_result.extension:
                return native_result.extension
            return None
    if simplify and require_derived is None and require_not_derived is None:
        prepared = _prepare_residual_requirements(
            framework,
            semantics=semantics,
            require_assumptions=require_assumptions,
        )
        residual_required = prepared.projected_requirements
        if residual_required is None:
            return None
        if not prepared.is_trivial:
            witness = sat_support_extension(
                prepared.residual,
                semantics,
                require_assumptions=residual_required,
                simplify=False,
            )
            return None if witness is None else prepared.lift(witness)
    if require_derived is not None and require_derived not in framework.language:
        raise ValueError(
            f"required literal is not in framework language: {require_derived!r}"
        )
    if (
        require_not_derived is not None
        and require_not_derived not in framework.language
    ):
        raise ValueError(
            f"excluded literal is not in framework language: {require_not_derived!r}"
        )
    if (
        semantics == "preferred"
        and require_derived is None
        and require_not_derived is None
    ):
        from argumentation.structured.aba.aba_decomposition import (
            decomposed_prefsat_extension,
        )

        decomposed = decomposed_prefsat_extension(
            framework,
            require_assumptions=require_assumptions,
        )
        if decomposed.extension is None:
            return None
        if require_assumptions <= decomposed.extension:
            return decomposed.extension
        return None
    if semantics == "preferred" and (
        require_derived is not None or require_not_derived is not None
    ):
        return _sat_preferred_extension_satisfying(
            framework,
            require_derived=require_derived,
            require_not_derived=require_not_derived,
            require_assumptions=require_assumptions,
        )

    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    if semantics == "complete":
        _add_complete_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )
    for assumption in sorted(require_assumptions, key=repr):
        solver.add(variables[assumption])

    if semantics == "complete":
        if solver.check() != z3.sat:
            return None
        return _model_extension(z3, solver, variables)

    if solver.check() != z3.sat:
        return None
    current = _model_extension(z3, solver, variables)
    while True:
        outside = framework.assumptions - current
        if not outside:
            return current
        solver.push()
        try:
            for assumption in sorted(current, key=repr):
                solver.add(variables[assumption])
            solver.add(
                z3.Or(
                    *(variables[assumption] for assumption in sorted(outside, key=repr))
                )
            )
            if solver.check() != z3.sat:
                return current
            larger = _model_extension(z3, solver, variables)
        finally:
            solver.pop()
        if not current < larger:
            raise RuntimeError(
                "ABA preferred SAT growth did not produce a strict superset"
            )
        current = larger


def _sat_preferred_extension_satisfying(
    framework: ABAFramework,
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
    require_assumptions: AssumptionSet,
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )
    for assumption in sorted(require_assumptions, key=repr):
        solver.add(variables[assumption])

    while solver.check() == z3.sat:
        seed = _model_extension(z3, solver, variables)
        preferred = sat_support_extension(
            framework,
            "preferred",
            require_assumptions=seed,
        )
        if preferred is None:
            return None
        if _extension_satisfies_constraints(
            preferred,
            supports,
            require_derived=require_derived,
            require_not_derived=require_not_derived,
        ):
            return preferred
        outside = framework.assumptions - preferred
        if outside:
            solver.add(
                z3.Or(
                    *(variables[assumption] for assumption in sorted(outside, key=repr))
                )
            )
        else:
            solver.add(z3.BoolVal(False))
    return None


class _NativeCnfPrefSatSolver:
    def __init__(self, framework: ABAFramework) -> None:
        solver_class = _load_pysat_solver()
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self._next_var = 1
        self.in_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.out_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.undec_vars = {
            assumption: self._new_var() for assumption in self.assumptions
        }
        self.solver = solver_class(name="glucose4")
        self.telemetry = {
            "native_cnf_variables": self._next_var - 1,
            "native_cnf_clauses": 0,
            "native_cnf_solver_checks": 0,
            "native_cnf_candidate_models": 0,
            "native_cnf_candidate_blocks": 0,
            "native_cnf_z3_main_checks": 0,
            "native_cnf_closure_materializations": 0,
            "prefsat_labelling_variables": 3 * len(self.assumptions),
            "prefsat_exactly_one_clauses": 0,
            "prefsat_complete_clauses": 0,
            "prefsat_support_materializations": 0,
            "prefsat_solver_checks": 0,
            "prefsat_candidate_models": 0,
            "prefsat_candidate_blocks": 0,
            "prefsat_rejected_supersets": 0,
            "prefsat_max_in_count_seen": 0,
            "prefsat_final_in_count": 0,
            "prefsat_attacker_solver_builds": 0,
            "prefsat_attacker_solver_checks": 0,
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self.progress_events: list[dict[str, int]] = []
        self._attacker_closure = _BitsetHornClosure.from_framework(
            framework,
            self.telemetry,
        )
        self._contrary_bits = {
            assumption: self._attacker_closure.literal_bits[
                framework.contrary[assumption]
            ]
            for assumption in self.assumptions
        }
        self._empty_closure_mask = self._attacker_closure.closure_mask(frozenset())
        self._add_labelling_skeleton()
        self._add_static_conflict_clauses()
        self.solver.set_phases(
            [self.in_vars[assumption] for assumption in self.assumptions]
        )

    def _new_var(self) -> int:
        variable = self._next_var
        self._next_var += 1
        return variable

    def _add_clause(self, clause: list[int]) -> None:
        self.solver.add_clause(clause)
        self.telemetry["native_cnf_clauses"] += 1
        self.telemetry["prefsat_complete_clauses"] += 1

    def _add_labelling_skeleton(self) -> None:
        for assumption in self.assumptions:
            in_var = self.in_vars[assumption]
            out_var = self.out_vars[assumption]
            undec_var = self.undec_vars[assumption]
            self._add_clause([in_var, out_var, undec_var])
            self._add_clause([-in_var, -out_var])
            self._add_clause([-in_var, -undec_var])
            self._add_clause([-out_var, -undec_var])
            self.telemetry["prefsat_exactly_one_clauses"] += 1

    def _add_static_conflict_clauses(self) -> None:
        for target in self.assumptions:
            if self._empty_closure_mask & self._contrary_bits[target]:
                self._add_clause([-self.in_vars[target]])
        for source in self.assumptions:
            closure = self._closure_mask(frozenset({source}))
            for target in self.assumptions:
                if closure & self._contrary_bits[target]:
                    if source == target:
                        self._add_clause([-self.in_vars[target]])
                    else:
                        self._add_clause([-self.in_vars[source], -self.in_vars[target]])

    def preferred_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet:
        current = self._solve_admissible(require_in=require_assumptions)
        if current is None:
            self.telemetry["prefsat_final_in_count"] = 0
            return frozenset()
        while True:
            outside = self.framework.assumptions - current
            if not outside:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            larger = self._solve_admissible(require_in=current, require_any_in=outside)
            if larger is None:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            if not current < larger:
                raise RuntimeError(
                    "native CNF PrefSat grow step did not produce a strict superset"
                )
            self._record_progress()
            current = larger

    def _solve_admissible(
        self,
        *,
        require_in: AssumptionSet = frozenset(),
        require_any_in: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        assumptions = [
            self.in_vars[assumption] for assumption in sorted(require_in, key=repr)
        ]
        if require_any_in:
            guard = self._new_var()
            self.telemetry["native_cnf_variables"] = self._next_var - 1
            self._add_clause(
                [
                    *(
                        self.in_vars[assumption]
                        for assumption in sorted(require_any_in, key=repr)
                    ),
                    -guard,
                ]
            )
            assumptions.append(guard)
        while True:
            self.telemetry["native_cnf_solver_checks"] += 1
            self.telemetry["prefsat_solver_checks"] += 1
            if not self.solver.solve(assumptions=assumptions):
                self._record_progress()
                return None
            self.telemetry["native_cnf_candidate_models"] += 1
            self.telemetry["prefsat_candidate_models"] += 1
            candidate = self._model_extension()
            closure = self._closure_mask(candidate)
            self.telemetry["prefsat_max_in_count_seen"] = max(
                self.telemetry["prefsat_max_in_count_seen"],
                len(candidate),
            )
            refinement = self._semantic_refinement(candidate, closure)
            if refinement is None:
                self._record_progress()
                return candidate
            self._add_clause(refinement)
            self.telemetry["native_cnf_candidate_blocks"] += 1
            self.telemetry["prefsat_candidate_blocks"] += 1
            self.telemetry["prefsat_rejected_supersets"] += 1
            self._record_progress()

    def _semantic_refinement(
        self,
        candidate: AssumptionSet,
        closure: int,
    ) -> list[int] | None:
        for target in sorted(candidate, key=repr):
            if closure & self._contrary_bits[target]:
                contrary = self.framework.contrary[target]
                attack_support = self._attacker_closure.shrink_support(
                    candidate, contrary
                )
                return [
                    -self.in_vars[target],
                    *(
                        -self.in_vars[assumption]
                        for assumption in sorted(attack_support - {target}, key=repr)
                    ),
                ]
        counterexample = self._attacker_counterexample(candidate, closure)
        if counterexample is None:
            return None
        target, attack_support = counterexample
        if not attack_support:
            return [-self.in_vars[target]]
        outside_candidate = self.framework.assumptions - candidate
        if outside_candidate:
            return [
                -self.in_vars[target],
                *(
                    self.in_vars[assumption]
                    for assumption in sorted(outside_candidate, key=repr)
                ),
            ]
        return [-self.in_vars[target]]

    def _attacker_counterexample(
        self,
        candidate: AssumptionSet,
        closure: int,
    ) -> tuple[Literal, AssumptionSet] | None:
        if not candidate:
            return None
        counterattacked = frozenset(
            assumption
            for assumption in self.assumptions
            if closure & self._contrary_bits[assumption]
        )
        available = self.framework.assumptions - counterattacked
        attacker_closure = self._attacker_closure.closure_mask(available)
        for target in sorted(candidate, key=repr):
            contrary_bit = self._contrary_bits[target]
            if attacker_closure & contrary_bit:
                if self._empty_closure_mask & contrary_bit:
                    return target, frozenset()
                return target, available
        return None

    def _model_extension(self) -> AssumptionSet:
        model = _positive_solver_model(self.solver)
        return frozenset(
            assumption
            for assumption, variable in self.in_vars.items()
            if variable in model
        )

    def _closure_mask(self, extension: AssumptionSet) -> int:
        return self._attacker_closure.closure_mask(extension)

    def _closure(self, extension: AssumptionSet) -> frozenset[Literal]:
        self.telemetry["native_cnf_closure_materializations"] += 1
        closure = self._closure_mask(extension)
        return frozenset(
            literal
            for literal, bit in self._attacker_closure.literal_bits.items()
            if closure & bit
        )

    def _record_progress(self) -> None:
        event = {
            "prefsat_max_in_count_seen": self.telemetry["prefsat_max_in_count_seen"],
            "prefsat_candidate_blocks": self.telemetry["prefsat_candidate_blocks"],
        }
        if not self.progress_events or self.progress_events[-1] != event:
            self.progress_events.append(event)

    def result(self, extension: AssumptionSet) -> RealPrefSatResult:
        closure = _closure(self.framework, extension)
        prefsat_in = {
            assumption: assumption in extension for assumption in self.assumptions
        }
        prefsat_out = {
            assumption: self.framework.contrary[assumption] in closure
            for assumption in self.assumptions
        }
        prefsat_undec = {
            assumption: not prefsat_in[assumption] and not prefsat_out[assumption]
            for assumption in self.assumptions
        }
        return RealPrefSatResult(
            extension=extension,
            prefsat_in=prefsat_in,
            prefsat_out=prefsat_out,
            prefsat_undec=prefsat_undec,
            telemetry=dict(self.telemetry),
            progress_events=tuple(self.progress_events),
            route_metadata={
                "backend": "sat",
                "algorithm": "native-cnf-prefsat",
                "rejected_substitutes": (
                    "z3-main-complete-labelling",
                    "asp-optimization",
                    "greedy-growth",
                ),
            },
        )


def _iterative_tarjan_scc(adjacency: list[list[int]]) -> list[int]:
    """Tarjan SCC indices for an adjacency-list digraph, without recursion."""
    node_count = len(adjacency)
    indices = [-1] * node_count
    lowlink = [0] * node_count
    on_stack = [False] * node_count
    scc_index = [-1] * node_count
    stack: list[int] = []
    counter = 0
    scc_count = 0
    for root in range(node_count):
        if indices[root] != -1:
            continue
        work: list[tuple[int, int]] = [(root, 0)]
        while work:
            node, next_child = work.pop()
            if next_child == 0:
                indices[node] = counter
                lowlink[node] = counter
                counter += 1
                stack.append(node)
                on_stack[node] = True
            descended = False
            successors = adjacency[node]
            for position in range(next_child, len(successors)):
                successor = successors[position]
                if indices[successor] == -1:
                    work.append((node, position + 1))
                    work.append((successor, 0))
                    descended = True
                    break
                if on_stack[successor]:
                    lowlink[node] = min(lowlink[node], indices[successor])
            if descended:
                continue
            if lowlink[node] == indices[node]:
                while True:
                    member = stack.pop()
                    on_stack[member] = False
                    scc_index[member] = scc_count
                    if member == node:
                        break
                scc_count += 1
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
    return scc_index


_EAGER_CYCLE_CLAUSE_CAP = 20000
_EAGER_CYCLE_STEP_CAP = 2000000


def _enumerate_elementary_edge_cycles(
    edges: list[tuple[Literal, Literal]],
    *,
    cycle_cap: int = _EAGER_CYCLE_CLAUSE_CAP,
    step_cap: int = _EAGER_CYCLE_STEP_CAP,
) -> list[tuple[tuple[Literal, Literal], ...]] | None:
    """All elementary cycles of the edge digraph, or None if a cap trips.

    Deterministic root-ordered DFS (roots and successors ordered by repr);
    each cycle is reported once, rooted at its repr-least node. The step cap
    bounds worst-case exploration so pathological graphs fall back to the
    lazy cycle CEGAR instead of stalling the encoder.
    """
    adjacency: dict[Literal, list[Literal]] = defaultdict(list)
    nodes: set[Literal] = set()
    for source, target in edges:
        adjacency[source].append(target)
        nodes.update((source, target))
    for targets in adjacency.values():
        targets.sort(key=repr)
    rank = {node: index for index, node in enumerate(sorted(nodes, key=repr))}

    cycles: list[tuple[tuple[Literal, Literal], ...]] = []
    steps = 0
    for root in sorted(nodes, key=repr):
        path = [root]
        on_path = {root}
        pending = [iter(adjacency.get(root, ()))]
        while pending:
            successor = next(pending[-1], None)
            if successor is None:
                on_path.discard(path.pop())
                pending.pop()
                continue
            steps += 1
            if steps > step_cap:
                return None
            if rank[successor] < rank[root]:
                continue
            if successor == root:
                cycle_nodes = [*path, root]
                cycles.append(tuple(zip(cycle_nodes, cycle_nodes[1:])))
                if len(cycles) > cycle_cap:
                    return None
                continue
            if successor in on_path:
                continue
            path.append(successor)
            on_path.add(successor)
            pending.append(iter(adjacency.get(successor, ())))
    return cycles


def _first_directed_edge_cycle(
    edges: list[tuple[Literal, Literal]],
) -> tuple[tuple[Literal, Literal], ...] | None:
    """First directed cycle among the given edges, as a tuple of edges."""
    adjacency: dict[Literal, list[Literal]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)
    for targets in adjacency.values():
        targets.sort(key=repr)

    state: dict[Literal, int] = {}
    for root in sorted(adjacency, key=repr):
        if state.get(root):
            continue
        state[root] = 1
        path = [root]
        pending = [iter(adjacency[root])]
        while path:
            successor = next(pending[-1], None)
            if successor is None:
                state[path.pop()] = 2
                pending.pop()
                continue
            successor_state = state.get(successor, 0)
            if successor_state == 2:
                continue
            if successor_state == 1:
                cycle_nodes = path[path.index(successor) :] + [successor]
                return tuple(zip(cycle_nodes, cycle_nodes[1:]))
            state[successor] = 1
            path.append(successor)
            pending.append(iter(adjacency.get(successor, ())))
    return None


class _NativeSparseNarrowStableSolver:
    def __init__(self, framework: ABAFramework, *, engine: str | None = None) -> None:
        solver_class = _load_pysat_solver()
        self._engine_arg = engine
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self.literals = tuple(
            sorted(
                set(framework.language)
                | set(framework.assumptions)
                | set(framework.contrary.values())
                | {rule.consequent for rule in framework.rules}
                | {
                    antecedent
                    for rule in framework.rules
                    for antecedent in rule.antecedents
                },
                key=repr,
            )
        )
        self._next_var = 1
        self.in_vars = {assumption: self._new_var() for assumption in self.assumptions}
        self.derived_vars = {literal: self._new_var() for literal in self.literals}
        self.rules = tuple(sorted(framework.rules, key=repr))
        self.support_vars = {
            rule: self._new_var() for rule in self.rules if rule.antecedents
        }
        self.telemetry = {
            "clingo_solver_calls": 0,
            "native_sparse_narrow_solver_checks": 0,
            "native_sparse_narrow_candidate_models": 0,
            "native_sparse_narrow_learned_clauses": 0,
            "native_sparse_narrow_z3_main_checks": 0,
            "native_sparse_narrow_closure_checks": 0,
            "native_sparse_narrow_rule_firings": 0,
            "native_sparse_narrow_loop_formulas": 0,
            "native_sparse_narrow_acyc_recursive_rules": 0,
            "native_sparse_narrow_acyc_edges": 0,
            "native_sparse_narrow_acyc_eager_cycle_clauses": 0,
            "native_sparse_narrow_edge_cycle_clauses": 0,
            "native_sparse_narrow_solve_times_ms": [],
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self._closure = _BitsetHornClosure.from_framework(framework, self.telemetry)
        self._literal_by_bit = {
            bit: literal for literal, bit in self._closure.literal_bits.items()
        }
        self._zero_rule_heads = frozenset(
            rule.consequent for rule in self.rules if not rule.antecedents
        )
        self._internal_atoms_by_rule = self._build_arc_shape()
        self.just_vars = {
            rule: self._new_var()
            for rule in sorted(self._internal_atoms_by_rule, key=repr)
        }
        self.edge_vars = {
            edge: self._new_var()
            for edge in sorted(
                {
                    (atom, rule.consequent)
                    for rule, atoms in self._internal_atoms_by_rule.items()
                    for atom in atoms
                },
                key=repr,
            )
        }
        self.telemetry["native_sparse_narrow_acyc_recursive_rules"] = len(
            self.just_vars
        )
        self.telemetry["native_sparse_narrow_acyc_edges"] = len(self.edge_vars)
        self.engine = (
            engine
            if engine is not None
            else _stable_engine_for(
                recursive_rules=len(self.just_vars),
                edges=len(self.edge_vars),
                assumptions=len(self.assumptions),
                rules=len(self.rules),
            )
        )
        self.telemetry["native_sparse_narrow_engine"] = self.engine
        if self.engine == "cadical221-batch":
            self.solver: Any = _BatchDimacsCadical(_find_cadical221_binary())
        else:
            self.solver = solver_class(name=self.engine)
        self._completion_options_by_head: dict[Literal, list[int]] = defaultdict(list)
        for rule, variable in self.support_vars.items():
            self._completion_options_by_head[rule.consequent].append(
                self.just_vars.get(rule, variable)
            )
        self._add_completion_clauses()
        self._add_arc_acyclic_clauses()
        self.phase_vector = [
            self.in_vars[assumption] for assumption in self.assumptions
        ] + [-variable for variable in self.edge_vars.values()]
        self.solver.set_phases(self.phase_vector)

    def _new_var(self) -> int:
        variable = self._next_var
        self._next_var += 1
        return variable

    def _add_clause(self, clause: list[int]) -> None:
        self.solver.add_clause(clause)
        self.telemetry["native_sparse_narrow_learned_clauses"] += 1

    def _add_completion_clauses(self) -> None:
        for assumption in self.assumptions:
            self._add_clause(
                [
                    -self.in_vars[assumption],
                    self.derived_vars[assumption],
                ]
            )
        for rule in self.rules:
            head = self.derived_vars[rule.consequent]
            body = [self.derived_vars[antecedent] for antecedent in rule.antecedents]
            if not body:
                self._add_clause([head])
                continue
            support = self.support_vars[rule]
            for variable in body:
                self._add_clause([-support, variable])
            self._add_clause([*[-variable for variable in body], support])
            self._add_clause([-support, head])
            self._add_clause([*[-variable for variable in body], head])
        for literal in self.literals:
            if literal in self._zero_rule_heads:
                continue
            support_options = list(self._completion_options_by_head.get(literal, ()))
            if literal in self.in_vars:
                support_options.append(self.in_vars[literal])
            if support_options:
                self._add_clause(
                    [
                        -self.derived_vars[literal],
                        *support_options,
                    ]
                )
            else:
                self._add_clause([-self.derived_vars[literal]])
        for assumption in self.assumptions:
            contrary = self.derived_vars[self.framework.contrary[assumption]]
            selected = self.in_vars[assumption]
            self._add_clause([-selected, -contrary])
            self._add_clause([selected, contrary])

    def _build_arc_shape(self) -> dict[Rule, tuple[Literal, ...]]:
        """Map each recursive rule to its body atoms inside the head's SCC.

        A rule is recursive iff its body node shares an SCC with its head in
        the bipartite atom/body dependency graph; only such rules can take
        part in unfounded (cyclic) self-support, so only they need the
        arc-justification machinery (see
        experiments/2026-07-09-abcgen-arc-acyc.md for the derivation).
        """
        literal_index = {literal: index for index, literal in enumerate(self.literals)}
        body_rules = [rule for rule in self.rules if rule.antecedents]
        adjacency: list[list[int]] = [
            [] for _ in range(len(self.literals) + len(body_rules))
        ]
        for offset, rule in enumerate(body_rules):
            body_node = len(self.literals) + offset
            adjacency[body_node].append(literal_index[rule.consequent])
            for antecedent in rule.antecedents:
                adjacency[literal_index[antecedent]].append(body_node)
        scc_index = _iterative_tarjan_scc(adjacency)
        internal_atoms_by_rule: dict[Rule, tuple[Literal, ...]] = {}
        for offset, rule in enumerate(body_rules):
            head_scc = scc_index[literal_index[rule.consequent]]
            if scc_index[len(self.literals) + offset] != head_scc:
                continue
            internal_atoms_by_rule[rule] = tuple(
                sorted(
                    (
                        antecedent
                        for antecedent in rule.antecedents
                        if scc_index[literal_index[antecedent]] == head_scc
                    ),
                    key=repr,
                )
            )
        return internal_atoms_by_rule

    def _add_arc_acyclic_clauses(self) -> None:
        demanding_rules: dict[tuple[Literal, Literal], list[int]] = defaultdict(list)
        for rule, internal_atoms in sorted(
            self._internal_atoms_by_rule.items(), key=lambda item: repr(item[0])
        ):
            just = self.just_vars[rule]
            support = self.support_vars[rule]
            edge_variables = [
                self.edge_vars[(atom, rule.consequent)] for atom in internal_atoms
            ]
            self._add_clause([-just, support])
            for edge_variable in edge_variables:
                self._add_clause([-just, edge_variable])
            self._add_clause(
                [just, -support, *[-variable for variable in edge_variables]]
            )
            for atom in internal_atoms:
                demanding_rules[(atom, rule.consequent)].append(just)
        for edge, variable in self.edge_vars.items():
            self._add_clause([-variable, *demanding_rules[edge]])
        cycles = _enumerate_elementary_edge_cycles(list(self.edge_vars))
        if cycles is not None:
            for cycle in cycles:
                self._add_clause([-self.edge_vars[edge] for edge in cycle])
            self.telemetry["native_sparse_narrow_acyc_eager_cycle_clauses"] = len(
                cycles
            )
            return
        # Cap tripped: block 2-cycles eagerly, longer cycles lazily in the
        # solve loop's edge-cycle CEGAR.
        self.telemetry["native_sparse_narrow_acyc_eager_cycle_clauses"] = -1
        for edge, variable in self.edge_vars.items():
            source, target = edge
            reciprocal = self.edge_vars.get((target, source))
            if reciprocal is not None and repr(source) < repr(target):
                self._add_clause([-variable, -reciprocal])

    def stable_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        assumptions = [
            self.in_vars[assumption]
            for assumption in sorted(require_assumptions, key=repr)
        ]
        while True:
            self.telemetry["native_sparse_narrow_solver_checks"] += 1
            started = time.perf_counter()
            solved = self.solver.solve(assumptions=assumptions)
            elapsed_ms = int(round((time.perf_counter() - started) * 1000))
            self.telemetry["native_sparse_narrow_solve_times_ms"].append(elapsed_ms)
            if not solved:
                return None
            self.telemetry["native_sparse_narrow_candidate_models"] += 1
            cycle = self._selected_edge_cycle()
            if cycle is None:
                extension = self._model_extension()
                self._verify_founded_model(extension)
                self._sync_closure_telemetry()
                return extension
            self._add_clause([-self.edge_vars[edge] for edge in cycle])
            self.telemetry["native_sparse_narrow_edge_cycle_clauses"] += 1
            self._sync_closure_telemetry()

    def _selected_edge_cycle(self) -> tuple[tuple[Literal, Literal], ...] | None:
        model = _positive_solver_model(self.solver)
        selected = [
            edge for edge, variable in self.edge_vars.items() if variable in model
        ]
        return _first_directed_edge_cycle(selected)

    def _verify_founded_model(self, extension: AssumptionSet) -> None:
        """Raise if the model derives anything outside the true Horn closure.

        The derivation in experiments/2026-07-09-abcgen-arc-acyc.md proves
        this cannot happen once the selected edges are acyclic; a failure
        here is an encoding bug, never a legitimate answer.
        """
        closure = self._closure.closure_mask(extension)
        model = _positive_solver_model(self.solver)
        derived = 0
        for literal, variable in self.derived_vars.items():
            if variable in model:
                derived |= self._closure.literal_bits[literal]
        unsupported = derived & ~closure
        if unsupported:
            unfounded = sorted(
                (repr(self._literal_by_bit[bit]) for bit in self._bits(unsupported)),
            )
            raise RuntimeError(
                "arc-acyclic stable encoding produced an unfounded model: "
                + ", ".join(unfounded)
            )

    def _bits(self, mask: int) -> list[int]:
        bits: list[int] = []
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            bits.append(bit)
            remaining ^= bit
        return bits

    def _model_extension(self) -> AssumptionSet:
        model = _positive_solver_model(self.solver)
        return frozenset(
            assumption
            for assumption, variable in self.in_vars.items()
            if variable in model
        )

    def _sync_closure_telemetry(self) -> None:
        self.telemetry["native_sparse_narrow_closure_checks"] = self.telemetry[
            "prefsat_attacker_bitset_closure_checks"
        ]
        self.telemetry["native_sparse_narrow_rule_firings"] = self.telemetry[
            "prefsat_attacker_bitset_rule_firings"
        ]


def _native_sparse_narrow_telemetry(telemetry: dict[str, int]) -> dict[str, int]:
    return {
        **telemetry,
        "clingo_solver_calls": 0,
        "native_sparse_narrow_solver_checks": telemetry.get(
            "native_cnf_solver_checks", 0
        ),
        "native_sparse_narrow_candidate_models": telemetry.get(
            "native_cnf_candidate_models", 0
        ),
        "native_sparse_narrow_learned_clauses": telemetry.get(
            "native_cnf_candidate_blocks", 0
        ),
        "native_sparse_narrow_z3_main_checks": telemetry.get(
            "native_cnf_z3_main_checks", 0
        ),
        "native_sparse_narrow_closure_checks": telemetry.get(
            "prefsat_attacker_bitset_closure_checks",
            0,
        ),
        "native_sparse_narrow_rule_firings": telemetry.get(
            "prefsat_attacker_bitset_rule_firings",
            0,
        ),
    }


def _native_sparse_narrow_route_metadata(
    semantics: str,
    telemetry: dict[str, int],
) -> dict[str, Any]:
    return {
        "backend": "sat",
        "algorithm": "native_sparse_narrow_sat",
        "semantics": semantics,
        "clingo_solver_calls": telemetry.get("clingo_solver_calls", 0),
        "paper_page_images": SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
    }


def _native_sparse_narrow_stable_extension(
    framework: ABAFramework,
    semantics: str,
    *,
    require_assumptions: AssumptionSet,
) -> NativeSparseNarrowSatResult | None:
    if semantics not in {"preferred", "stable"}:
        return None
    extension, telemetry = _stable_extension_with_fallback(
        framework, require_assumptions=require_assumptions
    )
    if extension is None:
        return None
    return NativeSparseNarrowSatResult(
        extension=extension,
        telemetry=telemetry,
        route_metadata=_native_sparse_narrow_route_metadata(semantics, telemetry)
        | {"algorithm_detail": "monotone_cegar_stable_witness"},
    )


class _RealPrefSatSolver:
    def __init__(self, framework: ABAFramework) -> None:
        self.z3 = _load_z3()
        self.framework = framework
        self.assumptions = tuple(sorted(framework.assumptions, key=repr))
        self.literals = tuple(sorted(framework.language, key=repr))
        self.solver = self.z3.Solver()
        self.prefsat_in = {
            assumption: self.z3.Bool(f"prefsat_in_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.prefsat_out = {
            assumption: self.z3.Bool(f"prefsat_out_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.prefsat_undec = {
            assumption: self.z3.Bool(f"prefsat_undec_{_literal_key(assumption)}")
            for assumption in self.assumptions
        }
        self.telemetry = {
            "prefsat_labelling_variables": 3 * len(self.assumptions),
            "prefsat_exactly_one_clauses": 0,
            "prefsat_complete_clauses": 0,
            "prefsat_support_materializations": 0,
            "prefsat_solver_checks": 0,
            "prefsat_candidate_models": 0,
            "prefsat_candidate_blocks": 0,
            "prefsat_rejected_supersets": 0,
            "prefsat_max_in_count_seen": 0,
            "prefsat_final_in_count": 0,
            "prefsat_attacker_solver_builds": 0,
            "prefsat_attacker_solver_checks": 0,
            "prefsat_attacker_bitset_closure_checks": 0,
            "prefsat_attacker_bitset_shrink_checks": 0,
            "prefsat_attacker_bitset_rule_firings": 0,
        }
        self.progress_events: list[dict[str, int]] = []
        self._pending_refinements: list = []
        self._attacker_closure = _BitsetHornClosure.from_framework(
            framework,
            self.telemetry,
        )
        self.derived = self._add_closure_constraints(
            "prefsat", self.solver, self.prefsat_in
        )
        self._add_labelling_constraints()

    def _add_closure_constraints(self, prefix: str, solver, variables):
        derived, clause_count = _prefsat_add_closure_constraints(
            self.z3,
            solver,
            self.framework,
            variables,
            prefix=prefix,
        )
        self.telemetry["prefsat_complete_clauses"] += clause_count
        return derived

    def _add_labelling_constraints(self) -> None:
        z3 = self.z3
        for assumption in self.assumptions:
            in_var = self.prefsat_in[assumption]
            out_var = self.prefsat_out[assumption]
            undec_var = self.prefsat_undec[assumption]
            attacked_by_in = self.derived[self.framework.contrary[assumption]]
            self.solver.add(z3.Or(in_var, out_var, undec_var))
            self.solver.add(z3.AtMost(in_var, out_var, undec_var, 1))
            self.solver.add(out_var == attacked_by_in)
            self.solver.add(undec_var == z3.And(z3.Not(in_var), z3.Not(out_var)))
            self.solver.add(z3.Implies(in_var, z3.Not(attacked_by_in)))
            self.telemetry["prefsat_exactly_one_clauses"] += 1
            self.telemetry["prefsat_complete_clauses"] += 4

    def preferred_extension(
        self,
        *,
        require_assumptions: AssumptionSet = frozenset(),
    ) -> AssumptionSet:
        current = self._solve_admissible(require_in=require_assumptions)
        if current is None:
            self.telemetry["prefsat_final_in_count"] = 0
            return frozenset()
        while True:
            outside = self.framework.assumptions - current
            if not outside:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            larger = self._solve_admissible(require_in=current, require_any_in=outside)
            if larger is None:
                self.telemetry["prefsat_final_in_count"] = len(current)
                return current
            if not current < larger:
                raise RuntimeError(
                    "real ABA PrefSat grow step did not produce a strict superset"
                )
            self.telemetry["prefsat_candidate_blocks"] += 1
            self._record_progress()
            current = larger

    def _solve_admissible(
        self,
        *,
        require_in: AssumptionSet = frozenset(),
        require_any_in: AssumptionSet = frozenset(),
    ) -> AssumptionSet | None:
        z3 = self.z3
        self.solver.push()
        try:
            for clause in self._pending_refinements:
                self.solver.add(clause)
            for assumption in sorted(require_in, key=repr):
                self.solver.add(self.prefsat_in[assumption])
            if require_any_in:
                self.solver.add(
                    z3.Or(
                        *(
                            self.prefsat_in[assumption]
                            for assumption in sorted(require_any_in, key=repr)
                        )
                    )
                )
            while True:
                self.telemetry["prefsat_solver_checks"] += 1
                if self.solver.check() != z3.sat:
                    self._record_progress()
                    return None
                self.telemetry["prefsat_candidate_models"] += 1
                candidate = self._model_extension()
                closure = self._model_closure()
                self.telemetry["prefsat_max_in_count_seen"] = max(
                    self.telemetry["prefsat_max_in_count_seen"],
                    len(candidate),
                )
                counterexample = self._attacker_counterexample(candidate, closure)
                if counterexample is None:
                    self._record_progress()
                    return candidate
                clause = self._defense_refinement_clause(counterexample)
                self._pending_refinements.append(clause)
                self.solver.add(clause)
                self.telemetry["prefsat_candidate_blocks"] += 1
                self.telemetry["prefsat_rejected_supersets"] += 1
                self._record_progress()
        finally:
            self.solver.pop()

    def _attacker_counterexample(
        self,
        candidate: AssumptionSet,
        closure: frozenset[Literal],
    ) -> tuple[Literal, AssumptionSet] | None:
        if not candidate:
            return None
        counterattacked = frozenset(
            assumption
            for assumption in self.assumptions
            if self.framework.contrary[assumption] in closure
        )
        available = self.framework.assumptions - counterattacked
        attacker_closure = self._attacker_closure.closure_mask(available)
        for target in sorted(candidate, key=repr):
            conclusion = self.framework.contrary[target]
            if self._attacker_closure.contains(attacker_closure, conclusion):
                return target, self._attacker_closure.shrink_support(
                    available, conclusion
                )
        return None

    def _defense_refinement_clause(self, counterexample):
        target, attack_support = counterexample
        if not attack_support:
            return self.z3.Not(self.prefsat_in[target])
        return self.z3.Or(
            self.z3.Not(self.prefsat_in[target]),
            *(
                self.derived[self.framework.contrary[attacker]]
                for attacker in sorted(attack_support, key=repr)
            ),
        )

    def _model_extension(self) -> AssumptionSet:
        model = self.solver.model()
        z3 = self.z3
        return frozenset(
            assumption
            for assumption, variable in self.prefsat_in.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def _model_closure(self) -> frozenset[Literal]:
        model = self.solver.model()
        z3 = self.z3
        return frozenset(
            literal
            for literal, variable in self.derived.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def _record_progress(self) -> None:
        event = {
            "prefsat_max_in_count_seen": self.telemetry["prefsat_max_in_count_seen"],
            "prefsat_candidate_blocks": self.telemetry["prefsat_candidate_blocks"],
        }
        if not self.progress_events or self.progress_events[-1] != event:
            self.progress_events.append(event)

    def result(self, extension: AssumptionSet) -> RealPrefSatResult:
        closure = _closure(self.framework, extension)
        prefsat_in = {
            assumption: assumption in extension for assumption in self.assumptions
        }
        prefsat_out = {
            assumption: self.framework.contrary[assumption] in closure
            for assumption in self.assumptions
        }
        prefsat_undec = {
            assumption: not prefsat_in[assumption] and not prefsat_out[assumption]
            for assumption in self.assumptions
        }
        return RealPrefSatResult(
            extension=extension,
            prefsat_in=prefsat_in,
            prefsat_out=prefsat_out,
            prefsat_undec=prefsat_undec,
            telemetry=dict(self.telemetry),
            progress_events=tuple(self.progress_events),
            route_metadata={
                "backend": "sat",
                "algorithm": "complete-labelling-prefsat",
                "rejected_substitutes": (
                    "old-support-aware-cegar",
                    "asp-optimization",
                    "greedy-growth",
                ),
            },
        )


def sat_stable_extension(
    framework: ABAFramework,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
    simplify: bool = True,
) -> AssumptionSet | None:
    """Return one stable assumption set satisfying optional query constraints."""
    del simplify
    return _sat_ranked_stable_extension(
        framework,
        require_derived=require_derived,
        require_not_derived=require_not_derived,
    )


def _sat_ranked_stable_extension(
    framework: ABAFramework,
    *,
    require_derived: Literal | None = None,
    require_not_derived: Literal | None = None,
) -> AssumptionSet | None:
    if require_derived is not None and require_derived not in framework.language:
        raise ValueError(
            f"required literal is not in framework language: {require_derived!r}"
        )
    if (
        require_not_derived is not None
        and require_not_derived not in framework.language
    ):
        raise ValueError(
            f"excluded literal is not in framework language: {require_not_derived!r}"
        )
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    solver = z3.Solver()
    derived = _add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption in sorted(framework.assumptions, key=repr):
        contrary = derived[framework.contrary[assumption]]
        solver.add(z3.Implies(variables[assumption], z3.Not(contrary)))
        solver.add(z3.Or(variables[assumption], contrary))
    if require_derived is not None:
        solver.add(derived[require_derived])
    if require_not_derived is not None:
        solver.add(z3.Not(derived[require_not_derived]))
    if solver.check() != z3.sat:
        return None
    return _model_extension(z3, solver, variables)


def sat_stable_acceptance(
    framework: ABAFramework,
    *,
    task: str,
    query: Literal,
    simplify: bool = True,
) -> tuple[bool, AssumptionSet | None]:
    """Return an ABA stable acceptance decision (with optional preprocessing)."""
    if task not in {"credulous", "skeptical"}:
        raise ValueError(f"unsupported ABA acceptance task: {task}")
    del simplify
    if task == "credulous":
        witness = sat_stable_extension(framework, require_derived=query, simplify=False)
        return witness is not None, witness
    counterexample = sat_stable_extension(
        framework, require_not_derived=query, simplify=False
    )
    return counterexample is None, counterexample


def _emit_ranked_closure_constraints(
    z3,
    solver,
    framework,
    variables,
    *,
    derived_prefix: str,
    rank_prefix: str,
):
    """Emit the shared Int ranked-closure Z3 constraints.

    The plain and prefsat encoders differ only in the variable-name prefixes
    used for the ``derived`` Bools and Int ``rank`` vars. This helper is the
    single source for the constraint structure; it always returns the
    ``derived`` map alongside the number of emitted clauses, and each caller
    keeps or discards the tally to preserve its own return contract.
    """
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    derived = {
        literal: z3.Bool(f"{derived_prefix}{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.Int(f"{rank_prefix}{_literal_key(literal)}") for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)
    clause_count = 0

    for literal in literals:
        solver.add(ranks[literal] >= 0, ranks[literal] <= rank_bound)
        clause_count += 1

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == 0))
        clause_count += 2

    for rule in sorted(framework.rules, key=repr):
        antecedents = tuple(rule.antecedents)
        if not antecedents:
            solver.add(derived[rule.consequent])
        else:
            solver.add(
                z3.Implies(
                    z3.And(*(derived[antecedent] for antecedent in antecedents)),
                    derived[rule.consequent],
                )
            )
        clause_count += 1

    for literal in literals:
        if literal in framework.assumptions:
            continue
        support_terms = []
        for rule in rules_by_consequent[literal]:
            antecedents = tuple(rule.antecedents)
            if not antecedents:
                support_terms.append(z3.BoolVal(True))
                continue
            support_terms.append(
                z3.And(
                    *(
                        z3.And(
                            derived[antecedent],
                            ranks[antecedent] < ranks[literal],
                        )
                        for antecedent in antecedents
                    )
                )
            )
        solver.add(
            z3.Implies(
                derived[literal],
                z3.Or(*support_terms) if support_terms else z3.BoolVal(False),
            )
        )
        clause_count += 1

    return derived, clause_count


def _add_ranked_closure_constraints(z3, solver, framework, variables):
    derived, _clause_count = _emit_ranked_closure_constraints(
        z3,
        solver,
        framework,
        variables,
        derived_prefix="der_",
        rank_prefix="rank_",
    )
    return derived


def _prefsat_add_closure_constraints(z3, solver, framework, variables, *, prefix: str):
    return _emit_ranked_closure_constraints(
        z3,
        solver,
        framework,
        variables,
        derived_prefix=f"{prefix}_derived_",
        rank_prefix=f"{prefix}_rank_",
    )


def _rules_by_consequent(framework: ABAFramework, literals: tuple[Literal, ...]):
    grouped: dict[Literal, list[Rule]] = {literal: [] for literal in literals}
    for rule in sorted(framework.rules, key=repr):
        grouped[rule.consequent].append(rule)
    return {literal: tuple(rules) for literal, rules in grouped.items()}


def _any_support_selected(z3, variables, supports: frozenset[AssumptionSet]):
    if not supports:
        return z3.BoolVal(False)
    return z3.Or(
        *(
            _support_selected(z3, variables, support)
            for support in sorted(
                supports, key=lambda item: (len(item), tuple(sorted(map(repr, item))))
            )
        )
    )


def _support_selected(z3, variables, support: AssumptionSet):
    if not support:
        return z3.BoolVal(True)
    return z3.And(*(variables[assumption] for assumption in sorted(support, key=repr)))


def _sat_preferred_counterexample_not_deriving(
    framework: ABAFramework,
    query: Literal,
) -> AssumptionSet | None:
    z3 = _load_z3()
    variables = {
        assumption: z3.Bool(f"in_{_literal_key(assumption)}")
        for assumption in sorted(framework.assumptions, key=repr)
    }
    supports = _minimal_supports(framework)
    solver = z3.Solver()
    _add_admissible_constraints(z3, solver, framework, variables, supports)
    _add_derived_constraints(
        z3,
        solver,
        variables,
        supports,
        require_derived=None,
        require_not_derived=query,
    )

    while solver.check() == z3.sat:
        seed = _model_extension(z3, solver, variables)
        preferred = sat_support_extension(
            framework,
            "preferred",
            require_assumptions=seed,
        )
        if preferred is None:
            return None
        if not _extension_derives(preferred, query, supports):
            return preferred
        outside = framework.assumptions - preferred
        if outside:
            solver.add(
                z3.Or(
                    *(variables[assumption] for assumption in sorted(outside, key=repr))
                )
            )
        else:
            solver.add(z3.BoolVal(False))
    return None


def _add_admissible_constraints(z3, solver, framework, variables, supports) -> None:
    for assumption in sorted(framework.assumptions, key=repr):
        attack_supports = supports.get(framework.contrary[assumption], frozenset())
        solver.add(
            z3.Implies(
                variables[assumption],
                z3.Not(_any_support_selected(z3, variables, attack_supports)),
            )
        )
        solver.add(
            z3.Implies(
                variables[assumption],
                _defended_expr(z3, framework, variables, supports, assumption),
            )
        )


def _add_complete_constraints(z3, solver, framework, variables, supports) -> None:
    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(
            z3.Implies(
                _defended_expr(z3, framework, variables, supports, assumption),
                variables[assumption],
            )
        )


def _defended_expr(z3, framework, variables, supports, assumption):
    attack_supports = supports.get(framework.contrary[assumption], frozenset())
    defenses = []
    for attack_support in sorted(
        attack_supports,
        key=lambda item: (len(item), tuple(sorted(map(repr, item)))),
    ):
        if not attack_support:
            return z3.BoolVal(False)
        defenses.append(
            z3.Or(
                *(
                    _any_support_selected(
                        z3,
                        variables,
                        supports.get(framework.contrary[target], frozenset()),
                    )
                    for target in sorted(attack_support, key=repr)
                )
            )
        )
    return z3.And(*defenses) if defenses else z3.BoolVal(True)


def _add_derived_constraints(
    z3,
    solver,
    variables,
    supports,
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
) -> None:
    if require_derived is not None:
        solver.add(
            _any_support_selected(
                z3, variables, supports.get(require_derived, frozenset())
            )
        )
    if require_not_derived is not None:
        solver.add(
            z3.Not(
                _any_support_selected(
                    z3,
                    variables,
                    supports.get(require_not_derived, frozenset()),
                )
            )
        )


def _model_extension(z3, solver, variables) -> AssumptionSet:
    model = solver.model()
    return frozenset(
        assumption
        for assumption, variable in variables.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def _extension_derives(
    extension: AssumptionSet,
    literal: Literal,
    supports: dict[Literal, frozenset[AssumptionSet]],
) -> bool:
    return any(support <= extension for support in supports.get(literal, frozenset()))


def _extension_satisfies_constraints(
    extension: AssumptionSet,
    supports: dict[Literal, frozenset[AssumptionSet]],
    *,
    require_derived: Literal | None,
    require_not_derived: Literal | None,
) -> bool:
    if require_derived is not None and not _extension_derives(
        extension, require_derived, supports
    ):
        return False
    if require_not_derived is not None and _extension_derives(
        extension, require_not_derived, supports
    ):
        return False
    return True


def _literal_key(literal: Literal) -> str:
    text = repr(literal)
    return "".join(character if character.isalnum() else "_" for character in text)


def _load_z3():
    return load_z3("ABA stable SAT solving")


def _load_pysat_solver():
    try:
        from pysat.solvers import Solver  # type: ignore[import-not-found]
    except ImportError as exc:
        raise OptionalDependencyUnavailable(
            feature="native ABA PrefSat solving",
            package="python-sat",
            install_hint="Install python-sat or use backend='native'.",
        ) from exc
    return Solver


__all__ = [
    "AssumptionKernel",
    "NativeSparseNarrowSatResult",
    "RealPrefSatResult",
    "native_cnf_prefsat_extension",
    "native_sparse_narrow_sat_extension",
    "real_prefsat_attack_edge_count",
    "real_prefsat_extension",
    "sat_stable_extension",
    "sat_support_acceptance",
    "sat_support_extension",
    "support_acceptance",
    "support_extensions",
]
