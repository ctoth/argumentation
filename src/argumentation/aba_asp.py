"""Clingo-backed flat ABA extension queries."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from argumentation import aba as aba_semantics
from argumentation.aba import ABAFramework, ABAPlusFramework, AssumptionSet, derives
from argumentation.aba_sat import _minimal_supports, support_extensions
from argumentation.aspic import Literal


@dataclass(frozen=True)
class ABAEncoding:
    facts: tuple[str, ...]
    signature: str
    metadata: dict[str, str]
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


def encode_aba_theory(framework: ABAFramework) -> ABAEncoding:
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
        metadata={"encoding": "flat_aba_assumption_facts"},
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
) -> ABAQueryResult:
    """Dispatch a flat ABA query to the support-reference or ASP backend."""
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

    encoding = encode_aba_theory(framework)
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

    if backend not in {"asp", "clingo"}:
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


def _task_result(
    framework: ABAFramework,
    *,
    encoding: ABAEncoding,
    semantics: str,
    backend: str,
    task: str,
    query: Literal | None,
    extensions: tuple[AssumptionSet, ...],
    metadata: dict[str, str],
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
