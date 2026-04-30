"""Dynamic abstract argumentation with recompute-from-scratch queries."""

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
