"""Clingo-backed flat ABA extension queries."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from argumentation import aba as aba_semantics
from argumentation.aba import ABAFramework, ABAPlusFramework, AssumptionSet, derives
from argumentation.aba_preprocessing import GROUNDED_REDUCT_ABA_SEMANTICS
from argumentation.aba_sat import _minimal_supports, support_extensions
from argumentation.aspic import Literal


@dataclass(frozen=True)
class ABAEncoding:
    facts: tuple[str, ...]
    signature: str
    metadata: dict[str, Any]
    assumption_by_id: dict[str, Literal] = field(default_factory=dict)
    literal_by_id: dict[str, Literal] = field(default_factory=dict)


@dataclass(frozen=True)
class ABAQueryResult:
    status: str
    semantics: str
    backend: str
    extensions: tuple[AssumptionSet, ...]
    accepted_assumptions: AssumptionSet
    encoding: ABAEncoding
    metadata: dict[str, str]
    answer: bool | None = None
    witness: AssumptionSet | None = None
    counterexample: AssumptionSet | None = None


def encode_aba_theory(framework: ABAFramework, *, include_supports: bool = True) -> ABAEncoding:
    """Encode a flat ABA framework into deterministic ASP facts."""
    assumption_by_id = {
        _literal_id(assumption): assumption
        for assumption in sorted(framework.assumptions, key=repr)
    }
    literal_by_id = {
        _literal_id(literal): literal
        for literal in sorted(framework.language, key=repr)
    }
    _reject_id_collisions(assumption_by_id, "assumption")
    _reject_id_collisions(literal_by_id, "literal")

    facts: set[str] = set()
    for assumption_id, assumption in assumption_by_id.items():
        facts.add(f"assumption({assumption_id}).")
        facts.add(f"assumption_literal({assumption_id},{_literal_id(assumption)}).")
        facts.add(f"contrary({assumption_id},{_literal_id(framework.contrary[assumption])}).")

    for index, rule in enumerate(sorted(framework.rules, key=repr)):
        rule_id = f"r_{index}"
        facts.add(f"rule({rule_id}).")
        facts.add(f"head({rule_id},{_literal_id(rule.consequent)}).")
        facts.add(f"body_count({rule_id},{len(rule.antecedents)}).")
        for antecedent in rule.antecedents:
            facts.add(f"body({rule_id},{_literal_id(antecedent)}).")

    if include_supports:
        support_index = 0
        for conclusion, supports in sorted(_minimal_supports(framework).items(), key=lambda item: repr(item[0])):
            for support in sorted(supports, key=lambda item: (len(item), tuple(sorted(map(repr, item))))):
                support_id = f"sup_{support_index}"
                support_index += 1
                facts.add(f"support_concludes({support_id},{_literal_id(conclusion)}).")
                facts.add(f"support_count({support_id},{len(support)}).")
                for assumption in sorted(support, key=repr):
                    facts.add(f"support_member({support_id},{_literal_id(assumption)}).")

    ordered_facts = tuple(sorted(facts))
    signature = hashlib.sha256("\n".join(ordered_facts).encode("utf-8")).hexdigest()
    return ABAEncoding(
        facts=ordered_facts,
        signature=signature,
        metadata={
            "encoding": (
                "flat_aba_assumption_support_facts"
                if include_supports
                else "flat_aba_core_facts"
            )
        },
        assumption_by_id=assumption_by_id,
        literal_by_id=literal_by_id,
    )


def solve_aba_with_backend(
    framework: ABAFramework | ABAPlusFramework,
    *,
    backend: str,
    semantics: str,
    task: str = "enum",
    query: Literal | None = None,
    binary: str = "clingo",
    timeout_seconds: float = 30.0,
    simplify: bool = True,
) -> ABAQueryResult:
    """Dispatch a flat ABA query to the support-reference or ASP backend."""
    if (
        simplify
        and isinstance(framework, ABAFramework)
        and semantics in GROUNDED_REDUCT_ABA_SEMANTICS
    ):
        from argumentation.aba_preprocessing import simplify_aba

        simplification = simplify_aba(framework, semantics=semantics)
        if not simplification.is_trivial:
            return _solve_simplified(
                simplification,
                backend=backend,
                semantics=semantics,
                task=task,
                query=query,
                binary=binary,
                timeout_seconds=timeout_seconds,
            )
    if isinstance(framework, ABAPlusFramework):
        base = framework.framework
        encoding = encode_aba_theory(base)
        return _failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="ABA+ ASP backend is not implemented",
        )

    needs_support_facts = backend not in {"asp", "clingo"}
    encoding = encode_aba_theory(framework, include_supports=needs_support_facts)
    if semantics not in {"admissible", "complete", "stable", "preferred", "grounded"}:
        return _failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=f"unsupported ABA semantics: {semantics}",
        )

    if backend in {"support_reference", "materialized_reference"}:
        extensions = _reference_extensions(framework, semantics)
        return _task_result(
            framework,
            encoding=encoding,
            semantics=semantics,
            backend=backend,
            task=task,
            query=query,
            extensions=extensions,
            metadata={"encoding": encoding.metadata["encoding"], "solver": "aba_support_reference"},
        )

    if backend in {"asp", "clingo"} and semantics in {"complete", "stable", "preferred", "grounded"}:
        return _solve_multishot(
            framework,
            encoding=encoding,
            semantics=semantics,
            backend=backend,
            task=task,
            query=query,
        )

    if backend not in {"asp", "clingo", "clingo_subprocess"}:
        return _failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="backend is not installed or registered",
        )

    from argumentation.solver_adapters import clingo

    module_semantics = "complete" if semantics == "grounded" else semantics
    module_semantics = "admissible" if module_semantics == "preferred" else module_semantics
    result = clingo.run_extension_enumeration_protocol(
        facts=encoding.facts,
        encoding_modules=(f"aba_{module_semantics}.lp",),
        known_argument_ids=frozenset(encoding.assumption_by_id),
        binary=binary,
        timeout_seconds=timeout_seconds,
        problem=f"ABA-{semantics.upper()}",
    )
    if isinstance(result, clingo.ClingoExtensionEnumerationSuccess):
        extensions = _decode_extensions(result.extensions, encoding)
        if semantics == "preferred":
            extensions = _maximal_extensions(extensions)
        elif semantics == "grounded":
            extensions = _minimal_extensions(extensions)
        return _task_result(
            framework,
            encoding=encoding,
            semantics=semantics,
            backend=backend,
            task=task,
            query=query,
            extensions=extensions,
            metadata={
                "encoding": encoding.metadata["encoding"],
                "solver": "clingo",
                "stdout": result.stdout,
            },
        )
    if isinstance(result, clingo.ClingoUnavailable):
        return _failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=result.reason,
        )
    status = "backend_error" if isinstance(result, clingo.ClingoProcessError) else "protocol_error"
    return _failure_result(
        status=status,
        semantics=semantics,
        backend=backend,
        encoding=encoding,
        reason=result.reason,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _solve_multishot(
    framework: ABAFramework,
    *,
    encoding: ABAEncoding,
    semantics: str,
    backend: str,
    task: str,
    query: Literal | None,
) -> ABAQueryResult:
    """Solve a flat ABA query with the incremental multi-shot clingo solver.

    Implements Lehtonen-Wallner-Jaervisalo TPLP 2021 Algorithm 1 for DS-PR (the
    timeout cluster); falls back to enumeration (Algorithm 4 for preferred, a
    single grounded solve for complete/stable) plus the shared task projection for
    the other ABA queries.
    """
    from argumentation import aba_incremental

    metadata_base = {
        "encoding": encoding.metadata["encoding"],
        "solver": "clingo_multishot",
        **aba_incremental.lehtonen_incremental_asp_metadata(),
    }
    try:
        solver = aba_incremental.AbaIncrementalSolver(framework, encoding=encoding)
    except RuntimeError as exc:
        return _failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=str(exc),
        )

    telemetry = aba_incremental.IncrementalTelemetry()

    # The DS-PR fast path: Algorithm 1, avoids enumerating every preferred set.
    if semantics == "preferred" and task == "skeptical" and query is not None:
        answer, counterexample = solver.is_skeptically_accepted_preferred(query, telemetry=telemetry)
        return ABAQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            extensions=tuple() if counterexample is None else (counterexample,),
            accepted_assumptions=counterexample or frozenset(),
            encoding=encoding,
            metadata=metadata_base
            | {"task": task, "algorithm": "L21-TPLP-Alg1"}
            | _incremental_telemetry_metadata(telemetry),
            answer=answer,
            counterexample=counterexample,
        )

    if task == "single-extension":
        if semantics == "grounded":
            extension = solver.grounded_extension()
        elif semantics == "complete":
            extension = solver.find_complete_extension(telemetry=telemetry)
        elif semantics == "stable":
            extension = solver.find_stable_extension(telemetry=telemetry)
        elif semantics == "preferred":
            extension = solver.find_preferred_extension(telemetry=telemetry)
        else:  # pragma: no cover - dispatcher gates this
            raise ValueError(f"unsupported ABA semantics for multishot: {semantics}")
        algorithm_metadata: dict[str, str] = {"algorithm": "first-model-witness"}
        if semantics == "preferred":
            algorithm_metadata = {
                "algorithm": "L21-complete-greedy-preferred-growth",
                "maximality_paper": aba_incremental.EGLY_PREFERRED_MAXIMALITY_CITATION,
                "maximality_paper_pages": aba_incremental.EGLY_PREFERRED_MAXIMALITY_PAGE_CITATIONS,
            }
        extensions = tuple() if extension is None else (extension,)
        return _task_result(
            framework,
            encoding=encoding,
            semantics=semantics,
            backend=backend,
            task=task,
            query=query,
            extensions=extensions,
            metadata=metadata_base
            | algorithm_metadata
            | _incremental_telemetry_metadata(telemetry),
        )

    if semantics == "grounded":
        extensions = (solver.grounded_extension(),)
    elif semantics == "complete":
        extensions = solver.enumerate_complete(telemetry=telemetry)
    elif semantics == "stable":
        extensions = solver.enumerate_stable(telemetry=telemetry)
    elif semantics == "preferred":
        extensions = solver.enumerate_preferred(telemetry=telemetry)
    else:  # pragma: no cover - dispatcher gates this
        raise ValueError(f"unsupported ABA semantics for multishot: {semantics}")

    return _task_result(
        framework,
        encoding=encoding,
        semantics=semantics,
        backend=backend,
        task=task,
        query=query,
        extensions=extensions,
        metadata=metadata_base | _incremental_telemetry_metadata(telemetry),
    )


def _incremental_telemetry_metadata(telemetry) -> dict[str, int]:
    return {
        "refinement_clauses": telemetry.refinement_clauses,
        "outer_iterations": telemetry.outer_iterations,
        "inner_iterations": telemetry.inner_iterations,
        "solver_calls": telemetry.solver_calls,
    }


def _solve_simplified(
    simplification,
    *,
    backend: str,
    semantics: str,
    task: str,
    query: Literal | None,
    binary: str,
    timeout_seconds: float,
) -> ABAQueryResult:
    """Solve a gated ABA query on the preprocessed residual and lift the answer back."""
    original = simplification.original
    residual = simplification.residual

    # DS-PR fast path: route skeptical-preferred through Algorithm 1 on the
    # residual (with the preprocessing lift rules in front), so the incremental
    # CEGAR loop is the default for the DS-PR timeout cluster even with
    # preprocessing enabled.
    if (
        semantics == "preferred"
        and task == "skeptical"
        and query is not None
        and backend in {"asp", "clingo"}
    ):
        return _solve_simplified_ds_pr(simplification, backend=backend, query=query)

    residual_task = "single-extension" if task == "single-extension" else "enum"
    residual_result = solve_aba_with_backend(
        residual,
        backend=backend,
        semantics=semantics,
        task=residual_task,
        query=None,
        binary=binary,
        timeout_seconds=timeout_seconds,
        simplify=False,
    )
    encoding = encode_aba_theory(original)
    if residual_result.status != "success":
        return _failure_result(
            status=residual_result.status,
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=residual_result.metadata.get("reason", "residual ABA solve failed"),
            stdout=residual_result.metadata.get("stdout", ""),
            stderr=residual_result.metadata.get("stderr", ""),
        )
    lifted = tuple(
        sorted(
            (simplification.lift(extension) for extension in residual_result.extensions),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )
    metadata = dict(residual_result.metadata)
    metadata["preprocessing"] = "grounded_reduct_aba"
    return _task_result(
        original,
        encoding=encoding,
        semantics=semantics,
        backend=backend,
        task=task,
        query=query,
        extensions=lifted,
        metadata=metadata,
    )


def _solve_simplified_ds_pr(simplification, *, backend: str, query: Literal) -> ABAQueryResult:
    """DS-PR on a non-trivial preprocessed framework: lift rules + Algorithm 1 on the residual.

    Lift rules (mirror ``aba_sat._simplified_support_acceptance``):

    * ``query`` is an assumption in ``fixed_in`` -> in every preferred set -> YES;
    * ``query`` is an assumption in ``fixed_out`` -> in no gated extension -> NO,
      with any preferred set of ``original`` (= lift of a residual preferred set)
      as the counterexample;
    * ``query`` is a sentence already in ``Th(fixed_in)`` -> derived by every
      preferred set -> YES;
    * ``query`` not in ``residual.language`` (and not in ``Th(fixed_in)``) -> not
      forward-derivable from any extension of ``original`` -> NO, counterexample =
      lift of a residual preferred set;
    * otherwise: ``query`` is skeptically accepted under preferred in ``original``
      iff it is in ``residual`` (the residual bakes in ``fixed_in``'s closure and
      drops ``fixed_out``-using rules), so run Algorithm 1 on the residual and
      lift the counterexample.
    """
    from argumentation import aba as _aba
    from argumentation import aba_incremental

    original = simplification.original
    residual = simplification.residual
    encoding = encode_aba_theory(original)
    metadata = {
        "encoding": encoding.metadata["encoding"],
        "solver": "clingo_multishot",
        "task": "skeptical",
        "algorithm": "L21-TPLP-Alg1",
        "preprocessing": "grounded_reduct_aba",
        **aba_incremental.lehtonen_incremental_asp_metadata(),
    }

    def _result(answer: bool, counterexample: AssumptionSet | None) -> ABAQueryResult:
        return ABAQueryResult(
            status="success",
            semantics="preferred",
            backend=backend,
            extensions=tuple() if counterexample is None else (counterexample,),
            accepted_assumptions=counterexample or frozenset(),
            encoding=encoding,
            metadata=dict(metadata) | _incremental_telemetry_metadata(telemetry),
            answer=answer,
            counterexample=counterexample,
        )

    try:
        residual_solver = aba_incremental.AbaIncrementalSolver(residual)
    except RuntimeError as exc:
        return _failure_result(
            status="unavailable_backend",
            semantics="preferred",
            backend=backend,
            encoding=encoding,
            reason=str(exc),
        )
    telemetry = aba_incremental.IncrementalTelemetry()

    def _some_preferred() -> AssumptionSet | None:
        residual_pref = residual_solver.find_preferred_extension(telemetry=telemetry)
        return None if residual_pref is None else simplification.lift(residual_pref)

    if query in simplification.fixed_in:
        return _result(True, None)
    if query in simplification.fixed_out:
        return _result(False, _some_preferred())
    closure_of_fixed_in = _aba._closure(original, simplification.fixed_in)
    if query in closure_of_fixed_in:
        return _result(True, None)
    if query not in residual.language:
        return _result(False, _some_preferred())

    answer, residual_counterexample = residual_solver.is_skeptically_accepted_preferred(query, telemetry=telemetry)
    if answer:
        return _result(True, None)
    counterexample = None if residual_counterexample is None else simplification.lift(residual_counterexample)
    return _result(False, counterexample)


def _task_result(
    framework: ABAFramework,
    *,
    encoding: ABAEncoding,
    semantics: str,
    backend: str,
    task: str,
    query: Literal | None,
    extensions: tuple[AssumptionSet, ...],
    metadata: dict[str, Any],
) -> ABAQueryResult:
    if task == "enum":
        return ABAQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            extensions=extensions,
            accepted_assumptions=extensions[0] if len(extensions) == 1 else frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
        )
    if task == "single-extension":
        extension = extensions[0] if extensions else frozenset()
        return ABAQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            extensions=extensions,
            accepted_assumptions=extension,
            encoding=encoding,
            metadata=metadata | {"task": task},
            witness=extension if extensions else None,
        )
    if query is None:
        return _failure_result(
            status="protocol_error",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="credulous and skeptical ABA tasks require query",
        )
    if task == "credulous":
        witness = next((extension for extension in extensions if derives(framework, extension, query)), None)
        return ABAQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            extensions=extensions,
            accepted_assumptions=witness or frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = next(
            (extension for extension in extensions if not derives(framework, extension, query)),
            None,
        )
        return ABAQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            extensions=extensions,
            accepted_assumptions=counterexample or frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
            answer=counterexample is None,
            counterexample=counterexample,
        )
    return _failure_result(
        status="unavailable_backend",
        semantics=semantics,
        backend=backend,
        encoding=encoding,
        reason=f"unsupported ABA task: {task}",
    )


def _reference_extensions(framework: ABAFramework, semantics: str) -> tuple[AssumptionSet, ...]:
    if semantics == "admissible":
        return tuple(
            candidate
            for candidate in aba_semantics._all_subsets(framework.assumptions)
            if aba_semantics.admissible(framework, candidate)
        )
    if semantics == "complete":
        return support_extensions(framework, "complete")
    if semantics == "stable":
        return support_extensions(framework, "stable")
    if semantics == "preferred":
        return support_extensions(framework, "preferred")
    if semantics == "grounded":
        return (aba_semantics.grounded_extension(framework),)
    raise ValueError(f"unsupported ABA semantics: {semantics}")


def _decode_extensions(
    encoded_extensions: tuple[frozenset[str], ...],
    encoding: ABAEncoding,
) -> tuple[AssumptionSet, ...]:
    return tuple(
        sorted(
            (
                frozenset(encoding.assumption_by_id[assumption_id] for assumption_id in extension)
                for extension in encoded_extensions
            ),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )


def _maximal_extensions(extensions: tuple[AssumptionSet, ...]) -> tuple[AssumptionSet, ...]:
    return tuple(extension for extension in extensions if not any(extension < other for other in extensions))


def _minimal_extensions(extensions: tuple[AssumptionSet, ...]) -> tuple[AssumptionSet, ...]:
    if not extensions:
        return tuple()
    minimal = [extension for extension in extensions if not any(other < extension for other in extensions)]
    return tuple(sorted(minimal, key=lambda extension: (len(extension), tuple(sorted(map(repr, extension))))))[:1]


def _failure_result(
    *,
    status: str,
    semantics: str,
    backend: str,
    encoding: ABAEncoding,
    reason: str,
    stdout: str = "",
    stderr: str = "",
) -> ABAQueryResult:
    metadata = {"reason": reason, "encoding": encoding.metadata["encoding"]}
    if stdout:
        metadata["stdout"] = stdout
    if stderr:
        metadata["stderr"] = stderr
    return ABAQueryResult(
        status=status,
        semantics=semantics,
        backend=backend,
        extensions=tuple(),
        accepted_assumptions=frozenset(),
        encoding=encoding,
        metadata=metadata,
    )


def _literal_id(literal: Literal) -> str:
    rendered = repr(literal)
    if rendered.startswith("~"):
        rendered = f"n_{rendered[1:]}"
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", rendered)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "literal"
    if cleaned[0].isupper():
        cleaned = cleaned[0].lower() + cleaned[1:]
    if not cleaned[0].islower():
        cleaned = f"l_{cleaned}"
    return cleaned


def _reject_id_collisions(mapping: dict[str, Literal], kind: str) -> None:
    if len(mapping) == len(set(mapping)):
        return
    raise ValueError(f"duplicate {kind} ASP ids")


__all__ = [
    "ABAEncoding",
    "ABAQueryResult",
    "encode_aba_theory",
    "solve_aba_with_backend",
]
