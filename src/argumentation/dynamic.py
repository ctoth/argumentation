"""Dynamic abstract argumentation with recompute and incremental updates.

The recompute oracle remains the executable specification for update streams.
For single attack updates, this module also implements the influenced-set and
reduced-AF construction from Alfano, Greco, and Parisi 2017, Algorithm 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from argumentation.dung import ArgumentationFramework
from argumentation.enforcement import SemanticsName, extensions_for


UpdateKind = Literal["add_arg", "del_arg", "add_att", "del_att"]


@dataclass(frozen=True)
class DynamicUpdate:
    kind: UpdateKind
    source: str
    target: str | None = None


@dataclass(frozen=True)
class DynamicRecomputeOracle:
    """Recompute-from-scratch oracle for dynamic update streams."""

    framework: ArgumentationFramework

    def apply(self, update: DynamicUpdate) -> DynamicRecomputeOracle:
        dynamic = DynamicArgumentationFramework(self.framework)
        dynamic.apply(update)
        return DynamicRecomputeOracle(dynamic.framework)

    def apply_all(self, updates: tuple[DynamicUpdate, ...]) -> DynamicRecomputeOracle:
        oracle = self
        for update in updates:
            oracle = oracle.apply(update)
        return oracle

    def extensions(self, semantics: SemanticsName) -> tuple[frozenset[str], ...]:
        return extensions_for(self.framework, semantics)


@dataclass(frozen=True)
class IncrementalUpdateResult:
    """Result and instrumentation for a single incremental update."""

    original_framework: ArgumentationFramework
    updated_framework: ArgumentationFramework
    update: DynamicUpdate
    semantics: SemanticsName
    initial_extension: frozenset[str]
    influenced: frozenset[str]
    reduced_framework: ArgumentationFramework
    reduced_extension: frozenset[str] | None
    extension: frozenset[str] | None
    used_incremental: bool
    fallback_reason: str | None = None


@dataclass(frozen=True)
class DynamicAcceptanceAnswer:
    """Acceptance query answer with an extension witness when available."""

    argument: str
    semantics: SemanticsName
    mode: Literal["credulous", "skeptical"]
    accepted: bool
    witness: frozenset[str] | None = None
    counterexample: frozenset[str] | None = None


@dataclass
class DynamicArgumentationFramework:
    framework: ArgumentationFramework

    def add_argument(self, argument: str) -> None:
        self.framework = ArgumentationFramework(
            arguments=self.framework.arguments | {argument},
            defeats=self.framework.defeats,
        )

    def remove_argument(self, argument: str) -> None:
        remaining = self.framework.arguments - {argument}
        self.framework = ArgumentationFramework(
            arguments=remaining,
            defeats=frozenset(
                (attacker, target)
                for attacker, target in self.framework.defeats
                if attacker in remaining and target in remaining
            ),
        )

    def add_attack(self, attacker: str, target: str) -> None:
        self._require_arguments(attacker, target)
        self.framework = ArgumentationFramework(
            arguments=self.framework.arguments,
            defeats=self.framework.defeats | {(attacker, target)},
        )

    def remove_attack(self, attacker: str, target: str) -> None:
        self.framework = ArgumentationFramework(
            arguments=self.framework.arguments,
            defeats=self.framework.defeats - {(attacker, target)},
        )

    def query_credulous(
        self,
        argument: str,
        *,
        semantics: SemanticsName,
    ) -> bool:
        self._require_arguments(argument)
        return any(
            argument in extension
            for extension in extensions_for(self.framework, semantics)
        )

    def query_skeptical(
        self,
        argument: str,
        *,
        semantics: SemanticsName,
    ) -> bool:
        self._require_arguments(argument)
        extensions = extensions_for(self.framework, semantics)
        return bool(extensions) and all(argument in extension for extension in extensions)

    def apply(self, update: DynamicUpdate) -> None:
        if update.kind == "add_arg":
            self.add_argument(update.source)
        elif update.kind == "del_arg":
            self.remove_argument(update.source)
        elif update.kind == "add_att":
            if update.target is None:
                raise ValueError("add_att update requires a target")
            self.add_attack(update.source, update.target)
        elif update.kind == "del_att":
            if update.target is None:
                raise ValueError("del_att update requires a target")
            self.remove_attack(update.source, update.target)
        else:
            raise ValueError(f"unsupported dynamic update: {update.kind}")

    def _require_arguments(self, *arguments: str) -> None:
        unknown = sorted(set(arguments) - self.framework.arguments)
        if unknown:
            raise ValueError(f"unknown arguments: {unknown!r}")


def _apply_update(
    framework: ArgumentationFramework,
    update: DynamicUpdate,
) -> ArgumentationFramework:
    dynamic = DynamicArgumentationFramework(framework)
    dynamic.apply(update)
    return dynamic.framework


def _extension_status(
    framework: ArgumentationFramework,
    extension: frozenset[str],
) -> dict[str, Literal["IN", "OUT", "UN"]]:
    attacked = frozenset(
        target for attacker, target in framework.defeats if attacker in extension
    )
    return {
        argument: (
            "IN"
            if argument in extension
            else "OUT"
            if argument in attacked
            else "UN"
        )
        for argument in framework.arguments
    }


def _attacked_by_extension(
    framework: ArgumentationFramework,
    extension: frozenset[str],
) -> frozenset[str]:
    return frozenset(
        target for attacker, target in framework.defeats if attacker in extension
    )


def _reachable_from(
    framework: ArgumentationFramework,
    source: str,
) -> frozenset[str]:
    if source not in framework.arguments:
        return frozenset()
    reachable: set[str] = {source}
    frontier = [source]
    while frontier:
        current = frontier.pop()
        for attacker, target in framework.defeats:
            if attacker == current and target not in reachable:
                reachable.add(target)
                frontier.append(target)
    return frozenset(reachable)


def _first_extension(
    framework: ArgumentationFramework,
    semantics: SemanticsName,
) -> frozenset[str] | None:
    extensions = extensions_for(framework, semantics)
    if not extensions:
        return None
    return sorted(extensions, key=lambda extension: (len(extension), tuple(sorted(extension))))[0]


def _is_extension(
    framework: ArgumentationFramework,
    semantics: SemanticsName,
    candidate: frozenset[str],
) -> bool:
    return candidate in extensions_for(framework, semantics)


def _validate_single_attack_update(
    framework: ArgumentationFramework,
    update: DynamicUpdate,
) -> tuple[str, str]:
    if update.kind not in {"add_att", "del_att"}:
        raise ValueError("incremental_extension_update supports single attack updates")
    if update.target is None:
        raise ValueError(f"{update.kind} update requires a target")
    if update.source not in framework.arguments or update.target not in framework.arguments:
        raise ValueError("single attack updates require existing arguments")
    if update.kind == "add_att" and (update.source, update.target) in framework.defeats:
        raise ValueError("add_att update requires a missing attack")
    if update.kind == "del_att" and (update.source, update.target) not in framework.defeats:
        raise ValueError("del_att update requires an existing attack")
    return update.source, update.target


def influenced_arguments(
    framework: ArgumentationFramework,
    update: DynamicUpdate,
    *,
    semantics: SemanticsName,
    initial_extension: frozenset[str],
) -> frozenset[str]:
    """Return Alfano et al.'s influenced set for a single attack update."""
    attacker, target = _validate_single_attack_update(framework, update)
    updated = _apply_update(framework, update)
    if _is_extension(updated, semantics, initial_extension):
        return frozenset()

    reachable = _reachable_from(framework, target)
    if any(
        source != attacker
        and source in initial_extension
        and source not in reachable
        for source, attacked in framework.defeats
        if attacked == target
    ):
        return frozenset()

    influenced: set[str] = {target}
    while True:
        next_influenced = set(influenced)
        for source, attacked in framework.defeats:
            if source not in influenced:
                continue
            defended_from_outside_reach = any(
                defender in initial_extension and defender not in reachable
                for defender, defended in framework.defeats
                if defended == attacked
            )
            if not defended_from_outside_reach:
                next_influenced.add(attacked)
        if next_influenced == influenced:
            return frozenset(influenced)
        influenced = next_influenced


