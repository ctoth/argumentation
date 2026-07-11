"""Bounded reference semantics for exact ABA assumption-cutset conditioning.

This is a diagnostic contract, not a production solver or routing surface.  It
uses exhaustive closure/support reasoning only after enforcing the frozen small
framework bounds.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from itertools import combinations, product
from typing import Mapping, TypeAlias

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_support_model import _SupportState
from argumentation.structured.aspic.aspic import Literal, Rule


ExtensionFamily: TypeAlias = frozenset[AssumptionSet]
GraphNode: TypeAlias = tuple[str, object]


@dataclass(frozen=True, order=True)
class CollectiveAttack:
    tail: AssumptionSet
    target: Literal


@dataclass(frozen=True)
class SemanticBounds:
    assumptions: int = 5
    non_assumption_literals: int = 4
    rules: int = 8
    body_width: int = 3
    cutset_size: int = 3
    collective_attacks: int = 512
    branch_states: int = 65_536


@dataclass(frozen=True)
class PathCounters:
    factual_normalizations: int = 0
    qualifying_empty_cutsets: int = 0
    qualifying_nonempty_cutsets: int = 0
    selected_cut_states: int = 0
    rejected_cut_states: int = 0
    attacked_cut_signatures: int = 0
    cut_defense_obligations_created: int = 0
    cut_defense_obligations_discharged: int = 0
    inactive_collective_tails: int = 0
    activated_collective_tails: int = 0
    independent_residual_components: int = 0
    deduplication_passes: int = 0
    duplicate_lifts_removed: int = 0
    incomparable_preferred_maxima: int = 0


@dataclass(frozen=True)
class CutsetComposition:
    cutset: AssumptionSet
    normalized_assumptions: AssumptionSet
    components: tuple[AssumptionSet, ...]
    admissible_lifts: ExtensionFamily
    preferred_extensions: ExtensionFamily
    paths: PathCounters


@dataclass(frozen=True)
class _NormalizedFramework:
    assumptions: AssumptionSet
    contrary: Mapping[Literal, Literal]
    fact_attacked: AssumptionSet
    factual_closure: frozenset[Literal]
    rules: tuple[Rule, ...]
    attacks: frozenset[CollectiveAttack]


class SemanticContractError(RuntimeError):
    """Base class for fail-closed diagnostic errors."""


class ContractBoundsExceeded(SemanticContractError):
    """A frozen semantic bound was exceeded."""


class NonSeparatorError(SemanticContractError):
    """The requested assumption set is not a qualifying separator."""


class AmbiguousAttackOwnership(SemanticContractError):
    """A collective attack has more than one residual owner."""


class OracleDisagreement(SemanticContractError):
    """The independent support authority disagrees with the reference."""


class MissingPathCoverage(SemanticContractError):
    """A required frozen semantic path was not observed."""


@dataclass
class _MutablePaths:
    factual_normalizations: int = 0
    qualifying_empty_cutsets: int = 0
    qualifying_nonempty_cutsets: int = 0
    selected_cut_states: int = 0
    rejected_cut_states: int = 0
    attacked_cut_signatures: int = 0
    cut_defense_obligations_created: int = 0
    cut_defense_obligations_discharged: int = 0
    inactive_collective_tails: int = 0
    activated_collective_tails: int = 0
    independent_residual_components: int = 0
    deduplication_passes: int = 0
    duplicate_lifts_removed: int = 0
    incomparable_preferred_maxima: int = 0


def qualifying_cutsets(
    framework: ABAFramework,
    *,
    bounds: SemanticBounds = SemanticBounds(),
) -> tuple[AssumptionSet, ...]:
    """Return every frozen-size qualifying cutset in deterministic order."""
    normalized = _normalize(framework, bounds)
    ordered = tuple(sorted(normalized.assumptions, key=repr))
    qualifying: list[AssumptionSet] = []
    for size in range(min(bounds.cutset_size, len(ordered)) + 1):
        for members in combinations(ordered, size):
            cutset = frozenset(members)
            components = _assumption_components(normalized, cutset)
            if (not normalized.assumptions and not cutset) or len(components) >= 2:
                _bucket_attacks(normalized.attacks, cutset, components)
                qualifying.append(cutset)
    return tuple(qualifying)


def compose_for_cutset(
    framework: ABAFramework,
    cutset: AssumptionSet,
    *,
    bounds: SemanticBounds = SemanticBounds(),
) -> CutsetComposition:
    """Enumerate exact conditioned admissible lifts for one qualifying cutset."""
    normalized = _normalize(framework, bounds)
    if not cutset <= normalized.assumptions:
        raise NonSeparatorError("cutset contains a fact-attacked or unknown assumption")
    if len(cutset) > min(bounds.cutset_size, len(normalized.assumptions)):
        raise ContractBoundsExceeded(
            f"cutset size: {len(cutset)} > {min(bounds.cutset_size, len(normalized.assumptions))}"
        )
    components = _assumption_components(normalized, cutset)
    if normalized.assumptions:
        if len(components) < 2:
            raise NonSeparatorError(
                f"cutset leaves {len(components)} assumption-bearing component; "
                "expected at least two (one assumption-bearing component)"
            )
    elif cutset:
        raise NonSeparatorError("empty normalized framework requires K=empty")

    pure, buckets = _bucket_attacks(normalized.attacks, cutset, components)
    paths = _MutablePaths(
        factual_normalizations=len(normalized.fact_attacked),
        qualifying_empty_cutsets=int(not cutset),
        qualifying_nonempty_cutsets=int(bool(cutset)),
        independent_residual_components=len(components) if len(components) >= 2 else 0,
    )
    lifts: list[AssumptionSet] = []
    branch_states = 0
    for selected_cut in _subsets(cutset):
        rejected_cut = cutset - selected_cut
        paths.selected_cut_states += int(bool(selected_cut))
        paths.rejected_cut_states += int(bool(rejected_cut))
        pure_attacked = _attacked_by(pure, selected_cut)
        if selected_cut & pure_attacked:
            continue

        choices_by_component = tuple(_subsets(component) for component in components)
        signature_values = tuple(
            tuple(
                sorted(
                    {
                        _attacked_by_component(bucket, cutset, selected_cut, choice)
                        & cutset
                        for choice in choices
                    },
                    key=_set_key,
                )
            )
            for bucket, choices in zip(buckets, choices_by_component, strict=True)
        )
        for signatures in product(*signature_values):
            branch_states += 1
            if branch_states > bounds.branch_states:
                raise ContractBoundsExceeded(
                    f"branch states: {branch_states} > {bounds.branch_states}"
                )
            paths.attacked_cut_signatures += sum(bool(item) for item in signatures)
            attacked_cut = frozenset().union(pure_attacked & cutset, *signatures)
            if selected_cut & attacked_cut:
                continue
            pure_obligations = tuple(
                attack
                for attack in pure
                if attack.target in selected_cut and not (attack.tail & attacked_cut)
            )
            if pure_obligations:
                continue

            local_families: list[tuple[AssumptionSet, ...]] = []
            valid_state = True
            for component, bucket, expected_signature, choices in zip(
                components,
                buckets,
                signatures,
                choices_by_component,
                strict=True,
            ):
                obligations = tuple(
                    attack
                    for attack in bucket
                    if attack.target in selected_cut
                    and not (attack.tail & attacked_cut)
                )
                paths.cut_defense_obligations_created += len(obligations)
                local: list[AssumptionSet] = []
                for choice in choices:
                    branch_states += 1
                    if branch_states > bounds.branch_states:
                        raise ContractBoundsExceeded(
                            f"branch states: {branch_states} > {bounds.branch_states}"
                        )
                    attacked = _attacked_by_component(
                        bucket, cutset, selected_cut, choice
                    )
                    signature = attacked & cutset
                    if signature != expected_signature:
                        continue
                    _count_cut_tail_paths(
                        bucket,
                        cutset,
                        selected_cut,
                        choice,
                        paths,
                    )
                    if choice & attacked or selected_cut & attacked:
                        continue
                    if not _defends_local_choices(
                        choice,
                        bucket,
                        attacked | attacked_cut,
                    ):
                        continue
                    if not all(
                        bool((obligation.tail & component) & attacked)
                        for obligation in obligations
                    ):
                        continue
                    paths.cut_defense_obligations_discharged += len(obligations)
                    local.append(choice)
                if not local:
                    valid_state = False
                    break
                local_families.append(tuple(local))
            if not valid_state:
                continue
            for local_product in product(*local_families):
                lifts.append(frozenset().union(selected_cut, *local_product))

    paths.deduplication_passes += 1
    unique_lifts = frozenset(lifts)
    paths.duplicate_lifts_removed += len(lifts) - len(unique_lifts)
    preferred = _maximal(unique_lifts)
    if len(preferred) >= 2:
        paths.incomparable_preferred_maxima += len(preferred)
    return CutsetComposition(
        cutset=cutset,
        normalized_assumptions=normalized.assumptions,
        components=components,
        admissible_lifts=unique_lifts,
        preferred_extensions=preferred,
        paths=_freeze_paths(paths),
    )


def exhaustive_admissible(
    framework: ABAFramework,
    *,
    bounds: SemanticBounds = SemanticBounds(),
) -> ExtensionFamily:
    """Independent exhaustive admissibility over bounded collective attacks."""
    normalized = _normalize(framework, bounds)
    admissible: set[AssumptionSet] = set()
    for candidate in _subsets(normalized.assumptions):
        attacked = _attacked_by(normalized.attacks, candidate)
        if candidate & attacked:
            continue
        if all(
            attack.target not in candidate or bool(attack.tail & attacked)
            for attack in normalized.attacks
        ):
            admissible.add(candidate)
    return frozenset(admissible)


def assert_support_oracle_admissible(
    framework: ABAFramework,
    actual: ExtensionFamily,
) -> None:
    """Fail closed unless the independent support-mask authority agrees."""
    state = _SupportState.from_framework(framework)
    expected = frozenset(
        state.extension(mask)
        for mask in range(1 << len(state.assumptions))
        if state.admissible(mask)
    )
    if actual != expected:
        missing = expected - actual
        extra = actual - expected
        raise OracleDisagreement(
            f"support admissibility disagreement: missing={_family_key(missing)!r}, "
            f"extra={_family_key(extra)!r}"
        )


def require_path_coverage(paths: PathCounters, required: frozenset[str]) -> None:
    """Fail closed when a frozen path counter is missing or unexercised."""
    known = {item.name for item in fields(PathCounters)}
    unknown = required - known
    if unknown:
        raise MissingPathCoverage(f"unknown path counters: {sorted(unknown)!r}")
    missing = sorted(name for name in required if getattr(paths, name) == 0)
    if missing:
        raise MissingPathCoverage(f"unexercised path counters: {missing!r}")


def assign_attack_owner(
    attack: CollectiveAttack,
    cutset: AssumptionSet,
    components: tuple[AssumptionSet, ...],
) -> int | None:
    """Return the unique residual owner, or ``None`` for a pure-cut attack."""
    residual = (attack.tail | frozenset({attack.target})) - cutset
    owners = [
        index for index, component in enumerate(components) if residual & component
    ]
    if not residual:
        return None
    if len(owners) != 1 or not residual <= components[owners[0]]:
        raise AmbiguousAttackOwnership(
            f"attack spans multiple residual components: {attack!r}"
        )
    return owners[0]


def _normalize(framework: ABAFramework, bounds: SemanticBounds) -> _NormalizedFramework:
    _check_bounds(framework, bounds)
    factual_closure = _closure(framework.rules, frozenset())
    fact_attacked = frozenset(
        assumption
        for assumption in framework.assumptions
        if framework.contrary[assumption] in factual_closure
    )
    assumptions = framework.assumptions - fact_attacked
    normalized_rules = tuple(
        sorted(
            (
                Rule(
                    tuple(
                        item for item in rule.antecedents if item not in factual_closure
                    ),
                    rule.consequent,
                    rule.kind,
                    rule.name,
                )
                for rule in framework.rules
                if not (frozenset(rule.antecedents) & fact_attacked)
            ),
            key=repr,
        )
    )
    attacks = _materialize_attacks(framework, assumptions, bounds)
    return _NormalizedFramework(
        assumptions=assumptions,
        contrary=dict(framework.contrary),
        fact_attacked=fact_attacked,
        factual_closure=factual_closure,
        rules=normalized_rules,
        attacks=attacks,
    )


def _check_bounds(framework: ABAFramework, bounds: SemanticBounds) -> None:
    checks = (
        ("assumptions", len(framework.assumptions), bounds.assumptions),
        (
            "non-assumption literals",
            len(framework.language - framework.assumptions),
            bounds.non_assumption_literals,
        ),
        ("rules", len(framework.rules), bounds.rules),
        (
            "body width",
            max((len(rule.antecedents) for rule in framework.rules), default=0),
            bounds.body_width,
        ),
    )
    for label, actual, limit in checks:
        if actual > limit:
            raise ContractBoundsExceeded(f"{label}: {actual} > {limit}")


def _materialize_attacks(
    framework: ABAFramework,
    assumptions: AssumptionSet,
    bounds: SemanticBounds,
) -> frozenset[CollectiveAttack]:
    attacks: set[CollectiveAttack] = set()
    subsets = _subsets(assumptions)
    for target in sorted(assumptions, key=repr):
        deriving = [
            support
            for support in subsets
            if framework.contrary[target] in _closure(framework.rules, support)
        ]
        minimal = [
            support
            for support in deriving
            if not any(other < support for other in deriving)
        ]
        attacks.update(CollectiveAttack(support, target) for support in minimal)
        if len(attacks) > bounds.collective_attacks:
            raise ContractBoundsExceeded(
                f"collective attacks: {len(attacks)} > {bounds.collective_attacks}"
            )
    return frozenset(attacks)


def _assumption_components(
    normalized: _NormalizedFramework,
    cutset: AssumptionSet,
) -> tuple[AssumptionSet, ...]:
    adjacency: dict[GraphNode, set[GraphNode]] = {}

    def connect(left: GraphNode, right: GraphNode) -> None:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)

    for literal in normalized.assumptions:
        if literal not in cutset:
            adjacency.setdefault(("literal", literal), set())
    for index, rule in enumerate(normalized.rules):
        rule_node: GraphNode = ("rule", index)
        adjacency.setdefault(rule_node, set())
        for literal in (rule.consequent, *rule.antecedents):
            literal_node: GraphNode = ("literal", literal)
            if literal not in cutset:
                connect(rule_node, literal_node)
    for assumption in normalized.assumptions:
        if assumption in cutset:
            continue
        contrary = normalized.contrary[assumption]
        if contrary not in cutset:
            connect(("literal", assumption), ("literal", contrary))

    seen: set[GraphNode] = set()
    components: list[AssumptionSet] = []
    for start in sorted(adjacency, key=repr):
        if start in seen:
            continue
        pending = [start]
        connected: set[GraphNode] = set()
        while pending:
            node = pending.pop()
            if node in connected:
                continue
            connected.add(node)
            pending.extend(adjacency.get(node, ()))
        seen.update(connected)
        members = frozenset(
            literal
            for kind, literal in connected
            if kind == "literal"
            and isinstance(literal, Literal)
            and literal in normalized.assumptions
            and literal not in cutset
        )
        if members:
            components.append(members)
    return tuple(sorted(components, key=_set_key))


def _bucket_attacks(
    attacks: frozenset[CollectiveAttack],
    cutset: AssumptionSet,
    components: tuple[AssumptionSet, ...],
) -> tuple[frozenset[CollectiveAttack], tuple[frozenset[CollectiveAttack], ...]]:
    pure: set[CollectiveAttack] = set()
    buckets = [set() for _ in components]
    for attack in attacks:
        owner = assign_attack_owner(attack, cutset, components)
        if owner is None:
            pure.add(attack)
        else:
            buckets[owner].add(attack)
    return frozenset(pure), tuple(frozenset(bucket) for bucket in buckets)


def _attacked_by(
    attacks: frozenset[CollectiveAttack], selected: AssumptionSet
) -> AssumptionSet:
    return frozenset(attack.target for attack in attacks if attack.tail <= selected)


def _attacked_by_component(
    attacks: frozenset[CollectiveAttack],
    cutset: AssumptionSet,
    selected_cut: AssumptionSet,
    selected_local: AssumptionSet,
) -> AssumptionSet:
    selected = selected_cut | selected_local
    return frozenset(
        attack.target
        for attack in attacks
        if attack.tail & cutset <= selected_cut
        and attack.tail - cutset <= selected_local
        and attack.tail <= selected
    )


def _defends_local_choices(
    selected: AssumptionSet,
    attacks: frozenset[CollectiveAttack],
    attacked: AssumptionSet,
) -> bool:
    return all(
        attack.target not in selected or bool(attack.tail & attacked)
        for attack in attacks
    )


def _count_cut_tail_paths(
    attacks: frozenset[CollectiveAttack],
    cutset: AssumptionSet,
    selected_cut: AssumptionSet,
    selected_local: AssumptionSet,
    paths: _MutablePaths,
) -> None:
    for attack in attacks:
        cut_tail = attack.tail & cutset
        if not cut_tail:
            continue
        if not cut_tail <= selected_cut:
            paths.inactive_collective_tails += 1
        elif attack.tail - cutset and attack.tail - cutset <= selected_local:
            paths.activated_collective_tails += 1


def _closure(
    rules: frozenset[Rule] | tuple[Rule, ...], premises: AssumptionSet
) -> frozenset[Literal]:
    closure: set[Literal] = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if (
                all(item in closure for item in rule.antecedents)
                and rule.consequent not in closure
            ):
                closure.add(rule.consequent)
                changed = True
    return frozenset(closure)


def _subsets(items: AssumptionSet) -> tuple[AssumptionSet, ...]:
    ordered = tuple(sorted(items, key=repr))
    return tuple(
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    )


def _maximal(candidates: ExtensionFamily) -> ExtensionFamily:
    return frozenset(
        candidate
        for candidate in candidates
        if not any(candidate < other for other in candidates)
    )


def _set_key(items: AssumptionSet) -> tuple[int, tuple[str, ...]]:
    return len(items), tuple(sorted(map(repr, items)))


def _family_key(items: ExtensionFamily) -> tuple[tuple[int, tuple[str, ...]], ...]:
    return tuple(sorted((_set_key(item) for item in items)))


def _freeze_paths(paths: _MutablePaths) -> PathCounters:
    return PathCounters(
        **{item.name: getattr(paths, item.name) for item in fields(PathCounters)}
    )
