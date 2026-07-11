"""Bounded independent reference for Probe 8 true-clone quotient semantics.

This diagnostic module is deliberately outside production.  It constructs an
exact colored incidence serialization, verifies fix-outside transpositions
from that serialization alone, and reasons exhaustively over bounded flat ABA.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import contextmanager
import ctypes
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import json
import os
import sys
from collections.abc import Iterator
from typing import TypeAlias, cast

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import Literal, Rule, Scalar


NodeId: TypeAlias = str
SerializedIncidence: TypeAlias = tuple[str, NodeId, NodeId]
ExtensionFamily: TypeAlias = frozenset[AssumptionSet]


@dataclass(frozen=True)
class SemanticBounds:
    assumptions: int = 8
    rules: int = 16
    literals: int = 32
    body_width: int = 8
    concrete_subsets: int = 256
    quotient_states: int = 256


@dataclass(frozen=True)
class TranspositionCertificate:
    left: NodeId
    right: NodeId
    fixes_every_other_node: bool = True
    preserves_all_colors: bool = True
    preserves_all_incidences: bool = True


@dataclass(frozen=True)
class TrueCloneClass:
    members: tuple[NodeId, ...]
    transpositions: tuple[TranspositionCertificate, ...]


@dataclass(frozen=True)
class QuotientState:
    multiplicities: tuple[int, ...]
    selected_singletons: frozenset[NodeId]


@dataclass(frozen=True)
class NormalizedFramework:
    serialized: str
    assumption_nodes: tuple[NodeId, ...]
    _literal_by_node: Mapping[NodeId, Literal]

    def literal_for(self, node: NodeId) -> Literal:
        try:
            return self._literal_by_node[node]
        except KeyError as exc:
            raise InvalidNormalizedFramework(f"unknown literal node: {node!r}") from exc


@dataclass(frozen=True)
class QuotientResult:
    normalized: NormalizedFramework
    normalized_sha256: str
    classes: tuple[TrueCloneClass, ...]
    preferred_states: tuple[QuotientState, ...]
    lifted_preferred_family: ExtensionFamily
    examined_state_count: int


class SemanticContractError(RuntimeError):
    """Base class for fail-closed Gate A errors."""


class ContractBoundsExceeded(SemanticContractError):
    """The framework exceeds a frozen limit before exhaustive reasoning."""


class InvalidNormalizedFramework(SemanticContractError):
    """The complete normalized serialization is malformed."""


class InvalidCloneCertificate(SemanticContractError):
    """A proposed class is not certified by every required transposition."""


class OrbitSemanticDisagreement(SemanticContractError):
    """Concrete members of one certified multiplicity orbit disagree."""


@contextmanager
def process_memory_limit(limit_bytes: int) -> Iterator[None]:
    """Apply a reversible hard address-space/process-memory cap fail-closed."""
    if limit_bytes <= 0:
        raise ContractBoundsExceeded("process memory limit must be positive")
    if sys.platform == "win32":
        with _windows_job_memory_limit(limit_bytes):
            yield
        return

    try:
        import resource
    except ImportError as exc:
        raise ContractBoundsExceeded("no process memory limiter is available") from exc
    old_soft, old_hard = resource.getrlimit(resource.RLIMIT_AS)
    new_soft = (
        min(limit_bytes, old_hard)
        if old_hard != resource.RLIM_INFINITY
        else limit_bytes
    )
    resource.setrlimit(resource.RLIMIT_AS, (new_soft, old_hard))
    try:
        yield
    finally:
        resource.setrlimit(resource.RLIMIT_AS, (old_soft, old_hard))


def normalize_framework(
    framework: ABAFramework,
    *,
    bounds: SemanticBounds = SemanticBounds(),
) -> NormalizedFramework:
    """Serialize the complete bounded ordinary flat ABA incidence hypergraph."""
    _check_bounds(framework, bounds)
    literal_nodes = {literal: _literal_node(literal) for literal in framework.language}
    if len(set(literal_nodes.values())) != len(literal_nodes):
        raise InvalidNormalizedFramework("literal serialization is not injective")

    nodes: list[tuple[NodeId, str]] = [
        (
            node,
            "assumption_literal"
            if literal in framework.assumptions
            else "non_assumption_literal",
        )
        for literal, node in literal_nodes.items()
    ]
    incidences: set[SerializedIncidence] = set()
    for assumption in framework.assumptions:
        incidences.add(
            (
                "contrary",
                literal_nodes[assumption],
                literal_nodes[framework.contrary[assumption]],
            )
        )

    for index, rule in enumerate(sorted(framework.rules, key=_rule_key)):
        rule_node = f"rule:{index:04d}"
        nodes.append((rule_node, f"rule:{rule.kind}"))
        incidences.add(("head", rule_node, literal_nodes[rule.consequent]))
        if rule.antecedents:
            incidences.update(
                ("body", rule_node, literal_nodes[literal])
                for literal in rule.antecedents
            )
        else:
            incidences.add(("factual", rule_node, rule_node))

    assumption_nodes = tuple(
        sorted(literal_nodes[assumption] for assumption in framework.assumptions)
    )
    document = {
        "nodes": sorted([list(item) for item in nodes]),
        "incidences": sorted([list(item) for item in incidences]),
        "assumptions": list(assumption_nodes),
    }
    serialized = json.dumps(document, sort_keys=True, separators=(",", ":"))
    return NormalizedFramework(
        serialized=serialized,
        assumption_nodes=assumption_nodes,
        _literal_by_node={node: literal for literal, node in literal_nodes.items()},
    )


def verify_fix_outside_transposition(
    serialized: str,
    left: NodeId,
    right: NodeId,
) -> TranspositionCertificate | None:
    """Verify one transposition from only the serialized complete hypergraph."""
    nodes, colors, incidences, assumptions = _parse_normalized(serialized)
    if left == right or left not in assumptions or right not in assumptions:
        return None

    def transpose(node: NodeId) -> NodeId:
        if node == left:
            return right
        if node == right:
            return left
        return node

    if any(transpose(node) not in nodes for node in nodes):
        return None
    if any(colors[transpose(node)] != color for node, color in colors.items()):
        return None
    mapped = {
        (kind, transpose(source), transpose(target))
        for kind, source, target in incidences
    }
    if mapped != incidences:
        return None
    return TranspositionCertificate(left=left, right=right)


def certify_true_clone_classes(serialized: str) -> tuple[TrueCloneClass, ...]:
    """Return maximal nontrivial classes certified pairwise by the verifier."""
    _, _, _, assumptions = _parse_normalized(serialized)
    adjacency = {node: set[NodeId]() for node in assumptions}
    certificates: dict[frozenset[NodeId], TranspositionCertificate] = {}
    for left, right in combinations(sorted(assumptions), 2):
        certificate = verify_fix_outside_transposition(serialized, left, right)
        if certificate is not None:
            adjacency[left].add(right)
            adjacency[right].add(left)
            certificates[frozenset({left, right})] = certificate

    classes: list[TrueCloneClass] = []
    pending = set(assumptions)
    while pending:
        start = min(pending)
        component: set[NodeId] = set()
        frontier = [start]
        while frontier:
            node = frontier.pop()
            if node in component:
                continue
            component.add(node)
            frontier.extend(adjacency[node] - component)
        pending -= component
        if len(component) < 2:
            continue
        members = tuple(sorted(component))
        required: list[TranspositionCertificate] = []
        for left, right in combinations(members, 2):
            certificate = certificates.get(frozenset({left, right}))
            if certificate is None:
                raise InvalidCloneCertificate(
                    "candidate component lacks a required fix-outside transposition"
                )
            required.append(certificate)
        classes.append(TrueCloneClass(members, tuple(required)))
    return tuple(sorted(classes, key=lambda item: item.members))


def expand_state(
    classes: Sequence[TrueCloneClass],
    state: QuotientState,
    normalized: NormalizedFramework,
) -> ExtensionFamily:
    """Expand one multiplicity state to its complete concrete orbit."""
    if len(state.multiplicities) != len(classes):
        raise InvalidCloneCertificate("multiplicity/class arity mismatch")
    class_members = frozenset(member for item in classes for member in item.members)
    if state.selected_singletons & class_members:
        raise InvalidCloneCertificate("class member was also selected as a singleton")
    if not state.selected_singletons <= set(normalized.assumption_nodes):
        raise InvalidCloneCertificate("state contains an unknown singleton")

    choices: list[tuple[tuple[NodeId, ...], ...]] = []
    for certificate, multiplicity in zip(classes, state.multiplicities, strict=True):
        if not 0 <= multiplicity <= len(certificate.members):
            raise InvalidCloneCertificate(
                "multiplicity is outside its exact class range"
            )
        choices.append(tuple(combinations(certificate.members, multiplicity)))
    selected_singletons = tuple(sorted(state.selected_singletons))
    node_extensions = (
        frozenset(
            (
                *selected_singletons,
                *(member for choice in selected for member in choice),
            )
        )
        for selected in product(*choices)
    )
    return frozenset(
        frozenset(normalized.literal_for(node) for node in extension)
        for extension in node_extensions
    )


def evaluate_preferred_quotient(
    framework: ABAFramework,
    *,
    bounds: SemanticBounds = SemanticBounds(),
) -> QuotientResult:
    """Independently enumerate quotient states and lift the preferred family."""
    _check_bounds(framework, bounds)
    normalized = normalize_framework(framework, bounds=bounds)
    classes = certify_true_clone_classes(normalized.serialized)
    class_nodes = frozenset(member for item in classes for member in item.members)
    singletons = tuple(
        node for node in normalized.assumption_nodes if node not in class_nodes
    )
    states = _states(classes, singletons, bounds)
    concrete_subsets = _literal_subsets(framework.assumptions)
    if len(concrete_subsets) > bounds.concrete_subsets:
        raise ContractBoundsExceeded(
            f"concrete subsets: {len(concrete_subsets)} > {bounds.concrete_subsets}"
        )
    admissible = {
        candidate: _admissible(framework, candidate, concrete_subsets)
        for candidate in concrete_subsets
    }

    admissible_states: list[QuotientState] = []
    for state in states:
        orbit = expand_state(classes, state, normalized)
        values = {admissible[extension] for extension in orbit}
        if len(values) != 1:
            raise OrbitSemanticDisagreement(
                "a certified class state has non-uniform concrete admissibility"
            )
        if values == {True}:
            admissible_states.append(state)
    preferred_states = tuple(
        state
        for state in admissible_states
        if not any(
            state != other and _state_leq(state, other) for other in admissible_states
        )
    )
    lifted_parts = [
        expand_state(classes, state, normalized) for state in preferred_states
    ]
    lifted = frozenset(extension for family in lifted_parts for extension in family)
    if sum(map(len, lifted_parts)) != len(lifted):
        raise OrbitSemanticDisagreement("preferred state orbits overlap")
    return QuotientResult(
        normalized=normalized,
        normalized_sha256=sha256(normalized.serialized.encode("utf-8")).hexdigest(),
        classes=classes,
        preferred_states=preferred_states,
        lifted_preferred_family=lifted,
        examined_state_count=len(states),
    )


def canonical_witness(family: ExtensionFamily) -> AssumptionSet:
    """Select one witness after family construction; never construct a family."""
    if not family:
        raise SemanticContractError("cannot select a witness from an empty family")
    return min(family, key=lambda extension: tuple(sorted(map(repr, extension))))


@contextmanager
def _windows_job_memory_limit(limit_bytes: int) -> Iterator[None]:
    from ctypes import wintypes

    class _BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class _ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BasicLimitInformation),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_job = kernel32.CreateJobObjectW
    create_job.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
    create_job.restype = wintypes.HANDLE
    set_information = kernel32.SetInformationJobObject
    set_information.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    )
    set_information.restype = wintypes.BOOL
    assign_process = kernel32.AssignProcessToJobObject
    assign_process.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    assign_process.restype = wintypes.BOOL
    get_process = kernel32.GetCurrentProcess
    get_process.argtypes = ()
    get_process.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL

    job = create_job(None, None)
    if not job:
        raise ContractBoundsExceeded(
            f"CreateJobObjectW failed: winerror={ctypes.get_last_error()} pid={os.getpid()}"
        )
    try:
        information = _ExtendedLimitInformation()
        information.BasicLimitInformation.LimitFlags = 0x00000100
        information.ProcessMemoryLimit = limit_bytes
        if not set_information(
            job, 9, ctypes.byref(information), ctypes.sizeof(information)
        ):
            raise ContractBoundsExceeded(
                f"SetInformationJobObject failed: winerror={ctypes.get_last_error()}"
            )
        if not assign_process(job, get_process()):
            raise ContractBoundsExceeded(
                f"AssignProcessToJobObject failed: winerror={ctypes.get_last_error()}"
            )
        yield
    finally:
        close_handle(job)


def _check_bounds(framework: ABAFramework, bounds: SemanticBounds) -> None:
    checks = (
        ("assumptions", len(framework.assumptions), bounds.assumptions),
        ("rules", len(framework.rules), bounds.rules),
        ("literals", len(framework.language), bounds.literals),
        (
            "body width",
            max((len(rule.antecedents) for rule in framework.rules), default=0),
            bounds.body_width,
        ),
    )
    for label, actual, limit in checks:
        if actual > limit:
            raise ContractBoundsExceeded(f"{label}: {actual} > {limit}")


def _states(
    classes: Sequence[TrueCloneClass],
    singletons: tuple[NodeId, ...],
    bounds: SemanticBounds,
) -> tuple[QuotientState, ...]:
    states = tuple(
        QuotientState(tuple(multiplicities), frozenset(selected))
        for multiplicities in product(
            *(range(len(item.members) + 1) for item in classes)
        )
        for selected in _node_subsets(singletons)
    )
    if len(states) > bounds.quotient_states:
        raise ContractBoundsExceeded(
            f"quotient states: {len(states)} > {bounds.quotient_states}"
        )
    return states


def _admissible(
    framework: ABAFramework,
    candidate: AssumptionSet,
    attackers: tuple[AssumptionSet, ...],
) -> bool:
    if _attacks(framework, candidate, candidate):
        return False
    return all(
        not _attacks(framework, attacker, candidate)
        or _attacks(framework, candidate, attacker)
        for attacker in attackers
    )


def _attacks(
    framework: ABAFramework,
    attacker: AssumptionSet,
    target: AssumptionSet,
) -> bool:
    closure = _closure(framework.rules, attacker)
    return any(framework.contrary[assumption] in closure for assumption in target)


def _closure(rules: frozenset[Rule], premises: AssumptionSet) -> frozenset[Literal]:
    result: set[Literal] = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if (
                all(item in result for item in rule.antecedents)
                and rule.consequent not in result
            ):
                result.add(rule.consequent)
                changed = True
    return frozenset(result)


def _state_leq(left: QuotientState, right: QuotientState) -> bool:
    return left.selected_singletons <= right.selected_singletons and all(
        left_count <= right_count
        for left_count, right_count in zip(
            left.multiplicities, right.multiplicities, strict=True
        )
    )


def _literal_subsets(items: frozenset[Literal]) -> tuple[AssumptionSet, ...]:
    ordered = tuple(sorted(items, key=repr))
    return tuple(
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    )


def _node_subsets(items: tuple[NodeId, ...]) -> tuple[frozenset[NodeId], ...]:
    return tuple(
        frozenset(choice)
        for size in range(len(items) + 1)
        for choice in combinations(items, size)
    )


def _literal_node(literal: Literal) -> NodeId:
    token = {
        "predicate": literal.atom.predicate,
        "arguments": [_scalar_token(item) for item in literal.atom.arguments],
        "negated": literal.negated,
    }
    return "literal:" + json.dumps(token, sort_keys=True, separators=(",", ":"))


def _scalar_token(value: Scalar) -> tuple[str, str]:
    return type(value).__name__, repr(value)


def _rule_key(rule: Rule) -> tuple[object, ...]:
    return (
        tuple(_literal_node(item) for item in rule.antecedents),
        _literal_node(rule.consequent),
        rule.kind,
        rule.name or "",
    )


def _parse_normalized(
    serialized: str,
) -> tuple[
    frozenset[NodeId],
    dict[NodeId, str],
    frozenset[SerializedIncidence],
    frozenset[NodeId],
]:
    try:
        raw = cast(dict[str, object], json.loads(serialized))
        node_rows = cast(list[list[str]], raw["nodes"])
        incidence_rows = cast(list[list[str]], raw["incidences"])
        assumption_rows = cast(list[str], raw["assumptions"])
        colors = {row[0]: row[1] for row in node_rows}
        nodes = frozenset(colors)
        incidences = frozenset((row[0], row[1], row[2]) for row in incidence_rows)
        assumptions = frozenset(assumption_rows)
    except (KeyError, TypeError, ValueError, IndexError, json.JSONDecodeError) as exc:
        raise InvalidNormalizedFramework("unparseable normalized framework") from exc
    if len(colors) != len(node_rows):
        raise InvalidNormalizedFramework("duplicate normalized node")
    if not assumptions <= nodes:
        raise InvalidNormalizedFramework("unknown assumption node")
    if any(colors[node] != "assumption_literal" for node in assumptions):
        raise InvalidNormalizedFramework("assumption node has the wrong color")
    if any(
        source not in nodes or target not in nodes for _, source, target in incidences
    ):
        raise InvalidNormalizedFramework("incidence references an unknown node")
    return nodes, colors, incidences, assumptions


__all__ = [
    "ContractBoundsExceeded",
    "NormalizedFramework",
    "OrbitSemanticDisagreement",
    "QuotientResult",
    "QuotientState",
    "SemanticBounds",
    "TrueCloneClass",
    "canonical_witness",
    "certify_true_clone_classes",
    "evaluate_preferred_quotient",
    "expand_state",
    "normalize_framework",
    "process_memory_limit",
    "verify_fix_outside_transposition",
]