def reduced_framework(
    framework: ArgumentationFramework,
    update: DynamicUpdate,
    *,
    semantics: SemanticsName,
    initial_extension: frozenset[str],
) -> ArgumentationFramework:
    """Return Alfano et al.'s reduced AF for a single attack update."""
    influenced = influenced_arguments(
        framework,
        update,
        semantics=semantics,
        initial_extension=initial_extension,
    )
    if not influenced:
        return ArgumentationFramework(arguments=frozenset(), defeats=frozenset())

    updated = _apply_update(framework, update)
    old_attacked = _attacked_by_extension(framework, initial_extension)
    arguments = set(influenced)
    defeats = {
        defeat
        for defeat in updated.defeats
        if defeat[0] in influenced and defeat[1] in influenced
    }
    for source, target in updated.defeats:
        if source not in influenced and source in initial_extension and target in influenced:
            arguments.add(source)
            arguments.add(target)
            defeats.add((source, target))
        if (
            target in influenced
            and source not in influenced
            and source not in initial_extension
            and source not in old_attacked
        ):
            arguments.add(target)
            defeats.add((target, target))
    return ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
    )


def incremental_extension_update(
    framework: ArgumentationFramework,
    update: DynamicUpdate,
    *,
    semantics: SemanticsName,
    initial_extension: frozenset[str] | None = None,
) -> IncrementalUpdateResult:
    """Run Alfano et al.'s single-update incremental extension algorithm."""
    if semantics not in {"complete", "preferred", "stable", "grounded"}:
        raise ValueError(f"unsupported dynamic incremental semantics: {semantics}")
    _validate_single_attack_update(framework, update)
    if initial_extension is None:
        initial_extension = _first_extension(framework, semantics)
        if initial_extension is None:
            raise ValueError(f"no initial {semantics} extension exists")
    if not _is_extension(framework, semantics, initial_extension):
        raise ValueError("initial_extension is not an extension of the original framework")

    updated = _apply_update(framework, update)
    influenced = influenced_arguments(
        framework,
        update,
        semantics=semantics,
        initial_extension=initial_extension,
    )
    empty = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())
    if not influenced:
        return IncrementalUpdateResult(
            original_framework=framework,
            updated_framework=updated,
            update=update,
            semantics=semantics,
            initial_extension=initial_extension,
            influenced=influenced,
            reduced_framework=empty,
            reduced_extension=None,
            extension=initial_extension,
            used_incremental=True,
        )

    reduced = reduced_framework(
        framework,
        update,
        semantics=semantics,
        initial_extension=initial_extension,
    )
    reduced_extension = _first_extension(reduced, semantics)
    if reduced_extension is not None:
        candidate = (initial_extension - influenced) | reduced_extension
        if _is_extension(updated, semantics, candidate):
            return IncrementalUpdateResult(
                original_framework=framework,
                updated_framework=updated,
                update=update,
                semantics=semantics,
                initial_extension=initial_extension,
                influenced=influenced,
                reduced_framework=reduced,
                reduced_extension=reduced_extension,
                extension=candidate,
                used_incremental=True,
            )

    fallback_extension = _first_extension(updated, semantics)
    return IncrementalUpdateResult(
        original_framework=framework,
        updated_framework=updated,
        update=update,
        semantics=semantics,
        initial_extension=initial_extension,
        influenced=influenced,
        reduced_framework=reduced,
        reduced_extension=reduced_extension,
        extension=fallback_extension,
        used_incremental=False,
        fallback_reason=(
            "reduced_solver_no_extension"
            if reduced_extension is None
            else "combined_extension_invalid"
        ),
    )


@dataclass
class IncrementalDynamicArgumentationFramework:
    """Stateful dynamic AF using Algorithm 1 where its preconditions hold."""

    framework: ArgumentationFramework
    semantics: SemanticsName
    current_extension: frozenset[str] | None = None
    last_result: IncrementalUpdateResult | None = None

    def __post_init__(self) -> None:
        if self.current_extension is None:
            self.current_extension = _first_extension(self.framework, self.semantics)
        elif not _is_extension(self.framework, self.semantics, self.current_extension):
            raise ValueError("current_extension is not valid for the initial framework")

    def apply(self, update: DynamicUpdate) -> IncrementalUpdateResult:
        if update.kind in {"add_att", "del_att"}:
            try:
                result = incremental_extension_update(
                    self.framework,
                    update,
                    semantics=self.semantics,
                    initial_extension=self.current_extension,
                )
            except ValueError as exc:
                result = self._recompute_result(update, str(exc))
        else:
            result = self._recompute_result(update, "unsupported_update_kind")
        self.framework = result.updated_framework
        self.current_extension = result.extension
        self.last_result = result
        return result

    def query_credulous(self, argument: str) -> DynamicAcceptanceAnswer:
        self._require_argument(argument)
        extensions = extensions_for(self.framework, self.semantics)
        witness = next(
            (extension for extension in extensions if argument in extension),
            None,
        )
        return DynamicAcceptanceAnswer(
            argument=argument,
            semantics=self.semantics,
            mode="credulous",
            accepted=witness is not None,
            witness=witness,
            counterexample=None if witness is not None else (extensions[0] if extensions else None),
        )

    def query_skeptical(self, argument: str) -> DynamicAcceptanceAnswer:
        self._require_argument(argument)
        extensions = extensions_for(self.framework, self.semantics)
        counterexample = next(
            (extension for extension in extensions if argument not in extension),
            None,
        )
        accepted = bool(extensions) and counterexample is None
        return DynamicAcceptanceAnswer(
            argument=argument,
            semantics=self.semantics,
            mode="skeptical",
            accepted=accepted,
            witness=extensions[0] if accepted else None,
            counterexample=counterexample,
        )

    def _recompute_result(
        self,
        update: DynamicUpdate,
        reason: str,
    ) -> IncrementalUpdateResult:
        updated = _apply_update(self.framework, update)
        extension = _first_extension(updated, self.semantics)
        return IncrementalUpdateResult(
            original_framework=self.framework,
            updated_framework=updated,
            update=update,
            semantics=self.semantics,
            initial_extension=self.current_extension or frozenset(),
            influenced=frozenset(),
            reduced_framework=ArgumentationFramework(
                arguments=frozenset(),
                defeats=frozenset(),
            ),
            reduced_extension=None,
            extension=extension,
            used_incremental=False,
            fallback_reason=reason,
        )

    def _require_argument(self, argument: str) -> None:
        if argument not in self.framework.arguments:
            raise ValueError(f"unknown argument: {argument}")


def parse_update_stream(text: str) -> tuple[DynamicUpdate, ...]:
    """Parse a compact dynamic update stream."""
    updates: list[DynamicUpdate] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] in {"add_arg", "del_arg"} and len(parts) == 2:
            updates.append(DynamicUpdate(cast(UpdateKind, parts[0]), parts[1]))
            continue
        if parts[0] in {"add_att", "del_att"} and len(parts) == 3:
            updates.append(DynamicUpdate(cast(UpdateKind, parts[0]), parts[1], parts[2]))
            continue
        raise ValueError(f"invalid dynamic update line {line_number}: {line!r}")
    return tuple(updates)


def apply_update_stream(
    dynamic: DynamicArgumentationFramework,
    updates: tuple[DynamicUpdate, ...],
) -> DynamicArgumentationFramework:
    for update in updates:
        dynamic.apply(update)
    return dynamic
